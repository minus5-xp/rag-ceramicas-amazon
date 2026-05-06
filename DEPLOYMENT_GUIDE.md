# 🚀 Guía de Deployment en Streamlit Cloud

## 📋 Requisitos Previos

- Cuenta en [GitHub](https://github.com)
- Cuenta en [Streamlit Cloud](https://share.streamlit.io)
- API key de Google Gemini (obtén la tuya en [Google AI Studio](https://aistudio.google.com/apikey))

## 🔧 Pasos para Publicar

### 1. Crear Repositorio en GitHub

```bash
# Inicializar git (si no está inicializado)
git init

# Añadir archivos
git add app_rag_ceramicas_simple.py
git add ceramic_tiles_reviews.csv
git add requirements.txt
git add README.md
git add SECURITY.md
git add .gitignore

# Commit
git commit -m "Initial commit: RAG app for ceramic tiles reviews"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU_USUARIO/rag-ceramicas.git
git branch -M main
git push -u origin main
```

### 2. Deploy en Streamlit Cloud

1. Ir a https://share.streamlit.io
2. Click en **"New app"**
3. Seleccionar tu repositorio: `TU_USUARIO/rag-ceramicas`
4. Branch: `main`
5. Main file path: `app_rag_ceramicas_simple.py`
6. Click en **"Advanced settings"**

### 3. Configurar Secrets en Streamlit Cloud

En **Advanced settings** → **Secrets**, añadir:

```toml
GOOGLE_API_KEY = "tu-api-key-de-google-gemini-aqui"
```

⚠️ **IMPORTANTE**: Usa tu propia API key de Google Gemini (obtén una en https://aistudio.google.com/apikey)

### 4. Deploy

Click en **"Deploy!"** y esperar 2-3 minutos.

## ✅ Verificación

Una vez desplegado:

1. Probar la carga automática del CSV (tab "📊 Reviews Reales")
2. Verificar que muestra: "50,000 reviews"
3. Probar preguntas comparativas: "Vinilo vs Cerámica: ¿Cuál es mejor?"
4. Confirmar que la API key NO es visible en la interfaz

## 🔒 Seguridad

- ✅ API key almacenada en Streamlit Cloud Secrets
- ✅ `.gitignore` protege `secrets.toml` local
- ✅ Sin inputs de API key en la interfaz
- ✅ CSV no contiene información sensible

## 📊 Dataset

- **50,000 reviews** de productos relacionados con:
  - Ceramic tiles
  - Vinyl flooring
  - Tile installation
  - Grout y accesorios

## 🌐 URL Pública

Después del deployment, tu app estará disponible en:
```
https://TU_USUARIO-rag-ceramicas-app-rag-ceramicas-simple-HASH.streamlit.app
```

## 🆘 Troubleshooting

### Error: "API key not found"
- Verifica Secrets en Streamlit Cloud
- Reinicia la app desde el dashboard

### Error: "CSV not found"
- Confirma que `ceramic_tiles_reviews.csv` está en el repo
- Verifica el path en `app_rag_ceramicas_simple.py`

### App muy lenta
- Normal en primera carga (creando vectorstore)
- ChromaDB se crea en caché de Streamlit
- Siguientes cargas serán más rápidas
