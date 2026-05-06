"""
Prueba directa del SDK de Google Gemini sin LangChain
"""
import google.generativeai as genai

def test_direct_api():
    api_key = "AIzaSyC_TztBmFF_Ot24MYbvoMKNK-s3enc0Wrs"
    
    print("🔍 Probando Google Gemini API directamente...")
    
    # Configurar API
    genai.configure(api_key=api_key)
    
    # Listar modelos disponibles
    print("\n📋 Modelos disponibles:")
    try:
        for model in genai.list_models():
            if 'embed' in model.name.lower() or 'embedding' in model.name.lower():
                print(f"   🎯 {model.name}")
                print(f"      Métodos soportados: {model.supported_generation_methods}")
    except Exception as e:
        print(f"   ❌ Error listando modelos: {e}")
    
    # Intentar usar embeddings con diferentes modelos
    print("\n🧪 Probando embedContent:")
    models_to_try = [
        "models/gemini-embedding-001",
        "models/gemini-embedding-2",
        "models/embedding-001",
        "models/text-embedding-004",
        "embedding-001",
    ]
    
    for model_name in models_to_try:
        try:
            print(f"\n   Probando: {model_name}")
            result = genai.embed_content(
                model=model_name,
                content="This is a test"
            )
            print(f"   ✅ ¡FUNCIONA! Dimension: {len(result['embedding'])}")
            print(f"   Primeros valores: {result['embedding'][:5]}")
            return model_name
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"   ❌ No disponible (404)")
            else:
                print(f"   ❌ Error: {error_msg[:150]}")
    
    return None

if __name__ == "__main__":
    working_model = test_direct_api()
    if working_model:
        print(f"\n✅ Modelo correcto encontrado: {working_model}")
    else:
        print("\n❌ No se encontró un modelo funcional")
