"""
Script de prueba para verificar embeddings de Google Gemini
"""
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def test_embeddings():
    # API Key
    api_key = "AIzaSyC_TztBmFF_Ot24MYbvoMKNK-s3enc0Wrs"
    
    print("🔍 Probando embeddings de Google Gemini...")
    print(f"API Key: {api_key[:20]}...")
    
    # Lista de modelos a probar
    models_to_test = [
        "models/gemini-embedding-001",
        "models/gemini-embedding-2",
        "models/text-embedding-004",
        "text-embedding-004",
        "models/embedding-001",
        "embedding-001",
        "models/text-embedding-latest",
    ]
    
    test_text = ["This is a test"]
    
    for model_name in models_to_test:
        try:
            print(f"\n🧪 Probando: {model_name}")
            embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key=api_key
            )
            
            result = embeddings.embed_documents(test_text)
            print(f"   ✅ ¡FUNCIONA! Dimension: {len(result[0])}")
            print(f"   Primeros valores: {result[0][:5]}")
            print(f"\n✨ MODELO CORRECTO: {model_name}")
            return model_name
            
        except Exception as e:
            error_msg = str(e)
            if "NOT_FOUND" in error_msg or "404" in error_msg:
                print(f"   ❌ No disponible")
            else:
                print(f"   ❌ Error: {error_msg[:100]}")
    
    return None

if __name__ == "__main__":
    working_model = test_embeddings()
    if working_model:
        print(f"\n✅ ChromaDB es compatible - El problema era el nombre del modelo")
        print(f"✅ Usa este modelo en la app: {working_model}")
    else:
        print("\n❌ Ningún modelo de embeddings funciona - verificar API key o permisos")
