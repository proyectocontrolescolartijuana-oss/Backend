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
    fecha_autorizacion DATE,
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
    estado ENUM('ACTIVO','PENDIENTE','CERRADO') DEFAULT 'ACTIVO'
) ENGINE=InnoDB;

CREATE TABLE grupos (
    id_grupo BIGINT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    id_carrera INT,
    id_cuatrimestre INT,
    id_plan INT,
    turno ENUM('MATUTINO','VESPERTINO'),
    estatus ENUM('ACTIVO','CERRADO') DEFAULT 'ACTIVO',

    CONSTRAINT fk_grupo_carrera
        FOREIGN KEY (id_carrera)
        REFERENCES carreras(id_carrera),

    CONSTRAINT fk_grupo_cuatrimestre
        FOREIGN KEY (id_cuatrimestre)
        REFERENCES cuatrimestres(id_cuatrimestre),

    CONSTRAINT fk_grupo_plan
        FOREIGN KEY (id_plan)
        REFERENCES planes_estudio(id_plan)
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
    tipo_evaluacion ENUM('ORDINARIO','EXTRAORDINARIO','EQUIVALENCIA'),
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

CREATE TABLE cierres_periodo (
    id_cierre BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_periodo_cerrado INT NOT NULL,
    id_periodo_activado INT,
    resumen_json TEXT,
    fecha_cierre DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cierre_periodo_cerrado
        FOREIGN KEY (id_periodo_cerrado)
        REFERENCES periodos(id_periodo),

    CONSTRAINT fk_cierre_periodo_activado
        FOREIGN KEY (id_periodo_activado)
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
    carta_unifront BOOLEAN NOT NULL DEFAULT FALSE,
    carta_procedencia BOOLEAN NOT NULL DEFAULT FALSE,

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
    oficio_campo BOOLEAN NOT NULL DEFAULT FALSE,
    horas_campo INT,

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

CREATE TABLE documentos_egresado (
    id_documento BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_alumno BIGINT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documento_egresado_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumnos(id_alumno),

    CONSTRAINT uq_documento_egresado_tipo
        UNIQUE (id_alumno, tipo)
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

CREATE INDEX idx_documentos_titulacion_requisito
ON documentos_titulacion(id_titulacion, requisito);

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
    'Sistema',
    'Administrador',
    'Del',
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
    'BC-053-M2/14',
    'Licenciatura en Criminología',
    'LICENCIATURA',
    9,
    TRUE,
    'logo_criminologia.png'
),
(
    '260126',
    'BC-051-M2/14',
    'Licenciatura en Gastronomía',
    'LICENCIATURA',
    9,
    TRUE,
    'logo_gastronomia.png'
),
(
    '260127',
    'BC-L010-M2/17',
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
(7, 2, 'OBLIGATORIO'),
(17, 12, 'OBLIGATORIO'),
(19, 1, 'OBLIGATORIO'),
(21, 7, 'OBLIGATORIO');

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
('CURP');

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
    '1',
    'CONTROL',
    'ESCOLAR',
    'control.escolar@unifront.com',
    '$2b$12$fDyZK5l1./1TY19rgskvc.lVaerFgt3eIjBN3JVUl2guZ1i0V64Ii',
    '6862223344',
    'ACTIVO'
);

-- Relaciona el usuario de control escolar con el rol CONTROL_ESCOLAR.
INSERT INTO usuario_roles (id_usuario, id_rol)
VALUES (2, 2);
