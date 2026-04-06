# INFORME EJECUTIVO DE PREPRODUCCION — CecilIA v2

**Sistema de Inteligencia Artificial para Control Fiscal**
**Contraloria General de la Republica de Colombia — CD-TIC-CGR**

**Fecha:** 6 de abril de 2026
**Version:** 2.0.0
**Elaborado por:** Equipo Tecnico CecilIA — Ing. Gustavo Adolfo Castillo Romero

---

## Seccion 1: Resumen Ejecutivo

CecilIA v2 es el Sistema de Inteligencia Artificial desarrollado por la Contraloria Delegada para el Sector TIC (CD-TIC) de la Contraloria General de la Republica de Colombia. Su nombre deriva del latin *caecus* — "aquel que no se deslumbra por lo superficial" — y su proposito es asistir a los auditores de las direcciones DES (Estudios Sectoriales) y DVF (Vigilancia Fiscal) en sus procesos de control fiscal, cumpliendo estrictamente la Circular 023 de la CGR.

El sistema integra un pipeline RAG (Retrieval-Augmented Generation) con un corpus de documentos normativos e institucionales, un sistema multi-agente basado en LangGraph que distribuye consultas entre agentes especializados por fase de auditoria, y un generador de Formatos CGR 1-30 con encabezado institucional. CecilIA opera como asistente — nunca como reemplazo del auditor — generando borradores y sugerencias que requieren validacion humana obligatoria.

A la fecha se han completado 11 sprints de desarrollo que cubren: infraestructura base, pipeline RAG con 10,016 chunks vectorizados, chat con streaming SSE, generacion de formatos DOCX, gestion de hallazgos con workflow de aprobacion, modulo de capacitacion, conectores a APIs externas (SECOP, DANE, Congreso), observatorio TIC, pipeline de fine-tuning, dashboard de analitica y workspace local con memoria de sesion. El sistema esta listo para iniciar pruebas de contexto con auditores reales.

---

## Seccion 2: Funcionalidades Implementadas y Operativas

| # | Funcionalidad | Sprint | Estado | Descripcion para el auditor |
|---|---------------|--------|--------|---------------------------|
| 1 | Autenticacion y RBAC | 0 | Operativa | Login con 10 roles, seleccion de direccion DES/DVF, permisos por modulo |
| 2 | Pipeline RAG | 1 | Operativa | 221 documentos ingestados, 10,016 chunks con embeddings, busqueda semantica en 7 colecciones |
| 3 | Chat con IA (streaming) | 2 | Operativa | Chat con respuestas en tiempo real, sistema multi-agente con supervisor, disclaimer Circular 023, citacion de fuentes |
| 4 | CRUD de conversaciones | 2.1 | Operativa | Crear, renombrar, eliminar conversaciones, historial persistente |
| 5 | Circular 023 CGR | C023 | Operativa | Disclaimers, modal de aceptacion, checkbox de validacion, nota en documentos |
| 6 | Frontend profesional | 3 | Operativa | Login con logos institucionales, sidebar con 3 tabs, paleta de colores CGR |
| 7 | Formatos CGR 1-30 | 4 | Operativa | 15 formatos implementados de los 30 totales, generacion DOCX con encabezado institucional |
| 8 | Gestion de hallazgos | 5 | Operativa | CRUD con 4 elementos (condicion/criterio/causa/efecto), workflow de aprobacion, oficios de traslado |
| 9 | Capacitacion | 6 | Operativa | 4 rutas de aprendizaje, agente tutor experto, quizzes, simulador de auditoria |
| 10 | APIs externas | 7 | Parcial | SECOP funcional (datos reales), DANE con errores intermitentes, Congreso funcional, stubs CGR pendientes de credenciales |
| 11 | Observatorio TIC | 8 | Operativa | Crawlers MinTIC/CRC/ANE, alertas clasificadas por IA, solo visible para usuarios DES |
| 12 | Fine-tuning pipeline | 9 | Operativa (sin GPU) | Pipeline LoRA preparado, benchmark 50 preguntas, pendiente GPU para entrenamiento |
| 13 | Dashboard analitica | 10 | Operativa | Metricas de uso, feedback, auditorias, capacitacion, exportacion Excel/DOCX |
| 14 | Workspace local | 11 | Parcial | Desktop Agent Electron creado, backend WebSocket con auth, memoria de sesion funcional; agente requiere instalacion manual |
| 15 | Memoria de sesion | 11 | Operativa | Proyectos de auditoria con contexto persistente, resumen automatico de sesiones, restauracion al reconectar |

---

## Seccion 3: Funcionalidades Pendientes para Produccion

| # | Pendiente | Responsable | Dependencia |
|---|-----------|-------------|-------------|
| 1 | Despliegue en VPS con Nginx, SSL, CI/CD | Equipo Tecnico | Servidor asignado |
| 2 | Integracion con Active Directory CGR | Equipo Tecnico + OSEI | Credenciales AD |
| 3 | Credenciales sistemas internos (SIRECI, SIGECI, APA, DIARI) | OSEI | Aprobacion OSEI |
| 4 | GPU para modelo local (oficio 2026IE0029991) | CD-TIC | Aprobacion presupuestal |
| 5 | Pentesting por USATI | USATI | Coordinacion con USATI |
| 6 | Documentacion institucional completa (17 documentos) | Equipo Tecnico | Revision juridica |
| 7 | Capacitacion de usuarios finales | Equipo Tecnico + Directores | Post pruebas de contexto |
| 8 | Registro ante DNDA (Direccion Nacional de Derechos de Autor) | Coordinacion Juridica | Documentacion lista |
| 9 | Completar formatos CGR 15-30 | Equipo Tecnico | Plantillas GAF |
| 10 | Poblar colecciones vacias del corpus (academico, tecnico_tic, estadistico, jurisprudencial) | Equipo Tecnico | Documentos fuente |

---

## Seccion 4: Indicadores Tecnicos Reales

| Indicador | Valor | Nota |
|-----------|-------|------|
| Documentos en corpus | 221 | 3 colecciones pobladas, 4 vacias |
| Chunks vectorizados | 10,016 | normativo: 1,824; institucional: 7,840; auditoria: 352 |
| Colecciones RAG | 7 | 3 con datos, 4 vacias (academico, tecnico_tic, estadistico, jurisprudencial) |
| Formatos CGR implementados | 15 de 30 | Formatos 1, 3, 5, 7, 8, 10, 12, 14, 15, 17, 18, 20, 22, 25, 28 |
| Rutas de capacitacion | 4 | Conoce la CGR, Auditoria DVF, Estudios DES, Etica IA |
| Endpoints API | 70+ | 16 routers registrados |
| Usuarios registrados | 14 | 12 originales + 2 aprendices |
| Conversaciones registradas | 9 | Datos de prueba interna |
| Mensajes totales | 17 | Datos de prueba interna |
| Hallazgos creados | 0 | Ninguno creado en pruebas |
| Formatos generados en BD | 17 | De pruebas internas |
| Tablas PostgreSQL | 16+ | Incluyendo proyectos_auditoria (Sprint 11) |
| Modelo LLM activo | Gemini 2.5 Flash | Google Gemini como proveedor principal |
| Proveedor LLM backup | Claude (Anthropic) | Pendiente creditos |
| Cobertura de tests | Sin medicion automatizada | Tests manuales por sprint |
| Tiempo respuesta LLM | Variable | Dependiente del proveedor y carga |
| Arquitectura | Monorepo Docker | backend + frontend + postgres + redis + scheduler |

---

## Seccion 5: Riesgos y Mitigaciones para Pruebas de Contexto

| # | Riesgo | Impacto | Probabilidad | Mitigacion |
|---|--------|---------|-------------|------------|
| 1 | Creditos API insuficientes para LLM | Alto | Media | Sistema multi-proveedor: Gemini (principal), Claude (backup), Ollama (local). Cambiar 3 variables en .env |
| 2 | Corpus incompleto (4 colecciones vacias) | Medio | Alta | Las 3 colecciones pobladas cubren normativo + institucional + auditoria. Agregar documentos progresivamente |
| 3 | Errores en formatos DOCX | Medio | Baja | Validacion humana obligatoria (Circular 023). Checkbox antes de descarga |
| 4 | Alucinaciones del modelo | Alto | Media | Anti-alucinacion activo (temperature 0.2), citacion obligatoria de fuentes RAG, disclaimer en cada respuesta |
| 5 | Desconexion del proveedor LLM | Alto | Baja | Fallback automatico entre proveedores. Chat muestra error claro si no hay conexion |
| 6 | Carga concurrente en pruebas | Medio | Baja | Pool de conexiones configurado (10 + 20 overflow). Redis para cache de sesiones |
| 7 | Datos sensibles en pruebas | Alto | Baja | Anonimizacion activa (Ley 1581/2012), no usar datos reales de auditoria en pruebas |
| 8 | Falta de GPU para modelo local | Bajo | Alta | No bloquea pruebas. Fine-tuning es mejora futura, no requisito para preproduccion |

---

## Seccion 6: Cronograma Sugerido para Pruebas de Contexto

| Semana | Periodo | Actividad | Participantes | Entregable |
|--------|---------|-----------|---------------|------------|
| 1 | 7-11 abril 2026 | Pruebas funcionales internas | Ing. Gustavo Castillo, Dra. Karen Suevis | Lista de bugs corregidos |
| 2 | 14-18 abril 2026 | Revision de calidad por directores | Dr. Juan Carlos Cobo (DES), Dr. Jose Fernando Ramirez (DVF) | Feedback de directores |
| 3 | 21-25 abril 2026 | Pruebas con auditores DES | 3 auditores DES con casos reales | Formatos de retroalimentacion DES |
| 4 | 28 abril - 2 mayo 2026 | Pruebas con auditores DVF | 3 auditores DVF con casos reales | Formatos de retroalimentacion DVF |
| 5 | 5-9 mayo 2026 | Consolidacion y correcciones | Equipo Tecnico | Informe de pruebas, plan de correccion |

**Nota:** El cronograma esta sujeto a la disponibilidad de creditos API y acceso al servidor de preproduccion.

---

## Firmas

**Elaborado por:**
Ing. Gustavo Adolfo Castillo Romero — Lider Tecnico CecilIA
Contraloria Delegada para el Sector TIC — CD-TIC-CGR

**Revisado por:**
Dr. Hector Hernan Gonzalez Naranjo — Contralor Delegado TIC

**Proyecto concebido e impulsado bajo la direccion del Dr. Omar Javier Contreras Socarras**

---

*CecilIA v2.0 — Preproduccion — Abril 2026*
*Circular 023 CGR — Uso responsable de Inteligencia Artificial*
