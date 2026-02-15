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
# 2. LOGICA DEL ESCUDO (INFALIBLE)
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
# 3. ESTILOS CSS (GEOMETRÍA PERFECTA)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* FONDO GENERAL */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA */
    .header-box {
        text-align: center;
        padding: 40px;
        background: white;
        border-bottom: 4px solid #0E2F44; 
        margin-bottom: 40px;
    }
    
    .escudo-img {
        width: 140px;
        height: auto;
        margin-bottom: 20px;
    }

    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #0E2F44;
        margin: 0;
        line-height: 1.2;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #D4AF37;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 10px;
    }

    /* --- BOTONES PERFECTOS --- */
    div.stButton > button {
        /* ESTILO VISUAL */
        background: white !important;
        border: 2px solid #e0e0e0 !important;
        color: #0E2F44 !important;
        border-radius: 10px !important;
        
        /* GEOMETRÍA FIJA (AQUÍ ESTÁ EL TRUCO) */
        width: 100% !important;
        height: 100px !important;      /* Altura exacta para todos */
        min-height: 100px !important;  /* No encoger */
        max-height: 100px !important;  /* No crecer */
        margin-bottom: 15px !important; /* Espacio entre botones */
        
        /* ALINEACIÓN DE TEXTO */
        display: flex !important;
        justify-content: center !important; /* Centrado Horizontal */
        align-items: center !important;     /* Centrado Vertical */
        text-align: center !important;
        
        /* TIPOGRAFÍA */
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }

    /* HOVER (EFECTO AL PASAR MOUSE) */
    div.stButton > button:hover {
        background: #0E2F44 !important;
        color: white !important;
        border-color: #D4AF37 !important;
        transform: scale(1.02);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
    }

    /* ELIMINAR CUALQUIER ICONO O ROMBO */
    div.stButton > button::before { content: none !important; }
    div.stButton > button::after { content: none !important; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #fff; border-top: 1px solid #ddd; padding: 15px;
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

# CONTENEDOR CENTRAL (COLUMNA ÚNICA)
# Usamos columnas [1, 2, 1] para centrar el bloque de botones en la mitad de la pantalla
izq, centro, der = st.columns([1, 2, 1])

with centro:
    # Botón 1
    if st.button("SECRETARIO/A"):
        st.toast("Cargando...", icon="📝")
        # st.session_state.active_module = 'secretario'
        # st.rerun()

    # Botón 2
    if st.button("TALENTO HUMANO"):
        st.toast("Cargando...", icon="👤")
        # st.session_state.active_module = 'th'
        # st.rerun()

    # Botón 3
    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Cargando...", icon="🤖")
        # st.session_state.active_module = 'ia'
        # st.rerun()

    # Botón 4
    if st.button("ADMINISTRACIÓN"):
        st.toast("Cargando...", icon="🛡️")
        # st.session_state.active_module = 'admin'
        # st.rerun()

# FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v13.0 | DESARROLLADO POR: <b>JSCN</b> | cnjstalin@gmail.com | SOPORTE: 0996652042
    </div>
""", unsafe_allow_html=True)
