from datetime import datetime
from app.db.db_connection import get_connection
from app.utils.email import notificar_admin_pieza_vencida, notificar_gestores_remocion

def verificar_piezas_vencidas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Buscar piezas vencidas activas
    cursor.execute('''
        SELECT p.id_pieza, p.nombre, p.fecha_vencimiento, ia.id_almacen
        FROM pieza p
        JOIN inventario_almacen ia ON p.id_pieza = ia.id_pieza
        WHERE p.estado = TRUE AND p.fecha_vencimiento IS NOT NULL AND p.fecha_vencimiento < CURDATE()
    ''')
    piezas_vencidas = cursor.fetchall()

    for pieza in piezas_vencidas:
        id_pieza = pieza['id_pieza']
        nombre = pieza['nombre']
        id_almacen = pieza['id_almacen']

        # 1. Desactivar la pieza
        cursor.execute('''
            UPDATE pieza
            SET estado = FALSE, alerta_vencimiento = TRUE
            WHERE id_pieza = %s
        ''', (id_pieza,))

        # 2. Obtener el correo del administrador activo (id_tipo_usuario = 1)
        cursor.execute('''
            SELECT correo, p_nombre
            FROM usuario
            WHERE id_tipo_usuario = 1 AND estado = TRUE
            LIMIT 1
        ''')
        admin = cursor.fetchone()
        if admin:
            notificar_admin_pieza_vencida(admin['correo'], admin['p_nombre'], nombre, pieza['fecha_vencimiento'])

        # 3. Notificar a los gestores de inventario de ese almacén
        cursor.execute('''
            SELECT correo, p_nombre
            FROM usuario
            WHERE id_tipo_usuario = 2 AND id_almacen = %s AND estado = TRUE
        ''', (id_almacen,))
        gestores = cursor.fetchall()
        for gestor in gestores:
            notificar_gestores_remocion(gestor['correo'], gestor['p_nombre'], nombre)

    conn.commit()
    cursor.close()
    conn.close()
