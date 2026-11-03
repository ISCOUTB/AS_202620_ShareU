# shareU — configuración de Firebase

ShareU permite registrarse, iniciar sesión y publicar material académico como texto. **No requiere Firebase Storage ni subida de archivos**, para mantener bajos los costos. Las publicaciones quedan pendientes hasta que un administrador las apruebe.

## 1. Firebase
1. En Firebase Console, proyecto `shareu-96e84`, habilita **Authentication → Sign-in method → Email/Password**.
2. Crea **Firestore Database** en modo producción.
3. En **Project settings → General → Your apps**, registra o abre la aplicación web y copia su configuración en `firebase-config.js`.
4. Sustituye `REEMPLAZAR_API_KEY` por el valor real de `apiKey`. Los demás valores de configuración ya corresponden al proyecto ShareU.
5. En Authentication → Settings → Authorized domains, agrega el dominio donde publiques el sitio.

## 2. Reglas de Firestore
Publica las reglas del archivo `firestore.rules` desde Firestore → Rules. No uses reglas abiertas como `allow read, write: if true`. Las reglas deben permitir a usuarios autenticados crear sus propias publicaciones en estado `pending`, leer sus propias publicaciones y permitir lectura pública únicamente de publicaciones aprobadas. Solo administradores deben poder moderar publicaciones y cambiar roles.

## 3. Crear administrador
1. Registra la cuenta desde la web.
2. En Firebase Console → Firestore → colección `users`, abre el documento cuyo ID es el UID de la cuenta.
3. Cambia el campo `role` de `user` a `admin`.
4. Cierra sesión y vuelve a entrar.

## 4. Ejecutar localmente
Abre el proyecto con un servidor estático, no con `file://`. Por ejemplo:
```bash
python3 -m http.server 5500
```
Luego abre http://localhost:5500.

## Modelo de datos
- `users/{uid}`: perfil y rol (`user` o `admin`).
- `documents/{id}`: título, materia, carrera, universidad, tipo, contenido en texto, autor, fecha y estado (`pending`, `approved`, `rejected`).

**No se usa Firebase Storage.** La clave `apiKey` de una app web forma parte de la configuración del cliente; protege los datos con Authentication y reglas de Firestore, y nunca publiques claves privadas de cuentas de servicio.
