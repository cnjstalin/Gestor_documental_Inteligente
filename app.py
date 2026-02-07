import streamlit as st
import google.generativeai as genai
import os
import json
import time

st.set_page_config(page_title="S.I.G.D. DINIC - FINAL", layout="wide")

# --- 1. AUTENTICACIÓN ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 ERROR: No hay llave en Secrets.")
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error de llave: {e}")
    st.stop()

# --- 2. BUSCADOR AUTOMÁTICO DE MODELOS ---
def obtener_modelo_disponible():
    st.info("📡 Escaneando modelos disponibles para tu Llave Nueva...")
    try:
        # Preguntamos a Google qué modelos permite usar tu llave
        listado = genai.list_models()
        modelos_vistos = []
        
        for m in listado:
            modelos_vistos.append(m.name)
            # Buscamos si tu llave tiene acceso a Flash o Pro
            if 'flash' in m.name or 'pro' in m.name:
                if 'generateContent' in m.supported_generation_methods:
                    return m.name # ¡Encontrado!
        
        # Si no encuentra ninguno específico, devolvemos el primero que sirva
        st.warning(f"Modelos vistos: {modelos_vistos}")
        return "gemini-1.5-flash" # Intento forzoso
        
    except Exception as e:
        st.error(f"❌ Tu llave nueva tampoco funciona. Error: {e}")
        return None

# --- 3. INICIO DEL SISTEMA ---
st.title("👮‍♂️ S.I.G.D. - PRUEBA FINAL")

if st.button("🚔 INICIAR CONEXIÓN"):
    nombre_modelo = obtener_modelo_disponible()
    
    if nombre_modelo:
        try:
            model = genai.GenerativeModel(nombre_modelo)
            response = model.generate_content("¡Reporte de estado!")
            
            st.success(f"✅ ¡ÉXITO TOTAL! Conectado usando: {nombre_modelo}")
            st.balloons()
            st.write(f"🤖 La IA dice: {response.text}")
            st.success("YA PUEDES PEGAR EL CÓDIGO COMPLETO DE LA MATRIZ. EL PROBLEMA ESTÁ RESUELTO.")
            
        except Exception as e:
            st.error(f"Falló al conectar con {nombre_modelo}: {e}")
