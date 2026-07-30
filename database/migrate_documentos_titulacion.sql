CREATE TABLE documentos_titulacion (
    id_documento_titulacion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_titulacion BIGINT NOT NULL,
    requisito VARCHAR(100) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    observaciones TEXT,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documento_titulacion
        FOREIGN KEY (id_titulacion)
        REFERENCES titulacion(id_titulacion)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_documentos_titulacion_requisito
    ON documentos_titulacion(id_titulacion, requisito);
