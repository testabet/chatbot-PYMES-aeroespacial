DROP DATABASE IF EXISTS importaciones_aeroesp_2023;
CREATE DATABASE IF NOT EXISTS importaciones_aeroesp_2023;
USE importaciones_aeroesp_2023;

-- Tabla de paises  (la proyeccion de crecimiento, ECI_SITC y ECI_RANK_SITC son solo del 2023)

CREATE TABLE paises(
    id_pais SMALLINT UNSIGNED NOT NULL,
    codigo_ISO CHAR(3)NOT NULL COMMENT 'Código ISO 3 letras, ej: ARG, BRA',
    nombre VARCHAR(100) NOT NULL,
    proyeccion_de_crecimiento DECIMAL(4,3) COMMENT 'Proyeccion de crecimiento o proyección econocómica basada en el indice de complejidad económica',
    eci_sitc DECIMAL(4,3) NOT NULL COMMENT 'Indice de complejidad económica calculado utilizando la clasificación SITC de productos',
    eci_rank_sitc TINYINT UNSIGNED COMMENT 'Ranking global de complejidad económica calculado utilizando la clasificación SITC de productos',
    PRIMARY KEY (id_pais),
    INDEX idx_nombre (nombre), -- Ayuda a la IA a filtrar por nombre rápido
    INDEX idx_iso (codigo_ISO)
    );

-- Tabla de productos segun codigo SITC 4 digitos
CREATE TABLE productos (
    id_producto SMALLINT UNSIGNED NOT NULL,
    codigo_sitc VARCHAR(4) NOT NULL COMMENT 'Código de clasificaicón uniforme para el comercio internacional (SITC por sus siglas en ingles)',
    nombre_producto VARCHAR(200) NOT NULL COMMENT 'Descripción completa del producto aeroespacial',
    valor_total_exportacion_usd BIGINT COMMENT 'Valor total global de exportacion en el año 2023',
    PRIMARY KEY (id_producto),
    INDEX idx_sitc (codigo_sitc)
    );

-- Tabla de importaciones
CREATE TABLE importaciones (
    id_importacion INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_pais_exportador SMALLINT UNSIGNED NOT NULL COMMENT 'FK: País que vende',
    id_pais_importador SMALLINT UNSIGNED NOT NULL COMMENT 'FK: País que compra',
    id_producto SMALLINT UNSIGNED NOT NULL,
    anio  YEAR NOT NULL,
    valor_importacion_usd BIGINT UNSIGNED NOT NULL COMMENT 'Valor de la transacción en Dólares',
    PRIMARY KEY (id_importacion),
    
    -- Relación con Países
    CONSTRAINT fk_pais_importador 
    FOREIGN KEY (id_pais_importador) REFERENCES paises(id_pais),

    CONSTRAINT fk_pais_exportador 
    FOREIGN KEY (id_pais_exportador) REFERENCES paises(id_pais),
    
    -- Relación con Productos
    CONSTRAINT fk_producto 
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);



