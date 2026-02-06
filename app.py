import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Documental DINIC", layout="wide", page_icon="⚖️")

# --- GESTIÓN DE CREDENCIALES (SECRETS) ---
try:
    # Busca la clave en los secretos de Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY en los Secretos.")
    sistema_activo = False

# --- INTERFAZ LATERAL ---
with st.sidebar:
    st.title("Panel de Control")
    st.success("🟢 Sistema En Línea")
    
    # Opciones de departamentos
    dept_options = [
        "Dirección General",
        "Asesoría Jurídica",
        "Talento Humano",
        "Inteligencia e Investigación",
        "Operaciones",
        "Archivo General",
        "Logística y Financiero"
    ]
    st.write("---")

# --- LÓGICA PRINCIPAL ---
st.title("🏛️ Gestión Documental Inteligente - DINIC")
st.markdown("### Automatización de Respuesta a Oficios y Memorandos")

if sistema_activo:
    uploaded_file = st.file_uploader("Arrastra el documento PDF aquí", type=['pdf'])

    if uploaded_file is not None:
        if st.button("⚡ Analizar y Generar Respuesta"):
            with st.spinner("Leyendo documento y redactando..."):
                try:
                    # 1. Crear archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # 2. Subir a Google
                    file_upload = genai.upload_file(path=tmp_path, display_name="Doc_Entrante")
                    
                    # 3. Cargar Modelo (Nombre corregido)
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # 4. El Prompt (Instrucciones)
                    prompt = f"""
                    Actúa como Secretario Técnico de la DINIC. Analiza el PDF adjunto.
                    
                    TUS OBJETIVOS:
                    1. IDENTIFICAR: Remitente, Cargo y Asunto exacto.
                    2. CLASIFICAR: Selecciona el departamento de destino más lógico de esta lista: {dept_options}.
                    3. ACCIÓN:
                       - Si es informativo: Sugerir "Conocimiento y Archivo".
                       - Si requiere acción: Redactar el OFICIO DE RESPUESTA completo.

                    FORMATO DE SALIDA (Usa Markdown):
                    
                    ## 📊 Resumen Ejecutivo
                    * **Documento:** [Tipo y Número si existe]
                    * **Remitente:** [Nombre y Cargo]
                    * **Asunto:** [Síntesis en 10 palabras]
                    * **Prioridad:** [Alta/Media/Baja]
                    
                    ## 🎯 Derivación Sugerida
                    **Departamento:** [Nombre del Depto]
                    **Justificación:** [Por qué va ahí]

                    ## 📝 Borrador de Respuesta (Copiar y Pegar)
                    [Redacta aquí el oficio formal de respuesta.
                    Usa un tono institucional, sobrio y directo.
                    Incluye espacios para fecha y firma.]
                    """

                    # 5. Generar
                    response = model.generate_content([prompt, file_upload])
                    
                    # 6. Mostrar Resultado
                    st.success("✅ Documento Procesado")
                    st.markdown(response.text)

                    # Limpieza
                    os.remove(tmp_path)

                except Exception as e:
                    st.error(f"Error técnico: {e}")
    else:
        st.info("👆 Sube un archivo para comenzar.")
