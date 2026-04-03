# Política de Tratamiento de Datos — CecilIA v2

> Sistema de IA para Control Fiscal
> Contraloría General de la República de Colombia

## 1. Objeto

La presente política establece los lineamientos para el tratamiento de datos personales y datos institucionales dentro del sistema CecilIA v2, en cumplimiento de la Ley Estatutaria 1581 de 2012, el Decreto Reglamentario 1377 de 2013, y demás normatividad vigente en materia de protección de datos personales en Colombia.

## 2. Marco Normativo

| Norma | Descripción |
|-------|-------------|
| **Ley 1581 de 2012** | Ley Estatutaria de Protección de Datos Personales |
| **Decreto 1377 de 2013** | Reglamenta parcialmente la Ley 1581 de 2012 |
| **Ley 1712 de 2014** | Ley de Transparencia y del Derecho de Acceso a la Información Pública |
| **Decreto 1074 de 2015** | Decreto Único Reglamentario del Sector Comercio, Industria y Turismo (Título 26) |
| **Constitución Política** | Artículo 15 — Derecho a la intimidad y habeas data |
| **Ley 1266 de 2008** | Habeas data financiero |
| **Circular 002 de 2015 SIC** | Lineamientos de seguridad para el tratamiento de datos personales |

## 3. Definiciones

- **Dato personal:** Cualquier información vinculada o que pueda asociarse a una persona natural determinada o determinable.
- **Dato sensible:** Aquel que afecta la intimidad del titular o cuyo uso indebido puede generar discriminación (origen racial, orientación política, convicciones religiosas, datos biométricos, salud, vida sexual).
- **Tratamiento:** Cualquier operación sobre datos personales: recolección, almacenamiento, uso, circulación, supresión.
- **Responsable del tratamiento:** La Contraloría General de la República, a través del equipo CD-TIC-CGR.
- **Encargado del tratamiento:** El sistema CecilIA v2 y sus operadores técnicos.
- **Titular:** Persona natural cuyos datos personales sean objeto de tratamiento.

## 4. Principios Rectores

De conformidad con el artículo 4 de la Ley 1581 de 2012, el tratamiento de datos en CecilIA v2 se rige por:

1. **Legalidad:** Todo tratamiento se sujeta a lo establecido en la ley.
2. **Finalidad:** El tratamiento obedece a una finalidad legítima, informada al titular.
3. **Libertad:** El tratamiento solo puede ejercerse con el consentimiento previo, expreso e informado del titular.
4. **Veracidad:** La información sujeta a tratamiento debe ser veraz, completa, exacta y actualizada.
5. **Transparencia:** El titular puede conocer en cualquier momento la existencia de datos que le conciernan.
6. **Acceso y circulación restringida:** El tratamiento se sujeta a los límites derivados de la naturaleza de los datos.
7. **Seguridad:** La información se maneja con las medidas técnicas, humanas y administrativas necesarias.
8. **Confidencialidad:** Las personas que intervienen en el tratamiento están obligadas a garantizar la reserva.

## 5. Categorías de Datos Tratados

### 5.1 Datos de Usuarios del Sistema

| Campo | Tipo | Finalidad |
|-------|------|-----------|
| Nombre completo | Personal | Identificación en el sistema |
| Usuario (login) | Personal | Autenticación |
| Contraseña (hash) | Confidencial | Autenticación segura |
| Rol | Institucional | Control de acceso (RBAC) |
| Dirección técnica | Institucional | Segregación de funciones |
| Registro de actividad | Institucional | Auditoría del sistema |

### 5.2 Datos del Corpus Documental

- Documentos normativos de carácter público
- Documentos institucionales de la CGR
- Hallazgos previos **anonimizados** (sin datos que permitan identificar personas naturales)
- Datos estadísticos agregados

### 5.3 Datos Generados por el Sistema

- Historial de conversaciones con el asistente IA
- Resultados de análisis (materialidad, Benford, muestreo)
- Hallazgos generados asistidamente

## 6. Medidas de Seguridad Técnicas

### 6.1 Autenticación y Control de Acceso

- Contraseñas almacenadas exclusivamente como hash bcrypt (12 rondas); **NUNCA** en texto plano.
- Tokens JWT con expiración configurable.
- Control de acceso basado en roles (RBAC) con segregación por dirección técnica.
- Bloqueo de cuenta tras intentos fallidos de autenticación.

### 6.2 Cifrado

- **En tránsito:** TLS 1.3 obligatorio para todas las comunicaciones.
- **En reposo:** Cifrado a nivel de volumen para la base de datos PostgreSQL.
- **Tokens:** JWT firmados con clave secreta de al menos 256 bits.

### 6.3 Anonimización

- Todo documento del corpus que contenga datos personales debe ser anonimizado **antes** de su ingestión.
- Técnicas aplicables: supresión, generalización, pseudonimización.
- El equipo responsable debe verificar la efectividad de la anonimización.

### 6.4 Registro de Actividad

- Toda acción del sistema queda registrada con: usuario, fecha/hora, acción, recurso afectado.
- Los logs se almacenan de forma centralizada y se retienen por un mínimo de **5 años**.
- El acceso a los logs está restringido al rol ADMIN y LIDER_TECNICO.

### 6.5 Respaldo y Recuperación

- Respaldos automatizados de la base de datos cada 24 horas.
- Retención de respaldos por 30 días.
- Pruebas de restauración trimestrales.

## 7. Derechos de los Titulares

De conformidad con el artículo 8 de la Ley 1581 de 2012, los titulares tienen derecho a:

1. **Conocer, actualizar y rectificar** sus datos personales.
2. **Solicitar prueba** de la autorización otorgada.
3. **Ser informado** respecto del uso que se ha dado a sus datos.
4. **Presentar quejas** ante la Superintendencia de Industria y Comercio.
5. **Revocar** la autorización y/o solicitar la supresión del dato.
6. **Acceder gratuitamente** a sus datos personales que hayan sido objeto de tratamiento.

### Procedimiento para ejercer derechos

Los titulares pueden ejercer sus derechos mediante comunicación escrita dirigida a:

**Contraloría General de la República de Colombia**
Dirección de Tecnologías de la Información — CD-TIC-CGR
Correo: protecciondatos@contraloria.gov.co

El término de respuesta es de **quince (15) días hábiles** a partir de la recepción de la solicitud.

## 8. Transferencia y Transmisión de Datos

- CecilIA v2 **NO** transfiere datos personales a terceros ni a países fuera de Colombia.
- Las consultas a proveedores de LLM (OpenAI, Anthropic) se realizan sin incluir datos personales.
- El corpus documental utilizado para la generación de respuestas no contiene datos personales.

## 9. Uso de Inteligencia Artificial

### 9.1 Transparencia

- Los usuarios del sistema son informados de que interactúan con un asistente de IA.
- Las respuestas generadas por IA se presentan claramente como asistidas, no como decisiones definitivas.
- El auditor siempre mantiene la responsabilidad final sobre sus análisis y conclusiones.

### 9.2 No Discriminación

- El sistema no utiliza datos sensibles para la toma de decisiones.
- Se realizan evaluaciones periódicas de sesgo en los modelos empleados.

### 9.3 Supervisión Humana

- Todo hallazgo generado por CecilIA v2 requiere revisión y aprobación humana antes de su oficialización.
- Los directores de dirección técnica son responsables de la validación final.

## 10. Incidentes de Seguridad

En caso de un incidente que comprometa datos personales:

1. **Contención inmediata** del incidente (máximo 4 horas).
2. **Notificación interna** al oficial de protección de datos (máximo 24 horas).
3. **Notificación a la SIC** si el incidente afecta a titulares de datos personales (máximo 15 días hábiles).
4. **Notificación a los titulares** afectados cuando proceda.
5. **Documentación** del incidente y acciones correctivas.
6. **Revisión** de controles y actualización de medidas de seguridad.

## 11. Vigencia y Actualización

Esta política entra en vigencia a partir de abril de 2026 y será revisada y actualizada al menos una vez al año o cuando se presenten cambios normativos que lo requieran.

---

*Política de Tratamiento de Datos — CecilIA v2 — Sprint 0 — Abril 2026*
*Equipo Técnico CecilIA — CD-TIC-CGR*
