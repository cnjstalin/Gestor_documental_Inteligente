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
# 2. LOGICA ESCUDO
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
# 3. ESTILOS CSS (ELEGANCIA Y MÁRGENES)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* FONDO GRIS MUY SUAVE (PREMIUM) */
    .stApp {
        background-color: #f4f6f8;
        background-image: linear-gradient(to bottom, #ffffff 0%, #eff3f6 100%);
        color: #2c3e50;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* CABECERA */
    .header-box {
        text-align: center;
        padding-top: 40px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .escudo-img {
        width: 130px;
        height: auto;
        margin-bottom: 20px;
        filter: drop-shadow(0 5px 10px rgba(0,0,0,0.1)); /* Sombra suave al escudo */
    }

    .main-title {
        font-family: 'Roboto', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #0E2F44;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #D4AF37;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 5px;
        border-bottom: 2px solid #e1e4e8;
        padding-bottom: 20px;
        width: 100%;
        text-align: center;
    }

    /* --- BOTONES ESTILO "TARJETA EJECUTIVA" --- */
    div.stButton > button {
        /* APARIENCIA BASE */
        background-color: #ffffff !important; /* Blanco Puro */
        color: #0E2F44 !important; /* Texto Azul */
        border: 1px solid #e1e4e8 !important; /* Borde muy sutil */
        border-left: 8px solid #0E2F44 !important; /* BARRA LATERAL AZUL (El toque elegante) */
        border-radius: 8px !important;
        
        /* DIMENSIONES Y MÁRGENES */
        width: 100% !important;
        height: 80px !important;      
        margin-bottom: 20px !important; /* <--- AQUÍ ESTÁ EL MARGEN ELEGANTE */
        
        /* ALINEACIÓN */
        display: flex !important;
        justify-content: flex-start !important; /* Alineado a la izquierda */
        align-items: center !important;
        padding-left: 30px !important; /* Espacio para el texto */
        
        /* TIPOGRAFÍA */
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        /* SOMBRA SUAVE (Efecto flotante) */
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }

    /* HOVER (INTERACCIÓN) */
    div.stButton > button:hover {
        background-color: #ffffff !important;
        border-left: 8px solid #D4AF37 !important; /* La barra se vuelve DORADA */
        transform: translateX(5px); /* Se mueve un poco a la derecha */
        box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; /* Sombra más fuerte */
        color: #0E2F44 !important;
    }

    /* ICONOS */
    div.stButton > button::before { 
        content: "➤"; /* Icono sutil */
        margin-right: 15px;
        color: #b0b0b0;
        font-size: 18px;
    }
    div.stButton > button:hover::before { 
        color: #D4AF37; 
    }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #fff; border-top: 1px solid #eee; padding: 15px;
        font-size: 11px; color: #aaa; font-family: monospace;
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

# CONTENEDOR CENTRAL (COLUMNA ESTRECHA PARA ELEGANCIA)
# Usamos [1, 0.8, 1]. El 0.8 hace que el menú no sea ni muy ancho ni muy angosto.
izq, centro, der = st.columns([1, 0.8, 1])

with centro:
    if st.button("SECRETARIO/A"):
        st.toast("Iniciando...", icon="📝")

    if st.button("TALENTO HUMANO"):
        st.toast("Iniciando...", icon="👤")

    if st.button("GENERADOR"):
        st.toast("Iniciando...", icon="🤖")

    if st.button("ADMINISTRACIÓN"):
        st.toast("Iniciando...", icon="🛡️")

# FOOTER
st.markdown("""
    <div class="footer">
        SIGD DINIC v19.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
    </div>
""", unsafe_allow_html=True)
