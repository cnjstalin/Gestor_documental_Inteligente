import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Gestión Documental DINIC", layout="wide", page_icon="👮‍♂️")

# --- 2. AUTENTICACIÓN (INVISIBLE) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY en los Secretos.")
    sistema_activo = False

# --- 3. BARRA LATERAL (JERARQUÍA DINIC) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=70)
    st.title("Panel de Mando DINIC")
    st.success("🟢 Sistema Operativo")
    
    st.markdown("### 🏛️ Estructura Orgánica")
    st.info("El sistema aplicará las reglas de flujo de la DIGIN automáticamente.")

# --- 4. LÓGICA DEL CEREBRO ---
st.title("👮‍♂️ Asistente de Despacho - DINIC")
st.markdown("### Generador de Texto para QUIPUX")
st.caption("Sube el PDF recibido. La IA detectará si corresponde Oficio (a DIGIN) o Memorando (Interno).")

if sistema_activo:
    uploaded_file = st.file_uploader("Sube el documento recibido (PDF)", type=['pdf'])

    if uploaded_file is not None:
        if st.button("⚡ Generar Texto para Quipux"):
            with st.spinner("Analizando jerarquía, anexos y redactando respuesta..."):
                try:
                    # A. Crear temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # B. Subir a Google
                    file_upload = genai.upload_file(path=tmp_path, display_name="Doc_Analisis")
                    
                    # C. Modelo (Usamos el Flash Latest)
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # D. EL PROMPT MAESTRO (Tus Reglas de Oro)
                    prompt = """
                    Actúa como el ASISTENTE PERSONAL DEL DIRECTOR DE LA DINIC (Dirección Nacional de Investigación de Delitos Contra la Corrupción).
                    Tu único objetivo es redactar el CUERPO DEL TEXTO para pegar en QUIPUX.

                    CONTEXTO INSTITUCIONAL (REGLAS INQUEBRANTABLES):
                    1. YO SOY: El Director de la DINIC (Nivel 1).
                    2. MI JEFE (Superior): Dirección General de Investigación (DIGIN).
                    3. MIS SUBALTERNOS (Internos): 
                       - Dptos: Planificación, Jurídico, Comunicación, Análisis, Apoyo Op (Talento Humano, Logística), Financiero.
                       - Unidades Adscritas: UDAR, UNDECOF, UCAP.

                    REGLAS DE FLUJO Y TIPO DE DOCUMENTO:
                    - CASO A (Hacia Arriba/Afuera): Si el trámite va a la DIGIN o a una unidad externa a la DINIC -> Se redacta un OFICIO dirigido a la DIGIN (para que ellos canalicen).
                    - CASO B (Hacia Abajo/Interno): Si el trámite es para mis Dptos o Unidades -> Se redacta un MEMORANDO.
                    - CASO C (Reasignación): Si llega de un Dpto y debe ir a otro Dpto -> Se hace un comentario de Reasignación o Memorando.

                    INSTRUCCIONES DE ANÁLISIS:
                    1. Lee el documento adjunto.
                    2. Identifica quién lo envía y qué pide.
                    3. Si faltan datos en el principal, búscalos en el contexto de los anexos.
                    4. Define a quién debemos responder o derivar (Jurídica, Talento Humano, DIGIN, etc.).

                    FORMATO DE SALIDA (Sigue esto estrictamente):

                    ---
                    **ANÁLISIS RÁPIDO:**
                    * **Tipo de Documento Recomendado:** [OFICIO o MEMORANDO]
                    * **Destinatario Sugerido:** [Nombre del Dpto o DIGIN]
                    * **Razón:** [Breve explicación de la regla aplicada]
                    ---

                    **CUERPO DEL DOCUMENTO (COPIAR Y PEGAR EN QUIPUX):**
                    [Escribe aquí SOLO el texto del cuerpo. 
                    - Usa lenguaje formal policial/institucional ("De mi consideración...", "Por disposición...").
                    - Sé claro, directo y coherente.
                    - Menciona el documento recibido como referencia.
                    - Si es derivación: "Para su conocimiento y fines pertinentes..."]
                    
                    ---
                    """

                    # E. Generar
                    response = model.generate_content([prompt, file_upload])
                    
                    # F. Resultado
                    st.success("✅ Texto Generado")
                    st.markdown(response.text)

                    # Limpieza
                    os.remove(tmp_path)

                except Exception as e:
                    st.error(f"Error técnico: {e}")
    else:
        st.info("👆 Esperando archivo...")
