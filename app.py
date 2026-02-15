import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN BASE
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# URL del Escudo (Aseguramos que sea una URL pública válida o base64 si fuera local)
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS (DISEÑO TÁCTICO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@300;400;500&display=swap');

    /* FONDO */
    .stApp {
        background-color: #050a10;
        background-image: 
            radial-gradient(circle at 50% 30%, #122030 0%, #050a10 70%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        color: #e0e0e0;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; max-width: 1400px !important; }
    
    /* CABECERA PERSONALIZADA */
    .header-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 40px;
        padding: 20px;
        border-bottom: 2px solid rgba(212, 175, 55, 0.3); /* Línea dorada */
        background: rgba(13, 22, 33, 0.8);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem; /* TÍTULO GIGANTE */
        font-weight: 800;
        color: white;
        text-align: center;
        margin: 0;
        letter-spacing: 5px;
        text-shadow: 0 0 20px rgba(0, 188, 212, 0.5);
        line-height: 1;
    }
    
    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        color: #D4AF37; /* DORADO */
        text-align: center;
        margin-top: 10px;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* BOTONES HORIZONTALES */
    div.stButton > button {
        background: linear-gradient(90deg, rgba(20, 30, 45, 0.95), rgba(15, 25, 35, 0.95)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 10px !important;
        color: #fff !important;
        
        width: 100% !important;
        height: 100px !important; /* Altura controlada */
        
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: center !important;
        padding: 0 30px !important;
        gap: 20px;

        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    }

    div.stButton > button:hover {
        transform: translateX(10px) !important;
        background: linear-gradient(90deg, #1e3c50, #102030) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.2) !important;
    }

    /* Iconos CSS antes del texto */
    div.stButton > button::before {
        font-size: 40px;
        margin: 0;
        filter: grayscale(100%);
        transition: 0.3s;
    }
    div.stButton > button:hover::before { filter: grayscale(0%); transform: scale(1.2); }

    /* Asignar Iconos */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #080c10; color: #546e7a; font-size: 11px; padding: 5px;
        border-top: 1px solid #333; font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LAYOUT VISUAL
# ==============================================================================

# --- CABECERA ---
# Usamos columnas de Streamlit para centrar la imagen (Método infalible)
c1, c2, c3 = st.columns([4, 2, 4])
with c2:
    st.image(URL_ESCUDO, use_container_width=True)

st.markdown("""
    <div class="header-wrapper">
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# --- GRID DE BOTONES (2 Columnas x 2 Filas para que se vean grandes y ordenados) ---
col_izq, col_der = st.columns(2, gap="large")

with col_izq:
    st.markdown("#### 📂 GESTIÓN OPERATIVA")
    if st.button("SECRETARIO/A"):
        st.toast("Cargando Módulo Secretaría...", icon="📝")
    
    st.markdown("#### 🧠 INTELIGENCIA ARTIFICIAL")
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Iniciando Generador IA...", icon="🤖")

with col_der:
    st.markdown("#### 👥 PERSONAL")
    if st.button("TALENTO HUMANO"):
        st.toast("Accediendo a TH...", icon="👤")

    st.markdown("#### 🔒 CONTROL")
    if st.button("ADMINISTRACIÓN"):
        st.toast("Verificando permisos de Admin...", icon="🛡️")

# --- FOOTER ---
st.markdown('<div class="footer">DINIC 2026 | PROTEGIDO POR LEY ORGÁNICA DE SEGURIDAD</div>', unsafe_allow_html=True)
