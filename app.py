import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN BASE Y CONSTANTES ETERNAS
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC | Centro de Mando",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed" # Ocultamos barra lateral para look de "Sistema"
)

# CONSTANTES INMUTABLES
NOMBRE_SISTEMA = "SISTEMA INTEGRAL DE GESTION DOCUMENTAL DINIC"
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. INYECCIÓN DE CSS (EL DISEÑO VISUAL PROFESIONAL)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTAR FUENTES TÉCNICAS (ROBOTO Y RAJDHANI PARA TÍTULOS) */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Roboto:wght@300;400;700&display=swap');

    /* --- 2.1 ESTRUCTURA GENERAL (FONDO Y LIMPIEZA) --- */
    .stApp {
        /* Fondo degradado oscuro profesional con una sutil textura de red */
        background-color: #0a1018;
        background-image: 
            radial-gradient(circle at 50% 0%, #1a2a3a 0%, #0a1018 70%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 30px 30px, 30px 30px;
        color: #e0e0e0;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Ocultar elementos nativos de Streamlit que ensucian la interfaz */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    hr { border-color: rgba(212, 175, 55, 0.3) !important; margin: 40px 0 !important; } /* Separadores dorados sutiles */


    /* --- 2.2 CABECERA INSTITUCIONAL (HEADER) --- */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 40px;
        padding-bottom: 30px;
        border-bottom: 3px solid #D4AF37; /* Línea dorada policial */
        background: rgba(13, 22, 33, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .logo-box img {
        width: 110px;
        filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.6)); /* Resplandor dorado al escudo */
        margin-right: 30px;
    }

    .title-box h1 {
        font-family: 'Rajdhani', sans-serif;
        color: #ffffff;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
        background: -webkit-linear-gradient(white, #b0bec5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .title-box h3 {
        font-family: 'Roboto', sans-serif;
        color: #D4AF37; /* Color Dorado */
        font-size: 1.3rem;
        font-weight: 400;
        margin: 10px 0 0 0;
        letter-spacing: 5px;
        text-transform: uppercase;
    }


    /* --- 2.3 TARJETAS DE MÓDULOS (ESTILIZACIÓN AVANZADA DE BOTONES) --- */
    /* Transformamos los botones estándar de Streamlit en tarjetas interactivas */
    div.stButton > button {
        background: linear-gradient(145deg, rgba(20, 30, 45, 0.9), rgba(10, 20, 30, 0.9)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important; /* Borde sutil dorado */
        border-radius: 16px !important;
        color: #e0e0e0 !important;
        
        /* Tamaño y disposición */
        width: 100% !important;
        height: 280px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 20px !important;

        /* Tipografía */
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3), inset 0 0 0 1px rgba(255,255,255,0.05) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Iconos (Emojis) grandes dentro de los botones */
    div.stButton > button::before {
        font-size: 70px;
        margin-bottom: 25px;
        filter: grayscale(90%) opacity(0.8); /* Apagados por defecto */
        transition: all 0.4s ease;
    }

    /* Subtítulos (Descripciones) dentro de los botones */
    div.stButton > button::after {
        content: attr(data-desc); /* Texto descriptivo */
        font-family: 'Roboto', sans-serif;
        font-size: 0.85rem;
        font-weight: 400;
        color: #90a4ae;
        text-transform: none;
        letter-spacing: 0.5px;
        margin-top: 10px;
        opacity: 0.7;
        transition: all 0.4s ease;
    }
    
    /* --- EFECTOS HOVER (AL PASAR EL MOUSE) --- */
    div.stButton > button:hover {
        transform: translateY(-8px) !important; /* Levantar */
        background: linear-gradient(145deg, rgba(25, 40, 60, 1), rgba(15, 25, 35, 1)) !important;
        border-color: #D4AF37 !important; /* Borde dorado brillante */
        box-shadow: 0 15px 35px rgba(0,0,0,0.5), 0 0 20px rgba(212, 175, 55, 0.2) !important; /* Resplandor dorado */
        color: #ffffff !important;
    }

    div.stButton > button:hover::before {
        filter: grayscale(0%) opacity(1) drop-shadow(0 0 15px rgba(255,255,255,0.4)); /* Activar color icono */
        transform: scale(1.1);
    }
    
    div.stButton > button:hover::after {
        color: #D4AF37; /* Descripción dorada */
        opacity: 1;
    }
    
    /* Asignación de Iconos y Descripciones específicas por posición */
    /* Tarjeta 1: Secretaría */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(1) button { --desc: "Gestión, Recepción y Trámite Documental V44"; }
    /* Tarjeta 2: Asesor IA */
    div.row-widget.stButton:nth-of-type(2) button::before { content: "🧠"; }
    div.row-widget.stButton:nth-of-type(2) button { --desc: "Análisis Inteligente con Gemini Pro"; }
    /* Tarjeta 3: Talento Humano */
    div.row-widget.stButton:nth-of-type(3) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button { --desc: "Control de Personal, Partes y Sanciones"; }
    /* Tarjeta 4: Admin */
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }
    div.row-widget.stButton:nth-of-type(4) button { --desc: "Auditoría, Usuarios y Configuración Global"; }

    /* Truco para inyectar la descripción en el pseudo-elemento ::after */
    div.stButton > button::after { content: var(--desc); }

    /* FOOTER SIMPLE */
    .footer-status {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; padding: 10px;
        background: rgba(0,0,0,0.8); color: #546e7a; font-size: 11px; border-top: 1px solid #263238;
        font-family: 'Roboto Mono', monospace;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. ESTRUCTURA DEL LAYOUT (HTML/PYTHON)
# ==============================================================================

# --- 3.1 CABECERA (HEADER) ---
# Usamos columnas para alinear el escudo y el título de forma precisa
col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    # Contenedor para el escudo con la clase CSS aplicada
    st.markdown(f"""<div class="logo-box"><img src="{URL_ESCUDO}"></div>""", unsafe_allow_html=True)

with col_titulo:
    # Contenedor para los títulos con las clases CSS aplicadas
    st.markdown(f"""
        <div class="title-box">
            <h1>{NOMBRE_SISTEMA}</h1>
            <h3>CENTRO DE MANDO OPERATIVO | NIVEL CENTRAL</h3>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---") # Separador visual sutil

# --- 3.2 GRID DE ACCESO A MÓDULOS (TARJETAS) ---
# Creamos 4 columnas para los 4 módulos principales
m1, m2, m3, m4 = st.columns(4, gap="large")

with m1:
    # El texto del botón se renderizará con la fuente Rajdhani y mayúsculas por CSS
    if st.button("SECRETARÍA"):
        st.toast("Iniciando Módulo de Secretaría...", icon="📝")
        # AQUÍ IRÁ LA LÓGICA PARA CAMBIAR DE PÁGINA LUEGO

with m2:
    if st.button("ASESOR IA"):
        st.toast("Conectando con Motor Neuronal...", icon="🧠")
        # AQUÍ IRÁ LA LÓGICA PARA CAMBIAR DE PÁGINA LUEGO

with m3:
    if st.button("TALENTO HUMANO"):
        st.toast("Validando Credenciales de TH...", icon="👤")
        # AQUÍ IRÁ LA LÓGICA PARA CAMBIAR DE PÁGINA LUEGO

with m4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Acceso de Nivel Superior Requerido.", icon="🛡️")
        # AQUÍ IRÁ LA LÓGICA PARA CAMBIAR DE PÁGINA LUEGO

# --- 3.3 PIE DE PÁGINA (ESTADO DEL SISTEMA) ---
st.markdown("""
    <div class="footer-status">
        ESTADO DEL SISTEMA: OPERATIVO | VERSIÓN: 1.0 ALPHA | CONEXIÓN SEGURA SSL
    </div>
""", unsafe_allow_html=True)
