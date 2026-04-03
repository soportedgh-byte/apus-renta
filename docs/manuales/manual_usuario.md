# Manual de Usuario — CecilIA v2

> Sistema de IA para Control Fiscal
> Contraloría General de la República de Colombia

## 1. Introducción

### 1.1 Acerca de CecilIA v2

CecilIA v2 es un asistente de inteligencia artificial desarrollado por la Contraloría General de la República de Colombia (CGR) para apoyar a los auditores en los procesos de control fiscal. El sistema combina inteligencia artificial generativa con herramientas especializadas de auditoría y un corpus documental del dominio fiscal colombiano.

### 1.2 Audiencia de este manual

Este manual está dirigido a todos los usuarios del sistema:

- Directores de dirección técnica (DES, DVF)
- Auditores fiscales
- Líderes técnicos
- Coordinadores
- Observadores

### 1.3 Requisitos previos

- Navegador web moderno (Chrome 120+, Firefox 120+, Edge 120+)
- Conexión a la red de la CGR
- Credenciales de acceso proporcionadas por el administrador del sistema

---

## 2. Acceso al Sistema

### 2.1 Inicio de sesión

1. Abra su navegador web y navegue a la URL del sistema proporcionada por su área de TI.
2. Ingrese su **nombre de usuario** y **contraseña**.
3. Haga clic en **"Iniciar sesión"**.
4. Si las credenciales son correctas, será redirigido al panel principal.

### 2.2 Primer inicio de sesión

En su primer acceso se recomienda:

1. Cambiar la contraseña temporal por una contraseña segura.
2. Verificar que su perfil muestre el rol y la dirección técnica correctos.
3. Familiarizarse con la interfaz mediante el recorrido guiado.

### 2.3 Cierre de sesión

- Haga clic en su nombre de usuario en la esquina superior derecha.
- Seleccione **"Cerrar sesión"**.
- La sesión expira automáticamente tras 8 horas de inactividad.

---

## 3. Interfaz Principal

### 3.1 Panel de navegación

| Elemento | Descripción |
|----------|-------------|
| **Chat** | Conversación con el asistente CecilIA |
| **Auditorías** | Listado de procesos auditores asignados |
| **Herramientas** | Acceso directo a herramientas de análisis |
| **Corpus** | Exploración del corpus documental |
| **Configuración** | Ajustes de perfil y preferencias |

### 3.2 Barra superior

- Nombre del usuario y rol activo
- Notificaciones del sistema
- Botón de cierre de sesión

---

## 4. Chat con CecilIA

### 4.1 Iniciar una conversación

1. Navegue a la sección **"Chat"**.
2. Haga clic en **"Nueva conversación"**.
3. Escriba su pregunta o solicitud en el campo de texto.
4. Presione **Enter** o haga clic en el botón de enviar.

### 4.2 Tipos de consultas soportadas

CecilIA puede asistirle con:

- **Consultas normativas:** "Que establece el artículo 268 de la Constitución sobre control fiscal?"
- **Cálculos de auditoría:** "Calcula la materialidad para un presupuesto de $500.000 millones"
- **Análisis de datos:** "Aplica la Ley de Benford a estos datos de pagos"
- **Redacción de hallazgos:** "Ayúdame a redactar un hallazgo sobre sobrecostos en contratación"
- **Consultas institucionales:** "Cual es el procedimiento de la CGR para auditorías de desempeño?"

### 4.3 Interpretación de respuestas

- Las respuestas incluyen **citas** al corpus documental cuando aplica.
- Las citas se presentan con la referencia al documento fuente.
- Las respuestas son **asistidas**: el auditor siempre debe validar y complementar con su criterio profesional.

### 4.4 Historial de conversaciones

- Las conversaciones se guardan automáticamente.
- Puede acceder al historial desde el panel lateral izquierdo.
- Puede buscar conversaciones anteriores por texto o fecha.

---

## 5. Herramientas de Auditoría

### 5.1 Calculadora de Materialidad

**Propósito:** Calcular la materialidad global y de ejecución según las Normas Internacionales de Auditoría (NIA 320).

**Pasos:**
1. Navegue a **Herramientas > Materialidad**.
2. Ingrese el presupuesto total del sujeto de control.
3. Seleccione el nivel de confianza deseado.
4. Seleccione la base de cálculo (presupuesto de inversión, ingresos totales, activos totales).
5. Haga clic en **"Calcular"**.
6. Revise los resultados: materialidad global, materialidad de ejecución y justificación.

### 5.2 Análisis de Benford

**Propósito:** Detectar anomalías en distribuciones numéricas de registros financieros usando la Ley de Benford.

**Pasos:**
1. Navegue a **Herramientas > Análisis de Benford**.
2. Cargue el archivo con los datos financieros (XLSX o CSV).
3. Seleccione la columna a analizar.
4. Haga clic en **"Analizar"**.
5. Revise el gráfico comparativo (distribución observada vs. esperada) y las desviaciones significativas.

### 5.3 Muestreo Estadístico

**Propósito:** Calcular el tamaño de muestra apropiado para una auditoría.

**Pasos:**
1. Navegue a **Herramientas > Muestreo**.
2. Ingrese el tamaño de la población.
3. Seleccione el nivel de confianza y el margen de error aceptable.
4. Haga clic en **"Calcular"**.
5. Obtenga el tamaño de muestra y la metodología de selección recomendada.

### 5.4 Generador de Hallazgos

**Propósito:** Asistir en la redacción de hallazgos fiscales con la estructura Condición-Criterio-Causa-Efecto (CCCE).

**Pasos:**
1. Navegue a **Herramientas > Hallazgos** o solicite la generación desde el chat.
2. Describa la situación encontrada.
3. CecilIA generará una propuesta con los cuatro elementos del hallazgo.
4. **Revise, ajuste y valide** el hallazgo antes de incorporarlo al informe.

---

## 6. Gestión de Auditorías

### 6.1 Consultar auditorías asignadas

1. Navegue a **"Auditorías"**.
2. Visualice el listado de procesos auditores asignados a su perfil.
3. Filtre por estado (en planificación, en ejecución, en informe, cerrada).

### 6.2 Asociar conversaciones a una auditoría

1. Desde una conversación de chat, haga clic en **"Vincular a auditoría"**.
2. Seleccione el proceso auditor correspondiente.
3. La conversación quedará asociada para referencia futura.

---

## 7. Agente de Escritorio

### 7.1 Instalación

1. Descargue el instalador del Agente CecilIA desde la sección de descargas.
2. Ejecute el instalador y siga las instrucciones en pantalla.
3. Inicie sesión con sus credenciales del sistema.

### 7.2 Funcionalidades

- **Acceso a archivos locales:** Permite a CecilIA leer archivos de su equipo para análisis.
- **Vigilancia de carpetas:** Monitorea cambios en carpetas de trabajo designadas.
- **Bandeja del sistema:** Acceso rápido desde la barra de tareas de Windows.

### 7.3 Seguridad

- El agente solo accede a las carpetas que usted autorice explícitamente.
- Los archivos se procesan localmente; solo se envían fragmentos necesarios al servidor.
- Puede revocar permisos en cualquier momento desde la configuración del agente.

---

## 8. Roles y Permisos

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **ADMIN** | Administrador del sistema | Acceso total, gestión de usuarios |
| **DIRECTOR_DES** | Director de la DES | Supervisión de auditorías DES, aprobación de hallazgos |
| **DIRECTOR_DVF** | Director de la DVF | Supervisión de auditorías DVF, aprobación de hallazgos |
| **AUDITOR_DES** | Auditor de la DES | Chat, herramientas, gestión de auditorías DES |
| **AUDITOR_DVF** | Auditor de la DVF | Chat, herramientas, gestión de auditorías DVF |
| **LIDER_TECNICO** | Líder técnico del proyecto | Configuración técnica, acceso a logs |
| **COORDINADOR** | Coordinador del proyecto | Vista transversal, reportes |
| **OBSERVADOR** | Observador con acceso de lectura | Solo lectura en todas las secciones |

---

## 9. Preguntas Frecuentes

**P: Las respuestas de CecilIA son definitivas?**
R: No. CecilIA es un asistente que genera propuestas y análisis. El auditor siempre debe validar las respuestas con su criterio profesional y la normatividad vigente.

**P: Puedo confiar en las citas normativas?**
R: Las citas provienen del corpus documental verificado, pero se recomienda consultar siempre la fuente original para verificar vigencia y contexto.

**P: Mis conversaciones son privadas?**
R: Las conversaciones son visibles para usted y los administradores del sistema. Están sujetas a la Política de Tratamiento de Datos.

**P: Que hago si el sistema no responde?**
R: Verifique su conexión a la red. Si el problema persiste, contacte al equipo de soporte técnico.

**P: Puedo usar CecilIA fuera de la red de la CGR?**
R: El acceso está restringido a la red institucional de la CGR, salvo configuración especial de VPN.

---

## 10. Soporte Técnico

Para reportar incidentes o solicitar asistencia:

- **Correo:** soporte.cecilia@contraloria.gov.co
- **Mesa de ayuda:** Extensión interna 2500
- **Horario:** Lunes a viernes, 7:00 a.m. a 5:00 p.m.

---

*Manual de Usuario — CecilIA v2 — Sprint 0 — Abril 2026*
*Equipo Técnico CecilIA — CD-TIC-CGR*
