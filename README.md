# 🏠 Sistema RAG para Análisis de Reviews de Productos de Pisos

Aplicación Streamlit para análisis inteligente de **10,000 reviews reales de Amazon** usando RAG (Retrieval-Augmented Generation) con Google Gemini. Compara baldosas cerámicas vs pisos de vinilo basándose en opiniones reales de clientes.

## 🌐 Demo en Vivo

🔗 **[Accede a la aplicación desplegada](https://share.streamlit.io)** (Streamlit Community Cloud)

## 📋 Características

- ✅ **10,000 reviews reales** extraídas de base de datos MySQL (26.7M registros)
- ✅ **Keywords específicas**: ceramic tiles, vinyl flooring, ceramic tile, vinyl floor, tiles, ceramic
- ✅ **Product types cubiertos**: Vinyl Flooring (16,171 reviews), Ceramic Floor Tile (2,489 reviews)
- ✅ Índice vectorial con ChromaDB y embeddings de Gemini (dimensión 3072)
- ✅ **RAG comparativo**: Analiza diferencias entre cerámicas y vinilo
- ✅ **Seguridad total**: API key completamente oculta (no visible en interfaz)
- ✅ Interfaz con 3 pestañas: CSV real, datos de ejemplo, carga personalizada
- ✅ 8 preguntas sugeridas + preguntas libres
- ✅ Optimizado para Streamlit Cloud (límite 5K documentos en vectorstore)

## ⚡ Quick Start (3 pasos)

```bash
# 1. Clonar y instalar
git clone https://github.com/minus5-xp/rag-ceramicas-amazon.git
cd rag-ceramicas-amazon
pip install -r requirements.txt

# 2. Configurar API key (OBLIGATORIO)
# Crea .streamlit/secrets.toml con tu API key de Google Gemini
echo 'GOOGLE_API_KEY = "tu-api-key-aqui"' > .streamlit/secrets.toml

# 3. Ejecutar
streamlit run app_rag_ceramicas_simple.py
# Abre http://localhost:8501 en tu navegador
```

**🎯 Obtén tu API key gratis**: [Google AI Studio](https://aistudio.google.com/apikey)

## 🚀 Instalación Local

### Requisitos
- Python 3.11 o superior
- Conda (recomendado) o virtualenv
- Acceso a internet para API de Google Gemini

### 1. Clonar el repositorio

```bash
git clone https://github.com/minus5-xp/rag-ceramicas-amazon.git
cd rag-ceramicas-amazon
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Dependencias principales:
- `streamlit`: Framework web
- `langchain`, `langchain-google-genai`: RAG y LLM
- `langchain-chroma`, `chromadb`: Base de datos vectorial
- `pandas`: Manipulación de datos

### 3. Configurar API Key de Google Gemini (OBLIGATORIO)

**⚠️ Lee el archivo [SECURITY.md](SECURITY.md) para configurar tu API key de forma segura.**

**Método 1: Archivo local (recomendado para desarrollo)**
1. Ve a [Google AI Studio](https://aistudio.google.com/apikey) y crea una API key
2. Crea el archivo `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "tu-api-key-aqui"
   ```
3. **NUNCA** subas este archivo a GitHub (ya está en `.gitignore`)

**Método 2: Variable de entorno**
```bash
export GOOGLE_API_KEY="tu-api-key-aqui"  # Linux/Mac
set GOOGLE_API_KEY=tu-api-key-aqui       # Windows CMD
```

**⚠️ IMPORTANTE**: La API key NO se introduce en la interfaz. Se carga automáticamente desde `secrets.toml` o variables de entorno.

## ▶️ Ejecutar la aplicación

**ANTES de ejecutar**, asegúrate de haber configurado tu API key en `.streamlit/secrets.toml`

```bash
streamlit run app_rag_ceramicas_simple.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

**Nota**: La API key se carga automáticamente desde `secrets.toml` y **nunca se muestra en la interfaz**.

## 📖 Cómo usar

### Pestaña 1: 📊 Reviews Reales (CSV) - RECOMENDADO

**Auto-carga al iniciar la app**

1. **Dataset incluido**: `ceramic_tiles_reviews.csv` (10,000 reviews, ~5MB)
   - Extraídas de base de datos MySQL con 26.7M registros
   - Keywords: ceramic tile, vinyl flooring, tiles, vinyl floor
   - Columnas: `title`, `text`, `rating`, `parent_asin`

2. **Crear índice vectorial**: 
   - Click en "🚀 Crear Índice Vectorial"
   - Espera 2-3 minutos (se procesa una vez y se cachea)
   - Se limita a 5,000 documentos para optimización en cloud

3. **Hacer consultas**:
   - Usa las **8 preguntas sugeridas** (4 comparativas vinyl vs ceramic)
   - O escribe tu propia pregunta
   - El sistema recupera las 5-8 reviews más relevantes
   - Obtendrás respuesta sintetizada por Gemini 2.5 Flash

### Pestaña 2: 🎲 Datos de Ejemplo

- Genera 1,500 reviews sintéticas de 15 plantillas
- Útil para pruebas sin esperar la carga del CSV
- Menor calidad que datos reales

### Pestaña 3: 📤 Cargar Otro CSV

- Formatos admitidos: `.csv`, `.xlsx`, `.json`
- Columnas requeridas: `title`, `text`, `rating`, `parent_asin`
- Máximo recomendado: 10,000 reviews

## 🌐 Desplegar en Streamlit Cloud (GRATIS)

**✅ Ya desplegado en:** [share.streamlit.io](https://share.streamlit.io)

### Cómo replicar el deployment:

1. **Prepara tu repositorio GitHub**
   ```bash
   git push origin main
   ```

2. **Conecta a Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con GitHub
   - Click en "New app"
   - Selecciona: `minus5-xp/rag-ceramicas-amazon`
   - Main file: `app_rag_ceramicas_simple.py`

3. **Configura Secrets (CRÍTICO)**
   - En "Advanced settings" > "Secrets"
   - Añade:
     ```toml
     GOOGLE_API_KEY = "tu-api-key-de-google-gemini"
     ```
   - **NUNCA** pongas la API key en el código

4. **Deploy**
   - Click en "Deploy"
   - Espera 2-3 minutos
   - ¡Tu app estará online 24/7 gratis!

### Limitaciones de Streamlit Cloud (Free Tier):
- 1 GB RAM
- Se limita a 5,000 documentos en vectorstore (implementado en el código)
- Se recomienda CSV ≤ 10,000 reviews

## 💰 Costos

### Gemini API (Google)
- **Gemini 2.5 Flash**: GRATIS hasta 1,500 requests/día
- **Embeddings (models/gemini-embedding-001)**: GRATIS hasta 1,500 requests/día
- **Dimensión de embeddings**: 3,072
- Para 10,000 reviews: ~$0 (dentro del tier gratuito)

### Streamlit Community Cloud
- **Hosting**: GRATIS permanente
- Límites: 1GB RAM, uso razonable
- Auto-deploy desde GitHub en cada push

### Base de Datos MySQL (origen de datos)
- **Local**: localhost:3306
- **Reviews totales en DB**: 26,765,000 registros
- **Extraídas para este proyecto**: 10,000 (optimizado)

**Total: $0/mes** 🎉

## 📊 Preguntas de Ejemplo Sugeridas

### 🆚 Comparativas (Vinyl vs Ceramic):
1. **"¿Qué es mejor para cocinas: baldosas cerámicas o suelos de vinilo?"**
2. **"Compara durabilidad: vinilo vs cerámica según las reviews"**
3. **"¿Cuál es más fácil de instalar: ceramic tiles o vinyl floor?"**
4. **"Vinilo vs Cerámica: ¿Cuál tiene mejor relación calidad-precio?"**

### 🔍 Específicas de Cerámicas:
5. **"¿Qué problemas comunes tienen las baldosas cerámicas?"**
6. **"¿Qué opinan los clientes sobre baldosas cerámicas autoadhesivas?"**

### 🔍 Específicas de Vinilo:
7. **"¿Los pisos de vinilo son resistentes al agua según las reviews?"**
8. **"¿Qué dicen sobre la instalación de vinyl flooring?"**

### 💡 Generales:
- "¿Qué productos recomiendan para baños?"
- "¿Vale la pena el precio de las baldosas premium?"
- "¿Hay diferencias de calidad entre marcas?"

## 🔧 Solución de Problemas

### Error: "No se pudo cargar la API key"
- **Causa**: No existe el archivo `.streamlit/secrets.toml`
- **Solución**: Crea el archivo con tu API key (ver sección Instalación)
- **Verificación**: Asegúrate de que el archivo NO esté en `.gitignore`

### Error: "API Key inválida"
- Verifica que copiaste la key completa desde [Google AI Studio](https://aistudio.google.com/apikey)
- Asegúrate de que la key esté activa (las keys pueden expirar)
- Formato correcto: `GOOGLE_API_KEY = "AIzaSy..."` (con comillas)

### Error: "Rate limit exceeded"
- Gemini Free tier: 1,500 requests/día
- Espera 24 horas o actualiza a plan de pago
- Considera reducir el número de reviews procesadas

### Error: 404 en modelo de embeddings
- **CRÍTICO**: Usar `models/gemini-embedding-001` (no `text-embedding-004`)
- Verifica la versión de `langchain-google-genai` (4.2.2+)

### Error: ValueError con ChatPromptTemplate
- **Solución implementada**: Se usa `PromptTemplate` en lugar de `ChatPromptTemplate`
- Asegúrate de tener `convert_system_message_to_human=True` en el LLM

### La carga del índice es lenta
- **Normal**: 2-3 minutos para 10,000 reviews
- **Optimización**: Se cachea con `@st.cache_resource`, solo se carga una vez
- **Límite cloud**: Se procesan máximo 5,000 documentos en Streamlit Cloud

### CSV no se carga automáticamente
- Verifica que `ceramic_tiles_reviews.csv` esté en el directorio raíz
- Tamaño máximo recomendado: 10 MB (~10,000 reviews)
- Formato requerido: columnas `title`, `text`, `rating`, `parent_asin`

## 📚 Estructura del Proyecto

```
.
├── app_rag_ceramicas_simple.py     # 🎯 Aplicación Streamlit principal
├── ceramic_tiles_reviews.csv       # 📊 Dataset de 10K reviews reales
├── requirements.txt                # 📦 Dependencias Python
├── README.md                       # 📖 Este archivo
├── SECURITY.md                     # 🔒 Guía de seguridad para API keys
├── DEPLOYMENT_GUIDE.md             # 🚀 Guía detallada de deployment
├── .gitignore                      # 🚫 Archivos excluidos de Git
└── .streamlit/
    └── secrets.toml                # 🔑 API key (NO incluido en repo)
```

### Archivos NO incluidos en GitHub (`.gitignore`):
- `.streamlit/secrets.toml` - Contiene API key sensible
- `.venv/` - Entorno virtual de Python
- `*.ipynb` - Notebooks de desarrollo
- Scripts de desarrollo (`extraer_reviews_mysql.py`, `buscar_*.py`)

### Modelos y Tecnologías:
- **LLM**: Gemini 2.5 Flash (`gemini-2.5-flash`)
- **Embeddings**: Gemini Embedding 001 (`models/gemini-embedding-001`)
- **Vector DB**: ChromaDB 1.5.9 con LangChain-Chroma 1.1.0
- **Framework**: Streamlit + LangChain
- **Prompt**: `PromptTemplate` con `convert_system_message_to_human=True`

## 📊 Base de Datos y Dataset

### Origen de Datos: MySQL Local
- **Host**: localhost:3306
- **Base de datos**: `amazon_reviews`
- **Tabla**: `reviews_raw` con **26,765,000 registros**
- **Motor**: MySQL 8.0.45
- **Conexión**: PyMySQL + SQLAlchemy con charset UTF-8

### Proceso de Extracción:
```sql
-- Query principal usada
SELECT id, rating, title, text, asin, parent_asin, user_id, 
       timestamp, verified_purchase, helpful_vote, main_category, 
       product_type, price, store
FROM reviews_raw
WHERE LOWER(text) LIKE '%ceramic tiles%' 
   OR LOWER(text) LIKE '%vinyl flooring%'
   OR LOWER(title) LIKE '%ceramic tile%'
   OR LOWER(title) LIKE '%vinyl floor%'
   OR LOWER(text) LIKE '%tiles%'
   OR LOWER(text) LIKE '%ceramic%'
LIMIT 10000;
```

### Estadísticas del Dataset:
- **Reviews extraídas**: 300,086 (primera extracción)
- **Reviews optimizadas**: 10,000 (deployment final)
- **Product types principales**:
  - Vinyl Flooring: 16,171 reviews
  - Ceramic Floor Tile: 2,489 reviews
  - Hardwood Flooring: 2,728 reviews
- **Limpieza aplicada**: Eliminación de caracteres especiales, emojis, normalización de acentos

## 🛠️ Stack Tecnológico Completo

### Backend:
- **Python**: 3.11.9
- **LangChain**: Framework RAG
- **LangChain Google GenAI**: 4.2.2 (integración Gemini)
- **ChromaDB**: 1.5.9 (vector store)
- **LangChain-Chroma**: 1.1.0 (integración)
- **Pandas**: Manipulación de datos
- **PyMySQL**: 1.1.1 (conexión MySQL)
- **SQLAlchemy**: 2.0.44 (ORM)

### Frontend:
- **Streamlit**: Framework web interactivo
- **Interface**: 3 pestañas (CSV real, ejemplo, carga custom)
- **Caching**: `@st.cache_data`, `@st.cache_resource`

### AI/ML:
- **Google Gemini 2.5 Flash**: Generación de respuestas
- **Gemini Embedding 001**: Embeddings de 3,072 dimensiones
- **Configuración LLM**:
  - Temperature: 0.3 (respuestas consistentes)
  - `convert_system_message_to_human=True` (compatibilidad Gemini)

### DevOps:
- **Git**: Control de versiones
- **GitHub**: `minus5-xp/rag-ceramicas-amazon`
- **Streamlit Cloud**: Hosting y deployment automático
- **Secrets Management**: `.streamlit/secrets.toml` + Streamlit Cloud Secrets

## 📈 Métricas del Proyecto

### Performance:
- **Tiempo de carga inicial**: 2-3 minutos (primera vez)
- **Embeddings generados**: 5,000 documentos (límite cloud)
- **Retrieval**: 5-8 documentos relevantes por query
- **Latencia de respuesta**: 3-5 segundos
- **Tamaño CSV**: 5 MB (10,000 reviews)

### Optimizaciones Implementadas:
1. ✅ Límite de 5K docs en vectorstore (Streamlit Cloud RAM)
2. ✅ Caching de embeddings con `@st.cache_resource`
3. ✅ Limpieza de texto (emojis, acentos, ASCII)
4. ✅ Reducción dataset: 300K → 10K reviews
5. ✅ Prompt optimizado para comparaciones vinyl vs ceramic
6. ✅ Retriever configurable (k=5 default)

## 🎓 Contexto Académico

Proyecto desarrollado para la **Sesión 2** del curso de **IA Generativa** en **ISDI MDA Módulo 3** por Alberto Cámara.

## 📄 Licencia

Este proyecto es de uso educativo para el curso de ISDI MDA.
