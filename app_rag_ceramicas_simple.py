"""
Aplicación RAG para Análisis de Reviews de Baldosas Cerámicas - Versión Simplificada
Sin dependencia de Hugging Face Datasets (para evitar problemas con PyTorch en Windows)
"""

import streamlit as st
import pandas as pd
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import json

# Configuración de la página
st.set_page_config(
    page_title="RAG - Reviews Baldosas Ceramicas",
    page_icon=":wrench:",
    layout="wide"
)

# Título principal
st.title("Sistema RAG para Análisis de Reviews de Baldosas Cerámicas")
st.markdown("### Análisis inteligente de reviews de productos de cermica y vinilo")

# Cargar API Key de forma segura (solo desde secrets.toml)
api_key = None
try:
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if api_key == "tu-api-key-aqui" or not api_key:
        api_key = None
except:
    api_key = None

# Verificación crítica de API key
if api_key is None:
    st.error("❌ API Key de Google Gemini no encontrada")
    st.warning("🔑 Para usar esta app, configura `GOOGLE_API_KEY` en los Secrets de Streamlit Cloud")
    st.info("👉 Ve a 'Manage app' → 'Settings' → 'Secrets' y añade tu API key")
    st.code('GOOGLE_API_KEY = "tu-api-key-de-google-gemini"', language="toml")
    st.stop()

# Sidebar para configuración
with st.sidebar:
    st.header("Configuracion")
    
    st.markdown("### Keywords de busqueda")
    st.code("""
    • ceramic tile
    • tiles
    • ceramic
    • vinyl floor
    """)
    
    st.markdown("---")
    st.info("Nota: Esta version usa datos de ejemplo o archivo CSV local")

# Función para generar datos de ejemplo
def generar_datos_ejemplo(num_reviews=100):
    """Genera reviews de ejemplo para demostración"""
    
    reviews_ejemplo = [
        {
            "title": "Great ceramic tiles for bathroom renovation",
            "text": "These ceramic tiles are perfect for my bathroom. Easy to install, waterproof, and look amazing. The grout lines are clean and the tiles are durable. Highly recommend for any home improvement project.",
            "rating": 5,
            "parent_asin": "B001"
        },
        {
            "title": "Vinyl flooring - Good quality but difficult installation",
            "text": "The vinyl floor tiles look great once installed, but the installation process was challenging. The adhesive didn't stick well initially. However, the final result is worth it. Good for kitchen floors.",
            "rating": 4,
            "parent_asin": "B002"
        },
        {
            "title": "Ceramic tile - Broke during shipping",
            "text": "Ordered these ceramic tiles for my kitchen backsplash. Unfortunately, several tiles arrived broken. The ones that were intact look good, but I had to reorder. Packaging needs improvement.",
            "rating": 2,
            "parent_asin": "B003"
        },
        {
            "title": "Perfect for DIY bathroom project",
            "text": "As a DIY enthusiast, these ceramic tiles were perfect. Easy to cut, waterproof coating works well, and the price is reasonable. Used them for bathroom walls and floor. No issues after 6 months.",
            "rating": 5,
            "parent_asin": "B004"
        },
        {
            "title": "Vinyl floor tiles - Not very durable",
            "text": "These vinyl tiles looked great initially, but after a few months, some started peeling off. The adhesive quality is questionable. Might work for low-traffic areas but not recommended for kitchen.",
            "rating": 3,
            "parent_asin": "B005"
        },
        {
            "title": "Excellent ceramic tiles for kitchen backsplash",
            "text": "Beautiful ceramic tiles! The glossy finish looks professional and the tiles are thick and durable. Installation was straightforward with proper tools. My kitchen looks amazing now.",
            "rating": 5,
            "parent_asin": "B006"
        },
        {
            "title": "Ceramic tile grout issues",
            "text": "The tiles themselves are fine, but the grout lines are difficult to work with. The tiles are slightly uneven, making grouting challenging. End result is okay but could be better.",
            "rating": 3,
            "parent_asin": "B007"
        },
        {
            "title": "Best vinyl flooring for the price",
            "text": "Amazing value for money! These vinyl floor tiles are easy to install, waterproof, and look like real wood. Perfect for basement renovation. Installation took only one weekend.",
            "rating": 5,
            "parent_asin": "B008"
        },
        {
            "title": "Ceramic tiles - Color doesn't match description",
            "text": "The tiles are good quality but the color is darker than shown in pictures. Would have been 5 stars if the color matched. Still usable but not what I expected for my bathroom.",
            "rating": 3,
            "parent_asin": "B009"
        },
        {
            "title": "Professional quality ceramic tiles",
            "text": "Used these tiles for a commercial bathroom renovation. Excellent quality, consistent thickness, and the ceramic material is highly durable. Would definitely purchase again for future projects.",
            "rating": 5,
            "parent_asin": "B010"
        }
    ]
    
    # Expandir los ejemplos
    reviews = []
    for i in range(num_reviews):
        review = reviews_ejemplo[i % len(reviews_ejemplo)].copy()
        review['parent_asin'] = f"B{i:04d}"
        reviews.append(review)
    
    return pd.DataFrame(reviews)

# Función para cargar reviews desde CSV (si existe)
@st.cache_data(show_spinner=False)
def cargar_reviews_desde_csv(filepath):
    """Carga reviews desde un archivo CSV"""
    try:
        df = pd.read_csv(filepath)
        required_cols = ['title', 'text', 'rating', 'parent_asin']
        if all(col in df.columns for col in required_cols):
            return df
        else:
            st.error(f"El CSV debe contener columnas: {required_cols}")
            return None
    except Exception as e:
        st.error(f"Error cargando CSV: {e}")
        return None

# Función para limpiar texto de emojis y caracteres problemáticos
def limpiar_texto(texto):
    """Elimina emojis y caracteres no-ASCII que causan problemas"""
    if not isinstance(texto, str):
        return str(texto)
    
    # Reemplazar caracteres acentuados comunes
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ü': 'u', 'Ü': 'U',
        '¿': '', '¡': '',
        '–': '-', '—': '-', ''': "'", ''': "'", '"': '"', '"': '"'
    }
    
    for old, new in reemplazos.items():
        texto = texto.replace(old, new)
    
    # Mantener solo caracteres ASCII imprimibles (32-126)
    texto_limpio = ''.join(char for char in texto if 32 <= ord(char) <= 126)
    
    # Limpiar espacios múltiples
    texto_limpio = ' '.join(texto_limpio.split())
    
    return texto_limpio

# Función para crear el índice vectorial
@st.cache_resource(show_spinner=False)
def crear_vectorstore(_df, _api_key):
    """Crea el índice vectorial en ChromaDB"""
    
    # Limitar número de documentos para evitar límites de API en cloud
    MAX_DOCS = 5000
    if len(_df) > MAX_DOCS:
        st.warning(f"⚠️ Limitando a {MAX_DOCS:,} reviews para optimizar rendimiento en cloud")
        _df = _df.sample(n=MAX_DOCS, random_state=42)
    
    st.info(f"Generando embeddings para {len(_df):,} reviews...")
    
    try:
        # Configurar embeddings de Gemini (usando el modelo correcto de Google)
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=_api_key,
            task_type="retrieval_document"
        )
        
        # Convertir a Documents (limpiando el texto)
        docs = [
            Document(
                page_content=limpiar_texto(f"{row['title']}\n\n{row['text']}"),
                metadata={
                    "rating": int(row["rating"]),
                    "parent_asin": str(row["parent_asin"])
                }
            )
            for _, row in _df.iterrows()
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Creando índice vectorial...")
        
        # Crear vectorstore con batching automático
        vectorstore = Chroma.from_documents(
            docs, 
            embeddings,
            collection_name="ceramic_tiles_reviews_v2"
        )
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Índice vectorial creado: {len(docs):,} vectores")
        
        return vectorstore
        
    except Exception as e:
        st.error(f"❌ Error al crear vectorstore: {str(e)}")
        st.error("Verifica que la API key de Google Gemini sea válida y tenga cuota disponible")
        raise

# Función para crear la cadena RAG
def crear_rag_chain(vectorstore, api_key, k=5):
    """Crea la cadena RAG completa"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.3
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    
    prompt_rag = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente experto en análisis de productos para el hogar, especializado en baldosas cerámicas, azulejos y pisos de vinilo.

Tu función es analizar las reviews de clientes y proporcionar insights útiles. Puedes:
- Comparar diferentes tipos de productos (vinilo vs cerámica, diferentes marcas, etc.)
- Identificar patrones y tendencias en las opiniones de los clientes
- Sintetizar información de múltiples reviews para dar respuestas completas
- Hacer análisis comparativos de ventajas y desventajas
- Recomendar según el caso de uso (baños, cocinas, tráfico alto/bajo, etc.)

Basa tus respuestas en la información de las reviews proporcionadas, pero puedes hacer inferencias razonables y comparaciones entre los productos mencionados.

Cuando hagas comparaciones:
- Indica claramente qué dicen los clientes sobre cada tipo de producto
- Menciona el rating promedio si es relevante
- Cita ejemplos específicos de las reviews para respaldar tus puntos
- Si una comparación específica no tiene suficiente información, indícalo

Reviews recuperadas:
{context}"""),
        ("human", "{question}")
    ])
    
    def format_docs(docs):
        """Formatea los documentos recuperados con más contexto para comparaciones"""
        formatted = []
        for i, d in enumerate(docs, 1):
            rating = d.metadata.get('rating', '?')
            content = d.page_content[:700]  # Más contexto para comparaciones
            formatted.append(f"Review #{i} | Rating: {rating}★\n{content}")
        return "\n\n" + "="*80 + "\n\n".join(formatted)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_rag
        | llm
        | StrOutputParser()
    )
    
    return rag_chain, retriever

# ============================================================================
# FLUJO PRINCIPAL DE LA APLICACIÓN
# ============================================================================

# Verificar API Key
if not api_key:
    st.error("Configuracion requerida: API Key no encontrada")
    st.info("""
    Para usar esta aplicacion, configura tu Google API Key en el archivo:
    
    `.streamlit/secrets.toml`
    
    Consulta el archivo README.md para mas instrucciones.
    """)
    st.stop()

# Inicializar estado de sesión
if 'df' not in st.session_state:
    st.session_state.df = None
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None

# Sección 1: Carga de datos
st.header("1. Carga de Datos")

# Intentar cargar CSV de reviews reales primero
CSV_FILE = "ceramic_tiles_reviews.csv"
csv_exists = os.path.exists(CSV_FILE)

if csv_exists:
    st.success(f"✅ Encontrado archivo con reviews reales: {CSV_FILE}")

# Opciones de carga
tab1, tab2, tab3 = st.tabs(["📊 Reviews Reales (CSV)", "🎲 Datos de Ejemplo", "📤 Cargar Otro CSV"])

with tab1:
    st.markdown("### Reviews reales extraídas de la base de datos MySQL")
    
    if csv_exists:
        if st.button("Cargar Reviews Reales", type="primary"):
            df_real = cargar_reviews_desde_csv(CSV_FILE)
            if df_real is not None:
                st.session_state.df = df_real
                st.session_state.vectorstore = None
                st.session_state.rag_chain = None
                st.success(f"[OK] {len(df_real):,} reviews reales cargadas")
    else:
        st.warning(f"❌ No se encontró el archivo {CSV_FILE}")
        st.info("💡 Ejecuta `extraer_reviews_mysql.py` para generar el archivo con reviews reales")

with tab2:
    st.markdown("### Datos sintéticos para pruebas")
    num_reviews = st.slider(
        "Número de reviews de ejemplo",
        min_value=100,
        max_value=2000,
        value=1500,
        step=100
    )
    
    if st.button("Generar Datos de Ejemplo"):
        st.session_state.df = generar_datos_ejemplo(num_reviews)
        st.session_state.vectorstore = None
        st.session_state.rag_chain = None
        st.success(f"[OK] {len(st.session_state.df)} reviews generadas")

with tab3:
    st.markdown("### Carga tu propio archivo CSV")
    st.markdown("**Formato requerido:** `title`, `text`, `rating`, `parent_asin`")
    
    uploaded_file = st.file_uploader("Selecciona archivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        required_cols = ['title', 'text', 'rating', 'parent_asin']
        
        if all(col in df_uploaded.columns for col in required_cols):
            st.session_state.df = df_uploaded
            st.session_state.vectorstore = None
            st.session_state.rag_chain = None
            st.success(f"[OK] {len(df_uploaded)} reviews cargadas desde CSV")
        else:
            st.error(f"El CSV debe contener las columnas: {required_cols}")

# Cargar datos por defecto
if st.session_state.df is None:
    if csv_exists:
        st.info("📥 Cargando reviews reales automáticamente...")
        df_auto = cargar_reviews_desde_csv(CSV_FILE)
        if df_auto is not None:
            st.session_state.df = df_auto
            st.success(f"✅ {len(df_auto):,} reviews reales cargadas automáticamente")
    else:
        st.info("🎲 Generando datos de ejemplo...")
        st.session_state.df = generar_datos_ejemplo(1500)

df = st.session_state.df

# Mostrar estadísticas
if df is not None and len(df) > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", f"{len(df):,}")
    
    with col2:
        avg_rating = df['rating'].mean()
        st.metric("Rating Promedio", f"{avg_rating:.2f}")
    
    with col3:
        products = df['parent_asin'].nunique()
        st.metric("Productos Unicos", f"{products:,}")
    
    with col4:
        rating_5 = (df['rating'] == 5).sum()
        pct_5 = (rating_5 / len(df)) * 100
        st.metric("Reviews 5 estrellas", f"{pct_5:.1f}%")
    
    # Distribución de ratings
    st.subheader("Distribucion de Ratings")
    rating_counts = df['rating'].value_counts().sort_index()
    st.bar_chart(rating_counts)
    
    # Muestra de reviews
    with st.expander("Ver muestra de reviews"):
        st.dataframe(
            df[['rating', 'title', 'text']].head(10),
            use_container_width=True
        )

# Sección 2: Creación del índice vectorial
st.header("2. Indice Vectorial")

if st.button("Crear Indice Vectorial", type="primary", disabled=(df is None or len(df) == 0)):
    with st.spinner("Generando embeddings y creando índice..."):
        st.session_state.vectorstore = crear_vectorstore(df, api_key)
        st.session_state.rag_chain = None

if st.session_state.vectorstore is not None:
    st.success(f"Indice vectorial listo")
    
    # Crear RAG chain
    if st.session_state.rag_chain is None:
        num_docs = st.sidebar.slider(
            "Documentos a recuperar",
            min_value=3,
            max_value=15,
            value=8,
            help="Numero de reviews mas relevantes para el contexto (usa mas para comparaciones)"
        )
        st.session_state.rag_chain, st.session_state.retriever = crear_rag_chain(
            st.session_state.vectorstore,
            api_key,
            k=num_docs
        )

# Sección 3: Consultas RAG
if st.session_state.rag_chain is not None:
    st.header("3. Consultas con RAG")
    
    # Preguntas predefinidas
    st.subheader("Preguntas Sugeridas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔍 Análisis específicos**")
        
        if st.button("Que problemas tienen las baldosas ceramicas?"):
            st.session_state.pregunta = "¿Qué problemas comunes tienen las baldosas cerámicas según los clientes?"
        
        if st.button("Problemas con pisos de vinilo?"):
            st.session_state.pregunta = "¿Qué problemas reportan los clientes con los pisos de vinilo?"
        
        if st.button("Dificultades con la instalacion?"):
            st.session_state.pregunta = "¿Los clientes mencionan problemas con la instalación?"
        
        if st.button("Opiniones sobre durabilidad?"):
            st.session_state.pregunta = "¿Qué productos tienen mejor valoración en durabilidad?"
    
    with col2:
        st.markdown("**⚖️ Comparaciones**")
        
        if st.button("Vinilo vs Cerámica: ¿Cuál es mejor?"):
            st.session_state.pregunta = "Compara las ventajas y desventajas entre pisos de vinilo y baldosas cerámicas según las reviews"
        
        if st.button("Facilidad de instalación: Vinilo vs Cerámica"):
            st.session_state.pregunta = "¿Qué es más fácil de instalar según los clientes: vinilo o cerámica?"
        
        if st.button("Mejor opción para cocinas?"):
            st.session_state.pregunta = "¿Qué recomiendan más los clientes para cocinas: vinilo o baldosas cerámicas? ¿Por qué?"
        
        if st.button("Relación calidad-precio: comparativa"):
            st.session_state.pregunta = "Compara la relación calidad-precio entre productos de vinilo y cerámica según las opiniones"
    
    st.markdown("---")
    
    # Input personalizado
    st.subheader("Pregunta Personalizada")
    
    pregunta_input = st.text_area(
        "Escribe tu pregunta:",
        value=st.session_state.get('pregunta', ''),
        height=100,
        placeholder="Ejemplo: ¿Qué dicen los clientes sobre la resistencia al agua de las baldosas?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        consultar = st.button("Consultar", type="primary", use_container_width=True)
    
    if consultar and pregunta_input:
        with st.spinner("Analizando reviews..."):
            # Recuperar documentos
            docs_recuperados = st.session_state.retriever.invoke(pregunta_input)
            
            # Generar respuesta
            respuesta = st.session_state.rag_chain.invoke(pregunta_input)
            
            # Mostrar respuesta
            st.subheader("Respuesta")
            st.markdown(f"**Pregunta:** {pregunta_input}")
            st.info(respuesta)
            
            # Mostrar documentos recuperados
            with st.expander(f"Ver {len(docs_recuperados)} reviews recuperadas"):
                for i, doc in enumerate(docs_recuperados, 1):
                    rating = doc.metadata.get('rating', '?')
                    st.markdown(f"**Review {i}** — Rating: {rating} estrellas")
                    st.text(doc.page_content[:400] + "...")
                    st.markdown("---")
            
            # Opción de comparación sin RAG
            with st.expander("Comparar con respuesta SIN RAG"):
                llm_sin_rag = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=api_key
                )
                respuesta_sin_rag = llm_sin_rag.invoke(pregunta_input)
                st.warning("**Respuesta sin contexto (conocimiento general):**")
                st.write(respuesta_sin_rag.content)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Sesion 2 - ISDI MDA</strong> | Curso de IA Generativa</p>
    <p>Sistema RAG para analisis de reviews de productos del hogar</p>
    <p>Version simplificada sin dependencias de PyTorch</p>
</div>
""", unsafe_allow_html=True)
