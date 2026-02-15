import streamlit as st
import base64
import os

# ==============================================================================
# 1. CONFIGURACIÓN "WIDE" REAL
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. LÓGICA DE ESCUDO (INFALIBLE)
# ==============================================================================
def get_escudo_html():
    # 1. Intento Local
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    
    # 2. Respaldo Web (Directo)
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

escudo_render = get_escudo_html()

# ==============================================================================
# 3. ESTILOS CSS (GEOMETRÍA ESTRICTA)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@400;500;700&display=swap');

    /* --- FONDO BLANCO --- */
    .stApp {
        background-color: #f4f7f6;
        background-image: linear-gradient(to bottom, #ffffff, #eef2f3);
        color: #1a2a3a;
    }
    
    /* --- LIMPIEZA DE MÁRGENES (FILO A FILO REAL) --- */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important; /* OCUPA TODA LA PANTALLA */
    }

    /* --- CABECERA --- */
    .header-box {
        text-align: center;
        padding: 30px;
        background: #ffffff;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-bottom: 5px solid #0E2F44;
        margin-bottom: 40px;
    }
    
    .escudo-img {
        width: 120px;
        height: auto;
        margin-bottom: 15px;
    }

    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: #0E2F44;
        margin: 0;
        line-height: 1;
    }
    
    .sub-title {
        font-family: 'Roboto', sans-serif;
        font-size: 1.1rem;
        color: #D4AF37;
        letter-spacing: 4px;
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: 700;
    }

    /* --- BOTONES: GEOMETRÍA FIJA (LA SOLUCIÓN A LA DISFORMIDAD) --- */
    div.stButton > button {
        background: linear-gradient(180deg, #0E2F44 0%, #0a1f2e 100%) !important;
        border: 1px solid #1a4f70 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        
        /* FUERZA BRUTA: ALTO Y ANCHO */
        width: 100% !important;         /* Llena la columna */
        height: 150px !important;       /* ALTO FIJO: Todos medirán 150px */
        min-height: 150px !important;   /* No se encogen */
        max-height: 150px !important;   /* No crecen */
        
        /* ALINEACIÓN DEL CONTENIDO */
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        
        /* TEXTO */
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        white-space: pre-wrap !important; /* Permite 2 líneas si es necesario */
        line-height: 1.2 !important;
        
        transition: all 0.2s ease !important;
        box-shadow: 0 5px 15px rgba(14, 47, 68, 0.2) !important;
    }

    /* EFECTO HOVER */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background: linear-gradient(180deg, #154666 0%, #0E2F44 100%) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 10px 25px rgba(14, 47, 68, 0.4) !important;
    }

    /* ICONOS (EMOJIS) DENTRO DEL BOTÓN */
    div.stButton > button::before {
        font-size: 40px;
        margin-bottom: 5px;
        filter: grayscale(0%);
        display: block;
        line-height: 1;
    }

    /* Asignar Iconos */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER */
    .dev-footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #ffffff; border-top: 1px solid #e0e0e0; padding: 10px;
        font-family: 'Roboto', monospace; font-size: 11px; color: #546e7a; z-index: 9999;
    }
    .dev-footer b { color: #0E2F44; margin: 0 5px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ VISUAL
# ==============================================================================

# CABECERA
st.markdown(f"""
    <div class="header-box">
        {escudo_render}
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# GRID 1 FILA x 4 COLUMNAS (FILO A FILO)
# Usamos columnas nativas. El CSS de arriba fuerza que los botones dentro sean idénticos.
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("SECRETARIO/A"):
        st.toast("Cargando...", icon="📝")

with c2:
    if st.button("TALENTO HUMANO"):
        st.toast("Accediendo...", icon="👤")

with c3:
    # Agregamos \n para forzar salto de línea controlado y que se vea igual a los otros
    if st.button("GENERADOR\nDOCUMENTAL"): 
        st.toast("IA Activada...", icon="🤖")

with c4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Login Admin...", icon="🛡️")

# FOOTER
st.markdown("""
    <div class="dev-footer">
        SIGD DINIC v11.0 | DESARROLLADO POR: <b>JSCN</b> | CORREO: <b>cnjstalin@gmail.com</b> | SOPORTE: <b>0996652042</b>
    </div>
""", unsafe_allow_html=True)
