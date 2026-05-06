"""
Script para descargar reviews reales de Amazon Home & Kitchen
filtradas por keywords de ceramic tiles y exportarlas a CSV
"""
import os
# Desactivar PyTorch para evitar errores de DLL
os.environ["TRANSFORMERS_OFFLINE"] = "0"
os.environ["HF_DATASETS_OFFLINE"] = "0"

from datasets import load_dataset
import pandas as pd

def descargar_reviews(num_reviews=1500):
    """Descarga reviews de Amazon filtradas por keywords de ceramic tiles"""
    
    print("🔍 Cargando dataset de Amazon Home and Kitchen...")
    print("⚠️ Esto puede tardar varios minutos dependiendo de tu conexión...")
    
    ds = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        "raw_review_Home_and_Kitchen",
        split="full",
        streaming=True,
        trust_remote_code=True,
    )

    # Keywords relacionadas con baldosas cerámicas y pisos
    keywords = ["tile", "tiles", "ceramic", "grout", "bathroom", "kitchen", "floor", "wall", "vinyl"]
    
    print(f"\n🎯 Buscando reviews con keywords: {keywords}")
    print(f"📊 Objetivo: {num_reviews} reviews")
    
    reviews = []
    processed_count = 0
    
    for item in ds:
        processed_count += 1
        
        if len(reviews) >= num_reviews:
            break
        
        text = str(item.get("text", "")).lower()
        title = str(item.get("title", "")).lower()
        
        # Incluir si contiene alguna palabra clave
        if any(keyword in text or keyword in title for keyword in keywords):
            reviews.append({
                "title": item.get("title", ""),
                "text": item.get("text", ""),
                "rating": item.get("rating", 0),
                "parent_asin": item.get("parent_asin", "")
            })
            
            # Mostrar progreso cada 100 reviews encontradas
            if len(reviews) % 100 == 0:
                print(f"   ✓ {len(reviews)} reviews encontradas (procesadas {processed_count})...")
    
    print(f"\n✅ {len(reviews)} reviews encontradas")
    
    # Crear DataFrame
    df = pd.DataFrame(reviews)
    df = df.dropna(subset=["text"])
    df["rating"] = df["rating"].astype(int)
    
    return df

def exportar_a_csv(df, filename="ceramic_tiles_reviews.csv"):
    """Exporta el DataFrame a CSV"""
    
    print(f"\n💾 Exportando a {filename}...")
    df.to_csv(filename, index=False, encoding="utf-8")
    
    print(f"✅ Exportado exitosamente")
    print(f"\n📊 Estadísticas:")
    print(f"   • Total de reviews: {len(df)}")
    print(f"   • Distribución de ratings:")
    for rating in sorted(df['rating'].unique()):
        count = len(df[df['rating'] == rating])
        print(f"      {rating}★: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n📝 Ejemplo de review:")
    sample = df.iloc[0]
    print(f"   Rating: {sample['rating']}★")
    print(f"   Title: {sample['title'][:80]}...")
    print(f"   Text: {sample['text'][:150]}...")

if __name__ == "__main__":
    try:
        # Descargar 1500 reviews
        df = descargar_reviews(num_reviews=1500)
        
        # Exportar a CSV
        exportar_a_csv(df)
        
        print("\n🎉 ¡Listo! Ahora puedes usar ceramic_tiles_reviews.csv en la app de Streamlit")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Si ves un error de PyTorch, es un problema conocido.")
        print("   La app seguirá funcionando con los datos de ejemplo.")
