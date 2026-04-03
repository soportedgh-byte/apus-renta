# Corpus Documental — CecilIA v2

> Sistema de IA para Control Fiscal
> Contraloría General de la República de Colombia

## Descripción General

Este directorio contiene el corpus documental que alimenta el motor RAG (Retrieval-Augmented Generation) de CecilIA v2. Los documentos están organizados en **7 colecciones temáticas**, cada una con un propósito específico dentro del dominio del control fiscal colombiano.

---

## Colecciones

### 1. `normativo/`

**Propósito:** Marco normativo vigente del control fiscal en Colombia.

**Contenido esperado:**
- Constitución Política de Colombia (artículos relevantes: 267–274)
- Leyes orgánicas de control fiscal (Ley 42 de 1993, Ley 610 de 2000, Ley 1474 de 2011)
- Decretos reglamentarios
- Resoluciones de la CGR
- Documentos CONPES relacionados con vigilancia fiscal
- Normas Internacionales de Auditoría (NIA) adoptadas

### 2. `institucional/`

**Propósito:** Documentación interna de la Contraloría General de la República.

**Contenido esperado:**
- Guías de auditoría de la CGR
- Manual del Sistema de Gestión y Control Interno (SIGECI)
- Estudios previos de procesos auditores
- Informes de auditoría publicados
- Planes de acción y mejora
- Procedimientos operativos estándar

### 3. `academico/`

**Propósito:** Literatura académica y de investigación sobre política pública y control fiscal.

**Contenido esperado:**
- Artículos indexados en revistas académicas (Scopus, WoS, SciELO)
- Libros y capítulos sobre control fiscal
- Tesis y trabajos de grado relevantes
- Documentos de organismos internacionales (INTOSAI, OLACEFS)
- Investigaciones sobre gobernanza y transparencia

### 4. `tecnico_tic/`

**Propósito:** Documentación técnica del sector TIC colombiano.

**Contenido esperado:**
- Documentos técnicos del MinTIC
- Informes del Plan Vive Digital y programas sucesores
- Indicadores sectoriales de telecomunicaciones
- Normatividad específica del sector TIC (Ley 1341 de 2009)
- Planes de conectividad nacional y regional
- Informes de ejecución de programas TIC

### 5. `estadistico/`

**Propósito:** Datos estadísticos y fuentes cuantitativas de referencia.

**Contenido esperado:**
- Datos del DANE (censos, encuestas, indicadores)
- Estadísticas del MinTIC (penetración, cobertura, inversión)
- Informes de la UIT (Unión Internacional de Telecomunicaciones)
- Series históricas de ejecución presupuestal
- Indicadores de gestión fiscal territorial

### 6. `jurisprudencial/`

**Propósito:** Jurisprudencia relevante de las Altas Cortes colombianas.

**Contenido esperado:**
- Sentencias de la Corte Constitucional sobre control fiscal
- Fallos del Consejo de Estado
- Conceptos de la Sala de Consulta y Servicio Civil
- Sentencias de la Corte Suprema de Justicia (casos relacionados)
- Autos y providencias relevantes

### 7. `auditoria/`

**Propósito:** Formatos, procedimientos y hallazgos previos para referencia.

**Contenido esperado:**
- Formatos estándar de hallazgos fiscales
- Procedimientos de auditoría (planificación, ejecución, informe)
- Hallazgos previos anonimizados (sin datos personales)
- Matrices de riesgo
- Papeles de trabajo modelo

---

## Instrucciones para Agregar Documentos

### Formatos soportados

| Formato | Extensión | Notas |
|---------|-----------|-------|
| PDF     | `.pdf`    | Preferiblemente con texto seleccionable (no escaneados) |
| Word    | `.docx`   | Compatible con Microsoft Word 2010+ |
| Excel   | `.xlsx`   | Todas las hojas serán procesadas |

### Pasos para agregar un documento

1. **Identificar la colección** adecuada según la temática del documento.

2. **Copiar el archivo** al subdirectorio correspondiente:
   ```bash
   cp mi_documento.pdf corpus/normativo/
   ```

3. **Nombrar el archivo** de forma descriptiva, sin espacios (usar guiones bajos):
   ```
   ley_42_1993_control_fiscal.pdf
   guia_auditoria_cgr_2024.docx
   ```

4. **Ejecutar la ingestión** para procesar el nuevo documento:
   ```bash
   python scripts/ingest_corpus.py
   ```

5. **Verificar** que el documento fue procesado correctamente en los logs de ingestión.

### Consideraciones importantes

- **Datos personales:** NO incluir documentos con datos personales sin anonimizar. La Ley 1581 de 2012 (Protección de Datos Personales) aplica.
- **Clasificación:** Verificar que el documento no tenga clasificación de seguridad que impida su procesamiento.
- **Calidad:** Documentos escaneados como imagen requieren OCR previo. Se recomienda texto nativo.
- **Tamaño:** Archivos mayores a 100 MB deben ser segmentados antes de la ingestión.
- **Duplicados:** El sistema detecta duplicados por nombre de archivo dentro de cada colección.

### Estructura de directorios esperada

```
corpus/
├── README.md                  ← Este archivo
├── normativo/
│   ├── constitucion_politica_arts_267_274.pdf
│   ├── ley_42_1993.pdf
│   └── ...
├── institucional/
│   ├── guia_auditoria_cgr.pdf
│   └── ...
├── academico/
│   └── ...
├── tecnico_tic/
│   └── ...
├── estadistico/
│   └── ...
├── jurisprudencial/
│   └── ...
└── auditoria/
    ├── formato_hallazgo_fiscal.docx
    └── ...
```

---

## Contacto

Para consultas sobre el corpus documental, comunicarse con el Equipo Técnico CecilIA — CD-TIC-CGR.
