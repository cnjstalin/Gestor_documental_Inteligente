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

# URL ESCUDO (Directa y pública)
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS (DISEÑO TÁCTICO UNIFORME)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@300;400;500&display=swap');

    /* FONDO DE PANTALLA TÁCTICO */
    .stApp {
        background-color: #050a10;
        background-image: 
            radial-gradient(circle at 50% 10%, #152535 0%, #050a10 90%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        color: #e0e0e0;
    }
    
    /* OCULTAR ELEMENTOS NATIVOS */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 1200px !important; }
    
    /* CABECERA INTEGRADA (ESCUDO + TÍTULOS) */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 40px;
        padding: 30px;
        background: rgba(13, 22, 33, 0.85);
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.15); /* Borde dorado tenue */
        box-shadow: 0 15px 40px rgba(0,0,0,0.6);
    }
    
    .escudo-box {
        margin-bottom: 20px;
        text-align: center;
        width: 100%;
        display: flex;
        justify-content: center;
    }

    .escudo-img {
        width: 130px !important;
        height: auto;
        filter: drop-shadow(0 0 25px rgba(212, 175, 55, 0.4));
        display: block;
    }
    
    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem; 
        font-weight: 800;
        color: white;
        text-align: center;
        margin: 0;
        line-height: 1;
        letter-spacing: 5px;
        text-shadow: 0 0 30px rgba(0, 188, 212, 0.3);
        background: -webkit-linear-gradient(#fff, #90a4ae);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.1rem;
        color: #D4AF37; /* DORADO */
        text-align: center;
        margin-top: 15px;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-weight: 500;
        border-top: 1px solid rgba(212, 175, 55, 0.3);
        padding-top: 15px;
        width: 100%;
        max-width: 800px;
    }

    /* BOTONES HORIZONTALES UNIFORMES (REGLA MAESTRA) */
    div.stButton > button {
        background: linear-gradient(90deg, rgba(20, 30, 45, 0.95), rgba(10, 20, 30, 0.98)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 12px !important;
        color: #fff !important;
        
        /* DIMENSIONES FIJAS PARA UNIFORMIDAD */
        width: 100% !important;
        height: 120px !important;      /* Altura fija */
        min-height: 120px !important;  /* Forzar altura mínima */
        max-height: 120px !important;  /* Forzar altura máxima */
        
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: center !important;
        padding: 0 40px !important; /* Espacio lateral interno */
        gap: 30px; /* Separación Icono-Texto */

        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background: linear-gradient(90deg, #1e3c50, #102030) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(212, 175, 55, 0.2) !important;
    }

    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Iconos CSS uniformes */
    div.stButton > button::before {
        font-size: 45px;
        margin: 0;
        filter: grayscale(100%) opacity(0.7);
        transition: 0.3s;
        width: 50px; /* Ancho fijo para el icono para alinear textos */
        text-align: center;
    }
    div.stButton > button:hover::before { filter: grayscale(0%) opacity(1); transform: scale(1.1); }

    /* Asignar Iconos */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER DE CRÉDITOS */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: rgba(5, 8, 12, 0.98); color: #607d8b; font-size: 10px; padding: 10px;
        border-top: 1px solid #1f2b38; font-family: 'Roboto', sans-serif; letter-spacing: 0.5px;
        z-index: 9999;
    }
    .footer span { color: #D4AF37; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LAYOUT VISUAL
# ==============================================================================

# --- CABECERA UNIFICADA ---
st.markdown(f"""
    <div class="header-container">
        <div class="escudo-box">
            <img src="{URL_ESCUDO}" class="escudo-img">
        </div>
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# --- GRID DE BOTONES UNIFORMES (2 Columnas x 2 Filas) ---
c1, c2 = st.columns(2, gap="large")

with c1:
    if st.button("SECRETARIO/A"):
        st.toast("Accediendo a Secretaría...", icon="📝")
        # Aquí irás agregando la lógica de cambio de página

    # Espacio vertical (Markdown vacío para separar)
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Iniciando IA Generativa...", icon="🤖")

with c2:
    if st.button("TALENTO HUMANO"):
        st.toast("Verificando credenciales...", icon="👤")
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("ADMINISTRACIÓN"):
        st.toast("Panel de Control activado.", icon="🛡️")

# --- FOOTER DE CRÉDITOS ---
st.markdown("""
    <div class="footer">
        SIGD DINIC V1.0 | Desarrollado por: <span>JSCN</span> | Correo: <span>cnjstalin@gmail.com</span> | Soporte: <span>0996652042</span>
    </div>
""", unsafe_allow_html=True)
