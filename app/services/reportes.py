from app.db.db_connection import get_connection
import pandas as pd
from datetime import datetime
from fastapi import HTTPException
from pydantic import EmailStr
from app.utils.email import enviar_correo_con_adjunto  
import os

def obtener_estado_inventario():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            p.id_pieza,
            p.nombre,
            p.descripcion,
            p.stock_minimo,
            ia.cantidad AS stock_actual,
            a.nombre AS almacen,
            c.nombre AS categoria,
            CASE 
                WHEN ia.cantidad <= p.stock_minimo THEN 'BAJO STOCK'
                ELSE 'OK'
            END AS estado_stock
        FROM pieza p
        JOIN inventario_almacen ia ON p.id_pieza = ia.id_pieza
        JOIN almacen a ON ia.id_almacen = a.id_almacen
        JOIN categoria c ON p.id_categoria = c.id_categoria
        WHERE p.estado = TRUE
        ORDER BY a.nombre, c.nombre, p.nombre;
        """

        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close() 
        conn.close()
        return resultados

    except Exception as e:
        print("Error en obtener_estado_inventario:", e)
        return []

def obtener_stock_bajo():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            p.id_pieza,
            p.nombre,
            ia.cantidad AS stock_actual,
            p.stock_minimo,
            a.nombre AS almacen,
            c.nombre AS categoria
        FROM pieza p
        JOIN inventario_almacen ia ON p.id_pieza = ia.id_pieza
        JOIN almacen a ON ia.id_almacen = a.id_almacen
        JOIN categoria c ON p.id_categoria = c.id_categoria
        WHERE ia.cantidad <= p.stock_minimo AND p.estado = TRUE
        ORDER BY ia.cantidad ASC;
        """

        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados

    except Exception as e:
        print("Error en obtener_stock_bajo:", e)
        return []

def obtener_tendencias_consumo():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            p.id_pieza,
            p.nombre,
            p.descripcion,
            COUNT(mi.id_movimiento) AS veces_utilizada,
            SUM(mi.cantidad) AS total_usada,
            c.nombre AS categoria
        FROM movimiento_inventario mi
        JOIN pieza p ON mi.id_pieza = p.id_pieza
        JOIN categoria c ON p.id_categoria = c.id_categoria
        WHERE mi.id_tipo_movimiento = 2
        GROUP BY p.id_pieza
        ORDER BY total_usada DESC;
        """

        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados

    except Exception as e:
        print("Error en obtener_tendencias_consumo:", e)
        return []

# NUEVO: Reporte General
def obtener_reporte_general():
    """
    Retorna un reporte combinado con todos los bloques:
    - Estado del inventario
    - Stock bajo
    - Tendencias de consumo
    """
    return {
        "estado_inventario": obtener_estado_inventario(),
        "stock_bajo": obtener_stock_bajo(),
        "tendencias_consumo": obtener_tendencias_consumo()
    }


#generar reportes con excel


output_dir = "reportes_generados"
os.makedirs(output_dir, exist_ok=True)

def generar_excel_reporte_general(data: dict) -> str:
    output_dir = "reportes_generados"
    os.makedirs(output_dir, exist_ok=True)

    nombre_archivo = os.path.join(
        output_dir, f"reporte_general_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    try:
        with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
            # Estado del inventario
            estado = data.get("estado_inventario", [])
            if estado:
                pd.DataFrame(estado).to_excel(writer, sheet_name="Estado Inventario", index=False)

            # Stock bajo
            stock_bajo = data.get("stock_bajo", [])
            if stock_bajo:
                pd.DataFrame(stock_bajo).to_excel(writer, sheet_name="Stock Bajo", index=False)

            # Tendencias
            tendencias = data.get("tendencias_consumo", [])
            if tendencias:
                pd.DataFrame(tendencias).to_excel(writer, sheet_name="Tendencias Consumo", index=False)

    except Exception as e:
        print("Error al generar el archivo Excel:", e)
        raise

    return nombre_archivo

def generar_excel_estado_inventario() -> str:
    data = obtener_estado_inventario()
    path = os.path.join(output_dir, f"estado_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    pd.DataFrame(data).to_excel(path, index=False)
    return path

def generar_excel_stock_bajo() -> str:
    data = obtener_stock_bajo()
    path = os.path.join(output_dir, f"stock_bajo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    pd.DataFrame(data).to_excel(path, index=False)
    return path

def generar_excel_tendencias() -> str:
    data = obtener_tendencias_consumo()
    path = os.path.join(output_dir, f"tendencias_consumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    pd.DataFrame(data).to_excel(path, index=False)
    return path




def generar_y_enviar_reporte_general(destinatario: EmailStr):
    """
    Genera el reporte general, crea un archivo Excel y lo envía por correo al destinatario.
    """
    try:
        data = obtener_reporte_general()
        archivo = generar_excel_reporte_general(data)

        cuerpo = (
            f"Estimado/a,\n\nAdjunto encontrará el reporte general de inventario solicitado.\n"
            f"Incluye:\n"
            f"• Estado actual del inventario\n"
            f"• Piezas con stock bajo\n"
            f"• Tendencias de consumo\n\n"
            f"Saludos,\nSistema de Inventario - Maestranzas Unidos S.A."
        )

        enviar_correo_con_adjunto(
            destinatario=destinatario,
            asunto="📊 Reporte General de Inventario",
            cuerpo=cuerpo,
            adjunto_path=archivo
        )

        return {"mensaje": f"Reporte general enviado correctamente a {destinatario}"}

    except Exception as e:
        print("Error al enviar reporte general:", e)
        raise HTTPException(status_code=500, detail="No se pudo generar o enviar el reporte general")


def generar_y_enviar_reporte_estado(destinatario: EmailStr):
    """
    Genera el reporte de estado de inventario y lo envía por correo.
    """
    try:
        archivo = generar_excel_estado_inventario()

        cuerpo = (
            f"Estimado/a,\n\nAdjunto encontrará el reporte de estado actual del inventario.\n\n"
            f"Saludos,\nSistema de Inventario - Maestranzas Unidos S.A."
        )

        enviar_correo_con_adjunto(
            destinatario=destinatario,
            asunto="📦 Estado del Inventario",
            cuerpo=cuerpo,
            adjunto_path=archivo
        )

        return {"mensaje": f"Reporte de estado de inventario enviado a {destinatario}"}

    except Exception as e:
        print("Error al enviar reporte estado:", e)
        raise HTTPException(status_code=500, detail="No se pudo enviar el reporte de estado")


def generar_y_enviar_reporte_stock_bajo(destinatario: EmailStr):
    """
    Genera el reporte de stock bajo y lo envía por correo.
    """
    try:
        archivo = generar_excel_stock_bajo()

        cuerpo = (
            f"Estimado/a,\n\nAdjunto encontrará el reporte de piezas con stock bajo.\n\n"
            f"Por favor, verificar reposición según las alertas mostradas.\n\n"
            f"Saludos,\nSistema de Inventario - Maestranzas Unidos S.A."
        )

        enviar_correo_con_adjunto(
            destinatario=destinatario,
            asunto="⚠️ Alerta de Stock Bajo",
            cuerpo=cuerpo,
            adjunto_path=archivo
        )

        return {"mensaje": f"Reporte de stock bajo enviado a {destinatario}"}

    except Exception as e:
        print("Error al enviar reporte de stock bajo:", e)
        raise HTTPException(status_code=500, detail="No se pudo enviar el reporte de stock bajo")


def generar_y_enviar_reporte_tendencias(destinatario: EmailStr):
    """
    Genera el reporte de tendencias de consumo y lo envía por correo.
    """
    try:
        archivo = generar_excel_tendencias()

        cuerpo = (
            f"Estimado/a,\n\nAdjunto encontrará el reporte de tendencias de consumo de piezas.\n"
            f"Muestra qué componentes son más utilizados para facilitar decisiones de reposición.\n\n"
            f"Saludos,\nSistema de Inventario - Maestranzas Unidos S.A."
        )

        enviar_correo_con_adjunto(
            destinatario=destinatario,
            asunto="📈 Tendencias de Consumo",
            cuerpo=cuerpo,
            adjunto_path=archivo
        )

        return {"mensaje": f"Reporte de tendencias enviado a {destinatario}"}

    except Exception as e:
        print("Error al enviar reporte de tendencias:", e)
        raise HTTPException(status_code=500, detail="No se pudo enviar el reporte de tendencias")
