import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente DINIC - Quipux", layout="wide")

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración Maestra")
    api_key = st.text_input("Ingresa tu Gemini API Key", type="password")
    st.warning("⚠️ Sistema de uso interno. No subir documentos clasificados como SECRETOS.")

# --- LÓGICA PRINCIPAL ---
st.title("📂 Analizador de Documentación Oficial (Quipux)")
st.markdown("""
Sube el Oficio, Memo o Circular. El sistema analizará:
1. **Síntesis:** De qué trata.
2. **Derivación:** A qué departamento corresponde.
3. **Respuesta:** Borrador de oficio de contestación.
""")

# Carga de Archivo
uploaded_file = st.file_uploader("Sube el archivo (PDF)", type=['pdf'])

if uploaded_file is not None and api_key:
    genai.configure(api_key=api_key)
    
    if st.button("🚀 Analizar Documento con IA"):
        with st.spinner("Leyendo documento y redactando respuesta..."):
            try:
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # Subir a Gemini
                file_upload = genai.upload_file(path=tmp_path, display_name="Documento Quipux")
                
                # El Cerebro (Modelo)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')

                # El Prompt
                prompt = """
                Actúa como un Secretario Experto de la DINIC. Analiza este documento adjunto.
                
                TAREA 1: IDENTIFICACIÓN
                - Resume el pedido principal en 1 frase.
                - Identifica el remitente y el grado jerárquico.

                TAREA 2: DERIVACIÓN (LOGICA)
                - Basado en el contenido, ¿a qué departamento interno debería enviarse esto para su trámite? (Ej: Asesoría Jurídica, Administrativo, Inteligencia, RRHH). Explica por qué.

                TAREA 3: RESPUESTA FORMAL
                - Redacta el borrador del Oficio de respuesta o el comentario de reasignación en Quipux.
                - Usa un tono formal, institucional y respetuoso ("De mi consideración...").
                """

                # Generar
                response = model.generate_content([prompt, file_upload])
                
                st.success("✅ Análisis Completado")
                st.write(response.text)

                # Limpieza
                os.remove(tmp_path)

            except Exception as e:
                st.error(f"Error: {e}")

elif not api_key:
    st.info("👈 Por favor, ingresa la API Key en la barra lateral para iniciar.")
