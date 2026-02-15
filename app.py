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
# 2. ESCUDO (HTML PURO)
# ==============================================================================
def get_escudo_html():
    # Intento 1: Local
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    # Intento 2: Web (Enlace directo PNG)
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

escudo_render = get_escudo_html()

# ==============================================================================
# 3. ESTILOS CSS (MINIMALISTA Y CENTRADO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* FONDO BLANCO */
    .stApp {
        background-color: #ffffff;
        color: #212529;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA CENTRADA */
    .header-box {
        text-align: center;
        padding-top: 40px;
        padding-bottom: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
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
        color: #0E2F44; /* Azul Policial */
        margin: 0;
        line-height: 1.2;
        text-transform: uppercase;
        text-align: center;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #D4AF37; /* Dorado */
        font-weight: 400;
        letter-spacing: 4px;
        margin-top: 10px;
        margin-bottom: 30px; /* Espacio antes de los botones */
        text-align: center;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 15px;
        width: 100%;
    }

    /* --- BOTONES INVISIBLES CENTRADOS --- */
    div.stButton > button {
        /* ESTILO: Solo texto, sin caja */
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #0E2F44 !important; /* Texto Azul */
        
        /* DIMENSIONES EXACTAS */
        width: 100% !important;
        height: 70px !important;      /* Altura fija */
        margin: 0 auto !important;    /* Centrado automático */
        margin-bottom: 10px !important;
        
        /* ALINEACIÓN DE TEXTO */
        display: flex !important;
        justify-content: center !important; /* Centrado Horizontal */
        align-items: center !important;     /* Centrado Vertical */
        
        /* TIPOGRAFÍA */
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.2s ease !important;
    }

    /* HOVER (EFECTO AL PASAR EL MOUSE) */
    div.stButton > button:hover {
        background-color: #f4f6f9 !important; /* Gris muy muy suave */
        color: #D4AF37 !important; /* Dorado */
        transform: scale(1.05); /* Zoom sutil */
        border-radius: 8px !important;
    }

    /* ELIMINAR ICONOS EXTRAÑOS */
    div.stButton > button::before { content: none !important; }
    div.stButton > button::after { content: none !important; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #fff; border-top: 1px solid #eee; padding: 15px;
        font-size: 11px; color: #aaa; font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

# --- CANAL CENTRAL (COLUMNAS) ---
# Usamos [1, 1.5, 1] para crear un carril central perfecto donde irá todo.
izq, centro, der = st.columns([1, 1.5, 1])

with centro:
    # 1. ESCUDO Y TÍTULOS (Dentro de la misma columna que los botones para alineación perfecta)
    st.markdown(f"""
        <div class="header-box">
            {escudo_render}
            <div class="main-title">SIGD DINIC</div>
            <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. BOTONES (Justo debajo, en el mismo eje)
    # Agregamos los iconos como emojis dentro del texto para que se centren junto con las letras
    
    if st.button("📝 SECRETARIO/A"):
        st.toast("Iniciando...", icon="✅")
        # st.session_state.modulo = 'secretario'; st.rerun()

    if st.button("👤 TALENTO HUMANO"):
        st.toast("Iniciando...", icon="✅")
        # st.session_state.modulo = 'th'; st.rerun()

    if st.button("🤖 GENERADOR DOCUMENTAL"):
        st.toast("Iniciando...", icon="✅")
        # st.session_state.modulo = 'ia'; st.rerun()

    if st.button("🛡️ ADMINISTRACIÓN"):
        st.toast("Iniciando...", icon="✅")
        # st.session_state.modulo = 'admin'; st.rerun()

# FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v16.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
    </div>
""", unsafe_allow_html=True)
