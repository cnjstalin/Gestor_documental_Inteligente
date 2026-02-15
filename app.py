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
# 2. ESCUDO
# ==============================================================================
def get_escudo_html():
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

escudo_render = get_escudo_html()

# ==============================================================================
# 3. ESTILOS CSS (MINIMALISMO PURO - SOLO TEXTO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;700&display=swap');

    /* FONDO BLANCO PURO */
    .stApp {
        background-color: #ffffff;
        color: #212529;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA */
    .header-box {
        text-align: center;
        padding: 40px 20px;
        background: white;
        margin-bottom: 20px;
    }
    
    .escudo-img {
        width: 140px;
        height: auto;
        margin-bottom: 20px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #0E2F44; /* Azul Institucional */
        margin: 0;
        line-height: 1.2;
        text-transform: uppercase;
        text-align: center;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #D4AF37; /* Dorado */
        font-weight: 300;
        letter-spacing: 4px;
        margin-top: 10px;
        text-align: center;
        border-bottom: 1px solid #eee;
        padding-bottom: 20px;
    }

    /* --- BOTONES INVISIBLES (SOLO TEXTO) --- */
    div.stButton > button {
        /* QUITAR BORDE Y FONDO */
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #0E2F44 !important; /* Texto Azul */
        
        /* DIMENSIONES FIJAS PARA UNIFORMIDAD */
        width: 100% !important;
        height: 80px !important;      /* Altura fija */
        margin-bottom: 5px !important;
        
        /* ALINEACIÓN PERFECTA */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        
        /* TIPOGRAFÍA */
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.5rem !important; /* Letra grande */
        font-weight: 700 !important;  /* Negrita */
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        
        transition: all 0.3s ease !important;
    }

    /* HOVER (SOLO CAMBIA DE COLOR SUAVEMENTE) */
    div.stButton > button:hover {
        background-color: #f8f9fa !important; /* Gris muy tenue al pasar mouse */
        color: #D4AF37 !important; /* Texto se vuelve dorado */
        transform: scale(1.05); /* Crece un poquito */
        border-radius: 10px !important;
    }

    /* QUITAR ICONOS EXTRAÑOS CSS */
    div.stButton > button::before { content: none !important; }
    div.stButton > button::after { content: none !important; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #fff; border-top: 1px solid #f0f0f0; padding: 15px;
        font-size: 11px; color: #999; font-family: monospace;
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

# --- COLUMNA CENTRAL (CENTRADO PERFECTO) ---
# Usamos [1, 2, 1] para centrar. El 2 es el ancho del menú.
izq, centro, der = st.columns([1, 2, 1])

with centro:
    # Agregamos los iconos directamente en el texto del botón para alineación perfecta
    if st.button("📝 SECRETARIO/A"):
        st.toast("Cargando...", icon="✅")
        # st.session_state.active_module = 'secretario'; st.rerun()

    if st.button("👤 TALENTO HUMANO"):
        st.toast("Cargando...", icon="✅")
        # st.session_state.active_module = 'th'; st.rerun()

    if st.button("🤖 GENERADOR DOCUMENTAL"):
        st.toast("Cargando...", icon="✅")
        # st.session_state.active_module = 'ia'; st.rerun()

    if st.button("🛡️ ADMINISTRACIÓN"):
        st.toast("Cargando...", icon="✅")
        # st.session_state.active_module = 'admin'; st.rerun()

# FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v15.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
    </div>
""", unsafe_allow_html=True)
