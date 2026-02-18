<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                        GUÍA DE ESTILOS PARA CONVERSIÓN A HTML               ║
║                                                                              ║
║  Al convertir este documento a HTML, aplicar exactamente los estilos        ║
║  definidos en esta sección. Cada token tiene su nombre semántico            ║
║  y su valor CSS correspondiente.                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PALETA DE COLORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  COLOR PRIMARIO (acentos, H3, highlights):
    --color-primary:        #e67e22  (naranja)
    --color-primary-dark:   #d35400  (naranja oscuro)

  COLOR SECUNDARIO (headers de tablas, feature cards):
    --color-secondary-a:    #667eea  (violeta azulado)
    --color-secondary-b:    #764ba2  (violeta oscuro)
    → Gradiente: linear-gradient(135deg, #667eea 0%, #764ba2 100%)

  TEXTOS:
    --color-text-primary:   #1a202c  (casi negro — H1 y body)
    --color-text-secondary: #2d3748  (gris oscuro — H2)
    --color-text-muted:     #4a5568  (gris medio — H4, section-intro)
    --color-text-light:     #718096  (gris claro — labels en KPI cards)

  FONDO:
    --color-bg-page:        linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)
    --color-bg-container:   #ffffff
    --color-bg-row-alt:     #f7fafc  (filas pares de tabla)
    --color-bg-row-hover:   #edf2f7  (hover en filas de tabla)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TIPOGRAFÍA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  font-family:  'Inter', 'Segoe UI', sans-serif
  line-height:  1.6
  color base:   #1a202c

  H1: font-size 2.2em | bold | color #1a202c | border-bottom 3px solid #e67e22 | padding-bottom 15px
  H2: color #2d3748 | border-left 5px solid #e67e22 | bg #f7fafc | padding 15px | border-radius 0 8px 8px 0 | margin-top 40px
  H3: color #e67e22 | font-size 1.3em | margin-top 25px
  H4: color #4a5568 | margin-top 20px

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CONTENEDOR PRINCIPAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  body:       background linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)
              font-family 'Inter','Segoe UI',sans-serif | line-height 1.6 | color #1a202c
              max-width 1000px | margin 0 auto | padding 30px 20px

  .container: background white | border-radius 12px | padding 40px
              box-shadow 0 10px 40px rgba(0,0,0,0.1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TABLAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  table:  width 100% | border-collapse collapse | margin 25px 0
          box-shadow 0 4px 15px rgba(0,0,0,0.08) | border-radius 8px | overflow hidden

  th:     background linear-gradient(135deg, #667eea 0%, #764ba2 100%)
          color white | font-weight 600 | text-transform uppercase
          font-size 0.85em | letter-spacing 0.5px | padding 14px

  td:     border 1px solid #e2e8f0 | padding 14px | text-align left

  tr (even):  background #f7fafc
  tr (hover): background #edf2f7 | transition all 0.3s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BLOQUES ESPECIALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Los blockquotes de este MD se convierten a uno de estos 3 tipos según su prefijo emoji:

  💡 TECH-NOTE  →  .tech-note
    background: linear-gradient(135deg, #e8f6f3, #d5f4e6)
    border-left: 6px solid #1abc9c (verde agua)
    padding 20px | border-radius 10px | margin 20px 0
    Uso: notas de implementación, mejoras técnicas, decisiones de arquitectura

  ⚠️ WARNING    →  .warning-box
    background: linear-gradient(135deg, #fff5f5, #fed7d7)
    border-left: 6px solid #e53e3e (rojo)
    padding 20px | border-radius 10px | margin 20px 0
    Uso: reglas de negocio críticas, riesgos, restricciones

  ✅ SUCCESS    →  .success-box
    background: linear-gradient(135deg, #f0fff4, #c6f6d5)
    border-left: 6px solid #38a169 (verde)
    padding 20px | border-radius 10px | margin 20px 0
    Uso: objetivos del producto, beneficios, optimizaciones de costo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BLOQUE META-INFO (cabecera del documento)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .meta-info:
    background linear-gradient(135deg, #fff8e1, #ffecb3)
    border 2px solid #ffe0b2 | border-radius 10px | padding 20px
    display grid | grid-template-columns repeat(auto-fit, minmax(200px,1fr)) | gap 15px

  .meta-label: font-size 0.8em | color #795548 | font-weight 600
               text-transform uppercase | letter-spacing 0.5px
  .meta-value: font-size 1.1em | color #5d4037 | font-weight 700 | margin-top 4px

  → En el MD se representa como tabla bajo "Metadatos del Proyecto"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STATUS BADGES (estados en ciclo de vida)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Base: padding 6px 12px | border-radius 20px | font-size 0.8em
        font-weight 600 | color white | display inline-block

  🟠 PENDIENTE / EN PROCESO:  linear-gradient(135deg, #f39c12, #e67e22)
  🔵 EN RUTA / EN PROGRESO:   linear-gradient(135deg, #3498db, #2980b9)
  🟢 COMPLETADO / ÉXITO:      linear-gradient(135deg, #27ae60, #229954)
  🔴 ERROR / INCIDENCIA:      linear-gradient(135deg, #e74c3c, #c0392b)
  🟣 ASIGNADO / ESPECIAL:     linear-gradient(135deg, #9b59b6, #8e44ad)

  → En el MD se escribe como texto con emoji entre corchetes: [🟠 ESTADO]
    Al convertir a HTML, detectar el emoji y aplicar el badge correspondiente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FEATURE CARDS (cuadrícula de funcionalidades)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .feature-grid: display grid | grid-template-columns repeat(auto-fit,minmax(280px,1fr))
                 gap 20px | margin 25px 0

  .feature-card: background #f7fafc | border-radius 10px | padding 20px
                 border-top 4px solid #667eea

  .feature-title: font-weight 700 | color #2d3748 | font-size 1.1em | margin-bottom 10px

  → En el MD se marcan con "<!-- FEATURE CARD -->" en secciones de lista con título en negrita.
    Al convertir, cada bloque **[Emoji Título]:** con su lista se convierte en una feature-card.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KPI CARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .kpi-grid: display grid | grid-template-columns repeat(auto-fit,minmax(250px,1fr))
             gap 20px | margin 25px 0

  .kpi-card: background white | border 2px solid #e2e8f0 | border-radius 10px
             padding 20px | text-align center | box-shadow 0 2px 8px rgba(0,0,0,0.05)

  .kpi-title: font-size 0.9em | color #718096 | text-transform uppercase
              font-weight 600 | margin-bottom 10px

  .kpi-value:         font-size 2em | color #e67e22 | font-weight 700
  .kpi-value (alerta): color #e53e3e  ← usar cuando la métrica representa errores/problemas

  → En el MD se representa como tabla con columna "Color" indicando si usar naranja o rojo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INDICADORES DE PRIORIDAD (inline en texto)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔴 CRÍTICO:    color #e53e3e | font-weight 700
  🟠 IMPORTANTE: color #dd6b20 | font-weight 700
  🔵 DESEABLE:   color #3182ce | font-weight 700

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION INTRO y HIGHLIGHT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .section-intro:  font-size 1.05em | color #4a5568 | font-style italic
                   border-left 3px solid #cbd5e0 | padding-left 15px | margin-bottom 20px
    → En el MD: > *[texto en cursiva]*

  .highlight: background #fef5e7 | padding 2px 6px | border-radius 3px | font-weight 600
    → En el MD: `texto entre backticks`

-->

---

# 📦 PRD: [Nombre del Producto / Sistema]

> *[Descripción de una oración: qué digitaliza, automatiza o resuelve este sistema y para quién.]*

---

## Metadatos del Proyecto

| Campo | Valor |
|---|---|
| **Versión** | 1.0 |
| **Stack** | [Ej: React + Node + PostgreSQL] |
| **Enfoque** | [Ej: Mobile-first / API-first / Real-Time] |
| **Prioridad** | [Ej: Q1 2025] |
| **Estado** | [Borrador / En revisión / Aprobado] |
| **Fecha** | YYYY-MM-DD |
| **Responsable** | [Nombre del PM / Tech Lead] |

---

## 1. Visión del Producto

> *[Descripción breve del sistema y el contexto operativo que viene a resolver.]*

> ✅ SUCCESS: **🎯 Objetivo Principal:** [Ej: Reducir el tiempo de gestión en un X%, eliminar errores manuales, y mejorar la satisfacción del cliente.]

### 1.1 Problemas que Resuelve

- **[Problema 1]:** [Descripción breve de la situación actual y su impacto]
- **[Problema 2]:** [Descripción breve de la situación actual y su impacto]
- **[Problema 3]:** [Descripción breve de la situación actual y su impacto]
- **[Problema 4]:** [Descripción breve de la situación actual y su impacto]
- **[Problema 5]:** [Descripción breve de la situación actual y su impacto]

---

## 2. Arquitectura de Sistema

> *[Describir las capas principales. Adaptar el número de subsecciones según el proyecto.]*

### 2.1 Capa de Origen / Datos

- **Rol:** [Ej: Sistema de verdad (Source of Truth) para X]
- **Sincronización:** [Ej: Webhook automático cuando ocurre evento Y]
- **Datos clave:** [Listar los datos más importantes que fluyen desde esta capa]

> 💡 TECH-NOTE: **Mejora Técnica:** [Ej: Implementar geocodificación automática, validación en origen, caché de resultados frecuentes, etc.]

### 2.2 Capa de Negocio / Backend

- **Responsabilidades:**
  - [Gestión de usuarios y autenticación]
  - [Lógica de negocio principal]
  - [Procesamiento / validación de datos]
  - [Gestión de notificaciones]
  - [Generación de reportes]

### 2.3 Capas de Presentación

- **[Interface 1] ([Framework]):** Para [tipo de usuario]
- **[Interface 2] ([Framework]):** Para [tipo de usuario]
- **[Interface 3] (Opcional — Fase 2):** [Descripción]

---

## 3. Gestión de Usuarios y Roles

| Rol | Acceso | Capacidades Clave | Licencia / Auth |
|---|---|---|---|
| **Administrador** | [Interfaces] | Gestión total, crear usuarios, ver reportes | ✅ [Sistema principal] |
| **[Rol 2]** | [Interfaces] | [Capacidades] | ✅ Sí |
| **[Rol 3 — App]** | [App Móvil] | [Capacidades] | ❌ Auth independiente |
| **[Rol 4 — Solo Lectura]** | [Panel Web] | [Capacidades] | ✅ Sí |

> ✅ SUCCESS: **💰 Optimización de Costos:** [Ej: Al mantener ciertos usuarios fuera del sistema principal, se puede ahorrar X en licencias mensuales.]

---

## 4. Ciclo de Vida del Objeto Principal (Estados)
<!-- "Objeto Principal" = Pedido, Solicitud, Ticket, Tarea, etc. Renombrar según el proyecto -->
<!-- Cada celda de Estado se renderiza como STATUS BADGE. Ver paleta de badges en la guía -->

| Estado | Disparador | Validaciones Automáticas | Notificaciones |
|---|---|---|---|
| **[🟠 PENDIENTE]** | [Qué evento lo activa] | [Verificación automática del sistema] | — |
| **[🟣 ASIGNADO]** | [Qué evento lo activa] | [Validación] | Push a [usuario]: "[mensaje]" |
| **[🔵 EN RUTA]** | [Qué evento lo activa] | [Activar tracking / proceso automático] | [Canal] a [destinatario]: "[mensaje]" |
| **[🔵 PRÓXIMO]** | Sistema detecta [condición de proximidad] | [Geocerca / trigger automático] | [Canal]: "[mensaje]" |
| **[🟢 COMPLETADO]** | [Acción del usuario] + evidencia | **[Validación crítica]:** [Condición de aprobación] | [Canal] con [adjunto/evidencia] |
| **[🔴 INCIDENCIA]** | [Acción del usuario] + motivo | [Evidencia obligatoria] + selección de motivo | Alerta urgente a [roles afectados] |
| **[🔴 RETORNO]** | [Qué lo activa] | [Bloqueo hasta resolver incidencia] | [Notificación a ventas / admin] |

> ⚠️ WARNING: **Regla de Negocio Crítica:** [Describir la regla más importante que el sistema debe hacer cumplir. Ej: si ocurre condición X, bloquear acción Y y requerir justificación escrita.]

---

## 5. Funcionalidades: [Interface Principal — App Móvil / Frontend]

### 5.1 Autenticación y Seguridad

- **Login:** [Método + justificación de UX. Ej: RUT/Email + PIN de 6 dígitos para facilitar uso en campo]
- **[Opción avanzada — Fase 2]:** [Biometría / SSO / 2FA]
- **Cierre de sesión automático:** [Regla de expiración]

### 5.2 Pantalla Principal
<!-- FEATURE CARD: cada bloque **[Emoji Título]:** con su lista se convierte en una feature-card -->

**[🎯 Funcionalidad clave 1]:**
- [Detalle 1]
- [Detalle 2]
- [Detalle 3]

**[📊 Funcionalidad clave 2]:**
- [Detalle 1]
- [Detalle 2]
- [Detalle 3]

**[🗺️ Funcionalidad clave 3]:**
- [Detalle 1]
- [Detalle 2]

### 5.3 Detalle del Objeto Principal

- **[Sección A — Ej: Datos del cliente]:**
  - [Campo 1]
  - [Campo 2]
  - [Campo 3]
- **[Sección B — Ej: Detalle del pedido]:**
  - [Campo 1]
  - [Campo 2]
  - [Campo 3]

### 5.4 Proceso Principal (Flujo Step-by-Step)

1. **[Paso 1 — Inicio]:** [Acción del usuario + respuesta del sistema]
2. **[Paso 2 — Captura de evidencia]:**
   - [Sub-acción a]
   - [Sub-acción b]
3. **[Paso 3 — Información adicional]:**
   - [Campo obligatorio]
   - [Campo opcional]
4. **[Paso 4 — Validación]:** Sistema verifica [condición]. Si falla → advertencia + justificación obligatoria
5. **[Paso 5 — Confirmación]:** "[Mensaje de éxito]" + feedback visual/sonoro

### 5.5 Gestión de Errores / Incidencias

- **Motivos predefinidos:**
  - [Motivo 1]
  - [Motivo 2]
  - [Motivo 3]
  - Otro (requiere descripción)
- **Evidencia obligatoria:** [Foto / descripción / ambas]
- **Flujo de escalación:** [Qué ocurre después de registrar el error]

### 5.6 Funcionalidades Offline

> 💡 TECH-NOTE: **Mejora Crítica:** La app debe funcionar parcialmente sin internet:
> - [Dato que se cachea localmente al inicio de sesión]
> - [Acción permitida sin conexión]
> - [Acción que se encola para sincronización posterior]
> - Sincronización automática al recuperar conexión

---

## 6. Funcionalidades: Panel Administrativo / Backoffice

### 6.1 Dashboard Principal
<!-- KPI CARD: cada fila de esta tabla se renderiza como kpi-card. Ver estilos en guía -->

| KPI | Descripción | Color del valor |
|---|---|---|
| [KPI 1 — Ej: Total Hoy] | [Qué mide] | Naranja `#e67e22` |
| [KPI 2 — Ej: En Progreso] | [Qué mide] | Naranja `#e67e22` |
| [KPI 3 — Ej: Completados] | [Qué mide] | Naranja `#e67e22` |
| [KPI 4 — Ej: Errores / Alertas] | [Qué mide] | Rojo `#e53e3e` |

### 6.2 Monitor en Tiempo Real (si aplica)

- **[Vista principal — Ej: Mapa interactivo]:**
  - [Capa/elemento 1]
  - [Capa/elemento 2]
  - [Capa/elemento 3]
- **Filtros:** Por [campo 1], [campo 2], [campo 3], rango de fechas
- **Interacción:** Click en [X] muestra popup con [detalle]

### 6.3 Gestión del Objeto Principal

- **Búsqueda avanzada:** Por [campo 1], [campo 2], [campo 3], fecha
- **Acciones masivas:** [Ej: seleccionar múltiples y asignar / exportar]
- **Edición manual:** Solo superusuarios — con registro de auditoría
- **Exportación:** PDF, Excel, CSV

### 6.4 Gestión de Usuarios

- **CRUD:** Crear / Editar / Desactivar
- **Asignación de recursos:** [Vehículo / zona / equipo / capacidad]
- **Historial de desempeño:**
  - [Métrica 1 — Ej: total de operaciones]
  - [Métrica 2 — Ej: tasa de éxito]
  - [Calificación / feedback]

### 6.5 Reportes y Analítica

- **Reportes predefinidos:**
  - [Reporte 1: descripción]
  - [Reporte 2: descripción]
  - [Reporte 3: descripción]
- **Exportación:** PDF, Excel, CSV
- **Visualizaciones:** [Tipos: barras, líneas, heatmaps, tablas dinámicas]

---

## 7. Integraciones y APIs

### 7.1 Integración con [Sistema Principal — ERP / CRM / etc.]

| Dirección | Método | Datos | Frecuencia |
|---|---|---|---|
| [Sistema A] → [Sistema B] | Webhook (POST) | [Qué datos viajan] | [Cuándo — Ej: tiempo real] |
| [Sistema B] → [Sistema A] | API REST (PUT) | [Qué actualiza] | [Cuándo — Ej: al cambiar estado] |
| [Sistema B] → [Sistema A] | API REST (POST) | [Qué envía — Ej: evidencia/adjunto] | [Cuándo] |

### 7.2 APIs de Terceros

- **[API 1 — Ej: Google Maps]:** [Para qué se usa]
- **[API 2 — Ej: Twilio / WhatsApp]:** [Para qué se usa]
- **[API 3 — Ej: Firebase / Push]:** [Para qué se usa]
- **[API 4 — Opcional]:** [Para qué se usa]

---

## 8. Stack Tecnológico

### 8.1 Base de Datos

- **Principal:** [Ej: PostgreSQL] — [Justificación]
- **Cache / Real-time:** [Ej: Redis] — [Para qué]
- **Storage de archivos:** [Ej: AWS S3] — [Para qué]

### 8.2 Backend

- **Framework:** [Ej: Node.js + Express / Django / Laravel]
- **Autenticación:** [Ej: JWT con expiración automática]
- **WebSockets:** [Si aplica, para qué funcionalidades]

### 8.3 App Móvil (si aplica)

> 💡 TECH-NOTE: **Recomendación de Framework:** [Ej: Flutter]
> - **Ventajas:** [Razón principal — Ej: single codebase iOS/Android, rendimiento nativo]
> - **Alternativa:** [Ej: React Native si el equipo ya domina React]

### 8.4 Frontend Web

- **Framework:** [Ej: React / Vue.js / Next.js]
- **Mapas (si aplica):** [Ej: Google Maps JS API / Mapbox GL JS]
- **UI Components:** [Ej: Tailwind CSS / Material-UI / Ant Design]
- **State Management:** [Ej: Redux / Zustand / Pinia]

### 8.5 Infraestructura

- **Hosting Backend:** [Ej: AWS EC2 / Google Cloud Run / Railway]
- **Hosting Frontend:** [Ej: Vercel / Netlify / AWS Amplify]
- **Storage:** [Ej: AWS S3 / Google Cloud Storage]
- **CDN:** [Ej: CloudFlare]

---

## 9. Plan de Implementación por Fases

### Fase 1: MVP ([X] meses) — 🔴 CRÍTICO

- ✅ [Funcionalidad core 1]
- ✅ [Funcionalidad core 2]
- ✅ [Funcionalidad core 3]
- ✅ [Funcionalidad core 4]
- ✅ [Funcionalidad core 5]

### Fase 2: Mejoras Operativas ([X] meses) — 🟠 IMPORTANTE

- 🔄 [Mejora 1]
- 🔄 [Mejora 2]
- 🔄 [Mejora 3]
- 🔄 [Mejora 4]

### Fase 3: Experiencia del Usuario Final ([X] meses) — 🟠 IMPORTANTE

- 📱 [Feature de experiencia 1]
- 💬 [Feature de experiencia 2]
- ⭐ [Feature de experiencia 3]

### Fase 4: Inteligencia y Optimización ([X] meses) — 🔵 DESEABLE

- 🤖 [Feature avanzada 1 — IA / automatización]
- 📊 [Feature avanzada 2 — analítica]
- 🔮 [Feature avanzada 3 — predicción / ML]

---

## 10. Roadmap V2.0 — Funcionalidades Avanzadas

> *Estas funcionalidades se implementarían después del MVP consolidado, basándose en feedback real de usuarios y métricas de adopción.*

### 10.1 [Interface Principal] — Nuevas Capacidades
<!-- FEATURE CARD: cada bloque **[Emoji Título]:** con lista se convierte en feature-card -->

**[📞 Módulo A — Ej: Comunicación integrada]:**
- **[Feature 1]:** [Descripción y valor]
- **[Feature 2]:** [Descripción y valor]
- **[Feature 3]:** [Descripción y valor]

**[🎯 Módulo B — Ej: Optimización de rutas]:**
- **[Feature 1]:** [Descripción y valor]
- **[Feature 2]:** [Descripción y valor]

**[💰 Módulo C — Ej: Gestión financiera en campo]:**
- **[Feature 1]:** [Descripción]
- **[Feature 2]:** [Descripción]

### 10.2 Panel Administrativo — Funcionalidades Avanzadas

**[🤖 Automatización / Asignación Inteligente]:**
- **[Feature 1]:** [Descripción]
- **[Feature 2]:** [Descripción]

**[📈 Business Intelligence]:**
- **[Feature 1]:** [Descripción]
- **[Feature 2]:** [Descripción]
- **Integración con BI tools:** [Ej: Power BI / Tableau / Metabase]

### 10.3 Portal para Usuario Final (si aplica)

**[📱 Tracking en tiempo real]:**
- **[Feature]:** [Descripción]

**[🔔 Notificaciones personalizadas]:**
- **Multi-canal:** [Email / SMS / WhatsApp / Push — usuario elige]

**[⭐ Feedback y calificación]:**
- **[Sistema de rating]:** [Descripción]

### 10.4 Integraciones Adicionales

- **[Integración 1]:** [Para qué se usa]
- **[Integración 2]:** [Para qué se usa]
- **[Integración 3]:** [Para qué se usa]

### 10.5 Innovaciones Tecnológicas (Futuro 12–24 meses)

> 💡 TECH-NOTE: **🚀 Visión a Largo Plazo**
> - **[Innovación 1 — Ej: IA para OCR]:** [Descripción]
> - **[Innovación 2 — Ej: IoT en vehículos]:** [Descripción]
> - **[Innovación 3 — Ej: Blockchain / AR]:** [Descripción]

---

## 11. Métricas de Éxito (KPIs)

| Categoría | Métrica | Meta Año 1 | Cómo se Mide |
|---|---|---|---|
| **Operacionales** | [Tasa de éxito] | >X% | (Exitosos / Total) * 100 |
| **Operacionales** | [Tiempo promedio] | <X min | Desde inicio hasta confirmación |
| **Operacionales** | [Tasa de error] | <X% | (Errores / Total) * 100 |
| **Productividad** | [Métrica 4] | >X | [Promedio diario / semanal] |
| **Productividad** | [Métrica 5] | <X | [Ej: km / operación] |
| **Satisfacción** | CSAT | >4.5/5 | Encuesta post-operación |
| **Satisfacción** | NPS | >70 | Net Promoter Score |
| **Adopción** | Uso diario — usuario primario | 100% | Activos / Total |
| **Adopción** | Uso — usuario secundario | >X% | Sesiones semanales |

---

## 12. Consideraciones de Seguridad

### 12.1 Protección de Datos

- **Encriptación:** HTTPS en todas las comunicaciones, AES-256 para datos sensibles
- **Compliance:** [GDPR / LGPD / normativa local aplicable]
- **Anonimización:** Datos sensibles se desvinculan de identidad después de [X] días
- **Backups automáticos:** Copia diaria con retención de [X] días

### 12.2 Seguridad de Acceso

- **Autenticación multi-factor:** [Obligatoria / Opcional para admins]
- **Tokens JWT:** Sesiones con expiración automática
- **Rate limiting:** Prevenir ataques de fuerza bruta
- **Auditoría de accesos:** Log completo de intentos fallidos de login

---

## 13. Riesgos y Mitigación

| Riesgo | Impacto | Probabilidad | Mitigación |
|---|---|---|---|
| [Riesgo 1] | Alto | Media | [Estrategia de mitigación] |
| [Riesgo 2] | Alto | Alta | [Estrategia de mitigación] |
| [Riesgo 3] | Medio | Baja | [Estrategia de mitigación] |
| [Riesgo 4] | Medio | Media | [Estrategia de mitigación] |
| [Riesgo 5] | Alto | Media | [Estrategia de mitigación] |

---

## 14. Presupuesto Estimado

> ⚠️ WARNING: **💰 Inversión Inicial (Fase MVP — [X] meses)**
>
> | Ítem | Estimado |
> |---|---|
> | Desarrollo Backend + Frontend | $X,XXX – $XX,XXX |
> | Desarrollo App Móvil (si aplica) | $X,XXX – $XX,XXX |
> | Integración con [Sistema externo] | $X,XXX – $XX,XXX |
> | Infraestructura ([X] meses) | $X,XXX – $X,XXX |
> | APIs de Terceros ([X] meses) | $X,XXX – $X,XXX |
> | Testing y QA | $X,XXX – $X,XXX |
> | **TOTAL MVP** | **$XX,XXX – $XX,XXX** |

> ✅ SUCCESS: **📅 Costos Recurrentes Mensuales (Post-MVP)**
>
> | Ítem | Estimado / mes |
> |---|---|
> | Hosting e Infraestructura | $XXX – $X,XXX |
> | [API de tercero 1] | $XXX – $XXX |
> | [API de tercero 2] | $XXX – $XXX |
> | Storage (archivos / fotos) | $XXX – $XXX |
> | Mantenimiento y Soporte | $X,XXX – $X,XXX |
> | **TOTAL MENSUAL** | **$X,XXX – $X,XXX** |

---

## 15. Próximos Pasos

1. **Aprobación de PRD:** Revisión y sign-off de stakeholders
2. **Selección de equipo:** Contratar / asignar desarrolladores
3. **Diseño UX/UI:** Wireframes y mockups de todas las interfaces
4. **Setup de infraestructura:** Configurar servidores, bases de datos, CI/CD
5. **Sprint 0:** Arquitectura técnica detallada y configuración de repos
6. **Desarrollo iterativo:** Sprints de 2 semanas con demos
7. **Piloto:** Probar con [X] usuarios reales durante [X] semanas
8. **Lanzamiento gradual:** Rollout por fases a toda la operación

---

> 💡 TECH-NOTE: **📋 Documento vivo:** Este PRD debe actualizarse con feedback del equipo y aprendizajes durante el desarrollo.
