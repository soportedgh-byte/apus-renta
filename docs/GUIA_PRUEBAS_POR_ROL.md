# GUIA DE PRUEBAS POR ROL — CecilIA v2

**Pruebas de Contexto — Preproduccion**
**Contraloria General de la Republica — CD-TIC-CGR**
**Fecha:** Abril 2026

---

## Instrucciones Generales

1. Acceder a CecilIA en: **https://cecilia.apusinc.co** (o **http://localhost:3000** en ambiente local)
2. Usar las credenciales asignadas a su rol
3. Seguir los pasos de prueba en orden
4. Anotar observaciones en el Formato de Retroalimentacion
5. Reportar errores criticos inmediatamente a: gustavo.castillo@contraloria.gov.co

**Importante:** CecilIA genera borradores y sugerencias. Toda salida requiere validacion humana conforme a la Circular 023 de la CGR.

---

## Para ADMIN_TIC (Ing. Gustavo Castillo)

```
ACCESO: admin.cecilia / CecilIA_Admin_2026!
DIRECCION: Acceso total (DES + DVF)

QUE PROBAR:
1. Login -> verificar acceso a TODOS los modulos (12 modulos)
2. Administracion: gestionar usuarios, ver logs de trazabilidad
3. Chat: enviar consultas de ambas direcciones (DES y DVF)
4. RAG: verificar estado de colecciones en /admin
5. Analytics: revisar dashboard completo con todas las metricas
6. Observatorio: verificar alertas del sector TIC
7. Capacitacion: verificar las 4 rutas de aprendizaje
8. Formatos: generar al menos 2 formatos distintos y descargar DOCX
9. Configuracion: verificar modelo LLM activo
10. Verificar que creditos Dr. Omar Contreras aparecen en login y footer

EVALUAR:
- Acceso completo sin restricciones
- Que ningun modulo falle al cargar
- Que los logs de trazabilidad registren las operaciones
```

---

## Para LIDER_TECNICO (Ing. Gustavo Castillo)

```
ACCESO: gustavo.castillo / Lider_Tech_2026!
DIRECCION: Acceso total (DES + DVF)

QUE PROBAR:
1. Login -> verificar acceso equivalente a admin
2. Configuracion de modelos LLM
3. Administracion de colecciones RAG
4. Gestion de usuarios
5. Verificar que los 16 routers estan registrados en /docs

EVALUAR:
- Que el rol lider_tecnico tiene los mismos permisos que admin_tic
- Que puede configurar el modelo LLM activo
```

---

## Para DIRECTOR_DES (Dr. Juan Carlos Cobo)

```
ACCESO: juan.cobo / DES_Director_2026!
DIRECCION: Seleccionar DES al iniciar sesion

QUE PROBAR:
1. Login -> seleccionar DES -> verificar que ve 8 modulos:
   chat, documentos, hallazgos, formatos, auditoria, analitica, observatorio, capacitacion
2. Chat: "Cual es el estado del sector TIC en Colombia?"
   -> Verificar que la respuesta cita fuentes del RAG
   -> Verificar que aparece disclaimer Circular 023
3. Chat: "Necesito un analisis de ejecucion presupuestal del sector TIC"
   -> Verificar que CecilIA entiende el contexto DES
4. Observatorio TIC: verificar si hay alertas reales del sector
5. Analytics: revisar dashboard con metricas del equipo DES
6. Capacitacion: verificar que las rutas de aprendizaje tienen contenido
7. Formatos: generar un formato y verificar encabezado institucional CGR
8. Hallazgos: verificar panel, probar aprobacion (solo Director puede aprobar)

EVALUAR (escala 1-5):
- Calidad de las respuestas: son relevantes para DES?
- Citacion de fuentes: cita normatividad correcta?
- Facilidad de uso: la interfaz es intuitiva?
- Utilidad real: le ahorra tiempo en su trabajo?
- Observatorio: las alertas son relevantes para su direccion?
```

---

## Para DIRECTOR_DVF (Dr. Jose Fernando Ramirez)

```
ACCESO: jose.ramirez / DVF_Director_2026!
DIRECCION: Seleccionar DVF al iniciar sesion

QUE PROBAR:
1. Login -> seleccionar DVF -> verificar modulos DVF (8 modulos)
2. Chat: "Necesito planear una auditoria a MinTIC vigencia 2025"
   -> Verificar que responde con las fases del proceso auditor
   -> Verificar citacion de la GAF
3. Formatos: generar Formato 14 (Matriz de Riesgos)
   -> Descargar DOCX y verificar estructura
   -> Verificar encabezado institucional CGR
   -> Verificar nota Circular 023 en pie de pagina
   -> Verificar que checkbox de validacion funciona antes de descargar
4. Formatos: generar Formato 17 (Materialidad)
   -> Verificar calculos
5. Hallazgos: revisar panel de hallazgos
   -> Verificar que puede aprobar hallazgos (privilegio de Director)
   -> Verificar workflow: borrador -> revision -> aprobado
6. Analytics: revisar metricas del equipo DVF
7. Chat: "Calcula la materialidad para activos de 500.000 millones"
   -> Verificar que usa la herramienta de calculo de materialidad

EVALUAR (escala 1-5):
- Calidad de formatos DOCX: estructura correcta segun GAF?
- Workflow de hallazgos: el proceso de aprobacion es claro?
- Calculos de materialidad: son correctos segun Instructivo 2?
- Calidad general de las respuestas de auditoria
```

---

## Para AUDITOR_DVF (Auditores de campo)

```
ACCESO: auditor.dvf.01 / Auditor_DVF_2026!
DIRECCION: Seleccionar DVF

QUE PROBAR:
1. Login -> DVF -> verificar 6 modulos:
   chat, documentos, hallazgos, formatos, auditoria, capacitacion
2. Chat: probar acciones rapidas del sidebar:
   - "Consultar normativa vigente" sobre el tema que prefiera
   - "Estructurar hallazgo" para un hallazgo ficticio
   - "Generar formato CGR" pidiendo un formato especifico
   - "Verificar presupuesto entidad" para una entidad conocida
3. Chat: "Encontre un pago sin soporte por 50 millones en MinTIC"
   -> Verificar que CecilIA estructura el hallazgo con condicion/criterio/causa/efecto
4. Formatos: pedir "Genera el Formato 5 de analisis financiero"
   -> Descargar DOCX y verificar en Word/LibreOffice
5. Hallazgos: verificar que puede CREAR hallazgos pero NO aprobar
6. Documentos: intentar subir un PDF de prueba
7. Capacitacion: explorar al menos 1 ruta de aprendizaje

EVALUAR (escala 1-5):
- CecilIA entiende el lenguaje de auditoria?
- Los formatos se generan correctamente?
- Los hallazgos se estructuran bien (condicion/criterio/causa/efecto)?
- Le ahorraria tiempo real en una auditoria?
- Las fuentes citadas son correctas?
```

---

## Para AUDITOR_DES (Investigadores sectoriales)

```
ACCESO: auditor.des.01 / Auditor_DES_2026!
DIRECCION: Seleccionar DES

QUE PROBAR:
1. Login -> DES -> verificar 6 modulos:
   chat, documentos, hallazgos, formatos, auditoria, capacitacion
2. Chat: probar acciones rapidas DES:
   - "Consultar normativa vigente" sobre sector TIC
   - "Analizar riesgo sectorial" del sector telecomunicaciones
3. Chat: "Analiza la ejecucion presupuestal del FUTIC"
   -> Verificar que CecilIA conoce el FUTIC
4. Chat: "Que proyectos de ley del sector TIC estan en tramite?"
   -> Verificar si consulta la API del Congreso
5. Verificar que NO tiene acceso al modulo de Observatorio
   (solo Directores y admin)

EVALUAR (escala 1-5):
- Las respuestas son utiles para estudios sectoriales?
- Cita fuentes relevantes (DANE, MinTIC, ITU)?
- Entiende el contexto macro (DES) vs micro (DVF)?
```

---

## Para COORDINADOR (Dra. Karen Suevis)

```
ACCESO: karen.suevis / Coord_Legal_2026!
DIRECCION: DES o DVF (seleccionar)

QUE PROBAR:
1. Login -> verificar 7 modulos:
   chat, documentos, hallazgos, formatos, auditoria, analitica, capacitacion
2. Chat: "Que dice la Circular 023 sobre el uso de IA?"
   -> Verificar que cita la circular correctamente
3. Chat: "Cuales son los principios eticos del CONPES 4144?"
4. Verificar analitica: que las metricas reflejen datos reales
5. Verificar que puede crear y editar hallazgos pero NO aprobar
6. Generar un formato y verificar nota juridica en pie de pagina

EVALUAR (escala 1-5):
- Precision en citacion de normatividad
- Utilidad para revision juridica de documentos
- Cumplimiento de Circular 023 en la interfaz
```

---

## Para OBSERVATORIO (observador.cgr)

```
ACCESO: observador.cgr / Observador_2026!
DIRECCION: N/A (acceso observatorio)

QUE PROBAR:
1. Login -> verificar 5 modulos:
   chat, documentos, observatorio, analitica, capacitacion
2. Observatorio: revisar alertas activas del sector TIC
3. Observatorio: crear una nueva alerta de prueba
4. Chat: "Cuales son las tendencias del sector telecomunicaciones?"
5. Analitica: verificar que puede ver metricas de uso

EVALUAR:
- Las alertas del observatorio son relevantes?
- El clasificador de IA categoriza bien las alertas?
```

---

## Para APRENDIZ (Funcionarios nuevos)

```
ACCESO: aprendiz.dvf / Aprendiz_DVF_2026!
   O:   aprendiz.des / Aprendiz_DES_2026!
DIRECCION: DVF o DES segun usuario

QUE PROBAR:
1. Login -> verificar que SOLO ve 3 modulos: capacitacion, biblioteca, simulador
2. Verificar que NO tiene acceso a: chat general, hallazgos, formatos, auditorias
3. Explorar las 4 rutas de aprendizaje:
   - "Conoce la CGR" (estructura, funciones, marco constitucional)
   - "Auditoria DVF — Paso a paso" (5 fases del proceso auditor)
   - "Estudios DES" (metodologia de estudios sectoriales)
   - "Etica IA y Circular 023" (uso responsable de IA)
4. Completar al menos 2 lecciones de una ruta
5. Hacer el quiz de evaluacion de la ruta
6. Preguntar al tutor:
   - "Soy nuevo en la CGR, por donde empiezo?"
   - "Explicame que es un hallazgo fiscal"
   - "Que es la materialidad y como se calcula?"
   - "Que sistemas institucionales debo conocer?"
7. Verificar que el tutor responde como experto, no superficialmente

EVALUAR (escala 1-5):
- Las explicaciones son claras y didacticas?
- El tutor responde como un experto o como Wikipedia?
- Los quizzes evaluan conocimiento real?
- Se siente como hablar con un mentor experimentado?
- Las lecciones tienen contenido real (no placeholders)?
```

---

## Notas Importantes para Todos los Evaluadores

1. **Circular 023:** Cada respuesta de CecilIA debe incluir el disclaimer "Asistido por IA — Requiere validacion humana". Si no aparece, reportar como error.

2. **Fuentes:** Las respuestas deben citar las fuentes consultadas del RAG. Si una respuesta no cita fuentes, verificar si la pregunta requeria consulta al corpus.

3. **Formatos DOCX:** Al descargar cualquier formato, verificar:
   - Se abre correctamente en Word/LibreOffice
   - Tiene encabezado institucional de la CGR
   - Tiene nota Circular 023 en pie de pagina
   - El checkbox de validacion humana funciona

4. **Errores:** Si CecilIA responde "Ocurrio un error", anotar la pregunta exacta y reportar. Puede ser un problema de conexion con el proveedor LLM.

5. **Privacidad:** Los datos de auditoria se almacenan como contexto de sesion en servidores de la CGR. No se utilizan para entrenar modelos de IA.

---

*Guia elaborada por el Equipo Tecnico CecilIA — CD-TIC-CGR*
*Proyecto concebido e impulsado bajo la direccion del Dr. Omar Javier Contreras Socarras*
