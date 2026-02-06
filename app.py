import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Documental DINIC", layout="wide", page_icon="⚡")

# --- 2. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error: Falta API KEY en Secrets.")
    sistema_activo = False

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("Panel DINIC")
    st.success("🟢 Modo Agilidad: ACTIVO")
    
    st.markdown("### 🚦 Lógica de Decisión")
    st.info("**REASIGNAR:** Trámites internos de revisión, conocimiento o ejecución directa.")
    st.warning("**DOCUMENTO:** Envíos a DIGIN (Oficio) o disposiciones solemnes.")
    
    dept_list = "Jurídico, Talento Humano, Inteligencia, Operaciones, Logística, Archivo"

# --- 4. LÓGICA PRINCIPAL ---
st.title("⚡ Asistente de Gestión Rápida - QUIPUX")
st.markdown("### ¿Reasignar o Redactar? Deja que la IA decida.")

if sistema_activo:
    uploaded_file = st.file_uploader("Sube el PDF recibido", type=['pdf'])

    if uploaded_file is not None:
        if st.button("🤖 Analizar Trámite"):
            with st.spinner("Decidiendo la mejor vía (Reasignación vs. Documento)..."):
                try:
                    # A. Temporales
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # B. Subir
                    file_upload = genai.upload_file(path=tmp_path, display_name="Doc_Tramite")
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # C. PROMPT DE DECISIÓN (EL CEREBRO NUEVO)
                    prompt = f"""
                    Actúa como el ASISTENTE OPERATIVO DE LA DINIC. Tu misión es la AGILIDAD.
                    Analiza el documento y decide si solo se REASIGNA o si se debe ELABORAR DOCUMENTO.

                    CONTEXTO:
                    - Soy el Director DINIC.
                    - Mis departamentos son: {dept_list}.
                    - Mi superior es: DIGIN.

                    REGLAS DE DECISIÓN (Sigue este orden):

                    1. ¿ES PARA TRÁMITE INTERNO? (Vía Rápida - REASIGNAR)
                       - Si el documento requiere que Jurídica informe, que TH revise, que Operaciones ejecute, o es solo para conocimiento de ellos.
                       - O si aplica la EXCEPCIÓN DE TH (Declaraciones, Títulos) -> Se REASIGNA directamente a Talento Humano para verificación.
                       -> DECISIÓN: REASIGNAR.

                    2. ¿VA PARA AFUERA O ES MUY FORMAL? (Vía Formal - DOCUMENTO)
                       - Si va dirigido a la DIGIN, Comandancia, Fiscalía (Externos).
                       - O si es una sanción/felicitación formal que requiere Memorando escrito.
                       -> DECISIÓN: ELABORAR DOCUMENTO (Oficio o Memo).

                    --------------------------------------------------
                    FORMATO DE SALIDA OBLIGATORIO (MARKDOWN):

                    Si decides REASIGNAR:
                    ## 🟢 ACCIÓN: REASIGNAR EN QUIPUX
                    **Para:** [Nombre del Departamento]
                    **Motivo:** [Explicación breve]
                    
                    ### 💬 Comentario para copiar:
                    "[Escribe aquí un comentario corto y preciso. Ej: 'Para su conocimiento y fines pertinentes', 'Para revisión y trámite según normativa', 'Proceder con la verificación conforme Circular 05131'.]"

                    ---
                    
                    Si decides ELABORAR DOCUMENTO:
                    ## 🔴 ACCIÓN: ELABORAR DOCUMENTO
                    **Tipo:** [OFICIO a DIGIN / MEMORANDO Interno]
                    **Dirigido a:** [Destinatario]
                    
                    ### 📝 Texto del Documento:
                    [Redacta el cuerpo completo del Oficio/Memorando aquí, formal y listo para firma].
                    """

                    # D. Resultado
                    response = model.generate_content([prompt, file_upload])
                    st.markdown(response.text)

                    # Limpieza
                    os.remove(tmp_path)

                except Exception as e:
                    st.error(f"Error: {e}")
