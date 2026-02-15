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
# 3. ESTILOS CSS (CENTRADO MILIMÉTRICO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* FONDO BLANCO */
    .stApp { background-color: #ffffff; color: #212529; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA */
    .header-box {
        text-align: center;
        padding-top: 50px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        align-items: center; /* Centra el contenido de la caja */
    }
    
    .escudo-img {
        width: 140px;
        height: auto;
        margin-bottom: 20px;
        display: block;
    }

    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #0E2F44;
        margin: 0;
        line-height: 1;
        text-align: center;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #D4AF37;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 10px;
        text-align: center;
        width: 100%;
    }

    /* SEPARADOR ELEGANTE */
    .separator {
        width: 100px;
        height: 4px;
        background-color: #0E2F44;
        margin: 20px auto 40px auto; /* Auto en los lados centra el div */
        border-radius: 2px;
    }

    /* --- BOTONES: CENTRADO ABSOLUTO --- */
    div.stButton {
        text-align: center; /* Asegura que el contenedor del botón centre */
    }

    div.stButton > button {
        /* ESTILO: Solo texto */
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #0E2F44 !important;
        
        /* DIMENSIONES EXACTAS */
        width: 100% !important;
        height: 70px !important;
        margin: 0 auto !important; /* Margen automático para centrar bloque */
        
        /* FLEXBOX: LA CLAVE DEL CENTRADO */
        display: flex !important;
        justify-content: center !important; /* Centra horizontalmente el texto */
        align-items: center !important;     /* Centra verticalmente el texto */
        
        /* TIPOGRAFÍA */
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.2s ease !important;
    }

    div.stButton > button:hover {
        background-color: #f8f9fa !important;
        color: #D4AF37 !important;
        border-radius: 50px !important; /* Redondeado suave al pasar mouse */
        transform: scale(1.05);
    }

    /* ELIMINAR ICONOS RAROS */
    div.stButton > button::before { content: none !important; }
    div.stButton > button::after { content: none !important; }
    div.stButton > button p { font-size: 1.3rem !important; }

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

# 1. CABECERA
st.markdown(f"""
    <div class="header-box">
        {escudo_render}
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
    <div class="separator"></div>
""", unsafe_allow_html=True)

# 2. CONTENEDOR DE BOTONES (CENTRADO PERFECTO)
# Usamos una proporción donde el centro es estrecho (0.6) para obligar a los botones a alinearse
# [Espacio Vacío, Carril Central, Espacio Vacío]
izq, centro, der = st.columns([1, 0.6, 1])

with centro:
    # Usamos emojis en el texto para garantizar alineación junto con la palabra
    if st.button("📝 SECRETARIO/A"):
        st.toast("Cargando...", icon="✅")

    if st.button("👤 TALENTO HUMANO"):
        st.toast("Cargando...", icon="✅")

    if st.button("🤖 GENERADOR DOCUMENTAL"):
        st.toast("Cargando...", icon="✅")

    if st.button("🛡️ ADMINISTRACIÓN"):
        st.toast("Cargando...", icon="✅")

# 3. FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v17.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
    </div>
""", unsafe_allow_html=True)
