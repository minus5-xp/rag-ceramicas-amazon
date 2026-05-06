"""
Aplicación RAG para Análisis de Reviews de Baldosas Cerámicas
Sesión 2 - ISDI MDA - Curso IA Generativa
"""

import streamlit as st
import pandas as pd
from datasets import load_dataset
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="RAG - Reviews Baldosas Cerámicas",
    page_icon="🔧",
    layout="wide"
)

# Título principal
st.title("🔧 Sistema RAG para Análisis de Reviews de Baldosas Cerámicas")
st.markdown("### Análisis inteligente de 10,000 reviews de Amazon Home & Kitchen")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # API Key de Gemini
    api_key = st.text_input(
        "Google API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Introduce tu API key de Google Gemini"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Keywords de búsqueda")
    st.code("""
    • ceramic tile
    • tiles
    • ceramic
    • vinyl floor
    """)
    
    st.markdown("---")
    st.info("💡 **Tip**: La carga inicial puede tardar 5-10 minutos")

# Función para cargar y filtrar reviews
@st.cache_data(show_spinner=False)
def cargar_reviews(num_reviews=10000):
    """Carga y filtra reviews del dataset de Amazon"""
    
    keywords = ["ceramic tile", "tiles", "ceramic", "vinyl floor"]
    
    st.info(f"🔄 Cargando reviews de Amazon Home and Kitchen...")
    
    ds = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        "raw_review_Home_and_Kitchen",
        split="full",
        streaming=True,
        trust_remote_code=True,
    )
    
    reviews = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, item in enumerate(ds):
        if len(reviews) >= num_reviews:
            break
        
        text = str(item.get("text", "")).lower()
        title = str(item.get("title", "")).lower()
        
        # Filtrar por keywords
        if any(keyword.lower() in text or keyword.lower() in title for keyword in keywords):
            reviews.append(item)
            
            # Actualizar progreso cada 100 reviews
            if len(reviews) % 100 == 0:
                progress = len(reviews) / num_reviews
                progress_bar.progress(min(progress, 1.0))
                status_text.text(f"Reviews cargadas: {len(reviews):,} / {num_reviews:,}")
    
    progress_bar.progress(1.0)
    status_text.text(f"✅ {len(reviews):,} reviews cargadas correctamente")
    
    df = pd.DataFrame(reviews)[["title", "text", "rating", "parent_asin"]].dropna(subset=["text"])
    df["rating"] = df["rating"].astype(int)
    
    return df

# Función para crear el índice vectorial
@st.cache_resource(show_spinner=False)
def crear_vectorstore(_df, _api_key):
    """Crea el índice vectorial en ChromaDB"""
    
    st.info("🔄 Generando embeddings y creando índice vectorial...")
    
    # Configurar embeddings de Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=_api_key
    )
    
    # Convertir a Documents
    docs = [
        Document(
            page_content=f"{row['title']}\n\n{row['text']}",
            metadata={
                "rating": int(row["rating"]),
                "parent_asin": row["parent_asin"]
            }
        )
        for _, row in _df.iterrows()
    ]
    
    # Crear vectorstore con barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # ChromaDB procesa en batches, mostramos progreso estimado
    total_docs = len(docs)
    batch_size = 100
    
    vectorstore = Chroma.from_documents(
        docs, 
        embeddings,
        collection_name="ceramic_tiles_reviews"
    )
    
    progress_bar.progress(1.0)
    status_text.text(f"✅ Índice vectorial creado: {vectorstore._collection.count():,} vectores")
    
    return vectorstore

# Función para crear la cadena RAG
def crear_rag_chain(vectorstore, api_key, k=5):
    """Crea la cadena RAG completa"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=api_key,
        temperature=0.3
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    
    prompt_rag = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente experto en análisis de productos para el hogar, especialmente baldosas cerámicas, azulejos y pisos de vinilo.

Responde usando SOLO la información de las siguientes reviews de clientes reales de Amazon.
Si la información no aparece en las reviews, dilo explícitamente.
Cita ejemplos concretos de las reviews cuando sea relevante, mencionando el rating.

Reviews recuperadas:
{context}"""),
        ("human", "{question}")
    ])
    
    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[Rating: {d.metadata.get('rating', '?')}★]\n{d.page_content[:500]}"
            for d in docs
        )
    
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

if not api_key:
    st.warning("⚠️ Por favor, introduce tu Google API Key en la barra lateral")
    st.stop()

# Inicializar estado de sesión
if 'df' not in st.session_state:
    st.session_state.df = None
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None

# Sección 1: Carga de datos
st.header("📥 1. Carga de Datos")

col1, col2 = st.columns([3, 1])
with col1:
    num_reviews = st.slider(
        "Número de reviews a cargar",
        min_value=1000,
        max_value=10000,
        value=10000,
        step=1000
    )

with col2:
    if st.button("🔄 Cargar Reviews", type="primary", use_container_width=True):
        st.session_state.df = None
        st.session_state.vectorstore = None
        st.session_state.rag_chain = None

# Cargar datos
if st.session_state.df is None:
    with st.spinner("Cargando reviews..."):
        st.session_state.df = cargar_reviews(num_reviews)

df = st.session_state.df

# Mostrar estadísticas
if df is not None:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Reviews", f"{len(df):,}")
    
    with col2:
        avg_rating = df['rating'].mean()
        st.metric("⭐ Rating Promedio", f"{avg_rating:.2f}")
    
    with col3:
        products = df['parent_asin'].nunique()
        st.metric("📦 Productos Únicos", f"{products:,}")
    
    with col4:
        rating_5 = (df['rating'] == 5).sum()
        pct_5 = (rating_5 / len(df)) * 100
        st.metric("🌟 Reviews 5★", f"{pct_5:.1f}%")
    
    # Distribución de ratings
    st.subheader("📊 Distribución de Ratings")
    rating_counts = df['rating'].value_counts().sort_index()
    st.bar_chart(rating_counts)
    
    # Muestra de reviews
    with st.expander("👀 Ver muestra de reviews"):
        st.dataframe(
            df[['rating', 'title', 'text']].head(10),
            use_container_width=True
        )

# Sección 2: Creación del índice vectorial
st.header("🔍 2. Índice Vectorial")

if st.button("🚀 Crear Índice Vectorial", type="primary", disabled=(df is None)):
    with st.spinner("Generando embeddings y creando índice..."):
        st.session_state.vectorstore = crear_vectorstore(df, api_key)
        st.session_state.rag_chain = None  # Reset RAG chain

if st.session_state.vectorstore is not None:
    st.success(f"✅ Índice vectorial listo con {st.session_state.vectorstore._collection.count():,} vectores")
    
    # Crear RAG chain
    if st.session_state.rag_chain is None:
        num_docs = st.sidebar.slider(
            "📄 Documentos a recuperar",
            min_value=3,
            max_value=10,
            value=5,
            help="Número de reviews más relevantes para el contexto"
        )
        st.session_state.rag_chain, st.session_state.retriever = crear_rag_chain(
            st.session_state.vectorstore,
            api_key,
            k=num_docs
        )

# Sección 3: Consultas RAG
if st.session_state.rag_chain is not None:
    st.header("💬 3. Consultas con RAG")
    
    # Preguntas predefinidas
    st.subheader("🎯 Preguntas Sugeridas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 ¿Qué problemas tienen las baldosas cerámicas?"):
            st.session_state.pregunta = "¿Qué problemas comunes tienen las baldosas cerámicas según los clientes?"
        
        if st.button("⚙️ ¿Dificultades con la instalación?"):
            st.session_state.pregunta = "¿Los clientes mencionan problemas con la instalación?"
        
        if st.button("💪 ¿Opiniones sobre durabilidad?"):
            st.session_state.pregunta = "¿Qué baldosas tienen mejor valoración en durabilidad?"
    
    with col2:
        if st.button("🎨 ¿Calidad del material cerámico?"):
            st.session_state.pregunta = "¿Qué opinan sobre la calidad del material cerámico?"
        
        if st.button("🏠 ¿Diferencias cocina vs baño?"):
            st.session_state.pregunta = "¿Qué productos recomiendan para cocinas vs baños?"
        
        if st.button("✨ ¿Baldosas autoadhesivas valen la pena?"):
            st.session_state.pregunta = "¿Vale la pena comprar baldosas cerámicas autoadhesivas según los clientes?"
    
    st.markdown("---")
    
    # Input personalizado
    st.subheader("✍️ Pregunta Personalizada")
    
    pregunta_input = st.text_area(
        "Escribe tu pregunta:",
        value=st.session_state.get('pregunta', ''),
        height=100,
        placeholder="Ejemplo: ¿Qué dicen los clientes sobre la resistencia al agua de las baldosas?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        consultar = st.button("🔍 Consultar", type="primary", use_container_width=True)
    
    if consultar and pregunta_input:
        with st.spinner("🤔 Analizando reviews..."):
            # Recuperar documentos
            docs_recuperados = st.session_state.retriever.invoke(pregunta_input)
            
            # Generar respuesta
            respuesta = st.session_state.rag_chain.invoke(pregunta_input)
            
            # Mostrar respuesta
            st.subheader("💡 Respuesta")
            st.markdown(f"**Pregunta:** {pregunta_input}")
            st.info(respuesta)
            
            # Mostrar documentos recuperados
            with st.expander(f"📄 Ver {len(docs_recuperados)} reviews recuperadas"):
                for i, doc in enumerate(docs_recuperados, 1):
                    rating = doc.metadata.get('rating', '?')
                    st.markdown(f"**Review {i}** — Rating: {rating}⭐")
                    st.text(doc.page_content[:400] + "...")
                    st.markdown("---")
            
            # Opción de comparación sin RAG
            with st.expander("🔄 Comparar con respuesta SIN RAG"):
                llm_sin_rag = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=api_key
                )
                respuesta_sin_rag = llm_sin_rag.invoke(pregunta_input)
                st.warning("**Respuesta sin contexto (conocimiento general):**")
                st.write(respuesta_sin_rag.content)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📚 <strong>Sesión 2 - ISDI MDA</strong> | Curso de IA Generativa</p>
    <p>🔧 Sistema RAG para análisis de reviews de productos del hogar</p>
</div>
""", unsafe_allow_html=True)
