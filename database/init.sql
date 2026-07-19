SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS unifront
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE TABLE usuarios (
    id_usuario BIGINT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    correo VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE roles (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE usuario_roles (
    id_usuario BIGINT,
    id_rol INT,

    PRIMARY KEY (id_usuario, id_rol),

    CONSTRAINT fk_usuario_roles_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    CONSTRAINT fk_usuario_roles_rol
        FOREIGN KEY (id_rol)
        REFERENCES roles(id_rol)
) ENGINE=InnoDB;

CREATE TABLE carreras (
    id_carrera INT PRIMARY KEY AUTO_INCREMENT,
    clave VARCHAR(20) UNIQUE,
    rvoe VARCHAR(30) UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    nivel ENUM('TSU','LICENCIATURA','MAESTRIA', 'INGENIERIA') NOT NULL,
    duracion_cuatrimestres INT NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    logo VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE planes_estudio (
    id_plan INT PRIMARY KEY AUTO_INCREMENT,
    id_carrera INT NOT NULL,
    nombre_plan VARCHAR(100) NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    vigente BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_plan_carrera
        FOREIGN KEY (id_carrera)
        REFERENCES carreras(id_carrera)
) ENGINE=InnoDB;

CREATE TABLE cuatrimestres (
    id_cuatrimestre INT PRIMARY KEY AUTO_INCREMENT,
    numero INT NOT NULL,
    nombre VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE materias (
    id_materia BIGINT PRIMARY KEY AUTO_INCREMENT,
    clave VARCHAR(20) UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    creditos DECIMAL(5,2) NOT NULL,
    estado BOOLEAN DEFAULT TRUE,

    CONSTRAINT chk_creditos
        CHECK (creditos >= 0)
) ENGINE=InnoDB;

CREATE TABLE plan_materias (
    id_plan_materia BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_plan INT NOT NULL,
    id_materia BIGINT NOT NULL,
    id_cuatrimestre INT NOT NULL,
    obligatoria BOOLEAN DEFAULT TRUE,

    CONSTRAINT uq_plan_materia
        UNIQUE (id_plan, id_materia),

    CONSTRAINT fk_plan_materias_plan
        FOREIGN KEY (id_plan)
        REFERENCES planes_estudio(id_plan),

    CONSTRAINT fk_plan_materias_materia
        FOREIGN KEY (id_materia)
        REFERENCES materias(id_materia),

    CONSTRAINT fk_plan_materias_cuatrimestre
        FOREIGN KEY (id_cuatrimestre)
        REFERENCES cuatrimestres(id_cuatrimestre)
) ENGINE=InnoDB;

CREATE TABLE materias_prerrequisito (
    id_prerrequisito BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_materia BIGINT NOT NULL,
    id_materia_requerida BIGINT NOT NULL,
    tipo ENUM('OBLIGATORIO','RECOMENDADO') NOT NULL,

    CONSTRAINT fk_prerrequisito_materia
        FOREIGN KEY (id_materia)
        REFERENCES materias(id_materia),

    CONSTRAINT fk_prerrequisito_requerida
        FOREIGN KEY (id_materia_requerida)
        REFERENCES materias(id_materia)
) ENGINE=InnoDB;

CREATE TABLE alumnos (
    id_alumno BIGINT PRIMARY KEY AUTO_INCREMENT,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    numero_control VARCHAR(30) UNIQUE,
    id_usuario BIGINT NOT NULL,
    id_carrera INT NOT NULL,
    id_plan INT NOT NULL,
    fecha_nacimiento DATE,
    ciudad_nacimiento VARCHAR(100),
    municipio_nacimiento VARCHAR(100),
    nacionalidad VARCHAR(100),
    sexo ENUM('M','F'),
    curp VARCHAR(18),
    direccion TEXT,
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    correo_contacto VARCHAR(150),
    fecha_ingreso DATE,
    estatus ENUM('ACTIVO','BAJA','EGRESADO','TITULADO') DEFAULT 'ACTIVO',
    foto VARCHAR(255),

    CONSTRAINT fk_alumno_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    CONSTRAINT fk_alumno_carrera
        FOREIGN KEY (id_carrera)
        REFERENCES carreras(id_carrera),

    CONSTRAINT fk_alumno_plan
        FOREIGN KEY (id_plan)
        REFERENCES planes_estudio(id_plan)
) ENGINE=InnoDB;

CREATE TABLE procedencia_academica (
    id_procedencia BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT NOT NULL,
    escuela_procedencia VARCHAR(255),
    nivel_academico ENUM('BACHILLERATO','UNIVERSIDAD','OTRO'),
    estado_procedencia VARCHAR(100),
    promedio_general DECIMAL(5,2),
    fecha_egreso DATE,

    CONSTRAINT chk_promedio_procedencia
        CHECK (promedio_general >= 0 AND promedio_general <= 100),

    CONSTRAINT fk_procedencia_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno)
) ENGINE=InnoDB;

CREATE TABLE tutores (
    id_tutor BIGINT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    parentesco VARCHAR(50),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    ocupacion VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE alumno_tutor (
    id_alumno BIGINT,
    id_tutor BIGINT,

    PRIMARY KEY (id_alumno, id_tutor),

    CONSTRAINT fk_alumno_tutor_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_alumno_tutor_tutor
        FOREIGN KEY (id_tutor)
        REFERENCES tutores(id_tutor)
) ENGINE=InnoDB;

CREATE TABLE contactos_emergencia (
    id_contacto BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    parentesco VARCHAR(50),
    telefono VARCHAR(20),
    correo VARCHAR(150),
    direccion TEXT,
    contacto_principal BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_contacto_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno)
) ENGINE=InnoDB;

CREATE TABLE seguros_medicos (
    id_seguro BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT NOT NULL,
    tiene_seguro BOOLEAN DEFAULT FALSE,
    institucion VARCHAR(150),
    numero_poliza VARCHAR(100),

    CONSTRAINT fk_seguro_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno)
) ENGINE=InnoDB;

CREATE TABLE recepcion_documentos (
    id_recepcion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT NOT NULL,
    ficha_inscripcion BOOLEAN DEFAULT FALSE,
    acta_original BOOLEAN DEFAULT FALSE,
    acta_copias BOOLEAN DEFAULT FALSE,
    certificado_original BOOLEAN DEFAULT FALSE,
    constancia_terminacion BOOLEAN DEFAULT FALSE,
    fotografias BOOLEAN DEFAULT FALSE,
    curp_documento BOOLEAN DEFAULT FALSE,
    fecha_recepcion DATE,
    recibido_por BIGINT,
    observaciones TEXT,

    CONSTRAINT fk_recepcion_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_recepcion_usuario
        FOREIGN KEY (recibido_por)
        REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE docentes (
    id_docente BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_usuario BIGINT NOT NULL,
    numero_empleado VARCHAR(20) UNIQUE,
    especialidad VARCHAR(150),
    grado_academico VARCHAR(100),
    fecha_ingreso DATE,
    estado BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_docente_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE periodos (
    id_periodo INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    fecha_inicio DATE,
    fecha_fin DATE,
    estado ENUM('ACTIVO','CERRADO') DEFAULT 'ACTIVO'
) ENGINE=InnoDB;

CREATE TABLE grupos (
    id_grupo BIGINT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    id_carrera INT,
    id_cuatrimestre INT,
    turno ENUM('MATUTINO','VESPERTINO'),

    CONSTRAINT fk_grupo_carrera
        FOREIGN KEY (id_carrera)
        REFERENCES carreras(id_carrera),

    CONSTRAINT fk_grupo_cuatrimestre
        FOREIGN KEY (id_cuatrimestre)
        REFERENCES cuatrimestres(id_cuatrimestre)
) ENGINE=InnoDB;

CREATE TABLE grupos_materias (
    id_grupo_materia BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_grupo BIGINT,
    id_materia BIGINT,
    id_docente BIGINT,
    id_periodo INT,
    aula VARCHAR(20),
    cupo_maximo INT,

    CONSTRAINT fk_grupo_materia_grupo
        FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo),

    CONSTRAINT fk_grupo_materia_materia
        FOREIGN KEY (id_materia)
        REFERENCES materias(id_materia),

    CONSTRAINT fk_grupo_materia_docente
        FOREIGN KEY (id_docente)
        REFERENCES docentes(id_docente),

    CONSTRAINT fk_grupo_materia_periodo
        FOREIGN KEY (id_periodo)
        REFERENCES periodos(id_periodo)
) ENGINE=InnoDB;

CREATE TABLE inscripciones (
    id_inscripcion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_grupo BIGINT,
    id_periodo INT,
    fecha_inscripcion DATE,
    estado ENUM('ACTIVO','BAJA','FINALIZADO') DEFAULT 'ACTIVO',

    CONSTRAINT fk_inscripcion_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_inscripcion_grupo
        FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo),

    CONSTRAINT fk_inscripcion_periodo
        FOREIGN KEY (id_periodo)
        REFERENCES periodos(id_periodo)
) ENGINE=InnoDB;

CREATE TABLE carga_academica (
    id_carga BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_grupo_materia BIGINT,
    oportunidad ENUM('ORDINARIO','EXTRAORDINARIO'),
    intento INT,
    estatus ENUM('CURSANDO','APROBADA','REPROBADA','NP','BAJA') DEFAULT 'CURSANDO',
    fecha_inscripcion DATE,

    CONSTRAINT chk_intento
        CHECK (intento >= 1),

    CONSTRAINT fk_carga_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_carga_grupo_materia
        FOREIGN KEY (id_grupo_materia)
        REFERENCES grupos_materias(id_grupo_materia)
) ENGINE=InnoDB;

CREATE TABLE parciales (
    id_parcial INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    porcentaje DECIMAL(5,2)
) ENGINE=InnoDB;

CREATE TABLE calificaciones (
    id_calificacion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_carga BIGINT,
    id_parcial INT,
    calificacion DECIMAL(5,2),
    fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    capturado_por BIGINT,

    CONSTRAINT chk_calificacion
        CHECK (calificacion >= 0 AND calificacion <= 100),

    CONSTRAINT fk_calificacion_carga
        FOREIGN KEY (id_carga)
        REFERENCES carga_academica(id_carga),

    CONSTRAINT fk_calificacion_parcial
        FOREIGN KEY (id_parcial)
        REFERENCES parciales(id_parcial),

    CONSTRAINT fk_calificacion_usuario
        FOREIGN KEY (capturado_por)
        REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE extraordinarios (
    id_extraordinario BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_materia BIGINT,
    intento INT,
    fecha_examen DATE,
    calificacion DECIMAL(5,2),
    estatus ENUM('APROBADO','REPROBADO','NP'),
    observaciones TEXT,

    CONSTRAINT chk_extra_intento
        CHECK (intento >= 2 AND intento <= 4),

    CONSTRAINT chk_extra_calificacion
        CHECK (calificacion >= 0 AND calificacion <= 80),

    CONSTRAINT fk_extra_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_extra_materia
        FOREIGN KEY (id_materia)
        REFERENCES materias(id_materia)
) ENGINE=InnoDB;

CREATE TABLE historial_academico (
    id_historial BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_materia BIGINT,
    id_periodo INT,
    tipo_evaluacion ENUM('ORDINARIO','EXTRAORDINARIO'),
    oportunidad INT,
    calificacion_final DECIMAL(5,2),
    resultado ENUM('APROBADO','REPROBADO','NP'),
    fecha_cierre DATE,

    CONSTRAINT chk_historial_calificacion
        CHECK (calificacion_final >= 0 AND calificacion_final <= 100),

    CONSTRAINT fk_historial_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_historial_materia
        FOREIGN KEY (id_materia)
        REFERENCES materias(id_materia),

    CONSTRAINT fk_historial_periodo
        FOREIGN KEY (id_periodo)
        REFERENCES periodos(id_periodo)
) ENGINE=InnoDB;

CREATE TABLE asistencias (
    id_asistencia BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_carga BIGINT,
    id_parcial INT,
    fecha DATE,
    asistencia BOOLEAN,

    CONSTRAINT fk_asistencia_carga
        FOREIGN KEY (id_carga)
        REFERENCES carga_academica(id_carga),

    CONSTRAINT fk_asistencia_parcial
        FOREIGN KEY (id_parcial)
        REFERENCES parciales(id_parcial)
) ENGINE=InnoDB;

CREATE TABLE tipos_documento (
    id_tipo_documento INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE documentos_alumno (
    id_documento BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_tipo_documento INT,
    nombre_archivo VARCHAR(255),
    ruta_archivo VARCHAR(500),
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validado BOOLEAN DEFAULT FALSE,
    observaciones TEXT,

    CONSTRAINT fk_documento_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_documento_tipo
        FOREIGN KEY (id_tipo_documento)
        REFERENCES tipos_documento(id_tipo_documento)
) ENGINE=InnoDB;

CREATE TABLE empresas (
    id_empresa BIGINT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150),
    direccion TEXT,
    telefono VARCHAR(20),
    correo VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE servicio_social (
    id_servicio BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_empresa BIGINT,
    horas_requeridas INT,
    horas_completadas INT,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado ENUM('EN_PROCESO','COMPLETADO'),

    CONSTRAINT fk_servicio_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_servicio_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresas(id_empresa)
) ENGINE=InnoDB;

CREATE TABLE practicas_profesionales (
    id_practica BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    id_empresa BIGINT,
    proyecto VARCHAR(255),
    asesor_empresa VARCHAR(150),
    asesor_universidad VARCHAR(150),
    fecha_inicio DATE,
    fecha_fin DATE,
    estado ENUM('EN_PROCESO','COMPLETADO'),

    CONSTRAINT fk_practica_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT fk_practica_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresas(id_empresa)
) ENGINE=InnoDB;

CREATE TABLE titulacion (
    id_titulacion BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT,
    modalidad ENUM('PROMEDIO','TESIS','TESINA'),
    cumple_promedio BOOLEAN,
    servicio_social_liberado BOOLEAN,
    practicas_liberadas BOOLEAN,
    certificado_emitido BOOLEAN,
    pagos_titulacion_completos BOOLEAN,
    numero_autorizacion VARCHAR(100),
    acta_examen VARCHAR(255),
    titulo_emitido BOOLEAN,
    fecha_titulacion DATE,
    observaciones TEXT,

    CONSTRAINT fk_titulacion_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno)
) ENGINE=InnoDB;

-- =========================================================
-- INDICES IMPORTANTES
-- =========================================================

CREATE INDEX idx_alumnos_matricula
ON alumnos(matricula);

CREATE INDEX idx_alumnos_numero_control
ON alumnos(numero_control);

CREATE INDEX idx_alumnos_curp
ON alumnos(curp);

CREATE INDEX idx_historial_alumno
ON historial_academico(id_alumno);

CREATE INDEX idx_historial_materia
ON historial_academico(id_materia);

CREATE INDEX idx_carga_alumno
ON carga_academica(id_alumno);

CREATE INDEX idx_calificacion_carga
ON calificaciones(id_carga);

CREATE INDEX idx_asistencia_carga
ON asistencias(id_carga);

CREATE INDEX idx_asistencia_parcial
ON asistencias(id_parcial);

CREATE INDEX idx_usuario_correo
ON usuarios(correo);

-- =========================================================
-- RUTA DE CARGA DE INSERTS
-- 1. Catalogos base: roles, cuatrimestres, carreras, planes, materias, parciales, tipos de documento y periodos.
-- 2. Relaciones academicas: plan_materias y materias_prerrequisito.
-- 3. Usuarios y permisos: usuarios, usuario_roles, docentes y alumnos.
-- 4. Oferta e inscripcion: grupos, grupos_materias, inscripciones y carga_academica.
-- 5. Expediente del alumno: procedencia, tutores, contactos, seguros, recepcion_documentos y documentos_alumno.
-- 6. Seguimiento academico: calificaciones, asistencias, historial_academico y extraordinarios.
-- 7. Vinculacion y egreso: empresas, servicio_social, practicas_profesionales y titulacion.
-- =========================================================

-- ROLES FUNDAMENTALES
-- =========================================================

-- Inserta los roles base del sistema para separar permisos de administrador, control escolar, docente y alumno.
INSERT INTO roles (nombre) VALUES
('ADMIN'),
('CONTROL_ESCOLAR'),
('DOCENTE'),
('ALUMNO');

-- =========================================================
-- USUARIO ADMINISTRADOR
-- Password: Admin123*
-- =========================================================

-- Inserta el usuario administrador inicial con credenciales de acceso para operar el sistema.
INSERT INTO usuarios (
    nombre,
    apellido_paterno,
    apellido_materno,
    correo,
    password,
    telefono,
    estado
) VALUES (
    'Martin',
    'Administrador',
    'Sistema',
    'admin@unifront.com',
    '$2b$12$fDyZK5l1./1TY19rgskvc.lVaerFgt3eIjBN3JVUl2guZ1i0V64Ii',
    '6861234567',
    'ACTIVO'
);

-- Asignar rol ADMIN al usuario
-- Relaciona el usuario administrador inicial con el rol ADMIN.
INSERT INTO usuario_roles (id_usuario, id_rol)
VALUES (1, 1);

-- =========================================================
-- CUATRIMESTRES
-- =========================================================

-- Inserta el catalogo de cuatrimestres que se usa para organizar planes y grupos.
INSERT INTO cuatrimestres (numero, nombre) VALUES
(1, 'Primer Cuatrimestre'),
(2, 'Segundo Cuatrimestre'),
(3, 'Tercer Cuatrimestre'),
(4, 'Cuarto Cuatrimestre'),
(5, 'Quinto Cuatrimestre'),
(6, 'Sexto Cuatrimestre'),
(7, 'Séptimo Cuatrimestre'),
(8, 'Octavo Cuatrimestre'),
(9, 'Noveno Cuatrimestre'),
(10, 'Décimo Cuatrimestre'),
(11, 'Onceavo Cuatrimestre');

-- =========================================================
-- CARRERAS
-- =========================================================

-- Inserta las carreras principales que estaran disponibles en el sistema.
INSERT INTO carreras (
    clave,
    rvoe,
    nombre,
    nivel,
    duracion_cuatrimestres,
    estado,
    logo
) VALUES
(
    '260125',
    'RVOE-BC-053-M2/14',
    'Licenciatura en Criminología',
    'LICENCIATURA',
    9,
    TRUE,
    'logo_criminologia.png'
),
(
    '260126',
    'RVOE-BC-051-M2/14',
    'Licenciatura en Gastronomía',
    'LICENCIATURA',
    9,
    TRUE,
    'logo_gastronomia.png'
),
(
    '260127',
    'RVOE-BC-L010-M2/17',
    'Licenciatura en Nutrición',
    'LICENCIATURA',
    9,
    TRUE,
    'logo_nutricion.png'
);

-- =========================================================
-- PLANES DE ESTUDIO
-- =========================================================

-- Inserta los planes de estudio iniciales asociados a cada carrera principal.
INSERT INTO planes_estudio (
    id_carrera,
    nombre_plan,
    fecha_inicio
) VALUES
(
    1,
    'Plan 2014 Criminología',
    '2014-01-01'
),
(
    2,
    'Plan 2014 Gastronomía',
    '2014-01-01'
),
(
    3,
    'Plan 2017 Nutrición',
    '2017-01-01'
);

-- =========================================================
-- MATERIAS BÁSICAS
-- =========================================================

-- Inserta las materias base usadas por el plan de Criminologia.
INSERT INTO materias (
    clave,
    nombre,
    creditos,
    estado
) VALUES
('CRILI1', 'Criminalística I', 7.87, TRUE),
('CRIM02', 'Criminología I', 7.87, TRUE),
('CRINV1', 'Estadística Básica', 6.12, TRUE),
('CRIM01', 'Informática Aplicada a la Criminología', 5.25, TRUE),
('CRIJU1', 'Introducción al Estudio del Derecho', 6.12, TRUE),
('CRIM03', 'Bases Biológicas del Comportamiento', 7.87, TRUE),
('CRIM04', 'Criminología II', 7.87, TRUE),
('CRIJU2', 'Derecho Constitucional', 7, TRUE),
('CRIPS1', 'Introducción a la Psicología', 7.87, TRUE),
('CRILI2', 'Sistemas de Identificación', 6.12, TRUE),
('CRINV2', 'Metodología de la Investigación', 6.12, TRUE),
('CRIPE1', 'Derecho Penal I', 7.00, TRUE),
('CRIPS2', 'Psicología Criminal', 7.87, TRUE),
('CRSOC1', 'Sociología Criminal', 6.12, TRUE),
('CRMED1', 'Medicina Legal', 7.87, TRUE),
('CRINV3', 'Técnicas de Investigación Criminal', 7.87, TRUE),
('CRIPE2', 'Derecho Penal II', 7.00, TRUE),
('CRIVI1', 'Victimología', 6.12, TRUE),
('CRILI3', 'Criminalística II', 7.87, TRUE),
('CRETI1', 'Ética Profesional', 5.25, TRUE),
('CRCRI3', 'Criminología III', 7.87, TRUE),
('CRFOR1', 'Fotografía Forense', 6.12, TRUE),
('CRPEN1', 'Penología', 7.00, TRUE),
('CRINV4', 'Análisis de la Conducta Criminal', 7.87, TRUE),
('CRSEM1', 'Seminario de Investigación Criminológica', 6.12, TRUE);


-- =========================================================
-- RELACIÓN PLAN - MATERIAS
-- =========================================================

-- Relaciona el plan de estudio de Criminologia con sus materias y cuatrimestres.
INSERT INTO plan_materias (
    id_plan,
    id_materia,
    id_cuatrimestre,
    obligatoria
) VALUES
(1, 1, 1, TRUE),
(1, 2, 1, TRUE),
(1, 3, 1, TRUE),
(1, 4, 1, TRUE),
(1, 5, 1, TRUE),
(1, 6, 2, TRUE),
(1, 7, 2, TRUE),
(1, 8, 2, TRUE),
(1, 9, 2, TRUE),
(1, 10, 2, TRUE),
(1, 11, 3, TRUE),
(1, 12, 3, TRUE),
(1, 13, 3, TRUE),
(1, 14, 3, TRUE),
(1, 15, 3, TRUE),
(1, 16, 4, TRUE),
(1, 17, 4, TRUE),
(1, 18, 4, TRUE),
(1, 19, 4, TRUE),
(1, 20, 4, TRUE),
(1, 21, 5, TRUE),
(1, 22, 5, TRUE),
(1, 23, 5, TRUE),
(1, 24, 5, TRUE),
(1, 25, 5, TRUE);

-- =========================================================
-- PRERREQUISITOS
-- =========================================================

-- Inserta prerrequisitos entre materias para validar dependencias academicas.
INSERT INTO materias_prerrequisito (
    id_materia,
    id_materia_requerida,
    tipo
) VALUES
(7, 2, 'OBLIGATORIO');

-- =========================================================
-- PARCIALES
-- =========================================================

-- Inserta los parciales de evaluacion y su porcentaje dentro del periodo.
INSERT INTO parciales (nombre, porcentaje) VALUES
('Primer Parcial', 25),
('Segundo Parcial', 25),
('Tercer Parcial', 50);

-- =========================================================
-- TIPOS DE DOCUMENTO
-- =========================================================

-- Inserta el catalogo de tipos de documento que puede cargar o entregar un alumno.
INSERT INTO tipos_documento (nombre) VALUES
('Ficha de inscripción'),
('Acta de Nacimiento'),
('Certificado de Preparatoria'),
('Constancia de terminación de estudios'),
('Fotografías'),
('CURP');

-- =========================================================
-- PERIODO ACTIVO
-- =========================================================

-- Inserta el periodo academico activo inicial para inscripciones y grupos.
INSERT INTO periodos (
    nombre,
    fecha_inicio,
    fecha_fin,
    estado
) VALUES (
    'Enero - Abril 2026',
    '2026-01-01',
    '2026-04-30',
    'ACTIVO'
);

-- =========================================================
-- GRUPO DE PRUEBA
-- =========================================================

-- Inserta el grupo de prueba asociado a la carrera y cuatrimestre inicial.
INSERT INTO grupos (
    nombre,
    id_carrera,
    id_cuatrimestre,
    turno
) VALUES (
    'CRIM27',
    1,
    1,
    'MATUTINO'
);

-- =========================================================
-- DOCENTE DE PRUEBA
-- =========================================================

-- Inserta el usuario que servira como docente de prueba.
INSERT INTO usuarios (
    nombre,
    apellido_paterno,
    apellido_materno,
    correo,
    password,
    telefono,
    estado
) VALUES (
    'Carlos',
    'Ramirez',
    'Lopez',
    'docente@unifront.com',
    '$2b$12$fDyZK5l1./1TY19rgskvc.lVaerFgt3eIjBN3JVUl2guZ1i0V64Ii',
    '6865554444',
    'ACTIVO'
);

-- Relaciona el usuario docente de prueba con el rol DOCENTE.
INSERT INTO usuario_roles (id_usuario, id_rol)
VALUES (2, 3);

-- Registra los datos academicos del docente de prueba.
INSERT INTO docentes (
    id_usuario,
    numero_empleado,
    especialidad,
    grado_academico,
    fecha_ingreso,
    estado
) VALUES (
    2,
    'DOC-001',
    'Criminología',
    'Doctorado',
    '2020-01-10',
    TRUE
);

-- =========================================================
-- GRUPO - MATERIA BASE
-- Logica: el docente 1 se usa como docente de prueba y, por ahora,
-- solo debe tener una materia asignada para validar que las pantallas
-- de calificaciones y asistencia filtren por el docente autenticado.
-- =========================================================

-- Asigna una materia al grupo de prueba con su docente, periodo, aula y cupo.
INSERT INTO grupos_materias (
    id_grupo_materia,
    id_grupo,
    id_materia,
    id_docente,
    id_periodo,
    aula,
    cupo_maximo
) VALUES (
    1,
    1,
    6,
    1,
    1,
    'A-101',
    40
);

-- =========================================================
-- ALUMNO DE PRUEBA
-- =========================================================

-- Inserta el usuario que servira como alumno de prueba.
INSERT INTO usuarios (
    nombre,
    apellido_paterno,
    apellido_materno,
    correo,
    password,
    telefono,
    estado
) VALUES (
    'Juan',
    'Perez',
    'Gomez',
    'alumno@unifront.com',
    '$2b$12$fDyZK5l1./1TY19rgskvc.lVaerFgt3eIjBN3JVUl2guZ1i0V64Ii',
    '6869998888',
    'ACTIVO'
);

-- Relaciona el usuario alumno de prueba con el rol ALUMNO.
INSERT INTO usuario_roles (id_usuario, id_rol)
VALUES (3, 4);

-- Registra el expediente academico y datos personales del alumno de prueba.
INSERT INTO alumnos (
    matricula,
    numero_control,
    id_usuario,
    id_carrera,
    id_plan,
    fecha_nacimiento,
    ciudad_nacimiento,
    municipio_nacimiento,
    nacionalidad,
    sexo,
    curp,
    direccion,
    ciudad,
    estado,
    correo_contacto,
    fecha_ingreso,
    estatus
) VALUES (
    '20260001',
    'UC20260001',
    3,
    1,
    1,
    '2005-06-15',
    'Mexicali',
    'Mexicali',
    'Mexicana',
    'M',
    'PEGJ050615HBCRMS01',
    'Colonia Centro',
    'Mexicali',
    'Baja California',
    'juan.perez@example.com',
    '2026-01-05',
    'ACTIVO'
);

-- =========================================================
-- INSCRIPCIÓN DEL ALUMNO
-- =========================================================

-- Inscribe al alumno de prueba en el grupo y periodo inicial.
INSERT INTO inscripciones (
    id_alumno,
    id_grupo,
    id_periodo,
    fecha_inscripcion,
    estado
) VALUES (
    1,
    1,
    1,
    CURDATE(),
    'ACTIVO'
);

-- =========================================================
-- CARGA ACADÉMICA
-- =========================================================

-- Registra la carga academica inicial del alumno de prueba.
INSERT INTO carga_academica (
    id_alumno,
    id_grupo_materia,
    oportunidad,
    intento,
    estatus,
    fecha_inscripcion
) VALUES (
    1,
    1,
    'ORDINARIO',
    1,
    'APROBADA',
    CURDATE()
);

-- =========================================================
-- USUARIO DE CONTROL ESCOLAR
-- Password: Admin123*
-- =========================================================

-- Inserta el usuario de control escolar para tareas administrativas de alumnos y documentos.
INSERT INTO usuarios (
    nombre,
    apellido_paterno,
    apellido_materno,
    correo,
    password,
    telefono,
    estado
) VALUES (
    'Laura',
    'Hernandez',
    'Mendoza',
    'control.escolar@unifront.com',
    '$2b$12$fDyZK5l1./1TY19rgskvc.lVaerFgt3eIjBN3JVUl2guZ1i0V64Ii',
    '6862223344',
    'ACTIVO'
);

-- Relaciona el usuario de control escolar con el rol CONTROL_ESCOLAR.
INSERT INTO usuario_roles (id_usuario, id_rol)
VALUES (4, 2);

-- =========================================================
-- PROCEDENCIA ACADEMICA DEL ALUMNO
-- =========================================================

-- Registra la escuela de procedencia y promedio del alumno de prueba.
INSERT INTO procedencia_academica (
    id_alumno,
    escuela_procedencia,
    nivel_academico,
    estado_procedencia,
    promedio_general,
    fecha_egreso
) VALUES (
    1,
    'Colegio de Bachilleres Plantel Mexicali',
    'BACHILLERATO',
    'Baja California',
    88.50,
    '2025-07-15'
);

-- =========================================================
-- TUTOR Y RELACION CON ALUMNO
-- =========================================================

-- Inserta el tutor principal del alumno de prueba.
INSERT INTO tutores (
    nombre,
    parentesco,
    telefono,
    correo,
    ocupacion
) VALUES (
    'Maria Gomez Torres',
    'Madre',
    '6861112233',
    'maria.gomez@example.com',
    'Comerciante'
);

-- Relaciona el alumno de prueba con su tutor.
INSERT INTO alumno_tutor (
    id_alumno,
    id_tutor
) VALUES (
    1,
    1
);

-- =========================================================
-- CONTACTOS DE EMERGENCIA
-- =========================================================

-- Inserta contactos de emergencia para el alumno de prueba.
INSERT INTO contactos_emergencia (
    id_alumno,
    nombre,
    parentesco,
    telefono,
    correo,
    direccion,
    contacto_principal
) VALUES
(
    1,
    'Maria Gomez Torres',
    'Madre',
    '6861112233',
    'maria.gomez@example.com',
    'Colonia Centro, Mexicali, Baja California',
    TRUE
),
(
    1,
    'Roberto Perez Ruiz',
    'Padre',
    '6864445566',
    'roberto.perez@example.com',
    'Colonia Nueva, Mexicali, Baja California',
    FALSE
);

-- =========================================================
-- SEGURO MEDICO
-- =========================================================

-- Registra la informacion de seguro medico del alumno de prueba.
INSERT INTO seguros_medicos (
    id_alumno,
    tiene_seguro,
    institucion,
    numero_poliza
) VALUES (
    1,
    TRUE,
    'IMSS',
    'IMSS-2026-0001'
);

-- =========================================================
-- RECEPCION DE DOCUMENTOS
-- =========================================================

-- Registra los documentos fisicos recibidos para el expediente del alumno de prueba.
INSERT INTO recepcion_documentos (
    id_alumno,
    ficha_inscripcion,
    acta_original,
    acta_copias,
    certificado_original,
    constancia_terminacion,
    fotografias,
    curp_documento,
    fecha_recepcion,
    recibido_por,
    observaciones
) VALUES (
    1,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    '2026-01-05',
    4,
    'Expediente inicial completo y validado por control escolar.'
);

-- =========================================================
-- DOCUMENTOS DEL ALUMNO
-- =========================================================

-- Inserta documentos digitales asociados al expediente del alumno de prueba.
INSERT INTO documentos_alumno (
    id_alumno,
    id_tipo_documento,
    nombre_archivo,
    ruta_archivo,
    validado,
    observaciones
) VALUES
(
    1,
    1,
    'acta_nacimiento_20260001.pdf',
    '/documentos/alumnos/20260001/acta_nacimiento_20260001.pdf',
    TRUE,
    'Documento legible.'
),
(
    1,
    2,
    'curp_20260001.pdf',
    '/documentos/alumnos/20260001/curp_20260001.pdf',
    TRUE,
    'CURP coincide con el registro del alumno.'
),
(
    1,
    3,
    'certificado_bachillerato_20260001.pdf',
    '/documentos/alumnos/20260001/certificado_bachillerato_20260001.pdf',
    TRUE,
    'Certificado de bachillerato recibido.'
);

-- =========================================================
-- CALIFICACIONES
-- =========================================================

-- Inserta calificaciones iniciales para la carga academica del alumno de prueba.
INSERT INTO calificaciones (
    id_carga,
    id_parcial,
    calificacion,
    capturado_por
) VALUES
(
    1,
    1,
    92.00,
    2
),
(
    1,
    2,
    88.00,
    2
),
(
    1,
    3,
    90.00,
    2
);

-- =========================================================
-- ASISTENCIAS
-- =========================================================

-- Inserta asistencias iniciales para la carga academica del alumno de prueba.
INSERT INTO asistencias (
    id_carga,
    id_parcial,
    fecha,
    asistencia
) VALUES
(
    1,
    1,
    '2026-01-12',
    TRUE
),
(
    1,
    1,
    '2026-01-13',
    TRUE
),
(
    1,
    1,
    '2026-01-14',
    FALSE
),
(
    1,
    1,
    '2026-01-15',
    TRUE
);

-- =========================================================
-- HISTORIAL ACADEMICO
-- =========================================================

-- Inserta registros de historial academico para consultar resultados finales del alumno de prueba.
INSERT INTO historial_academico (
    id_alumno,
    id_materia,
    id_periodo,
    tipo_evaluacion,
    oportunidad,
    calificacion_final,
    resultado,
    fecha_cierre
) VALUES (
    1,
    1,
    1,
    'ORDINARIO',
    1,
    90.00,
    'APROBADO',
    '2026-04-30'
);

-- =========================================================
-- EXTRAORDINARIOS
-- =========================================================

-- Inserta examenes extraordinarios de prueba para validar segundas oportunidades.
INSERT INTO extraordinarios (
    id_alumno,
    id_materia,
    intento,
    fecha_examen,
    calificacion,
    estatus,
    observaciones
) VALUES (
    1,
    8,
    2,
    '2026-05-10',
    76.00,
    'APROBADO',
    'Acreditado en segunda oportunidad.'
);

-- =========================================================
-- EMPRESAS
-- =========================================================

-- Inserta empresas base para servicio social y practicas profesionales.
INSERT INTO empresas (
    nombre,
    direccion,
    telefono,
    correo
) VALUES
(
    'Centro Comunitario Mexicali',
    'Av. Reforma 1200, Mexicali, Baja California',
    '6865550101',
    'contacto@centrocomunitariomxl.org'
),
(
    'Consultoria Integral del Noroeste',
    'Blvd. Benito Juarez 450, Mexicali, Baja California',
    '6865550202',
    'rh@consultorianoroeste.com'
);

-- =========================================================
-- SERVICIO SOCIAL
-- =========================================================

-- Registra el servicio social del alumno de prueba con avance de horas.
INSERT INTO servicio_social (
    id_alumno,
    id_empresa,
    horas_requeridas,
    horas_completadas,
    fecha_inicio,
    fecha_fin,
    estado
) VALUES (
    1,
    1,
    480,
    120,
    '2026-02-01',
    NULL,
    'EN_PROCESO'
);

-- =========================================================
-- PRACTICAS PROFESIONALES
-- =========================================================

-- Registra las practicas profesionales del alumno de prueba y sus asesores.
INSERT INTO practicas_profesionales (
    id_alumno,
    id_empresa,
    proyecto,
    asesor_empresa,
    asesor_universidad,
    fecha_inicio,
    fecha_fin,
    estado
) VALUES (
    1,
    2,
    'Diagnostico de factores de riesgo comunitario',
    'Ana Torres Salgado',
    'Carlos Ramirez Lopez',
    '2026-03-01',
    NULL,
    'EN_PROCESO'
);

-- =========================================================
-- TITULACION
-- =========================================================

-- Registra el avance del proceso de titulacion del alumno de prueba.
INSERT INTO titulacion (
    id_alumno,
    modalidad,
    cumple_promedio,
    servicio_social_liberado,
    practicas_liberadas,
    certificado_emitido,
    pagos_titulacion_completos,
    numero_autorizacion,
    acta_examen,
    titulo_emitido,
    fecha_titulacion,
    observaciones
) VALUES (
    1,
    'TESIS',
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    NULL,
    NULL,
    FALSE,
    NULL,
    'Registro preliminar de proceso de titulacion.'
);

-- =========================================================
-- DATOS COMPLEMENTARIOS PARA PRUEBAS
-- Minimo 10 registros por tabla.
-- Password para usuarios agregados: Admin123*
-- =========================================================

SET @demo_password = '$2b$12$fDyZK5l1./1TY19rgskvc.lVaerFgt3eIjBN3JVUl2guZ1i0V64Ii';

-- =========================================================
-- CARRERAS COMPLEMENTARIAS
-- =========================================================

-- Inserta carreras adicionales para ampliar el catalogo de pruebas.
INSERT INTO carreras (
    clave,
    rvoe,
    nombre,
    nivel,
    duracion_cuatrimestres,
    estado,
    logo
) VALUES
('ING01',   'RVOE-BC-ING01/22',  'Ingenieria en Sistemas Computacionales', 'INGENIERIA',   10, TRUE, NULL),
('LADM21',  'RVOE-BC-LADM/21',   'Licenciatura en Administracion',         'LICENCIATURA', 9,  TRUE, NULL),
('LDER21',  'RVOE-BC-LDER/21',   'Licenciatura en Derecho',                'LICENCIATURA', 9,  TRUE, NULL),
('LPSI20',  'RVOE-BC-LPSI/20',   'Licenciatura en Psicologia',             'LICENCIATURA', 9,  TRUE, NULL),
('LENF20',  'RVOE-BC-LENF/20',   'Licenciatura en Enfermeria',             'LICENCIATURA', 9,  TRUE, NULL),
('MEDU24',  'RVOE-BC-MEDU/24',   'Maestria en Educacion',                  'MAESTRIA',     6,  TRUE, NULL),
('TSUDS25', 'RVOE-BC-TSUDS/25',  'TSU en Desarrollo de Software',          'TSU',          6,  TRUE, NULL);

-- =========================================================
-- PLANES DE ESTUDIO COMPLEMENTARIOS
-- =========================================================

-- Inserta planes de estudio adicionales asociados a las carreras complementarias.
INSERT INTO planes_estudio (
    id_plan,
    id_carrera,
    nombre_plan,
    fecha_inicio,
    fecha_fin,
    vigente
) VALUES
(4, 4, 'Plan 2022 Sistemas Computacionales', '2022-01-01', NULL, TRUE),
(5, 5, 'Plan 2021 Administracion', '2021-01-01', NULL, TRUE),
(6, 6, 'Plan 2021 Derecho', '2021-01-01', NULL, TRUE),
(7, 7, 'Plan 2020 Psicologia', '2020-01-01', NULL, TRUE),
(8, 8, 'Plan 2020 Enfermeria', '2020-01-01', NULL, TRUE),
(9, 9, 'Plan 2024 Maestria en Educacion', '2024-01-01', NULL, TRUE),
(10, 10, 'Plan 2025 Desarrollo de Software', '2025-01-01', NULL, TRUE);

-- =========================================================
-- PRERREQUISITOS COMPLEMENTARIOS
-- =========================================================

-- Inserta prerrequisitos adicionales para probar dependencias entre materias.
INSERT INTO materias_prerrequisito (
    id_materia,
    id_materia_requerida,
    tipo
) VALUES
(6, 1, 'RECOMENDADO'),
(8, 5, 'OBLIGATORIO'),
(9, 6, 'RECOMENDADO'),
(10, 1, 'OBLIGATORIO'),
(4, 3, 'RECOMENDADO'),
(5, 2, 'RECOMENDADO'),
(3, 1, 'OBLIGATORIO'),
(2, 1, 'RECOMENDADO'),
(10, 7, 'RECOMENDADO');

-- =========================================================
-- PERIODOS COMPLEMENTARIOS
-- =========================================================

-- Inserta periodos academicos adicionales para escenarios historicos y futuros.
INSERT INTO periodos (
    id_periodo,
    nombre,
    fecha_inicio,
    fecha_fin,
    estado
) VALUES
(2, 'Mayo - Agosto 2026', '2026-05-01', '2026-08-31', 'ACTIVO'),
(3, 'Septiembre - Diciembre 2026', '2026-09-01', '2026-12-20', 'CERRADO'),
(4, 'Enero - Abril 2025', '2025-01-01', '2025-04-30', 'CERRADO'),
(5, 'Mayo - Agosto 2025', '2025-05-01', '2025-08-31', 'CERRADO'),
(6, 'Septiembre - Diciembre 2025', '2025-09-01', '2025-12-20', 'CERRADO'),
(7, 'Enero - Abril 2024', '2024-01-01', '2024-04-30', 'CERRADO'),
(8, 'Mayo - Agosto 2024', '2024-05-01', '2024-08-31', 'CERRADO'),
(9, 'Septiembre - Diciembre 2024', '2024-09-01', '2024-12-20', 'CERRADO'),
(10, 'Enero - Abril 2027', '2027-01-01', '2027-04-30', 'CERRADO'),
(11, 'Mayo - Agosto 2027', '2027-05-01', '2027-08-31', 'CERRADO');

-- =========================================================
-- GRUPOS COMPLEMENTARIOS
-- =========================================================

-- Inserta grupos complementarios para probar distintos cuatrimestres, carreras y turnos.
INSERT INTO grupos (
    id_grupo,
    nombre,
    id_carrera,
    id_cuatrimestre,
    turno
) VALUES
(2, 'CRIM28', 1, 1, 'VESPERTINO'),
(3, 'CRIM29', 1, 2, 'MATUTINO'),
(4, 'CRIM30', 1, 2, 'VESPERTINO'),
(5, 'CRIM31', 1, 3, 'MATUTINO'),
(6, 'CRIM32', 1, 3, 'VESPERTINO'),
(7, 'CRIM33', 1, 4, 'MATUTINO'),
(8, 'CRIM34', 1, 4, 'VESPERTINO'),
(9, 'CRIM35', 1, 5, 'MATUTINO'),
(10, 'CRIM36', 1, 5, 'VESPERTINO');

-- =========================================================
-- USUARIOS DOCENTES COMPLEMENTARIOS
-- =========================================================

-- Inserta usuarios docentes complementarios para poblar el sistema con varios profesores.
INSERT INTO usuarios (
    id_usuario,
    nombre,
    apellido_paterno,
    apellido_materno,
    correo,
    password,
    telefono,
    estado
) VALUES
(5, 'Adriana', 'Soto', 'Mendez', 'adriana.soto@unifront.com', @demo_password, '6865551005', 'ACTIVO'),
(6, 'Fernando', 'Luna', 'Garcia', 'fernando.luna@unifront.com', @demo_password, '6865551006', 'ACTIVO'),
(7, 'Patricia', 'Ortega', 'Ruiz', 'patricia.ortega@unifront.com', @demo_password, '6865551007', 'ACTIVO'),
(8, 'Hector', 'Vargas', 'Nunez', 'hector.vargas@unifront.com', @demo_password, '6865551008', 'ACTIVO'),
(9, 'Gabriela', 'Medina', 'Paz', 'gabriela.medina@unifront.com', @demo_password, '6865551009', 'ACTIVO'),
(10, 'Jorge', 'Cabrera', 'Leon', 'jorge.cabrera@unifront.com', @demo_password, '6865551010', 'ACTIVO'),
(11, 'Marisol', 'Campos', 'Reyes', 'marisol.campos@unifront.com', @demo_password, '6865551011', 'ACTIVO'),
(12, 'Alberto', 'Nava', 'Rios', 'alberto.nava@unifront.com', @demo_password, '6865551012', 'ACTIVO'),
(13, 'Claudia', 'Salazar', 'Pena', 'claudia.salazar@unifront.com', @demo_password, '6865551013', 'ACTIVO');

-- Relaciona los docentes complementarios con el rol DOCENTE.
INSERT INTO usuario_roles (
    id_usuario,
    id_rol
) VALUES
(5, 3),
(6, 3),
(7, 3),
(8, 3),
(9, 3),
(10, 3),
(11, 3),
(12, 3),
(13, 3);

-- =========================================================
-- DOCENTES COMPLEMENTARIOS
-- =========================================================

-- Registra los perfiles academicos de los docentes complementarios.
INSERT INTO docentes (
    id_docente,
    id_usuario,
    numero_empleado,
    especialidad,
    grado_academico,
    fecha_ingreso,
    estado
) VALUES
(2, 5, 'DOC-002', 'Criminalistica de campo', 'Maestria', '2021-02-15', TRUE),
(3, 6, 'DOC-003', 'Derecho penal', 'Maestria', '2019-08-20', TRUE),
(4, 7, 'DOC-004', 'Psicologia forense', 'Doctorado', '2018-05-10', TRUE),
(5, 8, 'DOC-005', 'Estadistica aplicada', 'Maestria', '2022-01-17', TRUE),
(6, 9, 'DOC-006', 'Metodologia de investigacion', 'Doctorado', '2020-09-01', TRUE),
(7, 10, 'DOC-007', 'Sociologia criminal', 'Maestria', '2023-01-09', TRUE),
(8, 11, 'DOC-008', 'Victimologia', 'Maestria', '2021-09-06', TRUE),
(9, 12, 'DOC-009', 'Medicina legal', 'Especialidad', '2017-04-03', TRUE),
(10, 13, 'DOC-010', 'Tecnicas de entrevista', 'Maestria', '2024-01-12', TRUE);

-- =========================================================
-- GRUPOS - MATERIAS COMPLEMENTARIOS
-- Logica: se ofertan las demas materias del Plan 2014 para el grupo
-- CRIM27 en el periodo activo, pero se reparten entre docentes 2 al 10.
-- Esto mantiene al docente 1 con una sola clase y permite probar que
-- cada docente vea solo sus asignaciones en calificaciones y asistencia.
-- =========================================================

-- Asigna materias complementarias a grupos, docentes y periodos para probar oferta academica.
INSERT INTO grupos_materias (
    id_grupo_materia,
    id_grupo,
    id_materia,
    id_docente,
    id_periodo,
    aula,
    cupo_maximo
) VALUES
-- Docente 2: toma Criminalistica I para que docente 1 no concentre todo.
(2, 1, 1, 2, 1, 'A-102', 40),
-- Docente 3: toma Criminologia I en el mismo grupo y periodo activo.
(3, 1, 2, 3, 1, 'A-103', 40),
-- Docente 4: toma Estadistica Basica para cubrir otra materia del plan.
(4, 1, 3, 4, 1, 'A-104', 40),
-- Docente 5: toma Informatica Aplicada a la Criminologia.
(5, 1, 4, 5, 1, 'A-105', 40),
-- Docente 6: toma Introduccion al Estudio del Derecho.
(6, 1, 5, 6, 1, 'A-106', 40),
-- Docente 7: toma Criminologia II.
(7, 1, 7, 7, 1, 'B-101', 40),
-- Docente 8: toma Derecho Constitucional.
(8, 1, 8, 8, 1, 'B-102', 40),
-- Docente 9: toma Introduccion a la Psicologia.
(9, 1, 9, 9, 1, 'B-103', 40),
-- Docente 10: toma Sistemas de Identificacion.
(10, 1, 10, 10, 1, 'B-104', 40),
-- Oferta historica para que el kardex del alumno de prueba muestre varios cuatrimestres.
(11, 5, 11, 2, 3, 'C-101', 40),
(12, 5, 12, 3, 3, 'C-102', 40),
(13, 5, 13, 4, 3, 'C-103', 40),
(14, 5, 14, 5, 3, 'C-104', 40),
(15, 5, 15, 6, 3, 'C-105', 40),
(16, 7, 16, 7, 10, 'D-101', 40),
(17, 7, 17, 8, 10, 'D-102', 40),
(18, 7, 18, 9, 10, 'D-103', 40),
(19, 7, 19, 10, 10, 'D-104', 40),
(20, 7, 20, 2, 10, 'D-105', 40),
(21, 9, 21, 3, 11, 'E-101', 40),
(22, 9, 22, 4, 11, 'E-102', 40),
(23, 9, 23, 5, 11, 'E-103', 40),
(24, 9, 24, 6, 11, 'E-104', 40),
(25, 9, 25, 7, 11, 'E-105', 40);

-- =========================================================
-- USUARIOS ALUMNOS COMPLEMENTARIOS
-- =========================================================

-- Inserta usuarios alumnos complementarios para pruebas de listados, filtros y expedientes.
INSERT INTO usuarios (
    id_usuario,
    nombre,
    apellido_paterno,
    apellido_materno,
    correo,
    password,
    telefono,
    estado
) VALUES
(14, 'Ana', 'Morales', 'Rivera', 'ana.morales@alumnos.unifront.com', @demo_password, '6865552014', 'ACTIVO'),
(15, 'Luis', 'Hernandez', 'Soto', 'luis.hernandez@alumnos.unifront.com', @demo_password, '6865552015', 'ACTIVO'),
(16, 'Sofia', 'Torres', 'Vega', 'sofia.torres@alumnos.unifront.com', @demo_password, '6865552016', 'ACTIVO'),
(17, 'Diego', 'Castillo', 'Flores', 'diego.castillo@alumnos.unifront.com', @demo_password, '6865552017', 'ACTIVO'),
(18, 'Valeria', 'Navarro', 'Cruz', 'valeria.navarro@alumnos.unifront.com', @demo_password, '6865552018', 'ACTIVO'),
(19, 'Miguel', 'Rojas', 'Aguilar', 'miguel.rojas@alumnos.unifront.com', @demo_password, '6865552019', 'ACTIVO'),
(20, 'Fernanda', 'Pineda', 'Luna', 'fernanda.pineda@alumnos.unifront.com', @demo_password, '6865552020', 'ACTIVO'),
(21, 'Ricardo', 'Salas', 'Ortega', 'ricardo.salas@alumnos.unifront.com', @demo_password, '6865552021', 'ACTIVO'),
(22, 'Daniela', 'Vega', 'Montes', 'daniela.vega@alumnos.unifront.com', @demo_password, '6865552022', 'ACTIVO');

-- Relaciona los alumnos complementarios con el rol ALUMNO.
INSERT INTO usuario_roles (
    id_usuario,
    id_rol
) VALUES
(14, 4),
(15, 4),
(16, 4),
(17, 4),
(18, 4),
(19, 4),
(20, 4),
(21, 4),
(22, 4);

-- =========================================================
-- ALUMNOS COMPLEMENTARIOS
-- =========================================================

-- Registra expedientes academicos y datos personales de los alumnos complementarios.
INSERT INTO alumnos (
    id_alumno,
    matricula,
    numero_control,
    id_usuario,
    id_carrera,
    id_plan,
    fecha_nacimiento,
    ciudad_nacimiento,
    municipio_nacimiento,
    nacionalidad,
    sexo,
    curp,
    direccion,
    ciudad,
    estado,
    correo_contacto,
    fecha_ingreso,
    estatus
) VALUES
(2, '20260002', 'UC20260002', 14, 1, 1, '2005-02-03', 'Mexicali', 'Mexicali', 'Mexicana', 'F', 'MORA050203MBCRNV02', 'Av. Reforma 210, Colonia Nueva', 'Mexicali', 'Baja California', 'ana.morales@example.com', '2026-01-05', 'ACTIVO'),
(3, '20260003', 'UC20260003', 15, 1, 1, '2004-11-22', 'Tecate', 'Tecate', 'Mexicana', 'M', 'HESL041122HBCRTO03', 'Calle Roble 45, Colonia Industrial', 'Mexicali', 'Baja California', 'luis.hernandez@example.com', '2026-01-05', 'ACTIVO'),
(4, '20260004', 'UC20260004', 16, 1, 1, '2005-07-09', 'Tijuana', 'Tijuana', 'Mexicana', 'F', 'TOVS050709MBCRGF04', 'Calle Encino 76, Colonia Independencia', 'Mexicali', 'Baja California', 'sofia.torres@example.com', '2026-01-05', 'ACTIVO'),
(5, '20260005', 'UC20260005', 17, 1, 1, '2004-04-18', 'Ensenada', 'Ensenada', 'Mexicana', 'M', 'CAFD040418HBCSLG05', 'Av. Universidad 300, Colonia Esperanza', 'Mexicali', 'Baja California', 'diego.castillo@example.com', '2026-01-05', 'ACTIVO'),
(6, '20260006', 'UC20260006', 18, 1, 1, '2005-09-30', 'Mexicali', 'Mexicali', 'Mexicana', 'F', 'NACV050930MBCVRL06', 'Calle Sauce 118, Colonia Hidalgo', 'Mexicali', 'Baja California', 'valeria.navarro@example.com', '2026-01-05', 'ACTIVO'),
(7, '20260007', 'UC20260007', 19, 1, 1, '2004-12-14', 'San Felipe', 'San Felipe', 'Mexicana', 'M', 'ROAM041214HBCJGG07', 'Calle Rio Colorado 91, Colonia Progreso', 'Mexicali', 'Baja California', 'miguel.rojas@example.com', '2026-01-05', 'ACTIVO'),
(8, '20260008', 'UC20260008', 20, 1, 1, '2005-03-26', 'Mexicali', 'Mexicali', 'Mexicana', 'F', 'PILF050326MBCNNR08', 'Blvd. Lazaro Cardenas 805, Colonia Rivera', 'Mexicali', 'Baja California', 'fernanda.pineda@example.com', '2026-01-05', 'ACTIVO'),
(9, '20260009', 'UC20260009', 21, 1, 1, '2004-10-08', 'Tecate', 'Tecate', 'Mexicana', 'M', 'SAOR041008HBCLRC09', 'Calle Mision 66, Colonia Baja', 'Mexicali', 'Baja California', 'ricardo.salas@example.com', '2026-01-05', 'ACTIVO'),
(10, '20260010', 'UC20260010', 22, 1, 1, '2005-05-19', 'Tijuana', 'Tijuana', 'Mexicana', 'F', 'VEMD050519MBCGNN10', 'Privada Del Sol 12, Colonia Jardin', 'Mexicali', 'Baja California', 'daniela.vega@example.com', '2026-01-05', 'ACTIVO');

-- =========================================================
-- INSCRIPCIONES COMPLEMENTARIAS
-- =========================================================

-- Inscribe a los alumnos complementarios en grupos y periodos de prueba.
INSERT INTO inscripciones (
    id_inscripcion,
    id_alumno,
    id_grupo,
    id_periodo,
    fecha_inscripcion,
    estado
) VALUES
(2, 2, 1, 1, '2026-01-05', 'ACTIVO'),
(3, 3, 1, 1, '2026-01-05', 'ACTIVO'),
(4, 4, 1, 1, '2026-01-05', 'ACTIVO'),
(5, 5, 1, 1, '2026-01-05', 'ACTIVO'),
(6, 6, 1, 1, '2026-01-05', 'ACTIVO'),
(7, 7, 1, 2, '2026-05-06', 'ACTIVO'),
(8, 8, 1, 2, '2026-05-06', 'ACTIVO'),
(9, 9, 1, 2, '2026-05-06', 'ACTIVO'),
(10, 10, 1, 2, '2026-05-06', 'ACTIVO');

-- =========================================================
-- CARGAS ACADEMICAS COMPLEMENTARIAS
-- =========================================================

-- Registra cargas academicas complementarias para los alumnos inscritos.
INSERT INTO carga_academica (
    id_carga,
    id_alumno,
    id_grupo_materia,
    oportunidad,
    intento,
    estatus,
    fecha_inscripcion
) VALUES
(2, 2, 1, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(3, 3, 1, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(4, 4, 1, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(5, 5, 1, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(6, 6, 1, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(7, 7, 1, 'ORDINARIO', 1, 'CURSANDO', '2026-05-06'),
(8, 8, 1, 'ORDINARIO', 1, 'CURSANDO', '2026-05-06'),
(9, 9, 1, 'ORDINARIO', 1, 'CURSANDO', '2026-05-06'),
(10, 10, 1, 'ORDINARIO', 1, 'CURSANDO', '2026-05-06');

-- =========================================================
-- PROCEDENCIA ACADEMICA COMPLEMENTARIA
-- =========================================================

-- Inserta la procedencia academica de los alumnos complementarios.
INSERT INTO procedencia_academica (
    id_procedencia,
    id_alumno,
    escuela_procedencia,
    nivel_academico,
    estado_procedencia,
    promedio_general,
    fecha_egreso
) VALUES
(2, 2, 'Cobach Plantel Baja California', 'BACHILLERATO', 'Baja California', 91.20, '2025-07-10'),
(3, 3, 'Cecyte Plantel Xochimilco', 'BACHILLERATO', 'Baja California', 86.40, '2025-07-12'),
(4, 4, 'Preparatoria Federal Lazaro Cardenas', 'BACHILLERATO', 'Baja California', 92.10, '2025-07-08'),
(5, 5, 'Colegio de Bachilleres Plantel Ensenada', 'BACHILLERATO', 'Baja California', 84.70, '2025-07-14'),
(6, 6, 'Cbtis 21', 'BACHILLERATO', 'Baja California', 89.90, '2025-07-13'),
(7, 7, 'Cecyte Plantel San Felipe', 'BACHILLERATO', 'Baja California', 87.50, '2025-07-11'),
(8, 8, 'Preparatoria Tecnica Municipal', 'BACHILLERATO', 'Baja California', 94.30, '2025-07-09'),
(9, 9, 'Cobach Plantel Tecate', 'BACHILLERATO', 'Baja California', 85.80, '2025-07-15'),
(10, 10, 'Cbtis 140', 'BACHILLERATO', 'Baja California', 90.60, '2025-07-16');

-- =========================================================
-- TUTORES COMPLEMENTARIOS
-- =========================================================

-- Inserta tutores complementarios para los alumnos adicionales.
INSERT INTO tutores (
    id_tutor,
    nombre,
    parentesco,
    telefono,
    correo,
    ocupacion
) VALUES
(2, 'Elena Rivera Castro', 'Madre', '6865553002', 'elena.rivera@example.com', 'Contadora'),
(3, 'Rafael Hernandez Mora', 'Padre', '6865553003', 'rafael.hernandez@example.com', 'Tecnico'),
(4, 'Lucia Vega Padilla', 'Madre', '6865553004', 'lucia.vega@example.com', 'Docente'),
(5, 'Manuel Castillo Ruiz', 'Padre', '6865553005', 'manuel.castillo@example.com', 'Comerciante'),
(6, 'Rosa Cruz Lopez', 'Madre', '6865553006', 'rosa.cruz@example.com', 'Enfermera'),
(7, 'Guillermo Rojas Soto', 'Padre', '6865553007', 'guillermo.rojas@example.com', 'Mecanico'),
(8, 'Patricia Luna Garcia', 'Madre', '6865553008', 'patricia.luna@example.com', 'Administradora'),
(9, 'Sergio Salas Ruiz', 'Padre', '6865553009', 'sergio.salas@example.com', 'Ingeniero'),
(10, 'Martha Montes Reyes', 'Madre', '6865553010', 'martha.montes@example.com', 'Abogada');

-- Relaciona alumnos complementarios con sus tutores.
INSERT INTO alumno_tutor (
    id_alumno,
    id_tutor
) VALUES
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10);

-- =========================================================
-- CONTACTOS DE EMERGENCIA COMPLEMENTARIOS
-- =========================================================

-- Inserta contactos de emergencia complementarios por alumno.
INSERT INTO contactos_emergencia (
    id_contacto,
    id_alumno,
    nombre,
    parentesco,
    telefono,
    correo,
    direccion,
    contacto_principal
) VALUES
(3, 2, 'Elena Rivera Castro', 'Madre', '6865553002', 'elena.rivera@example.com', 'Av. Reforma 210, Mexicali', TRUE),
(4, 3, 'Rafael Hernandez Mora', 'Padre', '6865553003', 'rafael.hernandez@example.com', 'Calle Roble 45, Mexicali', TRUE),
(5, 4, 'Lucia Vega Padilla', 'Madre', '6865553004', 'lucia.vega@example.com', 'Calle Encino 76, Mexicali', TRUE),
(6, 5, 'Manuel Castillo Ruiz', 'Padre', '6865553005', 'manuel.castillo@example.com', 'Av. Universidad 300, Mexicali', TRUE),
(7, 6, 'Rosa Cruz Lopez', 'Madre', '6865553006', 'rosa.cruz@example.com', 'Calle Sauce 118, Mexicali', TRUE),
(8, 7, 'Guillermo Rojas Soto', 'Padre', '6865553007', 'guillermo.rojas@example.com', 'Calle Rio Colorado 91, Mexicali', TRUE),
(9, 8, 'Patricia Luna Garcia', 'Madre', '6865553008', 'patricia.luna@example.com', 'Blvd. Lazaro Cardenas 805, Mexicali', TRUE),
(10, 9, 'Sergio Salas Ruiz', 'Padre', '6865553009', 'sergio.salas@example.com', 'Calle Mision 66, Mexicali', TRUE),
(11, 10, 'Martha Montes Reyes', 'Madre', '6865553010', 'martha.montes@example.com', 'Privada Del Sol 12, Mexicali', TRUE);

-- =========================================================
-- SEGUROS MEDICOS COMPLEMENTARIOS
-- =========================================================

-- Registra seguros medicos complementarios para los alumnos adicionales.
INSERT INTO seguros_medicos (
    id_seguro,
    id_alumno,
    tiene_seguro,
    institucion,
    numero_poliza
) VALUES
(2, 2, TRUE, 'IMSS', 'IMSS-2026-0002'),
(3, 3, TRUE, 'ISSSTE', 'ISSSTE-2026-0003'),
(4, 4, TRUE, 'IMSS', 'IMSS-2026-0004'),
(5, 5, FALSE, NULL, NULL),
(6, 6, TRUE, 'Seguro Popular', 'SP-2026-0006'),
(7, 7, TRUE, 'IMSS', 'IMSS-2026-0007'),
(8, 8, TRUE, 'ISSSTE', 'ISSSTE-2026-0008'),
(9, 9, FALSE, NULL, NULL),
(10, 10, TRUE, 'IMSS', 'IMSS-2026-0010');

-- =========================================================
-- RECEPCION DE DOCUMENTOS COMPLEMENTARIA
-- =========================================================

-- Registra recepcion de documentos complementaria para expedientes de alumnos adicionales.
INSERT INTO recepcion_documentos (
    id_recepcion,
    id_alumno,
    ficha_inscripcion,
    acta_original,
    acta_copias,
    certificado_original,
    constancia_terminacion,
    fotografias,
    curp_documento,
    fecha_recepcion,
    recibido_por,
    observaciones
) VALUES
(2, 2, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-01-05', 4, 'Expediente completo.'),
(3, 3, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-01-05', 4, 'Expediente completo.'),
(4, 4, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-01-05', 4, 'Expediente completo.'),
(5, 5, TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, '2026-01-05', 4, 'Pendiente entrega de fotografias.'),
(6, 6, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-01-05', 4, 'Expediente completo.'),
(7, 7, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-05-06', 4, 'Expediente completo.'),
(8, 8, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-05-06', 4, 'Expediente completo.'),
(9, 9, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, '2026-05-06', 4, 'Pendiente cotejo de certificado original.'),
(10, 10, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '2026-05-06', 4, 'Expediente completo.');

-- =========================================================
-- CALIFICACIONES COMPLEMENTARIAS
-- =========================================================

-- Inserta calificaciones complementarias para probar capturas y consultas academicas.
INSERT INTO calificaciones (
    id_calificacion,
    id_carga,
    id_parcial,
    calificacion,
    capturado_por
) VALUES
(4, 2, 1, 89.00, 5),
(5, 3, 1, 84.50, 6),
(6, 4, 1, 91.00, 7),
(7, 5, 1, 78.00, 8),
(8, 6, 1, 95.00, 9),
(9, 7, 1, 82.00, 10),
(10, 8, 1, 88.50, 11),
(11, 9, 1, 74.00, 12),
(12, 10, 1, 93.00, 13);

-- =========================================================
-- ASISTENCIAS COMPLEMENTARIAS
-- =========================================================

-- Inserta asistencias complementarias para probar control de asistencia.
INSERT INTO asistencias (
    id_asistencia,
    id_carga,
    id_parcial,
    fecha,
    asistencia
) VALUES
(5, 2, 1, '2026-01-12', TRUE),
(6, 3, 1, '2026-01-12', TRUE),
(7, 4, 1, '2026-01-12', TRUE),
(8, 5, 1, '2026-01-12', FALSE),
(9, 6, 1, '2026-01-12', TRUE),
(10, 7, 1, '2026-05-11', TRUE),
(11, 8, 1, '2026-05-11', TRUE),
(12, 9, 1, '2026-05-11', TRUE),
(13, 10, 1, '2026-05-11', FALSE);

-- =========================================================
-- HISTORIAL ACADEMICO COMPLEMENTARIO
-- =========================================================

-- Inserta historial academico complementario con resultados aprobados y reprobados.
INSERT INTO historial_academico (
    id_historial,
    id_alumno,
    id_materia,
    id_periodo,
    tipo_evaluacion,
    oportunidad,
    calificacion_final,
    resultado,
    fecha_cierre
) VALUES
(2, 2, 2, 1, 'ORDINARIO', 1, 89.00, 'APROBADO', '2026-04-30'),
(3, 3, 3, 1, 'ORDINARIO', 1, 84.50, 'APROBADO', '2026-04-30'),
(4, 4, 4, 1, 'ORDINARIO', 1, 91.00, 'APROBADO', '2026-04-30'),
(5, 5, 5, 1, 'ORDINARIO', 1, 78.00, 'APROBADO', '2026-04-30'),
(6, 6, 6, 1, 'ORDINARIO', 1, 95.00, 'APROBADO', '2026-04-30'),
(7, 7, 7, 2, 'ORDINARIO', 1, 82.00, 'APROBADO', '2026-08-31'),
(8, 8, 8, 2, 'ORDINARIO', 1, 88.50, 'APROBADO', '2026-08-31'),
(9, 9, 9, 2, 'ORDINARIO', 1, 64.00, 'REPROBADO', '2026-08-31'),
(10, 10, 10, 2, 'ORDINARIO', 1, 93.00, 'APROBADO', '2026-08-31');

-- =========================================================
-- DATOS ACADEMICOS PARA PROMEDIOS, REZAGO Y KARDEX
-- =========================================================

-- Agrega cargas del grupo CRIM27 para que Promedios y Kardex tengan todas las materias ofertadas.
INSERT INTO carga_academica (
    id_carga,
    id_alumno,
    id_grupo_materia,
    oportunidad,
    intento,
    estatus,
    fecha_inscripcion
) VALUES
(11, 1, 2, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(12, 1, 3, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(13, 1, 4, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(14, 1, 5, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(15, 1, 6, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(16, 1, 7, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(17, 1, 8, 'ORDINARIO', 1, 'REPROBADA', '2026-01-05'),
(18, 1, 9, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(19, 1, 10, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(20, 2, 2, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(21, 2, 3, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(22, 2, 4, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(23, 2, 5, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(24, 2, 6, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(25, 2, 7, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(26, 2, 8, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(27, 2, 9, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(28, 2, 10, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(29, 3, 2, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(30, 3, 3, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(31, 3, 4, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(32, 3, 5, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(33, 3, 6, 'ORDINARIO', 1, 'REPROBADA', '2026-01-05'),
(34, 3, 7, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(35, 3, 8, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(36, 3, 9, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(37, 3, 10, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(38, 4, 2, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(39, 4, 3, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(40, 4, 4, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(41, 4, 5, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(42, 4, 6, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(43, 4, 7, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(44, 4, 8, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(45, 4, 9, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(46, 4, 10, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(47, 5, 2, 'ORDINARIO', 1, 'REPROBADA', '2026-01-05'),
(48, 5, 3, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(49, 5, 4, 'ORDINARIO', 1, 'REPROBADA', '2026-01-05'),
(50, 5, 5, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(51, 5, 6, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(52, 5, 7, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(53, 5, 8, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(54, 5, 9, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(55, 5, 10, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(56, 6, 2, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(57, 6, 3, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(58, 6, 4, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(59, 6, 5, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(60, 6, 6, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(61, 6, 7, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(62, 6, 8, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(63, 6, 9, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(64, 6, 10, 'ORDINARIO', 1, 'APROBADA', '2026-01-05'),
(65, 1, 11, 'ORDINARIO', 1, 'APROBADA', '2026-09-05'),
(66, 1, 12, 'ORDINARIO', 1, 'APROBADA', '2026-09-05'),
(67, 1, 13, 'ORDINARIO', 1, 'APROBADA', '2026-09-05'),
(68, 1, 14, 'ORDINARIO', 1, 'APROBADA', '2026-09-05'),
(69, 1, 15, 'ORDINARIO', 1, 'APROBADA', '2026-09-05'),
(70, 1, 16, 'ORDINARIO', 1, 'APROBADA', '2027-01-05'),
(71, 1, 17, 'ORDINARIO', 1, 'APROBADA', '2027-01-05'),
(72, 1, 18, 'ORDINARIO', 1, 'APROBADA', '2027-01-05'),
(73, 1, 19, 'ORDINARIO', 1, 'APROBADA', '2027-01-05'),
(74, 1, 20, 'ORDINARIO', 1, 'APROBADA', '2027-01-05'),
(75, 1, 21, 'ORDINARIO', 1, 'APROBADA', '2027-05-05'),
(76, 1, 22, 'ORDINARIO', 1, 'APROBADA', '2027-05-05'),
(77, 1, 23, 'ORDINARIO', 1, 'APROBADA', '2027-05-05'),
(78, 1, 24, 'ORDINARIO', 1, 'APROBADA', '2027-05-05'),
(79, 1, 25, 'ORDINARIO', 1, 'APROBADA', '2027-05-05');

-- Captura calificaciones finales por carga; un parcial basta para que boleta-final calcule el promedio.
INSERT INTO calificaciones (
    id_calificacion,
    id_carga,
    id_parcial,
    calificacion,
    capturado_por
) VALUES
(13, 11, 1, 92.00, 5),
(14, 12, 1, 91.00, 6),
(15, 13, 1, 93.00, 7),
(16, 14, 1, 90.00, 8),
(17, 15, 1, 94.00, 9),
(18, 16, 1, 89.00, 10),
(19, 17, 1, 65.00, 11),
(20, 18, 1, 88.00, 12),
(21, 19, 1, 90.00, 13),
(22, 20, 1, 93.00, 5),
(23, 21, 1, 89.00, 6),
(24, 22, 1, 92.00, 7),
(25, 23, 1, 91.00, 8),
(26, 24, 1, 90.00, 9),
(27, 25, 1, 94.00, 10),
(28, 26, 1, 90.00, 11),
(29, 27, 1, 92.00, 12),
(30, 28, 1, 93.00, 13),
(31, 29, 1, 82.00, 5),
(32, 30, 1, 84.00, 6),
(33, 31, 1, 85.00, 7),
(34, 32, 1, 86.00, 8),
(35, 33, 1, 67.00, 9),
(36, 34, 1, 83.00, 10),
(37, 35, 1, 85.00, 11),
(38, 36, 1, 86.00, 12),
(39, 37, 1, 84.00, 13),
(40, 38, 1, 92.00, 5),
(41, 39, 1, 94.00, 6),
(42, 40, 1, 93.00, 7),
(43, 41, 1, 91.00, 8),
(44, 42, 1, 92.00, 9),
(45, 43, 1, 90.00, 10),
(46, 44, 1, 94.00, 11),
(47, 45, 1, 93.00, 12),
(48, 46, 1, 92.00, 13),
(49, 47, 1, 64.00, 5),
(50, 48, 1, 78.00, 6),
(51, 49, 1, 68.00, 7),
(52, 50, 1, 76.00, 8),
(53, 51, 1, 82.00, 9),
(54, 52, 1, 75.00, 10),
(55, 53, 1, 80.00, 11),
(56, 54, 1, 77.00, 12),
(57, 55, 1, 79.00, 13),
(58, 56, 1, 96.00, 5),
(59, 57, 1, 95.00, 6),
(60, 58, 1, 94.00, 7),
(61, 59, 1, 97.00, 8),
(62, 60, 1, 96.00, 9),
(63, 61, 1, 95.00, 10),
(64, 62, 1, 94.00, 11),
(65, 63, 1, 96.00, 12),
(66, 64, 1, 95.00, 13),
(67, 65, 1, 91.00, 5),
(68, 66, 1, 88.00, 6),
(69, 67, 1, 93.00, 7),
(70, 68, 1, 90.00, 8),
(71, 69, 1, 92.00, 9),
(72, 70, 1, 87.00, 10),
(73, 71, 1, 89.00, 11),
(74, 72, 1, 94.00, 12),
(75, 73, 1, 90.00, 13),
(76, 74, 1, 91.00, 5),
(77, 75, 1, 95.00, 6),
(78, 76, 1, 92.00, 7),
(79, 77, 1, 90.00, 8),
(80, 78, 1, 93.00, 9),
(81, 79, 1, 94.00, 10);

-- Completa historiales finales coherentes con las cargas para Kardex y el reporte de rezago.
INSERT INTO historial_academico (
    id_historial,
    id_alumno,
    id_materia,
    id_periodo,
    tipo_evaluacion,
    oportunidad,
    calificacion_final,
    resultado,
    fecha_cierre
) VALUES
(11, 1, 2, 1, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-04-30'),
(12, 1, 3, 1, 'ORDINARIO', 1, 91.00, 'APROBADO', '2026-04-30'),
(13, 1, 4, 1, 'ORDINARIO', 1, 93.00, 'APROBADO', '2026-04-30'),
(14, 1, 5, 1, 'ORDINARIO', 1, 90.00, 'APROBADO', '2026-04-30'),
(15, 1, 6, 1, 'ORDINARIO', 1, 90.00, 'APROBADO', '2026-04-30'),
(16, 1, 7, 1, 'ORDINARIO', 1, 89.00, 'APROBADO', '2026-04-30'),
(17, 1, 8, 1, 'ORDINARIO', 1, 65.00, 'REPROBADO', '2026-04-30'),
(18, 1, 9, 1, 'ORDINARIO', 1, 88.00, 'APROBADO', '2026-04-30'),
(19, 1, 10, 1, 'ORDINARIO', 1, 90.00, 'APROBADO', '2026-04-30'),
(20, 2, 1, 1, 'ORDINARIO', 1, 93.00, 'APROBADO', '2026-04-30'),
(21, 2, 3, 1, 'ORDINARIO', 1, 89.00, 'APROBADO', '2026-04-30'),
(22, 2, 4, 1, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-04-30'),
(23, 2, 5, 1, 'ORDINARIO', 1, 91.00, 'APROBADO', '2026-04-30'),
(24, 2, 6, 1, 'ORDINARIO', 1, 89.00, 'APROBADO', '2026-04-30'),
(25, 2, 7, 1, 'ORDINARIO', 1, 94.00, 'APROBADO', '2026-04-30'),
(26, 2, 8, 1, 'ORDINARIO', 1, 90.00, 'APROBADO', '2026-04-30'),
(27, 2, 9, 1, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-04-30'),
(28, 2, 10, 1, 'ORDINARIO', 1, 93.00, 'APROBADO', '2026-04-30'),
(29, 3, 1, 1, 'ORDINARIO', 1, 82.00, 'APROBADO', '2026-04-30'),
(30, 3, 2, 1, 'ORDINARIO', 1, 84.50, 'APROBADO', '2026-04-30'),
(31, 3, 4, 1, 'ORDINARIO', 1, 85.00, 'APROBADO', '2026-04-30'),
(32, 3, 5, 1, 'ORDINARIO', 1, 67.00, 'REPROBADO', '2026-04-30'),
(33, 3, 6, 1, 'ORDINARIO', 1, 84.50, 'APROBADO', '2026-04-30'),
(34, 3, 7, 1, 'ORDINARIO', 1, 83.00, 'APROBADO', '2026-04-30'),
(35, 3, 8, 1, 'ORDINARIO', 1, 85.00, 'APROBADO', '2026-04-30'),
(36, 3, 9, 1, 'ORDINARIO', 1, 86.00, 'APROBADO', '2026-04-30'),
(37, 3, 10, 1, 'ORDINARIO', 1, 84.00, 'APROBADO', '2026-04-30'),
(38, 4, 1, 1, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-04-30'),
(39, 4, 2, 1, 'ORDINARIO', 1, 94.00, 'APROBADO', '2026-04-30'),
(40, 4, 3, 1, 'ORDINARIO', 1, 91.00, 'APROBADO', '2026-04-30'),
(41, 4, 5, 1, 'ORDINARIO', 1, 91.00, 'APROBADO', '2026-04-30'),
(42, 4, 6, 1, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-04-30'),
(43, 4, 7, 1, 'ORDINARIO', 1, 90.00, 'APROBADO', '2026-04-30'),
(44, 4, 8, 1, 'ORDINARIO', 1, 94.00, 'APROBADO', '2026-04-30'),
(45, 4, 9, 1, 'ORDINARIO', 1, 93.00, 'APROBADO', '2026-04-30'),
(46, 4, 10, 1, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-04-30'),
(47, 5, 1, 1, 'ORDINARIO', 1, 64.00, 'REPROBADO', '2026-04-30'),
(48, 5, 2, 1, 'ORDINARIO', 1, 78.00, 'APROBADO', '2026-04-30'),
(49, 5, 3, 1, 'ORDINARIO', 1, 68.00, 'REPROBADO', '2026-04-30'),
(50, 5, 4, 1, 'ORDINARIO', 1, 76.00, 'APROBADO', '2026-04-30'),
(51, 5, 6, 1, 'ORDINARIO', 1, 78.00, 'APROBADO', '2026-04-30'),
(52, 5, 7, 1, 'ORDINARIO', 1, 75.00, 'APROBADO', '2026-04-30'),
(53, 5, 8, 1, 'ORDINARIO', 1, 80.00, 'APROBADO', '2026-04-30'),
(54, 5, 9, 1, 'ORDINARIO', 1, 77.00, 'APROBADO', '2026-04-30'),
(55, 5, 10, 1, 'ORDINARIO', 1, 79.00, 'APROBADO', '2026-04-30'),
(56, 6, 1, 1, 'ORDINARIO', 1, 96.00, 'APROBADO', '2026-04-30'),
(57, 6, 2, 1, 'ORDINARIO', 1, 95.00, 'APROBADO', '2026-04-30'),
(58, 6, 3, 1, 'ORDINARIO', 1, 94.00, 'APROBADO', '2026-04-30'),
(59, 6, 4, 1, 'ORDINARIO', 1, 97.00, 'APROBADO', '2026-04-30'),
(60, 6, 5, 1, 'ORDINARIO', 1, 96.00, 'APROBADO', '2026-04-30'),
(61, 6, 7, 1, 'ORDINARIO', 1, 95.00, 'APROBADO', '2026-04-30'),
(62, 6, 8, 1, 'ORDINARIO', 1, 94.00, 'APROBADO', '2026-04-30'),
(63, 6, 9, 1, 'ORDINARIO', 1, 96.00, 'APROBADO', '2026-04-30'),
(64, 6, 10, 1, 'ORDINARIO', 1, 95.00, 'APROBADO', '2026-04-30'),
(65, 1, 11, 3, 'ORDINARIO', 1, 91.00, 'APROBADO', '2026-12-20'),
(66, 1, 12, 3, 'ORDINARIO', 1, 88.00, 'APROBADO', '2026-12-20'),
(67, 1, 13, 3, 'ORDINARIO', 1, 93.00, 'APROBADO', '2026-12-20'),
(68, 1, 14, 3, 'ORDINARIO', 1, 90.00, 'APROBADO', '2026-12-20'),
(69, 1, 15, 3, 'ORDINARIO', 1, 92.00, 'APROBADO', '2026-12-20'),
(70, 1, 16, 10, 'ORDINARIO', 1, 87.00, 'APROBADO', '2027-04-30'),
(71, 1, 17, 10, 'ORDINARIO', 1, 89.00, 'APROBADO', '2027-04-30'),
(72, 1, 18, 10, 'ORDINARIO', 1, 94.00, 'APROBADO', '2027-04-30'),
(73, 1, 19, 10, 'ORDINARIO', 1, 90.00, 'APROBADO', '2027-04-30'),
(74, 1, 20, 10, 'ORDINARIO', 1, 91.00, 'APROBADO', '2027-04-30'),
(75, 1, 21, 11, 'ORDINARIO', 1, 95.00, 'APROBADO', '2027-08-31'),
(76, 1, 22, 11, 'ORDINARIO', 1, 92.00, 'APROBADO', '2027-08-31'),
(77, 1, 23, 11, 'ORDINARIO', 1, 90.00, 'APROBADO', '2027-08-31'),
(78, 1, 24, 11, 'ORDINARIO', 1, 93.00, 'APROBADO', '2027-08-31'),
(79, 1, 25, 11, 'ORDINARIO', 1, 94.00, 'APROBADO', '2027-08-31');

-- =========================================================
-- EXTRAORDINARIOS COMPLEMENTARIOS
-- =========================================================

-- Inserta extraordinarios complementarios para probar regularizaciones y no presentados.
INSERT INTO extraordinarios (
    id_extraordinario,
    id_alumno,
    id_materia,
    intento,
    fecha_examen,
    calificacion,
    estatus,
    observaciones
) VALUES
(2, 2, 2, 2, '2026-05-11', 72.00, 'APROBADO', 'Acreditado en segunda oportunidad.'),
(3, 3, 3, 2, '2026-05-12', 68.00, 'REPROBADO', 'No alcanzo el minimo aprobatorio.'),
(4, 4, 4, 2, '2026-05-13', 75.00, 'APROBADO', 'Acreditado en segunda oportunidad.'),
(5, 5, 5, 3, '2026-05-14', 70.00, 'APROBADO', 'Regularizacion aprobada.'),
(6, 6, 6, 2, '2026-05-15', 80.00, 'APROBADO', 'Calificacion maxima de extraordinario.'),
(7, 7, 7, 2, '2026-09-03', 65.00, 'REPROBADO', 'Requiere recursamiento.'),
(8, 8, 8, 2, '2026-09-04', 77.00, 'APROBADO', 'Acreditado en segunda oportunidad.'),
(9, 9, 9, 3, '2026-09-05', 0.00, 'NP', 'No se presento al examen.'),
(10, 10, 10, 2, '2026-09-06', 79.00, 'APROBADO', 'Acreditado en segunda oportunidad.');

-- =========================================================
-- EMPRESAS COMPLEMENTARIAS
-- =========================================================

-- Inserta empresas complementarias para servicio social y practicas.
INSERT INTO empresas (
    id_empresa,
    nombre,
    direccion,
    telefono,
    correo
) VALUES
(3, 'Laboratorio Forense del Pacifico', 'Calle Novena 900, Mexicali, Baja California', '6865550203', 'contacto@forensepacifico.com'),
(4, 'Instituto Municipal de Prevencion', 'Av. Ayuntamiento 120, Mexicali, Baja California', '6865550204', 'prevencion@institutomxl.gob.mx'),
(5, 'Clinica Integral del Valle', 'Blvd. Anahuac 700, Mexicali, Baja California', '6865550205', 'rh@clinicavalle.com'),
(6, 'Centro de Atencion Comunitaria Norte', 'Calle Norte 321, Mexicali, Baja California', '6865550206', 'contacto@cacnorte.org'),
(7, 'Consultores Educativos Frontera', 'Av. Colon 404, Mexicali, Baja California', '6865550207', 'info@cef.com.mx'),
(8, 'Despacho Juridico Rivera y Asociados', 'Calle Mexico 515, Mexicali, Baja California', '6865550208', 'contacto@riveraasociados.mx'),
(9, 'Seguridad Integral Baja', 'Blvd. Justo Sierra 280, Mexicali, Baja California', '6865550209', 'operaciones@seguridadbaja.mx'),
(10, 'Centro de Investigacion Social Aplicada', 'Av. Madero 618, Mexicali, Baja California', '6865550210', 'vinculacion@cisa.org.mx');

-- =========================================================
-- SERVICIO SOCIAL COMPLEMENTARIO
-- =========================================================

-- Registra servicios sociales complementarios con estados completados y en proceso.
INSERT INTO servicio_social (
    id_servicio,
    id_alumno,
    id_empresa,
    horas_requeridas,
    horas_completadas,
    fecha_inicio,
    fecha_fin,
    estado
) VALUES
(2, 2, 3, 480, 480, '2025-08-01', '2026-01-30', 'COMPLETADO'),
(3, 3, 4, 480, 260, '2026-02-01', NULL, 'EN_PROCESO'),
(4, 4, 5, 480, 480, '2025-08-01', '2026-01-30', 'COMPLETADO'),
(5, 5, 6, 480, 180, '2026-02-01', NULL, 'EN_PROCESO'),
(6, 6, 7, 480, 480, '2025-08-01', '2026-01-30', 'COMPLETADO'),
(7, 7, 8, 480, 90, '2026-05-10', NULL, 'EN_PROCESO'),
(8, 8, 9, 480, 140, '2026-05-10', NULL, 'EN_PROCESO'),
(9, 9, 10, 480, 480, '2025-08-01', '2026-01-30', 'COMPLETADO'),
(10, 10, 3, 480, 75, '2026-05-10', NULL, 'EN_PROCESO');

-- =========================================================
-- PRACTICAS PROFESIONALES COMPLEMENTARIAS
-- =========================================================

-- Registra practicas profesionales complementarias con proyectos y asesores.
INSERT INTO practicas_profesionales (
    id_practica,
    id_alumno,
    id_empresa,
    proyecto,
    asesor_empresa,
    asesor_universidad,
    fecha_inicio,
    fecha_fin,
    estado
) VALUES
(2, 2, 3, 'Apoyo en cadena de custodia documental', 'Roberto Valdez Cano', 'Adriana Soto Mendez', '2026-02-01', NULL, 'EN_PROCESO'),
(3, 3, 4, 'Programa de prevencion escolar', 'Isabel Duarte Solis', 'Fernando Luna Garcia', '2026-02-01', NULL, 'EN_PROCESO'),
(4, 4, 5, 'Analisis de expedientes clinicos', 'Mariana Ponce Diaz', 'Patricia Ortega Ruiz', '2026-02-01', NULL, 'EN_PROCESO'),
(5, 5, 6, 'Diagnostico comunitario de seguridad', 'Omar Beltran Nieto', 'Hector Vargas Nunez', '2026-02-01', NULL, 'EN_PROCESO'),
(6, 6, 7, 'Evaluacion de talleres preventivos', 'Ruth Campos Vera', 'Gabriela Medina Paz', '2026-02-01', NULL, 'EN_PROCESO'),
(7, 7, 8, 'Asistencia en archivo juridico', 'Laura Ibarra Leon', 'Jorge Cabrera Leon', '2026-05-15', NULL, 'EN_PROCESO'),
(8, 8, 9, 'Mapeo de indicadores de riesgo', 'Cesar Molina Paz', 'Marisol Campos Reyes', '2026-05-15', NULL, 'EN_PROCESO'),
(9, 9, 10, 'Investigacion social aplicada', 'Nadia Trejo Mora', 'Alberto Nava Rios', '2026-05-15', NULL, 'EN_PROCESO'),
(10, 10, 3, 'Control de evidencias digitales', 'Roberto Valdez Cano', 'Claudia Salazar Pena', '2026-05-15', NULL, 'EN_PROCESO');

-- =========================================================
-- TITULACION COMPLEMENTARIA
-- =========================================================

-- Registra procesos de titulacion complementarios con distintos avances.
INSERT INTO titulacion (
    id_titulacion,
    id_alumno,
    modalidad,
    cumple_promedio,
    servicio_social_liberado,
    practicas_liberadas,
    certificado_emitido,
    pagos_titulacion_completos,
    numero_autorizacion,
    acta_examen,
    titulo_emitido,
    fecha_titulacion,
    observaciones
) VALUES
(2, 2, 'PROMEDIO', TRUE, TRUE, FALSE, TRUE, FALSE, 'TIT-2026-0002', NULL, FALSE, NULL, 'Servicio social liberado, practicas en seguimiento.'),
(3, 3, 'TESINA', FALSE, FALSE, FALSE, FALSE, FALSE, NULL, NULL, FALSE, NULL, 'Registro preliminar de tesina.'),
(4, 4, 'PROMEDIO', TRUE, TRUE, FALSE, TRUE, TRUE, 'TIT-2026-0004', NULL, FALSE, NULL, 'Pendiente liberacion de practicas profesionales.'),
(5, 5, 'TESIS', FALSE, FALSE, FALSE, FALSE, FALSE, NULL, NULL, FALSE, NULL, 'Tema de tesis en revision.'),
(6, 6, 'PROMEDIO', TRUE, TRUE, FALSE, TRUE, TRUE, 'TIT-2026-0006', NULL, FALSE, NULL, 'Pendiente cierre de practicas.'),
(7, 7, 'TESINA', FALSE, FALSE, FALSE, FALSE, FALSE, NULL, NULL, FALSE, NULL, 'Expediente de titulacion iniciado.'),
(8, 8, 'TESIS', FALSE, FALSE, FALSE, FALSE, FALSE, NULL, NULL, FALSE, NULL, 'Proyecto de investigacion registrado.'),
(9, 9, 'PROMEDIO', FALSE, TRUE, FALSE, FALSE, FALSE, NULL, NULL, FALSE, NULL, 'Requiere acreditar materia pendiente.'),
(10, 10, 'TESINA', FALSE, FALSE, FALSE, FALSE, FALSE, NULL, NULL, FALSE, NULL, 'Registro preliminar de proceso de titulacion.');
