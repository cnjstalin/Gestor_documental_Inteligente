import streamlit as st
import google.generativeai as genai
import os
import json
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="S.I.G.D. DINIC - Conexión", layout="wide")

# --- 1. VALIDACIÓN DE LLAVE ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 FALTA LA LLAVE: Ve a Settings > Secrets y pega tu GEMINI_API_KEY.")
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- 2. FUNCIÓN LLAVE MAESTRA (Prueba modelos hasta conectar) ---
def conectar_ia_robusta():
    # Lista de nombres técnicos posibles. Probará uno por uno.
    candidatos = [
        "gemini-1.5-flash-001",  # Nombre técnico exacto (A veces el alias falla)
        "gemini-1.5-flash",      # Alias común
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",        # Versión potente
        "gemini-pro"             # Versión antigua (reserva final)
    ]
    
    log = []
    
    for modelo in candidatos:
        try:
            # Intenta conectar
            test_model = genai.GenerativeModel(modelo)
            # Prueba de fuego: Generar un "Hola" simple
            respuesta = test_model.generate_content("Test de conexión.")
            
            # Si llega aquí, FUNCIONÓ. Devolvemos este modelo.
            return test_model, modelo, log
            
        except Exception as e:
            # Si falla, anotamos el error y pasamos al siguiente
            log.append(f"❌ {modelo}: {str(e)}")
            continue
            
    # Si todos fallan
    return None, None, log

# --- 3. INTERFAZ ---
st.title("👮‍♂️ S.I.G.D. - Diagnóstico y Reparación")

with st.spinner("🔄 Probando llaves de acceso con Google..."):
    modelo_activo, nombre_modelo, historial = conectar_ia_robusta()

if modelo_activo:
    st.success(f"✅ ¡CONEXIÓN ESTABLECIDA! Modelo conectado: {nombre_modelo}")
    st.info("El sistema ya encontró el modelo correcto para tu cuenta. Procederemos a cargar la interfaz completa.")
    
    # AQUÍ IRÍA TU SISTEMA (Simulado para prueba)
    if st.button("🚔 Probar Generación de Informe"):
        res = modelo_activo.generate_content("Actúa como policía y di: 'Sistema operativo y sin novedades'.")
        st.write(f"**Respuesta:** {res.text}")

else:
    st.error("⚠️ NO SE PUDO CONECTAR. Aquí está el reporte técnico:")
    for linea in historial:
        st.text(linea)
        
    st.warning("🔍 SOLUCIÓN: Si ves error 404 en todos, tu API KEY podría no tener permisos habilitados. Crea una nueva en aistudio.google.com")
