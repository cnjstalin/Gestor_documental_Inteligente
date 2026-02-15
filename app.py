import streamlit as st
import base64
import requests
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
# 2. FUNCIÓN DE RECUPERACIÓN DE ESCUDO (CÓDIGO BASE RESTAURADO)
# ==============================================================================
def get_escudo_b64():
    # 1. Intenta cargar imagen local 'Captura.JPG' (Prioridad Código Base)
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: pass
    
    # 2. Si no hay local, intenta descargar de Wikipedia y convertir a Base64
    url = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"
    try:
        return base64.b64encode(requests.get(url).content).decode()
    except:
        return None

# Obtenemos la imagen procesada
escudo_b64 = get_escudo_b64()
img_tag = f'<img src="data:image/png;base64,{escudo_b64}" class="escudo-img">' if escudo_b64 else '<div style="font-size:50px">🛡️</div>'

# ==============================================================================
# 3. ESTILOS CSS (GRID 1x4 UNIFORME Y CABECERA)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@300;400;500&display=swap');

    .stApp {
        background-color: #050a10;
        background-image: radial-gradient(circle at 50% 20%, #1a253a 0%, #050a10 80%);
        color: #e0e0e0;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; max-width: 95% !important; }

    /* CABECERA */
    .header-box {
        text-align: center;
        padding: 30px;
        background: rgba(13, 20, 28, 0.9);
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 20px 20px;
    }
    
    .escudo-img {
        width: 140px;
        filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.6));
        margin-bottom: 15px;
    }
    
    .main-title { font-family: 'Rajdhani', sans-serif; font-size: 3.5rem; font-weight: 800; color: white; margin: 0; line-height: 1; text-shadow: 0 0 20px rgba(0, 188, 212, 0.6); }
    .sub-title { font-family: 'Roboto', sans-serif; font-size: 1.1rem; color: #D4AF37; letter-spacing: 4px; margin-top: 10px; font-weight: 500; }

    /* BOTONES - GRID PERFECTO */
    div.stButton > button {
        background: linear-gradient(180deg, #1e2a38 0%, #101820 100%) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        
        /* FUERZA UNIFORMIDAD */
        width: 100% !important;
        height: 160px !important;      
        min-height: 160px !important;
        
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px !important;
        
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.2s !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3) !important;
    }

    /* ICONOS */
    div.stButton > button::before {
        font-size: 45px;
        margin-bottom: 10px;
        filter: grayscale(100%) opacity(0.8);
        transition: 0.3s;
        display: block;
    }
    div.stButton > button:hover::before { filter: grayscale(0%) opacity(1); transform: scale(1.1); }

    /* ASIGNACIÓN DE ICONOS */
    div.row-widget.stButton:nth-of-type(1) button::before { content: "📝"; }
    div.row-widget.stButton:nth-of-type(2) button::before { content: "👤"; }
    div.row-widget.stButton:nth-of-type(3) button::before { content: "🤖"; }
    div.row-widget.stButton:nth-of-type(4) button::before { content: "🛡️"; }

    /* FOOTER */
    .dev-footer {
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #080c10; padding: 10px; border-top: 1px solid #333;
        font-family: 'Roboto', monospace; font-size: 11px; color: #607d8b;
        z-index: 9999;
    }
    .dev-footer b { color: #D4AF37; margin: 0 5px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================

# CABECERA
st.markdown(f"""
    <div class="header-box">
        {img_tag}
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
        SIGD DINIC v9.0 | DESARROLLADO POR: <b>JSCN</b> | CORREO: <b>cnjstalin@gmail.com</b> | SOPORTE: <b>0996652042</b>
    </div>
""", unsafe_allow_html=True)
