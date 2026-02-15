import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Enlace directo al escudo (WikiMedia)
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS (DISEÑO ESTRICTO)
# ==============================================================================
st.markdown("""
    <style>
    /* FUENTES TÉCNICAS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@400;500&display=swap');

    /* RESET GENERAL */
    .stApp {
        background-color: #050a10;
        background-image: radial-gradient(circle at 50% 20%, #101820 0%, #000000 80%);
        color: #e0e0e0;
    }
    
    /* OCULTAR ELEMENTOS NATIVOS MOLESTOS */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 98% !important; }

    /* --- CABECERA (HEADER) --- */
    .header-box {
        text-align: center;
        padding: 40px 20px;
        background: rgba(13, 20, 28, 0.8);
        border-bottom: 3px solid #D4AF37; /* Dorado */
        margin-bottom: 50px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    }
    
    /* IMAGEN DEL ESCUDO (FORZADA) */
    .escudo-img {
        width: 140px;
        max-width: 140px;
        height: auto;
        display: block;
        margin: 0 auto 20px auto; /* Centrado absoluto */
        filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.5));
    }

    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 188, 212, 0.6); /* Azul neón */
    }
    
    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        color: #D4AF37;
        letter-spacing: 3px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* --- BOTONES UNIFORMES (LA SOLUCIÓN) --- */
    /* Forzamos dimensiones fijas para todos los botones */
    div.stButton > button {
        background: linear-gradient(180deg, #1a2634 0%, #0d131a 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #fff !important;
        
        /* DIMENSIONES EXACTAS */
        width: 100% !important;
        height: 160px !important;      /* Altura fija para todos */
        min-height: 160px !important;
        max-height: 160px !important;
        
        /* ALINEACIÓN INTERNA */
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px 5px !important;
        
        /* TEXTO */
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        white-space: normal !important; /* Permite 2 líneas si es largo */
        line-height: 1.1 !important;
        text-align: center !important;
        
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
    }

    /* EFECTO HOVER */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        border-color: #D4AF37 !important;
        background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%) !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3) !important;
    }

    /* ICONOS CSS */
    div.stButton > button::before {
        font-size: 40px;
        margin-bottom: 10px;
        filter: grayscale(100%);
        transition: 0.3s;
        display: block;
    }
    div.stButton > button:hover::before { filter: grayscale(0%); transform: scale(1.1); }

    /* ASIGNACIÓN DE ICONOS */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* --- FOOTER DE DATOS --- */
    .dev-footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #080c10; border-top: 1px solid #333; padding: 10px;
        font-family: 'Roboto', monospace; font-size: 11px; color: #546e7a;
        z-index: 9999;
    }
    .dev-footer strong { color: #D4AF37; margin: 0 5px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

# --- CABECERA (HTML PURO) ---
# Usamos HTML directo para garantizar que la imagen y el texto se rendericen juntos y centrados
st.markdown(f"""
    <div class="header-box">
        <img src="{URL_ESCUDO}" class="escudo-img" alt="Escudo PN">
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# --- GRID UNIFICADO (1 FILA x 4 COLUMNAS) ---
# Usamos gap="small" para que entren bien en pantallas medianas
c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    if st.button("SECRETARIO/A"):
        st.toast("Cargando Módulo...", icon="📝")
        # st.session_state.page = 'secretario'
        # st.rerun()

with c2:
    if st.button("TALENTO HUMANO"):
        st.toast("Validando Acceso...", icon="👤")
        # st.session_state.page = 'th'
        # st.rerun()

with c3:
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Iniciando IA...", icon="🤖")
        # st.session_state.page = 'ia'
        # st.rerun()

with c4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Acceso Restringido", icon="🛡️")
        # st.session_state.page = 'admin'
        # st.rerun()

# --- DATOS DE DESARROLLADOR ---
st.markdown("""
    <div class="dev-footer">
        VERSIÓN DEL SISTEMA: <strong>v64.0</strong> | 
        DESARROLLADO POR: <strong>JSCN</strong> | 
        CORREO: <strong>cnjstalin@gmail.com</strong> | 
        SOPORTE: <strong>0996652042</strong>
    </div>
""", unsafe_allow_html=True)
