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

# URL DEL ESCUDO
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS (BOTONES UNIFICADOS 1x4)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@300;400;500&display=swap');

    /* FONDO */
    .stApp {
        background-color: #050a10;
        background-image: 
            radial-gradient(circle at 50% 0%, #152535 0%, #050a10 80%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        color: #e0e0e0;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 95% !important; }
    
    /* TÍTULOS */
    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem; 
        font-weight: 800;
        color: white;
        text-align: center;
        margin: 0;
        line-height: 1;
        text-shadow: 0 0 30px rgba(0, 188, 212, 0.3);
        background: -webkit-linear-gradient(#fff, #90a4ae);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        color: #D4AF37;
        text-align: center;
        margin-top: 5px;
        letter-spacing: 3px;
        font-weight: 500;
        margin-bottom: 40px;
    }

    /* --- REGLA MAESTRA PARA BOTONES UNIFORMES --- */
    div.stButton > button {
        background: linear-gradient(180deg, rgba(20, 30, 45, 0.9), rgba(10, 20, 30, 0.95)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 15px !important;
        color: #fff !important;
        
        /* DIMENSIONES FORZADAS (CUADRADOS VERTICALES PARA FILA DE 4) */
        width: 100% !important;
        height: 200px !important;      
        min-height: 200px !important;  
        
        display: flex !important;
        flex-direction: column !important; /* Icono arriba, texto abajo */
        justify-content: center !important;
        align-items: center !important;
        padding: 20px !important;
        gap: 15px;

        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.3rem !important; /* Texto ajustado */
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        text-align: center !important;
        white-space: normal !important; /* Permite que el texto baje de línea */
        
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-10px) !important;
        background: linear-gradient(180deg, #1e3c50, #102030) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.3) !important;
    }

    /* ICONOS GIGANTES CENTRADOS */
    div.stButton > button::before {
        font-size: 50px;
        margin-bottom: 10px;
        filter: grayscale(100%) opacity(0.8);
        transition: 0.3s;
        display: block;
    }
    div.stButton > button:hover::before { filter: grayscale(0%) opacity(1); transform: scale(1.1); }

    /* ASIGNACIÓN DE ICONOS POR ORDEN */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: rgba(5, 8, 12, 0.95); color: #607d8b; font-size: 11px; padding: 12px;
        border-top: 1px solid #1f2b38; font-family: 'Roboto', sans-serif;
    }
    .footer span { color: #D4AF37; font-weight: bold; margin: 0 5px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LAYOUT VISUAL
# ==============================================================================

# --- CABECERA (MÉTODO INFALIBLE PARA LA IMAGEN) ---
# Usamos 3 columnas vacías a los lados para centrar la imagen al medio
c_left, c_center, c_right = st.columns([5, 2, 5])

with c_center:
    # st.image es nativo de Python, no falla como HTML/CSS a veces
    st.image(URL_ESCUDO, use_container_width=True)

st.markdown("""
    <div class="main-title">SIGD DINIC</div>
    <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
""", unsafe_allow_html=True)

# --- GRID EN UNA SOLA FILA (4 COLUMNAS) ---
# Usamos 4 columnas iguales. El CSS forzará la altura exacta en todas.
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    if st.button("SECRETARIO/A"):
        st.toast("Módulo Secretaría", icon="📝")

with col2:
    if st.button("TALENTO HUMANO"):
        st.toast("Módulo TH", icon="👤")

with col3:
    if st.button("GENERADOR DOC."): # Texto abreviado para que encaje mejor, o usa "DOCUMENTAL" si prefieres que baje de línea
        st.toast("Módulo IA", icon="🤖")

with col4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Módulo Admin", icon="🛡️")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        SIGD DINIC v5.0 | Desarrollado por: <span>JSCN</span> | Correo: <span>cnjstalin@gmail.com</span> | Soporte: <span>0996652042</span>
    </div>
""", unsafe_allow_html=True)
