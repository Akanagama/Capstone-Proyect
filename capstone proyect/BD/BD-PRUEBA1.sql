-- 1. CREAR LA BASE DE DATOS
CREATE DATABASE KialChickenDB;
GO

-- Le decimos a SQL que use esta nueva base de datos
USE KialChickenDB;
GO

-- 2. CREACIÓN DE TABLAS PRINCIPALES

-- Tabla de Usuarios (Seguridad)
CREATE TABLE Usuarios (
    UsuarioID INT IDENTITY(1,1) PRIMARY KEY,
    NombreCompleto VARCHAR(100) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(50) NOT NULL, -- Para la V1 lo haremos simple
    Rol VARCHAR(20) NOT NULL -- 'admin' o 'cajero'
);

-- Tabla de Clientes
CREATE TABLE Clientes (
    ClienteID INT IDENTITY(1,1) PRIMARY KEY,
    TipoDocumento VARCHAR(20), -- DNI o RUC
    NumeroDocumento VARCHAR(20) UNIQUE NOT NULL,
    NombreCompleto VARCHAR(150) NOT NULL,
    Direccion VARCHAR(200),
    Telefono VARCHAR(20)
);

-- Tabla del Menú/Platos
CREATE TABLE Platos (
    PlatoID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Categoria VARCHAR(50) NOT NULL,
    Precio DECIMAL(10,2) NOT NULL,
    Estado VARCHAR(20) DEFAULT 'Activo'
);

-- Tabla de Insumos (Crucial para tu IA y el inventario)
CREATE TABLE Insumos (
    InsumoID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    UnidadMedida VARCHAR(20) NOT NULL, -- Kg, Litros, Unidades
    StockActual DECIMAL(10,2) NOT NULL,
    StockMinimo DECIMAL(10,2) NOT NULL -- Para saber cuándo lanzar alerta
);

-- Tabla de Ventas (Cabecera del comprobante)
CREATE TABLE Ventas (
    VentaID INT IDENTITY(1,1) PRIMARY KEY,
    Fecha Varchar(50) DEFAULT GETDATE(),
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    ClienteID INT NULL FOREIGN KEY REFERENCES Clientes(ClienteID), -- NULL porque puede ser venta rápida sin cliente
    MetodoPago VARCHAR(50) NOT NULL,
    SubTotal DECIMAL(10,2) NOT NULL,
    IGV DECIMAL(10,2) NOT NULL,
    Total DECIMAL(10,2) NOT NULL
);

-- Tabla de Detalle de Ventas (Qué platos llevó en esa venta específica)
CREATE TABLE DetalleVentas (
    DetalleID INT IDENTITY(1,1) PRIMARY KEY,
    VentaID INT FOREIGN KEY REFERENCES Ventas(VentaID),
    PlatoID INT FOREIGN KEY REFERENCES Platos(PlatoID),
    Cantidad INT NOT NULL,
    PrecioUnitario DECIMAL(10,2) NOT NULL,
    SubTotal DECIMAL(10,2) NOT NULL
);
GO

-- ==========================================
-- 3. INSERTAR DATOS DE PRUEBA (DUMMY DATA)
-- ==========================================

-- Insertamos los usuarios que configuramos en tu Frontend
INSERT INTO Usuarios (NombreCompleto, Username, Password, Rol)
VALUES 
('Arturo Medina', 'admin', '123', 'admin'),
('Arturo Bravo', 'arturo', '123', 'cajero');

-- Insertamos los platos de tu botones táctiles
INSERT INTO Platos (Nombre, Categoria, Precio)
VALUES 
('1/4 de Pollo', 'Pollos a la Brasa', 18.00),
('1/2 Pollo', 'Pollos a la Brasa', 32.00),
('Pollo Entero', 'Pollos a la Brasa', 65.00),
('Chicha 1L', 'Bebidas', 12.00),
('Porción Papas', 'Guarniciones', 10.00);

-- Insertamos el inventario base para el dashboard
INSERT INTO Insumos (Nombre, UnidadMedida, StockActual, StockMinimo)
VALUES 
('Pollos Enteros Macerados', 'Unidades', 45.00, 10.00),
('Papas Amarillas', 'Sacos 50kg', 15.00, 5.00),
('Aceite Vegetal', 'Bidones 20L', 2.00, 4.00);
GO