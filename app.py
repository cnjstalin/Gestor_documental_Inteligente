import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Estratega Documental DINIC", layout="wide", page_icon="⚖️")

# --- 2. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error crítico: No se detectan credenciales en Secrets.")
    sistema_activo = False

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.title("Estado Mayor DINIC")
    st.success("🟢 V8.0: Razonamiento Táctico")
    st.info("El sistema ahora justifica sus decisiones basándose en la jerarquía y el órgano regular.")

# --- 4. LÓGICA PRINCIPAL ---
st.title("🛡️ Sistema de Decisión y Redacción Policial")
st.markdown("### Análisis de Flujo, Justificación Legal y Redacción")

if sistema_activo:
    uploaded_file = st.file_uploader("Sube el expediente para análisis", type=['pdf'])

    if uploaded_file is not None:
        if st.button("⚖️ Analizar Causa y Redactar"):
            with st.spinner("Consultando reglamento, evaluando jerarquía y redactando..."):
                try:
                    # A. Temporales
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # B. Carga
                    file_upload = genai.upload_file(path=tmp_path, display_name="Doc_Analisis")
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # C. EL PROMPT DE RAZONAMIENTO (Aquí está la nueva lógica)
                    prompt = """
                    Actúa como el ASESOR JURÍDICO Y OPERATIVO DE LA DINIC. 
                    Analiza el documento adjunto y genera un reporte de decisión fundamentado.

                    JERARQUÍA Y REGLAS (TU BASE DE DATOS):
                    1. DIGIN (General) > DINIC (Director/Tcnl) > UNIDADES (UDAR/UNDECOF) > DEPARTAMENTOS.
                    2. REGLA DE ORO: Ninguna Unidad puede saltarse a la DINIC. Ninguna DINIC puede saltarse a la DIGIN para temas externos.
                    3. EXCEPCIÓN TH: Temas de Talento Humano (vacaciones, títulos) se derivan a TH-DINIC, no a DIGIN.

                    TU TAREA:
                    Genera una salida en dos partes estrictas:

                    PARTE 1: LA MATRIZ DE DECISIÓN (EL PORQUÉ)
                    Responde estas 4 preguntas clave:
                    1. **¿Qué tenemos aquí?** (Diagnóstico del documento entrante).
                    2. **¿Hacia dónde se canaliza?** (Destino correcto).
                    3. **¿POR QUÉ a ese destino?** (Justificación basada en el Órgano Regular. Ej: "Al ser un pedido externo, corresponde a la DIGIN autorizarlo").
                    4. **¿POR QUÉ NO se envía a otro lado?** (Razonamiento negativo. Ej: "NO se envía directo a la Unidad porque el Director debe validar primero" o "NO se envía a la DIGIN porque es un trámite interno de vacaciones que resuelve TH").

                    PARTE 2: EL PRODUCTO FINAL (EL CÓMO)
                    Redacta el texto exacto para Quipux (Memorando u Oficio) basándote en la decisión tomada.
                    - Si es hacia ARRIBA: Usa "Solicito por su digno intermedio se canalice...".
                    - Si es hacia ABAJO: Usa "Sírvanse avocar conocimiento y cumplir...".
                    - Incluye fechas límite calculadas (resta 24h al plazo original).

                    ------------------------------------------------------------
                    FORMATO DE SALIDA (MARKDOWN):

                    ## 🧠 FUNDAMENTACIÓN TÁCTICA
                    
                    | Criterio | Análisis del Sistema |
                    | :--- | :--- |
                    | **Tipo de Trámite** | [Ej: Solicitud de Pase / Orden de Operativo] |
                    | **Acción Recomendada** | [Ej: ELEVAR A DIGIN / DISPONER A UDAR] |
                    | **✅ Por qué SÍ aquí** | [Explica la lógica jerárquica] |
                    | **❌ Por qué NO allá** | [Explica por qué descartaste otras opciones] |

                    ---

                    ## 📝 TEXTO PARA QUIPUX (Copiar y Pegar)
                    
                    **Destinatario:** [Cargo]
                    **Asunto:** [Asunto sugerido]

                    [Redacta aquí el cuerpo completo del documento con el estilo formal policial, sin saludos ni explicaciones extra, solo el texto].
                    """

                    # D. Resultado
                    response = model.generate_content([prompt, file_upload])
                    st.markdown(response.text)

                    # Limpieza
                    os.remove(tmp_path)

                except Exception as e:
                    st.error(f"Error: {e}")
