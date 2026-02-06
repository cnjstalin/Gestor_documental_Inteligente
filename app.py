import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Documental DINIC", layout="wide", page_icon="⚖️")

# --- GESTIÓN DE CREDENCIALES (SECRETS) ---
# El sistema busca la clave automáticamente en el servidor
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error de Configuración: No se encontró la API KEY en los Secretos.")
    sistema_activo = False

# --- INTERFAZ LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80) # Icono genérico documento
    st.title("Panel de Control")
    st.info("Estado del Sistema: 🟢 EN LÍNEA")
    
    # Aquí definimos tus departamentos reales (Edítalos si faltan)
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
    st.caption("Sistema de Asistencia Técnica v1.2")

# --- LÓGICA PRINCIPAL ---
st.title("🏛️ Gestión Documental Inteligente - DINIC")
st.markdown("### Automatización de Respuesta a Oficios y Memorandos")

if sistema_activo:
    uploaded_file = st.file_uploader("Arrastra el documento PDF aquí", type=['pdf'])

    if uploaded_file is not None:
        if st.button("⚡ Analizar y Generar Respuesta"):
            with st.spinner("Leyendo documento, analizando contexto y redactando..."):
                try:
                    # 1. Archivo Temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # 2. Carga a Gemini
                    file_upload = genai.upload_file(path=tmp_path, display_name="Doc_Entrante")
                    
                    # 3. Modelo (Usamos el Flash Latest que es rápido y gratis)
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')

                    # 4. Prompt Avanzado (Aquí está la magia de John Rotot)
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

                    # 5. Generación
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

else:
    st.warning("El sistema requiere configuración de API Key en 'Secrets'.")
