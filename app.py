import streamlit as st
import base64
import os

# ==============================================================================
# 1. CONFIGURACIÓN
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. ESCUDO (HTML PURO PARA QUE SE VEA SIEMPRE)
# ==============================================================================
def get_escudo_html():
    # Intento 1: Local
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    # Intento 2: Web
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

escudo_render = get_escudo_html()

# ==============================================================================
# 3. ESTILOS CSS (GEOMETRÍA PERFECTA Y CENTRADO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500;700&display=swap');

    /* FONDO BLANCO */
    .stApp {
        background-color: #ffffff;
        color: #212529;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA */
    .header-box {
        text-align: center;
        padding-top: 20px;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    
    .escudo-img {
        width: 140px;
        height: auto;
        margin-bottom: 15px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #0E2F44; /* Azul Policial */
        margin: 0;
        line-height: 1.2;
        text-transform: uppercase;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #D4AF37; /* Dorado */
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 5px;
        text-transform: uppercase;
    }

    /* --- BOTONES: UNIFORMIDAD TOTAL --- */
    div.stButton > button {
        /* APARIENCIA */
        background: white !important;
        border: 2px solid #0E2F44 !important; /* Borde Azul */
        color: #0E2F44 !important;
        border-radius: 12px !important;
        
        /* TAMAÑO EXACTO PARA TODOS (FORZADO) */
        width: 100% !important;
        height: 100px !important;      /* Altura fija igual para todos */
        min-height: 100px !important;
        max-height: 100px !important;
        margin-bottom: 15px !important;
        
        /* ALINEACIÓN DE TEXTO */
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important; /* Centrado Vertical */
        align-items: center !important;     /* Centrado Horizontal */
        text-align: center !important;
        
        /* TIPOGRAFÍA */
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        white-space: pre-wrap !important; /* Permite que el texto baje si es largo */
        
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* HOVER (MOUSE ENCIMA) */
    div.stButton > button:hover {
        background: #0E2F44 !important;
        color: white !important;
        border-color: #D4AF37 !important;
        transform: scale(1.02);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2) !important;
    }

    /* ELIMINAR CUALQUIER ELEMENTO EXTRAÑO (ROMBOS) */
    div.stButton > button::before { content: none !important; display: none !important; }
    div.stButton > button::after { content: none !important; display: none !important; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #f8f9fa; border-top: 1px solid #ddd; padding: 15px;
        font-size: 12px; color: #666; font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

# CABECERA
st.markdown(f"""
    <div class="header-box">
        {escudo_render}
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# --- COLUMNA CENTRAL PARA ALINEACIÓN PERFECTA ---
# Usamos [1, 2, 1] para que los botones queden en el medio (ocupando el 50% del ancho)
izq, centro, der = st.columns([1, 2, 1])

with centro:
    # Botón 1
    if st.button("SECRETARIO/A"):
        st.toast("Cargando...", icon="📝")
        # st.session_state.active_module = 'secretario'; st.rerun()

    # Botón 2
    if st.button("TALENTO HUMANO"):
        st.toast("Cargando...", icon="👤")
        # st.session_state.active_module = 'th'; st.rerun()

    # Botón 3 (El que definía el tamaño, ahora todos son iguales a este)
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Cargando...", icon="🤖")
        # st.session_state.active_module = 'ia'; st.rerun()

    # Botón 4
    if st.button("ADMINISTRACIÓN"):
        st.toast("Cargando...", icon="🛡️")
        # st.session_state.active_module = 'admin'; st.rerun()

# FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v14.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
    </div>
""", unsafe_allow_html=True)
