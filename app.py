import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# URL ESCUDO (ENLACE DIRECTO)
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS (GRID PERFECTO 1x4)
# ==============================================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@400;500&display=swap');

    /* FONDO DE PANTALLA */
    .stApp {{
        background-color: #050a10;
        background-image: 
            radial-gradient(circle at 50% 0%, #1a253a 0%, #050a10 85%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 50px 50px, 50px 50px;
        color: #e0e0e0;
    }}
    
    /* LIMPIEZA */
    #MainMenu, footer, header {{visibility: hidden;}}
    [data-testid="collapsedControl"] {{display: none;}}
    .block-container {{ padding-top: 2rem !important; max-width: 95% !important; }}
    
    /* --- CABECERA INTEGRADA (HTML PURO PARA QUE SALGA SÍ O SÍ) --- */
    .header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background: rgba(13, 20, 28, 0.85);
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        margin-bottom: 50px;
    }}
    
    /* IMAGEN ESCUDO FORZADA */
    .escudo-img {{
        width: 140px;
        height: auto;
        filter: drop-shadow(0 0 25px rgba(212, 175, 55, 0.5));
        margin-bottom: 25px;
    }}
    
    .main-title {{
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem; 
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin: 0;
        text-shadow: 0 0 30px rgba(0, 188, 212, 0.5);
        line-height: 1;
    }}
    
    .sub-title {{
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        color: #D4AF37; /* DORADO */
        letter-spacing: 3px;
        margin-top: 15px;
        text-transform: uppercase;
        font-weight: 500;
        border-top: 2px solid rgba(212, 175, 55, 0.3);
        padding-top: 15px;
        width: 60%;
        text-align: center;
    }}

    /* --- BOTONES: UNIFORMIDAD TOTAL (140px ALTURA) --- */
    div.stButton > button {{
        background: linear-gradient(180deg, rgba(30, 40, 50, 0.9), rgba(15, 20, 25, 0.95)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 12px !important;
        color: #fff !important;
        
        /* FUERZA BRUTA PARA TAMAÑO EXACTO */
        width: 100% !important;
        height: 140px !important;
        min-height: 140px !important;
        max-height: 140px !important;
        
        display: flex !important;
        flex-direction: column !important; /* Icono arriba, Texto abajo */
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        gap: 10px;

        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    }}

    div.stButton > button:hover {{
        transform: translateY(-5px) !important;
        background: linear-gradient(180deg, #1e3c50, #102030) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.4) !important;
    }}

    /* ICONOS */
    div.stButton > button::before {{
        font-size: 40px;
        filter: grayscale(100%) opacity(0.8);
        transition: 0.3s;
        margin-bottom: 5px;
    }}
    div.stButton > button:hover::before {{ filter: grayscale(0%) opacity(1); transform: scale(1.1); }}

    /* ASIGNACIÓN DE ICONOS */
    div.row-widget.stButton:nth-of-type(1) button::before {{ content: "📝"; }}
    div.row-widget.stButton:nth-of-type(2) button::before {{ content: "👤"; }}
    div.row-widget.stButton:nth-of-type(3) button::before {{ content: "🤖"; }}
    div.row-widget.stButton:nth-of-type(4) button::before {{ content: "🛡️"; }}

    /* FOOTER */
    .footer-dev {{
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: #080c10; border-top: 1px solid #333; padding: 10px;
        font-family: 'Roboto', monospace; font-size: 11px; color: #546e7a;
        z-index: 9999;
    }}
    .footer-dev span {{ color: #D4AF37; font-weight: bold; margin: 0 5px; }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ VISUAL
# ==============================================================================

# --- CABECERA (HTML PURO) ---
# Al usar HTML directo con la etiqueta <img>, evitamos que Streamlit bloquee la imagen
st.markdown(f"""
    <div class="header-container">
        <img src="{URL_ESCUDO}" class="escudo-img">
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# --- GRID DE BOTONES (4 COLUMNAS UNIFORMES) ---
# Usamos 'gap="small"' para que quepan mejor en una sola fila
c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    if st.button("SECRETARIO/A"):
        st.toast("Cargando Módulo...", icon="📝")

with c2:
    if st.button("TALENTO HUMANO"):
        st.toast("Verificando Acceso...", icon="👤")

with c3:
    if st.button("GENERADOR DOC."): # Abreviado para mantener estética
        st.toast("Iniciando IA...", icon="🤖")

with c4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Acceso Restringido", icon="🛡️")

# --- FOOTER DE DESARROLLADOR ---
st.markdown("""
    <div class="footer-dev">
        VERSIÓN DEL SISTEMA: <span>v1.0.0</span> | 
        DESARROLLADO POR: <span>JSCN</span> | 
        CORREO: <span>cnjstalin@gmail.com</span> | 
        SOPORTE: <span>0996652042</span>
    </div>
""", unsafe_allow_html=True)
