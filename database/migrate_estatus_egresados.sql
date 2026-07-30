ALTER TABLE practicas_profesionales
    ADD COLUMN oficio_campo BOOLEAN NOT NULL DEFAULT FALSE AFTER estado,
    ADD COLUMN horas_campo INT NULL AFTER oficio_campo;

ALTER TABLE servicio_social
    ADD COLUMN carta_unifront BOOLEAN NOT NULL DEFAULT FALSE AFTER estado,
    ADD COLUMN carta_procedencia BOOLEAN NOT NULL DEFAULT FALSE AFTER carta_unifront;

CREATE TABLE documentos_egresado (
    id_documento BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documento_egresado_alumno
        FOREIGN KEY (id_alumno) REFERENCES alumnos(id_alumno),
    CONSTRAINT uq_documento_egresado_tipo UNIQUE (id_alumno, tipo)
) ENGINE=InnoDB;
