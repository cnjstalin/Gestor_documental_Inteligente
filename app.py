import streamlit as st
import base64
import os

# ==============================================================================
# 1. CONFIGURACIÓN BASE
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. LOGICA DEL ESCUDO (RESTAURADA DEL CÓDIGO ORIGINAL)
# ==============================================================================
def get_escudo_html():
    """
    Busca 'Captura.JPG' localmente. Si no existe, usa la URL de respaldo.
    Genera el HTML exacto para que se vea.
    """
    img_html = ""
    # 1. Intento Local (Tu archivo original)
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                img_html = f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except:
            pass
    
    # 2. Respaldo Web (Si no hay local)
    if not img_html:
        url = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"
        img_html = f'<img src="{url}" class="escudo-img">'
        
    return img_html

escudo_html = get_escudo_html()

# ==============================================================================
# 3. ESTILOS CSS (TEMA BLANCO / LIGHT MODE)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@400;500;700&display=swap');

    /* --- FONDO BLANCO GENERAL --- */
    .stApp {
        background-color: #f4f6f9; /* Gris muy suave, casi blanco */
        background-image: linear-gradient(135deg, #ffffff 0%, #eef2f3 100%);
        color: #1a2a3a; /* Texto oscuro para contraste */
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; max-width: 98% !important; }

    /* --- CABECERA (HEADER) BLANCA --- */
    .header-box {
        text-align: center;
        padding: 40px;
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); /* Sombra suave elegante */
        border-bottom: 4px solid #0E2F44; /* Línea Azul Policial */
        margin-bottom: 50px;
    }
    
    /* IMAGEN ESCUDO */
    .escudo-img {
        width: 130px;
        height: auto;
        margin-bottom: 20px;
        filter: drop-shadow(0 5px 5px rgba(0,0,0,0.1));
    }

    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: #0E2F44; /* Azul Oscuro Institucional */
        margin: 0;
        line-height: 1;
        letter-spacing: 2px;
    }
    
    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        color: #D4AF37; /* Dorado */
        letter-spacing: 4px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 700;
    }

    /* --- BOTONES UNIFORMES (ESTILO LIGHT) --- */
    div.stButton > button {
        /* Fondo Azul Oscuro para que contraste con el blanco de la página */
        background: linear-gradient(180deg, #0E2F44 0%, #081b29 100%) !important;
        border: 1px solid #1a4f70 !important;
        border-radius: 15px !important;
        color: #ffffff !important;
        
        /* DIMENSIONES EXACTAS (1x4) */
        width: 100% !important;
        height: 160px !important;      
        min-height: 160px !important;
        max-height: 160px !important;
        
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px !important;
        
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        white-space: normal !important;
        text-align: center !important;
        
        transition: all 0.2s ease !important;
        box-shadow: 0 8px 15px rgba(14, 47, 68, 0.2) !important;
    }

    /* EFECTO HOVER */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background: linear-gradient(180deg, #154666 0%, #0E2F44 100%) !important;
        border-color: #D4AF37 !important; /* Borde Dorado al pasar el mouse */
        box-shadow: 0 15px 25px rgba(14, 47, 68, 0.3) !important;
    }

    /* ICONOS (EMOJIS) */
    div.stButton > button::before {
        font-size: 45px;
        margin-bottom: 10px;
        filter: grayscale(0%); /* A color para que se vean bien sobre azul */
        display: block;
    }

    /* ASIGNACIÓN DE ICONOS */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER */
    .dev-footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #ffffff; 
        border-top: 1px solid #e0e0e0; 
        padding: 12px;
        font-family: 'Roboto', monospace; 
        font-size: 11px; 
        color: #546e7a;
        z-index: 9999;
    }
    .dev-footer b { color: #0E2F44; margin: 0 5px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

# CABECERA
st.markdown(f"""
    <div class="header-box">
        {escudo_html}
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# GRID DE BOTONES (1 FILA x 4 COLUMNAS)
c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    if st.button("SECRETARIO/A"):
        st.toast("Cargando...", icon="📝")

with c2:
    if st.button("TALENTO HUMANO"):
        st.toast("Accediendo...", icon="👤")

with c3:
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("IA Activada...", icon="🤖")

with c4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Login Admin...", icon="🛡️")

# FOOTER
st.markdown("""
    <div class="dev-footer">
        SIGD DINIC v10.0 | DESARROLLADO POR: <b>JSCN</b> | CORREO: <b>cnjstalin@gmail.com</b> | SOPORTE: <b>0996652042</b>
    </div>
""", unsafe_allow_html=True)
