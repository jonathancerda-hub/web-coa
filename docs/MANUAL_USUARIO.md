# Manual de Usuario - Sistema de Certificados Coadix

## Índice
1. Introducción
2. Acceso al sistema
3. Registro de nuevos certificados
4. Edición de certificados existentes
5. Dashboard y estadísticas
6. Búsqueda y filtrado de registros
7. Generación y descarga de PDF
8. Notas de referencia estructuradas (Nuevo)
9. Gestión de productos (Supervisores y Administradores)
10. Gestión de usuarios (Solo Administradores)
11. Validaciones y recomendaciones
12. Cierre de sesión
13. Soporte

---

## 1. Introducción
Este sistema permite gestionar certificados de análisis de productos farmacéuticos y veterinarios, facilitando el registro, edición, consulta y generación de certificados en formato PDF profesional.

## 2. Acceso al sistema

### 2.1 Inicio de sesión tradicional
- Ingrese su correo electrónico corporativo y contraseña en la pantalla de inicio de sesión.
- Haga clic en "Ingresar".
- **Contraseña por defecto:** Si es un usuario nuevo, contacte al administrador para obtener sus credenciales.

### 2.2 Inicio de sesión con Google
- Haga clic en el botón "Iniciar sesión con Google".
- Seleccione su cuenta corporativa de Google (@agrovetmarket.com o @pharmadix.com).
- El sistema le registrará automáticamente si es su primer acceso.
- **Nota:** Solo cuentas con dominios autorizados pueden acceder.

### 2.3 Recuperación de contraseña
- Si olvidó su contraseña, haga clic en "¿Olvidaste tu contraseña?".
- Contacte al administrador para que le restablezca su contraseña.

## 3. Registro de nuevos certificados
- Haga clic en "Nuevo Certificado" en el menú principal.
- Complete todos los campos obligatorios del formulario:
  - **Producto:** Seleccione desde el catálogo disponible
  - **Presentación:** Se cargará automáticamente según el producto
  - **Lote:** Ingrese el número de lote
  - **Fechas:** Producción, Vencimiento, Análisis, Emisión
  - **Ensayos:** Seleccione la versión de especificación y complete los resultados
  - **Conclusión:** APROBADO, RECHAZADO o PENDIENTE
- Las fechas deben ser válidas y coherentes (el sistema valida automáticamente).
- Presione "Guardar Cambios" para registrar el certificado.

## 4. Edición de certificados existentes
- En la lista de registros, haga clic en el botón "Editar" del certificado deseado.
- Modifique los campos necesarios.
- **Restricción:** Solo usuarios con rol Supervisor o Administrador pueden editar certificados.
- Las fechas originales pueden mantenerse aunque sean pasadas.
- Presione "Guardar Cambios" para actualizar.

## 5. Dashboard y estadísticas
- Acceda al Dashboard desde el menú principal.
- Visualice métricas clave:
  - Total de certificados registrados
  - Tasa de aprobación
  - Distribución por conclusión (gráfico de torta)
  - Tendencia mensual (gráfico de líneas)
- **Filtros disponibles:**
  - Por producto
  - Por rango de fechas
  - Por mes (haga clic en la tabla de resumen mensual)

## 6. Búsqueda y filtrado de registros
- Utilice la barra de búsqueda para filtrar por:
  - Código de certificado
  - Nombre del producto
  - Número de lote
  - Conclusión (APROBADO, RECHAZADO, PENDIENTE)
- Los resultados se actualizan automáticamente mientras escribe.
- **Búsqueda avanzada:** Puede combinar términos (ej: "APROBADO AMOXICILINA").

## 7. Generación y descarga de PDF
- En la lista de registros, use los botones:
  - **"PDF":** Genera certificado con diseño estándar Pharmadix
  - **"PDF Agrovet":** Genera certificado con diseño personalizado Agrovet Market
- El PDF se abrirá en una nueva pestaña.
- Puede descargarlo o imprimirlo directamente desde el navegador.
- **Nota:** Cada generación de PDF queda registrada en el log de actividad.

## 8. Notas de referencia estructuradas (Nuevo)

### 8.1 ¿Qué son las notas de referencia?
Las notas de referencia permiten agregar observaciones específicas a cada ensayo individual (como el laboratorio donde se realizó el análisis), que aparecerán numeradas de forma profesional en el PDF.

### 8.2 ¿Cómo usar las notas de referencia?
1. Al crear o editar un certificado, vaya a la tabla de análisis.
2. En la columna **"Nota de Ref."** (última columna), ingrese una nota corta para el ensayo correspondiente.
3. Ejemplos de notas comunes:
   - "Laboratorio Externo: Analizado en SGS"
   - "Método AOAC 925.10"
   - "Análisis subcontratado a Laboratorios ABC"

### 8.3 ¿Cómo aparecen en el PDF?
- **En PDF Pharmadix:**
  - Cada resultado con nota mostrará un número entre paréntesis: `10.5 (1)`
  - Al final del certificado, en la sección "OBSERVACIONES", aparecerá el catálogo completo:
    ```
    (1) LABORATORIO EXTERNO: ANALIZADO EN SGS
    (2) MÉTODO AOAC 925.10
    ```
  - Si varios ensayos tienen la misma nota, compartirán el mismo número.
  
- **En PDF Agrovet:**
  - Las notas NO se muestran (solo se muestra la referencia al certificado Pharmadix).

### 8.4 Consejos para usar las notas
- Sea conciso: máximo 80 caracteres por nota.
- Use mayúsculas para nombres de laboratorios.
- Evite repetir información que ya está en las observaciones generales.
- Las notas son opcionales; úselas solo cuando sea necesario.

### 8.5 Validaciones
- Caracteres permitidos: letras, números, espacios, guiones, puntos, paréntesis, dos puntos y comas.
- Longitud máxima: 80 caracteres.
- Campo opcional (no es obligatorio).

## 9. Gestión de productos (Supervisores y Administradores)
- Acceda a "Gestión de Productos" desde el menú.
- **Crear producto:**
  - Haga clic en "Nuevo Producto"
  - Complete: Nombre, Forma Farmacéutica, Presentación
  - Guarde los cambios
- **Eliminar producto:**
  - Haga clic en el botón "Eliminar" junto al producto
  - Confirme la acción

## 10. Gestión de usuarios (Solo Administradores)
- Acceda a "Gestión de Usuarios" desde el menú.
- **Crear usuario:**
  - Haga clic en "Nuevo Usuario"
  - Ingrese: Email corporativo, Contraseña, Rol
  - Guarde los cambios
- **Editar usuario:**
  - Haga clic en "Editar" junto al usuario
  - Modifique el rol o restablezca la contraseña
- **Eliminar usuario:**
  - Haga clic en "Eliminar" junto al usuario
  - **Restricción:** No puede eliminar su propia cuenta activa

### 10.1 Roles disponibles
- **Operario:** Puede ver y crear certificados, generar PDF
- **Supervisor:** Todo lo anterior + editar certificados, gestionar productos
- **Administrador:** Todo lo anterior + gestionar usuarios, ver logs de actividad

## 11. Validaciones y recomendaciones
- El sistema valida automáticamente:
  - Campos obligatorios
  - Formato de fechas
  - Coherencia entre fechas (producción < vencimiento)
  - Formato de email
- Si un campo es inválido, el sistema lo resaltará en rojo y mostrará un mensaje de error.
- Para editar registros antiguos, las fechas pasadas están permitidas.

## 12. Cierre de sesión
- Haga clic en el botón de cierre de sesión (ícono de salida) en la parte superior derecha.
- Su sesión expirará automáticamente después de 15 minutos de inactividad.

## 13. Soporte
- Para dudas o problemas, contacte al administrador del sistema.
- Email de soporte: soporte@agrovetmarket.com
- Usuario de soporte técnico: soporte@agrovetmarket.com (Contraseña: Soporte2026!)

---

**¡Gracias por usar el sistema de certificados Coadix!**

**Versión:** 2.0 | **Última actualización:** Febrero 2026
