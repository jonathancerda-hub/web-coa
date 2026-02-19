# Sistema de Notas de Referencia Estructuradas (Pharmadix)

## Descripción General
El sistema de notas de referencia permite asociar observaciones específicas a cada ensayo individual en el certificado de análisis, mostrándolas de forma profesional mediante superíndices numéricos en el PDF.

## Características Principales

### 1. Columna de Notas en el Formulario
- Ubicada a la derecha de la tabla de análisis con el encabezado **"Nota de Ref."**
- Permite ingresar texto corto (máximo 80 caracteres) para cada ensayo
- Validación de caracteres permitidos: letras, números, espacios, guiones, puntos, paréntesis, dos puntos y comas
- Campo opcional (no requerido)

### 2. Visualización en el PDF (Pharmadix)
Cuando se genera un PDF de tipo **Pharmadix**:

#### En la Tabla de Resultados:
- Si un ensayo tiene una nota asociada, aparecerá un número entre paréntesis al final del resultado
- Ejemplo: `10.5 (1)` donde (1) hace referencia a la primera nota del catálogo

#### En la Sección de Observaciones:
- Las notas se listan automáticamente al final de las observaciones manuales
- Formato: `(1) LABORATORIO EXTERNO: ANALIZADO EN...`
- Estilo visual:
  - Fuente más pequeña (7pt)
  - Texto en cursiva
  - Color gris oscuro para distinguir
  - Espaciado reducido para mantener elegancia

### 3. Comportamiento en PDF Agrovet
- Las notas **NO se muestran** en los PDFs de tipo Agrovet
- Solo se muestra: "Referencia Certificado de Análisis Pharmadix"

## Casos de Uso Comunes

### Ejemplo 1: Laboratorio Externo
```
Ensayo: Identificación
Resultado: Positivo (1)
Nota: LABORATORIO EXTERNO: ANALIZADO EN LABORATORIOS SGS
```

### Ejemplo 2: Múltiples Notas
```
Ensayo: Humedad
Resultado: 5.2% (1)
Nota: Método AOAC 925.10

Ensayo: Proteína
Resultado: 18.5% (2)
Nota: Método Kjeldahl modificado
```

### Ejemplo 3: Mismo Laboratorio para Varios Ensayos
Si varios ensayos tienen la misma nota (ej: "Lab. Externo"), el sistema automáticamente:
- Crea solo una entrada en el catálogo
- Asigna el mismo número a todos los ensayos con esa nota
- Evita duplicación en la lista de observaciones

## Almacenamiento de Datos

### Google Sheets
Las notas se almacenan en columnas `NOTA1` a `NOTA20` en la hoja de cálculo:
```
ENSAYO1 | ESPECIFICACION1 | RESULTADO1 | ... | NOTA1
ENSAYO2 | ESPECIFICACION2 | RESULTADO2 | ... | NOTA2
...
ENSAYO20 | ESPECIFICACION20 | RESULTADO20 | ... | NOTA20
```

### Base de Datos
Cada registro tiene campos dedicados para las 20 posibles notas.

## Validaciones Implementadas

### Frontend (HTML5)
- Patrón: `[A-Za-z0-9\s\-\.\(\):,]{0,80}`
- Longitud máxima: 80 caracteres
- Caracteres permitidos: alfanuméricos, espacios, guiones, puntos, paréntesis, dos puntos, comas

### Backend
- Almacenamiento seguro en Google Sheets
- Procesamiento correcto de caracteres especiales
- Manejo de notas vacías o nulas

## Flujo de Trabajo Recomendado

1. **Al Crear un Certificado:**
   - Complete los datos del producto y fechas
   - En la tabla de análisis, ingrese ensayos, especificaciones y resultados
   - Si un ensayo requiere una nota (ej: fue realizado externamente), escríbala en el campo "Nota de Ref."

2. **Al Generar el PDF:**
   - Seleccione el tipo de PDF (Pharmadix o Agrovet)
   - Si es Pharmadix, las notas aparecerán automáticamente
   - Si es Agrovet, las notas quedan ocultas

3. **Edición Posterior:**
   - Las notas pueden editarse junto con el resto del certificado
   - Los cambios se reflejan inmediatamente en el próximo PDF generado

## Ventajas del Sistema

✅ **Profesionalismo**: Referencias numeradas como en publicaciones científicas  
✅ **Claridad**: Separa observaciones generales de notas técnicas específicas  
✅ **Flexibilidad**: Cada ensayo puede tener su propia nota  
✅ **Eficiencia**: Notas duplicadas se consolidan automáticamente  
✅ **Elegancia**: Formato visual discreto pero informativo  
✅ **Compatibilidad**: Funciona tanto para PDFs Pharmadix como Agrovet (con comportamiento apropiado)

## Mantenimiento

- No requiere configuración adicional
- El catálogo se genera dinámicamente en cada PDF
- Los números se asignan automáticamente según el orden de aparición
- Sin límite en la cantidad de notas únicas (aunque solo 20 ensayos máximo)

## Soporte Técnico

Para dudas o problemas con el sistema de notas:
- Revisar este documento
- Contactar al administrador del sistema
- Verificar los logs en caso de errores de generación de PDF

---

**Última actualización**: Febrero 2026  
**Versión del sistema**: 2.0
