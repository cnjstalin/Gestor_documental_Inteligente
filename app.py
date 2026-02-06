import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente DINIC - Quipux", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    # Captura la API Key de forma segura
    api_key = st.text_input("Ingresa tu Gemini API Key", type="password")
    st.info("Modelo activo: gemini-2.0-flash")

# --- LÓGICA PRINCIPAL ---
st.title("📂 Analizador de Documentación Oficial (Quipux)")
st.markdown("""
**Sistema Inteligente de Gestión Documental**
Sube un Oficio, Circular o Memorando para obtener:
1.  **Resumen Ejecutivo**
2.  **Departamento de Destino** (Derivación)
3.  **Borrador de Respuesta**
""")

uploaded_file = st.file_uploader("Sube el archivo PDF aquí", type=['pdf'])

if uploaded_file is not None and api_key:
    try:
        # Configurar la IA con la clave
        genai.configure(api_key=api_key)
        
        # Botón de acción
        if st.button("🚀 Analizar Documento"):
            with st.spinner("Procesando con Gemini 2.0..."):
                
                # 1. Gestión del archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # 2. Subir archivo a la nube de Google (Capa de visión)
                file_upload = genai.upload_file(path=tmp_path, display_name="Doc Quipux")
                
                # 3. EL CEREBRO (Aquí usamos el modelo que SÍ tienes)
                model = genai.GenerativeModel('gemini-flash-latest')

                # 4. LAS INSTRUCCIONES (Prompt)
                # Aquí es donde pondremos tus reglas específicas luego
                prompt = """
                Actúa como un Analista Senior de Gestión Documental de la DINIC.
                Tu trabajo es procesar el documento adjunto y generar un reporte técnico.

                ESTRUCTURA DE RESPUESTA REQUERIDA:

                ### 1. SÍNTESIS DEL DOCUMENTO
                - **Remitente:** (Nombre y Cargo)
                - **Asunto Central:** (Resumen en 1 línea)
                - **Prioridad Detectada:** (Alta/Media/Baja según el tono y plazos)

                ### 2. ANÁLISIS DE DERIVACIÓN (Lógica Interna)
                - ¿A qué área debe ir este trámite? (Opciones: Jurídica, Talento Humano, Inteligencia, Administrativo, Archivo).
                - **Justificación:** ¿Por qué lo envías ahí?

                ### 3. BORRADOR DE RESPUESTA SUGERIDA
                - Redacta el texto formal para responder en Quipux.
                - Usa un tono institucional ("De mi consideración...", "Por disposición del Sr. Director...").
                - Deja espacios en blanco [___] para datos variables.
                """

                # 5. Generar contenido
                response = model.generate_content([prompt, file_upload])
                
                # 6. Mostrar resultados
                st.success("✅ Análisis Finalizado")
                st.markdown(response.text)

                # Limpieza
                os.remove(tmp_path)

    except Exception as e:
        st.error(f"Ocurrió un error técnico: {e}")

elif not api_key:
    st.warning("👈 Por favor, ingresa tu API Key en el menú de la izquierda para activar el sistema.")
