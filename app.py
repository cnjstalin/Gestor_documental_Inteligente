import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN DEL ENTORNO
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. ESTILOS CSS (ESTRICTOS Y UNIFORMES)
# ==============================================================================
st.markdown("""
    <style>
    /* FUENTES */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Roboto:wght@300;400;500&display=swap');

    /* FONDO GENERAL */
    .stApp {
        background-color: #050a10;
        background-image: 
            radial-gradient(circle at 50% 0%, #1a2a3a 0%, #050a10 85%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        color: #e0e0e0;
    }
    
    /* LIMPIEZA DE INTERFAZ */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 98% !important; }
    
    /* CABECERA HTML UNIFICADA */
    .header-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        background: rgba(13, 22, 33, 0.8);
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .header-logo {
        width: 120px;
        height: auto;
        filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.6));
        margin-bottom: 15px;
        display: block; /* Asegura que se comporte como bloque */
    }
    
    .header-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 188, 212, 0.5);
        line-height: 1.1;
        text-align: center;
    }
    
    .header-subtitle {
        font-family: 'Roboto', sans-serif;
        font-size: 1.1rem;
        color: #D4AF37;
        letter-spacing: 4px;
        margin-top: 10px;
        text-transform: uppercase;
        text-align: center;
    }

    /* BOTONES - GRID UNIFORME (1x4) */
    div.stButton > button {
        background: linear-gradient(180deg, rgba(25, 35, 45, 0.9), rgba(10, 15, 20, 0.95)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 12px !important;
        color: #fff !important;
        
        /* FUERZA BRUTA DE DIMENSIONES */
        width: 100% !important;
        height: 180px !important;
        min-height: 180px !important;
        max-height: 180px !important;
        
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px !important;
        gap: 10px;

        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        white-space: normal !important; /* Permite saltos de línea si el texto es largo */
        
        transition: all 0.2s ease !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background: linear-gradient(180deg, #1e3c50, #102030) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.3) !important;
    }

    /* Iconos CSS */
    div.stButton > button::before {
        font-size: 50px;
        margin-bottom: 5px;
        filter: grayscale(100%) opacity(0.8);
        transition: 0.3s;
        display: block;
    }
    div.stButton > button:hover::before { filter: grayscale(0%) opacity(1); transform: scale(1.1); }

    /* Asignación de Iconos */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER PERSONALIZADO */
    .custom-footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #080c10; color: #546e7a; font-size: 11px; padding: 12px;
        border-top: 1px solid #263238; font-family: 'Roboto', monospace;
        z-index: 9999;
    }
    .custom-footer b { color: #D4AF37; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

# --- CABECERA (HTML PURO PARA GARANTIZAR VISUALIZACIÓN) ---
st.markdown("""
    <div class="header-box">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="header-logo" alt="Escudo PN">
        
        <div class="header-title">SIGD DINIC</div>
        <div class="header-subtitle">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# --- GRID DE BOTONES (1 FILA X 4 COLUMNAS) ---
# Al usar CSS forzado arriba, todos tendrán la misma altura exacta
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    if st.button("SECRETARIO/A"):
        st.toast("Cargando Módulo...", icon="📝")

with col2:
    if st.button("TALENTO HUMANO"):
        st.toast("Verificando Acceso...", icon="👤")

with col3:
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Iniciando IA...", icon="🤖")

with col4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Acceso Restringido", icon="🛡️")

# --- FOOTER CON TUS DATOS ---
st.markdown("""
    <div class="custom-footer">
        SIGD DINIC v6.0 | DESARROLLADO POR: <b>JSCN</b> | CORREO: <b>cnjstalin@gmail.com</b> | SOPORTE: <b>0996652042</b>
    </div>
""", unsafe_allow_html=True)
