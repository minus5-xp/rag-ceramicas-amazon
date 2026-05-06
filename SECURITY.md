# ⚠️ SEGURIDAD - IMPORTANTE LEER

## 🔒 Configuración Segura de la API Key

### Para uso local:

1. **Copia el archivo de ejemplo**:
   ```bash
   copy .streamlit\secrets.toml.example .streamlit\secrets.toml
   ```

2. **Edita `.streamlit\secrets.toml`** y añade tu API key real:
   ```toml
   GOOGLE_API_KEY = "tu-api-key-real-aqui"
   ```

3. **Verifica que `.streamlit\secrets.toml` está en `.gitignore`**
   - ✅ Ya está incluido por defecto
   - Este archivo NUNCA debe subirse a GitHub

### Para desplegar en Streamlit Cloud:

1. Ve a la configuración de tu app en share.streamlit.io
2. En "Secrets", añade:
   ```toml
   GOOGLE_API_KEY = "tu-api-key"
   ```
3. No subas el archivo `secrets.toml` al repositorio

### ❌ NUNCA HAGAS ESTO:

- ❌ Subir `secrets.toml` a GitHub
- ❌ Hardcodear la API key en el código Python
- ❌ Compartir tu API key en Slack, Discord, email, etc.
- ❌ Hacer commit de archivos con tu API key
- ❌ Incluir la API key en capturas de pantalla

### ✅ BUENAS PRÁCTICAS:

- ✅ Usar `secrets.toml` para desarrollo local
- ✅ Usar variables de entorno en producción
- ✅ Añadir `secrets.toml` al `.gitignore`
- ✅ Rotar la API key si se expone accidentalmente
- ✅ Usar diferentes API keys para desarrollo y producción

### 🚨 Si expusiste tu API key accidentalmente:

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Elimina la API key comprometida
3. Genera una nueva API key
4. Actualiza tu configuración local
5. Si está en GitHub:
   - Borra el commit con `git rebase` o `git filter-branch`
   - O mejor: haz el repositorio privado y genera nueva key

### 📚 Más información:

- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Google AI Studio](https://makersuite.google.com/app/apikey)

---

**Recuerda**: Trata tu API key como una contraseña. Si se expone, cualquiera puede usarla y consumir tu cuota gratuita o generar cargos en tu cuenta.
