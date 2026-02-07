import streamlit as st
import google.generativeai as genai
import os
import json
import io
import re
import time
import pandas as pd
from datetime import datetime

# --- 1. VERIFICACIÓN DE VERSIÓN (EL CHIVATO) ---
version_actual = genai.__version__

st.set_page_config(page_title=f"S.I.G.D. (v{version_actual})", layout="wide")

# Si la versión es vieja, avisamos y paramos todo.
if version_actual < "0.8.3":
    st.error(f"🚨 ERROR CRÍTICO DE SERVIDOR: Estás usando la versión {version_actual} de la librería.")
    st.error("SOLUCIÓN: Ve a 'requirements.txt', agrega una línea vacía al final y guarda para forzar la actualización.")
    st.stop()

# --- 2. CONEXIÓN DIRECTA (SIN VUELTAS) ---
try:
    # Busca la clave en los secretos
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 FALTA LA LLAVE: Ve a Settings > Secrets y pega tu GEMINI_API_KEY.")
        st.stop()
        
    genai.configure(api_key=api_key)
    
    # CONFIGURACIÓN DIRECTA AL ÚNICO MODELO QUE FUNCIONA
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    st.success(f"✅ SISTEMA OPERATIVO | Motor: Gemini 1.5 Flash | Librería: v{version_actual}")
    
except Exception as e:
    st.error(f"❌ Error de Conexión: {e}")
    st.stop()

# --- 3. INTERFAZ SIMPLE DE PRUEBA ---
st.title("👮‍♂️ S.I.G.D. DINIC - Panel de Control")

st.info("Si ves el mensaje verde arriba, el sistema ya está conectado y listo para trabajar el lunes.")

# Prueba rápida
if st.button("🚔 Probar Conexión con IA"):
    try:
        response = model.generate_content("Responde solo con: '¡Comandante, el sistema está listo!'")
        st.balloons()
        st.markdown(f"### 🤖 Respuesta de la IA:\n**{response.text}**")
    except Exception as e:
        st.error(f"Error al generar: {e}")
