import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN BASE Y CONSTANTES ETERNAS
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC | Centro de Mando",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# CONSTANTES INMUTABLES
NOMBRE_SISTEMA = "SISTEMA INTEGRAL DE GESTION DOCUMENTAL DINIC"
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. INYECCIÓN DE CSS (DISEÑO TÁCTICO HORIZONTAL)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTAR FUENTES TÉCNICAS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Roboto:wght@300;400;500&display=swap');

    /* --- 2.1 ESTRUCTURA GENERAL --- */
    .stApp {
        background-color: #0a1018;
        background-image: 
            radial-gradient(circle at 50% 30%, #1a2a3a 0%, #0a1018 70%),
            linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        color: #e0e0e0;
        font-family: 'Roboto', sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 3rem !important; padding-bottom: 5rem !important; max-width: 1400px !important; }
    hr { border-color: rgba(212, 175, 55, 0.2) !important; margin: 50px 0 !important; }


    /* --- 2.2 CABECERA INSTITUCIONAL CENTRADA --- */
    .header-container {
        display: flex;
        flex-direction: column; /* Apilado verticalmente para centrar mejor */
        align-items: center;
        justify-content: center;
        margin-bottom: 50px;
        padding: 30px;
        background: rgba(13, 22, 33, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.1);
        text-align: center; /* Asegura que el texto interno esté centrado */
    }

    .logo-box img {
        width: 130px; /* Un poco más grande */
        filter: drop-shadow(0 0 20px rgba(212, 175, 55, 0.4));
        margin-bottom: 20px;
    }

    .title-box h1 {
        font-family: 'Rajdhani', sans-serif;
        color: #ffffff;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.8);
        background: -webkit-linear-gradient(#fff, #cfd8dc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .title-box h3 {
        font-family: 'Roboto', sans-serif;
        color: #D4AF37;
        font-size: 1.2rem;
        font-weight: 500;
        margin: 15px 0 0 0;
        letter-spacing: 4px;
        text-transform: uppercase;
        opacity: 0.9;
    }


    /* --- 2.3 TARJETAS HORIZONTALES (NUEVO DISEÑO) --- */
    div.stButton > button {
        background: linear-gradient(90deg, rgba(20, 30, 45, 0.95), rgba(15, 25, 35, 0.95)) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
        
        /* GEOMETRÍA HORIZONTAL */
        width: 100% !important;
        height: 140px !important; /* Más bajo */
        display: flex !important;
        flex-direction: row !important; /* Elementos lado a lado */
        justify-content: flex-start !important; /* Alineado a la izquierda */
        align-items: center !important;
        padding: 0 30px !important; /* Relleno horizontal */
        gap: 25px; /* Espacio entre icono y texto */

        /* TIPOGRAFÍA */
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        text-align: left !important;
        
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Iconos (Emojis) a la izquierda */
    div.stButton > button::before {
        font-size: 55px;
        margin-bottom: 0; /* Sin margen inferior en modo horizontal */
        filter: grayscale(100%) opacity(0.7);
        transition: all 0.3s ease;
        flex-shrink: 0; /* Evita que el icono se aplaste */
    }
    
    /* EFECTOS HOVER */
    div.stButton > button:hover {
        transform: translateX(5px) !important; /* Pequeño desplazamiento lateral */
        background: linear-gradient(90deg, rgba(30, 45, 70, 1), rgba(20, 30, 45, 1)) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 0 20px rgba(212, 175, 55, 0.1) !important;
        color: #ffffff !important;
    }

    div.stButton > button:hover::before {
        filter: grayscale(0%) opacity(1) drop-shadow(0 0 10px rgba(255,255,255,0.3));
    }
    
    /* Asignación de Iconos Específicos */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }

    /* FOOTER SIMPLE */
    .footer-status {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; padding: 10px;
        background: rgba(10, 16, 24, 0.9); color: #546e7a; font-size: 10px; border-top: 1px solid rgba(255,255,255,0.05);
        font-family: 'Roboto Mono', monospace; letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. ESTRUCTURA DEL LAYOUT
# ==============================================================================

# --- 3.1 CABECERA CENTRADA ---
st.markdown(f"""
    <div class="header-container">
        <div class="logo-box"><img src="{URL_ESCUDO}"></div>
        <div class="title-box">
            <h1>{NOMBRE_SISTEMA}</h1>
            <h3>CENTRO DE MANDO OPERATIVO | NIVEL CENTRAL</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- 3.2 GRID HORIZONTAL DE MÓDULOS (3 COLUMNAS) ---
# Usamos 3 columnas para que los botones sean anchos y horizontales
m1, m2, m3 = st.columns(3, gap="large")

with m1:
    # El icono 📝 se añade por CSS
    if st.button("SECRETARIO/A"):
        st.toast("Accediendo a Gestión Documental...", icon="📝")
        # Lógica de navegación aquí

with m2:
    # El icono 👤 se añade por CSS
    if st.button("TALENTO HUMANO"):
        st.toast("Validando credenciales TH...", icon="👤")
        # Lógica de navegación aquí

with m3:
    # El icono 🤖 se añade por CSS
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Iniciando motor de IA...", icon="🤖")
        # Lógica de navegación aquí

# --- 3.3 PIE DE PÁGINA ---
st.markdown("""
    <div class="footer-status">
        SISTEMA OPERATIVO | CONEXIÓN CIFRADA | DINIC 2026
    </div>
""", unsafe_allow_html=True)
