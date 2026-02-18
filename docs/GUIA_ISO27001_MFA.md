# Guía de Cumplimiento ISO 27001 - Autenticación Multifactor (MFA/2FA)

## 📋 Requisitos de ISO 27001 para Autenticación

### Control A.9.4.2 - Secure log-on procedures

**Requisito:**
> "Donde sea apropiado, el procedimiento de inicio de sesión debe estar diseñado para minimizar la oportunidad de acceso no autorizado. El procedimiento de inicio de sesión debe revelar la mínima información sobre el sistema."

**Interpretación para MFA:**
- Se requiere **autenticación multifactor (MFA)** para:
  - Acceso a sistemas críticos
  - Acceso remoto
  - Acceso administrativo
  - Datos sensibles o confidenciales

---

## ✅ Opciones de Implementación para Cumplir con ISO

### **Opción 1: Política de 2FA Obligatorio en Google Workspace** ⭐ Recomendado

**Descripción:**
Exigir que todos los usuarios corporativos tengan 2FA habilitado en sus cuentas de Google.

**Ventajas:**
- ✅ No requiere código adicional
- ✅ Google gestiona el 2FA
- ✅ Cumple con ISO si es política corporativa documentada
- ✅ Fácil de auditar

**Implementación:**

1. **Habilitar 2FA en Google Workspace:**
   - Admin Console → Seguridad → Autenticación
   - Activar "Verificación en dos pasos"
   - Marcar como "Obligatorio"

2. **Documentar la política:**
   ```
   POLÍTICA DE SEGURIDAD - MFA-001
   
   Todos los usuarios con acceso al sistema Coadix deben tener
   autenticación de dos factores (2FA) habilitada en su cuenta
   de Google Workspace corporativa.
   
   Métodos aceptados:
   - Google Authenticator
   - SMS al teléfono corporativo
   - Llave de seguridad física (FIDO2)
   ```

3. **Auditoría:**
   - Verificar mensualmente que todos los usuarios tienen 2FA activo
   - Usar Google Admin SDK para reportes automáticos

**Evidencia para auditoría ISO:**
- Captura de pantalla de la configuración de Google Workspace
- Reporte de usuarios con 2FA habilitado
- Política de seguridad documentada

---

### **Opción 2: Implementar TOTP (Google Authenticator)** ⭐ Control Total

**Descripción:**
Añadir un segundo factor con códigos de 6 dígitos usando el módulo `two_factor_auth_module.py`.

**Ventajas:**
- ✅ Control total del proceso
- ✅ No depende de Google
- ✅ Compatible con múltiples apps (Google Authenticator, Microsoft Authenticator, Authy)
- ✅ Cumple 100% con ISO

**Implementación:**

```bash
# 1. Instalar dependencias
pip install pyotp qrcode[pil]

# 2. Añadir campos a tu base de datos
# - totp_secret (String, 32 caracteres)
# - totp_enabled (Boolean)

# 3. Integrar el módulo (ver two_factor_auth_module.py)
```

**Flujo de usuario:**

1. Usuario inicia sesión con email + contraseña
2. Sistema verifica credenciales
3. Si tiene 2FA habilitado → solicita código de 6 dígitos
4. Usuario ingresa código de su app
5. Sistema valida y otorga acceso

**Evidencia para auditoría ISO:**
- Código fuente del módulo 2FA
- Logs de autenticación con 2FA
- Política de seguridad documentada
- Procedimiento de configuración de 2FA para usuarios

---

### **Opción 3: SMS o Email con OTP** ⚠️ Menos Seguro

**Descripción:**
Enviar códigos de un solo uso por SMS o email.

**Ventajas:**
- ✅ Fácil de implementar
- ✅ No requiere app adicional

**Desventajas:**
- ⚠️ SMS puede ser interceptado (SIM swapping)
- ⚠️ Email puede estar comprometido
- ⚠️ NIST desaconseja SMS como segundo factor

**Implementación:**

```python
import random
from twilio.rest import Client  # Para SMS

def send_otp_sms(phone_number):
    code = str(random.randint(100000, 999999))
    
    # Guardar código en sesión o BD con expiración de 5 minutos
    session['otp_code'] = code
    session['otp_expires'] = datetime.now() + timedelta(minutes=5)
    
    # Enviar SMS
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=f"Tu código de verificación es: {code}",
        from_=TWILIO_PHONE,
        to=phone_number
    )
```

**Evidencia para auditoría ISO:**
- Logs de envío de OTP
- Política de expiración de códigos
- Documentación del proceso

---

### **Opción 4: Llaves de Seguridad Física (FIDO2/WebAuthn)** 🔒 Máxima Seguridad

**Descripción:**
Usar llaves físicas USB (YubiKey, Google Titan Key).

**Ventajas:**
- ✅ Máxima seguridad (resistente a phishing)
- ✅ Recomendado por NIST
- ✅ Cumple con ISO 27001 y otros estándares

**Desventajas:**
- ⚠️ Costo de las llaves físicas
- ⚠️ Requiere distribución física

**Implementación:**

```bash
pip install webauthn
```

```python
from webauthn import generate_registration_options, verify_registration_response

# Ver documentación completa en:
# https://github.com/duo-labs/py_webauthn
```

---

## 📊 Comparación de Opciones

| Opción | Seguridad | Facilidad | Costo | Cumple ISO |
|--------|-----------|-----------|-------|------------|
| Google Workspace 2FA | Alta | Muy fácil | Incluido | ✅ Sí |
| TOTP (Authenticator) | Alta | Fácil | Gratis | ✅ Sí |
| SMS/Email OTP | Media | Muy fácil | Bajo | ⚠️ Parcial |
| FIDO2 (YubiKey) | Muy Alta | Media | Alto | ✅ Sí |

---

## 📝 Documentación Requerida para Auditoría ISO

Para demostrar cumplimiento con ISO 27001, debes tener:

1. **Política de Autenticación Multifactor**
   - Quién debe usar MFA
   - Métodos aceptados
   - Procedimiento de configuración
   - Excepciones (si las hay)

2. **Procedimientos Operativos**
   - Cómo configurar 2FA
   - Cómo recuperar acceso si se pierde el dispositivo
   - Proceso de desactivación/reactivación

3. **Evidencia Técnica**
   - Código fuente del módulo 2FA
   - Logs de autenticación
   - Reportes de usuarios con 2FA habilitado

4. **Registros de Capacitación**
   - Evidencia de que los usuarios fueron capacitados en el uso de 2FA

---

## 🎯 Recomendación Final

**Para Coadix, recomiendo:**

### **Implementación Híbrida:**

1. **Para usuarios normales (Operarios):**
   - Usar Google OAuth con 2FA obligatorio en Google Workspace
   - Política corporativa documentada

2. **Para usuarios privilegiados (Supervisores, Administradores):**
   - Implementar TOTP adicional con `two_factor_auth_module.py`
   - Doble capa de seguridad

**Flujo:**
```
Usuario Operario:
  Login → Google OAuth (con 2FA de Google) → Dashboard

Usuario Administrador:
  Login → Google OAuth (con 2FA de Google) → Código TOTP → Panel Admin
```

Esto cumple **100% con ISO 27001** y proporciona defensa en profundidad.

---

## 📚 Referencias

- [ISO 27001:2022 - Annex A.9.4.2](https://www.iso.org/standard/27001)
- [NIST SP 800-63B - Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**¿Necesitas ayuda para implementar alguna de estas opciones?**
