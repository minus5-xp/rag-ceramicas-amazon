# 🔧 Sistema RAG para Análisis de Reviews de Baldosas Cerámicas

Aplicación Streamlit para análisis inteligente de reviews de Amazon usando RAG (Retrieval-Augmented Generation) con Google Gemini.

## 📋 Características

- ✅ Carga y filtrado de hasta 10,000 reviews de Amazon Home & Kitchen
- ✅ Keywords: ceramic tile, tiles, ceramic, vinyl floor
- ✅ Índice vectorial con ChromaDB y embeddings de Gemini
- ✅ Consultas inteligentes con RAG
- ✅ Comparación con/sin RAG
- ✅ Interfaz interactiva con Streamlit

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key de Google Gemini (IMPORTANTE)

**⚠️ Lee el archivo [SECURITY.md](SECURITY.md) para configurar tu API key de forma segura.**

Resumen rápido:
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey) y crea una API key
2. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`
3. Edita `.streamlit/secrets.toml` y añade tu API key
4. **NUNCA** subas `secrets.toml` a GitHub (ya está en `.gitignore`)

Alternativamente, introduce la API key en la interfaz de la app.

## ▶️ Ejecutar la aplicación

**ANTES de ejecutar**, asegúrate de haber configurado tu API key en `.streamlit/secrets.toml`

```bash
streamlit run app_rag_ceramicas_simple.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

**Nota**: La API key se carga automáticamente desde `secrets.toml` y nunca se muestra en la interfaz.

## 📖 Cómo usar

### Paso 1: Cargar Reviews
1. Selecciona el número de reviews (100 - 2,000)
2. Click en "Generar Datos de Ejemplo"
3. Espera mientras se generan las reviews

### Paso 2: Crear Índice Vectorial
1. Click en "Crear Indice Vectorial"
2. Espera 5-10 minutos mientras se generan los embeddings
3. El índice se cachea automáticamente

### Paso 3: Hacer Consultas
- Usa las preguntas sugeridas o escribe tu propia pregunta
- El sistema recuperará las reviews más relevantes
- Obtendrás una respuesta basada en opiniones reales de clientes

**Nota**: La configuración de API está completamente automatizada y oculta.

## 🌐 Desplegar en la nube (GRATIS)

### Opción 1: Streamlit Community Cloud

1. Sube el código a un repositorio GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Configura la variable de entorno `GOOGLE_API_KEY` en los secrets
5. ¡Listo! Tu app estará online 24/7 gratis

**Configurar Secrets en Streamlit Cloud:**
```toml
# .streamlit/secrets.toml
GOOGLE_API_KEY = "tu-api-key-aqui"
```

### Opción 2: Google Colab (para desarrollo)

Puedes ejecutar el notebook directamente en Google Colab con acceso a GPU gratis.

## 💰 Costos

### Gemini API (Google)
- **Gemini 2.0 Flash**: GRATIS hasta 1,500 requests/día
- **Embeddings**: GRATIS hasta 1,500 requests/día
- Para 10,000 reviews: ~$0 (dentro del tier gratuito)

### Streamlit Community Cloud
- **Hosting**: GRATIS
- Límites: 1GB RAM, uso razonable

**Total: $0/mes** 🎉

## 📊 Preguntas de Ejemplo

- ¿Qué problemas comunes tienen las baldosas cerámicas según los clientes?
- ¿Los clientes mencionan problemas con la instalación?
- ¿Qué baldosas tienen mejor valoración en durabilidad?
- ¿Qué opinan sobre la calidad del material cerámico?
- ¿Vale la pena comprar baldosas cerámicas autoadhesivas?
- ¿Qué productos recomiendan para cocinas vs baños?

## 🔧 Solución de Problemas

### Error: "API Key inválida"
- Verifica que copiaste la key completa
- Asegúrate de haber activado la API de Gemini en Google Cloud

### Error: "Rate limit exceeded"
- Gemini Free tier: 1,500 requests/día
- Espera unas horas o actualiza a plan de pago

### La carga es muy lenta
- Normal para 10,000 reviews (5-10 min)
- Prueba con menos reviews primero (1,000-3,000)
- La app cachea los datos, solo se carga una vez

## 📚 Estructura del Proyecto

```
.
├── app_rag_ceramicas.py      # Aplicación Streamlit principal
├── demo_rag_ceramicas_v1.ipynb  # Notebook de desarrollo
├── requirements.txt          # Dependencias Python
└── README.md                # Este archivo
```

## 🎓 Contexto Académico

Proyecto desarrollado para la **Sesión 2** del curso de **IA Generativa** en **ISDI MDA Módulo 3** por Alberto Cámara.

## 📄 Licencia

Este proyecto es de uso educativo para el curso de ISDI MDA.
