import streamlit as st
import google.generativeai as genai
import sys

st.title("🛠️ Diagnóstico del Sistema")

# 1. Verificación de la API Key
api_key = st.sidebar.text_input("Pega tu API Key aquí", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    st.write("---")
    st.subheader("1. Versión de la Librería")
    # Esto nos dirá si el servidor nos hizo caso o sigue con la versión vieja
    try:
        version = genai.__version__
        st.info(f"Versión instalada de Google-GenerativeAI: **{version}**")
        
        if version < "0.5.0":
            st.error("❌ ALERTA: La versión es demasiado antigua. El servidor no ha actualizado.")
        else:
            st.success("✅ La versión es correcta (Moderna).")
            
    except Exception as e:
        st.error(f"No se pudo determinar la versión: {e}")

    st.write("---")
    st.subheader("2. Modelos Disponibles")
    st.write("Intentando conectar con Google para ver qué modelos nos permite usar tu clave...")
    
    try:
        # Esto lista lo que REALMENTE está disponible
        modelos = genai.list_models()
        encontrados = []
        for m in modelos:
            if 'generateContent' in m.supported_generation_methods:
                encontrados.append(m.name)
                st.code(m.name)
        
        if not encontrados:
            st.warning("⚠️ No se encontraron modelos. Verifica si tu API Key es correcta.")
        else:
            st.success(f"✅ Se encontraron {len(encontrados)} modelos disponibles.")
            
    except Exception as e:
        st.error(f"❌ Error crítico conectando con Google: {e}")

else:
    st.info("👈 Pega tu API Key en la izquierda para iniciar el diagnóstico.")
