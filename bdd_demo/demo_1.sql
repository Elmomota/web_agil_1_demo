-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 26-05-2025 a las 07:38:45
-- Versión del servidor: 10.4.25-MariaDB
-- Versión de PHP: 7.4.30
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;



-- TABLAS AUXILIARES
CREATE TABLE tipo_usuario (
    id_tipo_usuario INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tipo_rol_proyecto (
    id_rol_proyecto INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE estado_proyecto (
    id_estado INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE estado_orden_compra (
    id_estado INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 

CREATE TABLE tipo_movimiento (
    id_tipo_movimiento INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE region (
    id_region INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE comuna (
    id_comuna INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_region INT NOT NULL,
    FOREIGN KEY (id_region) REFERENCES region(id_region)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ALMACENES
CREATE TABLE almacen (
    id_almacen INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    id_comuna INT NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_comuna) REFERENCES comuna(id_comuna)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE codigos_recuperacion (
  id int(11) AUTO_INCREMENT PRIMARY KEY,
  correo varchar(255) NOT NULL UNIQUE,
  codigo varchar(6) NOT NULL,
  expiracion datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- USUARIOS Y UBICACIÓN
CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    direccion TEXT,
    id_comuna INT NOT NULL,
    id_tipo_usuario INT NOT NULL,
    id_almacen INT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_comuna) REFERENCES comuna(id_comuna),
    FOREIGN KEY (id_tipo_usuario) REFERENCES tipo_usuario(id_tipo_usuario),
    FOREIGN KEY (id_almacen) REFERENCES almacen(id_almacen)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- CATEGORÍAS
CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PROVEEDORES  / SE OMITE EN EL CASO
CREATE TABLE proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    direccion TEXT,
    id_comuna INT NOT NULL,
    condiciones_pago TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_comuna) REFERENCES comuna(id_comuna)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PROYECTOS
CREATE TABLE proyecto (
    id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    id_estado INT NOT NULL,
    id_usuario_responsable INT NOT NULL,
    FOREIGN KEY (id_estado) REFERENCES estado_proyecto(id_estado),
    FOREIGN KEY (id_usuario_responsable) REFERENCES usuario(id_usuario)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- RELACIÓN USUARIO-PROYECTO
CREATE TABLE usuario_proyecto (
    id_usuario INT NOT NULL,
    id_proyecto INT NOT NULL,
    id_rol_proyecto INT NOT NULL,
    PRIMARY KEY (id_usuario, id_proyecto),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto),
    FOREIGN KEY (id_rol_proyecto) REFERENCES tipo_rol_proyecto(id_rol_proyecto)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PIEZAS
CREATE TABLE pieza (
    id_pieza INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    numero_serie VARCHAR(100),
	imagen_referencial LONGBLOB,
    stock_minimo INT NOT NULL DEFAULT 0,
    id_categoria INT NOT NULL,
    fecha_vencimiento DATE,
    alerta_vencimiento BOOLEAN NOT NULL DEFAULT FALSE,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- INVENTARIO EN ALMACÉN (relación N:N pieza-almacén)
CREATE TABLE inventario_almacen (
    id_almacen INT NOT NULL,
    id_pieza INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_almacen, id_pieza),
    FOREIGN KEY (id_almacen) REFERENCES almacen(id_almacen),
    FOREIGN KEY (id_pieza) REFERENCES pieza(id_pieza)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- HISTORIAL DE PRECIO / Corregido
CREATE TABLE historial_precio (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_pieza INT NOT NULL,

    precio INT NOT NULL,
    fecha_compra DATE NOT NULL,
    FOREIGN KEY (id_pieza) REFERENCES pieza(id_pieza)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- KITS
CREATE TABLE kit (
    id_kit INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE kit_pieza (
    id_kit INT NOT NULL,
    id_pieza INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_kit, id_pieza),
    FOREIGN KEY (id_kit) REFERENCES kit(id_kit),
    FOREIGN KEY (id_pieza) REFERENCES pieza(id_pieza)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- USO DE KITS EN PROYECTOS
CREATE TABLE uso_kit (
    id_uso INT AUTO_INCREMENT PRIMARY KEY,
    id_kit INT NOT NULL,
    id_proyecto INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_kit) REFERENCES kit(id_kit),
    FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MOVIMIENTOS DE INVENTARIO
CREATE TABLE movimiento_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_pieza INT NOT NULL,
    id_tipo_movimiento INT NOT NULL,
    cantidad INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    id_proyecto INT NULL,
    observaciones TEXT,
    id_almacen INT NOT NULL,
    FOREIGN KEY (id_pieza) REFERENCES pieza(id_pieza),
    FOREIGN KEY (id_tipo_movimiento) REFERENCES tipo_movimiento(id_tipo_movimiento),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto),
    FOREIGN KEY (id_almacen) REFERENCES almacen(id_almacen)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;





-- ÓRDENES DE COMPRA / SE OMITE PORQUE SE RELACIONA CON LA LOGICA DE PROVEEDORES
CREATE TABLE orden_compra (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    fecha DATE NOT NULL,
    id_estado INT NOT NULL,
    total INT NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor),
    FOREIGN KEY (id_estado) REFERENCES estado_orden_compra(id_estado)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE detalle_orden_compra (
    id_detalle INT NOT NULL,
    id_orden INT NOT NULL,
    id_pieza INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario INT NOT NULL,
    PRIMARY KEY (id_detalle, id_orden),
    FOREIGN KEY (id_orden) REFERENCES orden_compra(id_orden),
    FOREIGN KEY (id_pieza) REFERENCES pieza(id_pieza)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;




--INSERT INTO `codigos_recuperacion` (`id`, `correo`, `codigo`, `expiracion`) VALUES
--(7, 'al.barreras@duocuc.cl', '800834', '2025-05-26 00:53:25');

-- --------------------------------------------------------

--

--INSERT INTO `usuarios` (`id_usuario`, `correo`, `contrasena`, `nombre`, `rol`) VALUES
--(1, 'al.barreras@duocuc.cl', 'fdb93b3f8adb19ce54346e91c00bc944e1c7f6fe41ad0d9ab803b72d4a16a703', 'Admin', 1);

--



/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
