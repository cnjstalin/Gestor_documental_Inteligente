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
# 2. LÓGICA DE ESCUDO (INFALIBLE)
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
# 3. ESTILOS CSS (DISEÑO VERTICAL LIMPIO)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* FONDO BLANCO LIMPIO */
    .stApp {
        background-color: #f8f9fa;
        background-image: linear-gradient(to bottom, #ffffff, #e9ecef);
        color: #212529;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA */
    .header-box {
        text-align: center;
        padding: 30px 20px;
        background: white;
        border-bottom: 4px solid #0E2F44; /* Azul Policial */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border-radius: 0 0 20px 20px;
    }
    
    .escudo-img {
        width: 120px;
        height: auto;
        margin-bottom: 15px;
    }

    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #0E2F44;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #D4AF37; /* Dorado */
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* --- BOTONES VERTICALES (ESTILO LISTA) --- */
    div.stButton > button {
        background: white !important;
        border: 1px solid #ced4da !important;
        border-left: 8px solid #0E2F44 !important; /* Borde izquierdo azul */
        color: #0E2F44 !important;
        border-radius: 8px !important;
        
        /* DIMENSIONES UNIFORMES */
        width: 100% !important;
        height: 80px !important;      /* Altura cómoda */
        margin-bottom: 10px !important;
        
        /* ALINEACIÓN (Icono Izq - Texto Centro) */
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important; /* Alinear contenido a la izq */
        padding-left: 30px !important;
        gap: 20px;

        font-family: 'Roboto', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }

    /* HOVER (EFECTO AL PASAR EL MOUSE) */
    div.stButton > button:hover {
        background: #0E2F44 !important; /* Fondo Azul */
        color: white !important;         /* Texto Blanco */
        border-left: 8px solid #D4AF37 !important; /* Borde Dorado */
        padding-left: 40px !important;   /* Pequeño desplazamiento */
        transform: scale(1.02);
    }

    /* ICONOS */
    div.stButton > button::before {
        font-size: 30px;
        margin-right: 15px;
        content: "🔹"; /* Icono por defecto si falla el CSS específico */
    }

    /* Asignar Iconos Específicos */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #fff; border-top: 1px solid #ddd; padding: 10px;
        font-size: 11px; color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================

# CABECERA
st.markdown(f"""
    <div class="header-box">
        {escudo_render}
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# CONTENEDOR CENTRAL (COLUMNA ESTRECHA PARA MENÚ VERTICAL)
# Usamos columnas [1, 2, 1] para centrar el menú en la pantalla
izq, centro, der = st.columns([1, 2, 1])

with centro:
    st.markdown("### SELECCIONE UN MÓDULO")
    
    if st.button("SECRETARIO/A"):
        st.toast("Cargando Secretaría...", icon="📝")
        # st.session_state.active_module = 'secretario'
        # st.rerun()

    if st.button("TALENTO HUMANO"):
        st.toast("Cargando TH...", icon="👤")
        # st.session_state.active_module = 'th'
        # st.rerun()

    if st.button("GENERADOR DOCUMENTAL"):
        st.toast("Cargando IA...", icon="🤖")
        # st.session_state.active_module = 'ia'
        # st.rerun()

    if st.button("ADMINISTRACIÓN"):
        st.toast("Solicitando Acceso...", icon="🛡️")
        # st.session_state.active_module = 'admin'
        # st.rerun()

# FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v12.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
    </div>
""", unsafe_allow_html=True)
