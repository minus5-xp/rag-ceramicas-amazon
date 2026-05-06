"""
Script para extraer reviews de Amazon desde MySQL local
Busca reviews relacionadas con 'ceramic tiles' y 'vinyl flooring'
"""
import pymysql
import pandas as pd
from sqlalchemy import create_engine, text
import sys

# Configuración de conexión MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'amazon_reviews',
    'charset': 'utf8mb4'
}

def conectar_mysql():
    """Conecta a MySQL y retorna el engine de SQLAlchemy"""
    try:
        print(f"🔌 Conectando a MySQL en {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        print(f"   Base de datos: {DB_CONFIG['database']}")
        
        # Crear connection string
        connection_string = (
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            f"?charset={DB_CONFIG['charset']}"
        )
        
        engine = create_engine(connection_string)
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"   ✅ Conectado a MySQL versión: {version}")
        
        return engine
        
    except Exception as e:
        print(f"   ❌ Error conectando a MySQL: {e}")
        return None

def listar_tablas(engine):
    """Lista las tablas disponibles en la base de datos"""
    try:
        print("\n📋 Tablas disponibles en la base de datos:")
        
        query = "SHOW TABLES"
        with engine.connect() as conn:
            result = conn.execute(text(query))
            tablas = [row[0] for row in result]
            
            if tablas:
                for tabla in tablas:
                    print(f"   • {tabla}")
                return tablas
            else:
                print("   (No se encontraron tablas)")
                return []
                
    except Exception as e:
        print(f"   ❌ Error listando tablas: {e}")
        return []

def inspeccionar_estructura_tabla(engine, tabla_name):
    """Muestra la estructura de una tabla"""
    try:
        print(f"\n🔍 Estructura de la tabla '{tabla_name}':")
        
        query = f"DESCRIBE {tabla_name}"
        with engine.connect() as conn:
            result = conn.execute(text(query))
            columnas = result.fetchall()
            
            for col in columnas:
                print(f"   • {col[0]} ({col[1]})")
            
            # Contar registros
            count_query = f"SELECT COUNT(*) FROM {tabla_name}"
            result = conn.execute(text(count_query))
            count = result.fetchone()[0]
            print(f"\n   Total de registros: {count:,}")
            
            return [col[0] for col in columnas]
            
    except Exception as e:
        print(f"   ❌ Error inspeccionando tabla: {e}")
        return []

def buscar_columnas_texto(engine, tabla_name):
    """Encuentra columnas de texto en la tabla"""
    query = f"""
    SELECT COLUMN_NAME, DATA_TYPE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}' 
    AND TABLE_NAME = '{tabla_name}'
    AND DATA_TYPE IN ('varchar', 'text', 'longtext', 'mediumtext', 'tinytext')
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return [(row[0], row[1]) for row in result]

def extraer_reviews(engine, tabla_name, num_reviews=None):
    """Extrae reviews filtradas por keywords de la tabla"""
    
    print(f"\n🔍 Buscando reviews en tabla '{tabla_name}'...")
    
    if num_reviews:
        print(f"   Límite: {num_reviews} reviews")
    else:
        print(f"   SIN LÍMITE - extrayendo todas las reviews relevantes")
    
    # Inspeccionar columnas
    columnas = inspeccionar_estructura_tabla(engine, tabla_name)
    
    if not columnas:
        print("❌ No se pudo obtener la estructura de la tabla")
        return None
    
    # Buscar columnas de texto
    columnas_texto = buscar_columnas_texto(engine, tabla_name)
    print(f"\n📝 Columnas de texto encontradas: {[col[0] for col in columnas_texto]}")
    
    # Intentar identificar columnas relevantes
    col_title = None
    col_text = None
    col_rating = None
    col_asin = None
    
    # Buscar columnas por nombre común
    for col in columnas:
        col_lower = col.lower()
        if 'title' in col_lower and not col_title:
            col_title = col
        elif 'text' in col_lower or 'review' in col_lower or 'content' in col_lower:
            col_text = col
        elif 'rating' in col_lower or 'score' in col_lower or 'stars' in col_lower:
            col_rating = col
        elif 'asin' in col_lower or 'product' in col_lower:
            col_asin = col
    
    print(f"\n🎯 Columnas identificadas:")
    print(f"   • Title: {col_title}")
    print(f"   • Text: {col_text}")
    print(f"   • Rating: {col_rating}")
    print(f"   • ASIN: {col_asin}")
    
    if not col_text:
        print("\n❌ No se pudo identificar la columna de texto de reviews")
        print("💡 Mostrando primeros registros para inspección manual:")
        
        query = f"SELECT * FROM {tabla_name} LIMIT 5"
        df_sample = pd.read_sql(query, engine)
        print(df_sample)
        return None
    
    # Construir query de búsqueda - usar keywords específicas
    keywords_principales = ['ceramic tiles', 'vinyl flooring', 'ceramic tile', 'vinyl floor']
    keywords_secundarias = ['tile', 'tiles', 'ceramic', 'vinyl', 'grout']
    
    # Seleccionar columnas
    select_cols = []
    col_map = {}
    
    if col_title:
        select_cols.append(col_title)
        col_map['title'] = col_title
    if col_text:
        select_cols.append(col_text)
        col_map['text'] = col_text
    if col_rating:
        select_cols.append(col_rating)
        col_map['rating'] = col_rating
    if col_asin:
        select_cols.append(col_asin)
        col_map['parent_asin'] = col_asin
    
    if not select_cols:
        print("❌ No se pudieron identificar las columnas necesarias")
        return None
    
    # Construir condiciones WHERE - priorizar keywords principales
    condiciones_principales = []
    for keyword in keywords_principales:
        if col_text:
            condiciones_principales.append(f"{col_text} LIKE '%%{keyword}%%'")
        if col_title:
            condiciones_principales.append(f"{col_title} LIKE '%%{keyword}%%'")
    
    condiciones_secundarias = []
    for keyword in keywords_secundarias:
        if col_text:
            condiciones_secundarias.append(f"{col_text} LIKE '%%{keyword}%%'")
        if col_title:
            condiciones_secundarias.append(f"{col_title} LIKE '%%{keyword}%%'")
    
    # Primero intentar con keywords principales
    where_clause_principal = " OR ".join(condiciones_principales)
    where_clause_secundario = " OR ".join(condiciones_secundarias)
    
    limit_clause = f"LIMIT {num_reviews}" if num_reviews else ""
    
    query = f"""
    SELECT {', '.join(select_cols)}
    FROM {tabla_name}
    WHERE ({where_clause_principal}) OR ({where_clause_secundario})
    {limit_clause}
    """
    
    print(f"\n📊 Ejecutando búsqueda...")
    print(f"   Keywords principales: {keywords_principales}")
    print(f"   Keywords secundarias: {keywords_secundarias}")
    if num_reviews:
        print(f"   Límite: {num_reviews} reviews")
    else:
        print(f"   SIN LÍMITE - extrayendo todas las reviews que coincidan")
    
    try:
        df = pd.read_sql(query, engine)
        
        # Renombrar columnas al formato esperado
        rename_map = {}
        for standard_name, db_col in col_map.items():
            if db_col in df.columns:
                rename_map[db_col] = standard_name
        
        df = df.rename(columns=rename_map)
        
        # Asegurar que tenemos las columnas necesarias
        if 'title' not in df.columns:
            df['title'] = ''
        if 'rating' not in df.columns:
            df['rating'] = 5
        if 'parent_asin' not in df.columns:
            df['parent_asin'] = [f'B{i:05d}' for i in range(len(df))]
        
        # Limpiar datos
        df = df.dropna(subset=['text'])
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(5).astype(int)
        
        print(f"\n✅ Encontradas {len(df)} reviews")
        
        return df
        
    except Exception as e:
        print(f"\n❌ Error ejecutando query: {e}")
        print(f"\nQuery intentada:\n{query}")
        return None

def exportar_a_csv(df, filename="ceramic_tiles_reviews.csv"):
    """Exporta el DataFrame a CSV"""
    
    if df is None or len(df) == 0:
        print("❌ No hay datos para exportar")
        return False
    
    print(f"\n💾 Exportando a {filename}...")
    df.to_csv(filename, index=False, encoding="utf-8")
    
    print(f"✅ Exportado exitosamente")
    print(f"\n📊 Estadísticas:")
    print(f"   • Total de reviews: {len(df)}")
    
    if 'rating' in df.columns:
        print(f"   • Distribución de ratings:")
        for rating in sorted(df['rating'].unique()):
            count = len(df[df['rating'] == rating])
            print(f"      {rating}★: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n📝 Ejemplo de review:")
    sample = df.iloc[0]
    if 'rating' in sample:
        print(f"   Rating: {sample['rating']}★")
    if 'title' in sample:
        print(f"   Title: {str(sample['title'])[:80]}")
    if 'text' in sample:
        print(f"   Text: {str(sample['text'])[:150]}...")
    
    return True

if __name__ == "__main__":
    try:
        # Conectar a MySQL
        engine = conectar_mysql()
        
        if not engine:
            print("\n❌ No se pudo conectar a MySQL")
            sys.exit(1)
        
        # Listar tablas
        tablas = listar_tablas(engine)
        
        if not tablas:
            print("\n❌ No se encontraron tablas en la base de datos")
            sys.exit(1)
        
        # Si hay una tabla que parece ser de reviews, usarla
        tabla_reviews = None
        for tabla in tablas:
            if 'review' in tabla.lower():
                tabla_reviews = tabla
                break
        
        # Si no, usar la primera tabla
        if not tabla_reviews:
            print(f"\n💡 No se encontró tabla con nombre 'review', usando primera tabla: {tablas[0]}")
            tabla_reviews = tablas[0]
        else:
            print(f"\n✅ Usando tabla: {tabla_reviews}")
        
        # Extraer reviews - Número grande pero manejable (50K reviews)
        print("\n🎯 Extrayendo reviews relevantes (50,000 máximo - óptimo para RAG)...")
        df = extraer_reviews(engine, tabla_reviews, num_reviews=50000)
        
        # Exportar a CSV
        if df is not None:
            exportar_a_csv(df)
            print("\n🎉 ¡Listo! Ahora puedes usar ceramic_tiles_reviews.csv en la app de Streamlit")
        else:
            print("\n❌ No se pudieron extraer las reviews")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
