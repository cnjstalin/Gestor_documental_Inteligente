import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Documental DINIC", layout="wide", page_icon="👮‍♂️")

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
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=70)
    st.title("Despacho DINIC")
    st.success("🟢 V6.0: Estilo Personalizado")
    st.markdown("""
    **Nuevas Capacidades:**
    1. 🕒 **Cálculo de Plazos:** Resta tiempo automáticamente para gestión interna.
    2. ✍️ **Fraseología Exacta:** Usa tus plantillas de "Digno intermedio" y "Avocar conocimiento".
    3. 🔗 **Extracción de Links:** Copia los enlaces de Zoom/Drive del original.
    """)

# --- 4. LÓGICA PRINCIPAL ---
st.title("👮‍♂️ Generador de Respuesta - Estilo DINIC")
st.markdown("### Automatización de Extractos (Réplica de Estilo de Mando)")

if sistema_activo:
    uploaded_file = st.file_uploader("Sube el PDF (Circular, Oficio, Memo)", type=['pdf'])

    if uploaded_file is not None:
        if st.button("⚡ Generar Extracto Exacto"):
            with st.spinner("Aplicando tus plantillas de redacción y calculando plazos..."):
                try:
                    # A. Temporales
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # B. Subir
                    file_upload = genai.upload_file(path=tmp_path, display_name="Doc_Tramite")
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # C. EL PROMPT DE RÉPLICA EXACTA
                    prompt = """
                    Actúa como el ASISTENTE PERSONAL DEL DIRECTOR DE LA DINIC.
                    Tu tarea es redactar el EXTRACTO exacto para Quipux, imitando el estilo de redacción del usuario basado en sus ejemplos históricos.

                    ANÁLISIS PREVIO:
                    1. Lee el documento.
                    2. Detecta si es FLUJO DE ELEVACIÓN (Hacia DIGIN/Superior) o FLUJO DE CASCADA (Hacia Unidades Subordinadas).
                    3. Si hay fechas límite en el documento original, calcula una "Fecha Interna" (resta 24 horas o 4 horas si es urgente) para el borrador.

                    --- PLANTILLAS DE REDACCIÓN OBLIGATORIAS ---

                    CASO 1: ELEVACIÓN (OFICIO A LA DIGIN)
                    *Úsalo cuando una unidad (UDAR/UNDECOF) pide algo que debe ir a otra dirección nacional.*
                    
                    [SALUDO]: "Mi [Rango del Superior]: Luego de expresarle un atento y cordial saludo, me permito poner en su conocimiento el Oficio Nro. [Nro Doc Entrante] de fecha [Fecha Doc Entrante], suscrito por [Cargo y Nombre del Remitente], mediante el cual [Resumen del pedido]."
                    
                    [PETICIÓN]: "En tal virtud, me permito solicitar que bajo su digno intermedio y a través del respectivo Órgano Regular se canalice la presente documentación hasta [Nombre de la Dirección de Destino Final], para [Finalidad: conocimiento, registro, trámite administrativo]."
                    
                    [DESPEDIDA]: "Hago propicia la ocasión para expresar mi sentimiento de consideración y estima. Con sentimientos de distinguida consideración."

                    ------------------------------------------------------------

                    CASO 2: CASCADA (MEMORANDO MÚLTIPLE A UNIDADES)
                    *Úsalo cuando llega una Circular o Disposición de la DIGIN/Comando que debe cumplirse.*

                    [ENCABEZADO]: "Señores servidores policiales nivel Directivo:" (o Singular si es uno solo).
                    
                    [CUERPO]: "Para conocimiento y cumplimiento remito el [Tipo y Nro Documento DIGIN] de fecha [Fecha], suscrito por el [Cargo del Remitente], y anexos adjuntos, mediante el cual solicita: [Puntos clave resumidos o lista de requerimientos].
                    [IMPORTANTE: Si hay enlaces de Zoom o Drive en el original, COPIALOS AQUÍ]."

                    [DISPOSICIÓN]: "Con estos antecedentes, sírvanse Sres. Jefes de las unidades [Listar: UDAR, UNDECOF, UCAP, etc.] avocar conocimiento y remitir la información requerida..."
                    
                    [PLAZOS - MUY IMPORTANTE]:
                    "...hasta las [HORA CALCULADA: Poner 2 a 24 horas ANTES de la hora real del documento] del día [FECHA], al correo [ticsdinic@gmail.com o el que corresponda] y a través de los canales oficiales (Quipux)."
                    
                    [CONSOLIDACIÓN]:
                    "Sr. Jefe de [Soporte Operativo / Coordinación Operacional / Talento Humano según el tema] de la DINIC: Sírvase avocar conocimiento, disponer a quien corresponda consolide la información de las unidades adscritas a fin de remitir un informe consolidado a la DIGIN."

                    ------------------------------------------------------------
                    
                    TU SALIDA:
                    Dame SOLO el texto listo para copiar y pegar. No me saludes, no me expliques.
                    """

                    # D. Resultado
                    response = model.generate_content([prompt, file_upload])
                    st.markdown(response.text)

                    # Limpieza
                    os.remove(tmp_path)

                except Exception as e:
                    st.error(f"Error: {e}")
