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

# URL ESCUDO TRANSPARENTE (PNG OFICIAL)
# Esta versión NO tiene fondo blanco, se adaptará al fondo de la App.
URL_ESCUDO = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Escudo_Policia_Nacional_del_Ecuador.png/600px-Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS (TEMA OSCURO TÁCTICO)
# ==============================================================================
st.markdown(f"""
    <style>
    /* FUENTES OFICIALES */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;800&family=Roboto:wght@300;400;500&display=swap');

    /* FONDO DE PANTALLA OSCURO (MODO TÁCTICO) */
    .stApp {{
        background-color: #050a10; /* Negro azulado profundo */
        background-image: 
            radial-gradient(circle at 50% 10%, #152535 0%, #050a10 90%), /* Luz cenital sutil */
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px); /* Rejilla táctica */
        background-size: 100% 100%, 50px 50px, 50px 50px;
        color: #e0e0e0; /* Texto claro para contraste */
    }}
    
    /* LIMPIEZA DE INTERFAZ */
    #MainMenu, footer, header {{visibility: hidden;}}
    [data-testid="collapsedControl"] {{display: none;}}
    .block-container {{ padding-top: 1.5rem !important; padding-bottom: 5rem !important; max-width: 95% !important; }}
    
    /* --- CABECERA INTEGRADA --- */
    .header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 35px;
        background: rgba(13, 20, 28, 0.85); /* Fondo semi-transparente */
        border-radius: 25px;
        border: 1px solid rgba(212, 175, 55, 0.25); /* Borde dorado policial */
        box-shadow: 0 20px 50px rgba(0,0,0,0.7);
        margin-bottom: 40px;
        backdrop-filter: blur(10px); /* Efecto vidrio */
    }}
    
    /* IMAGEN ESCUDO (AHORA TRANSPARENTE) */
    .escudo-img {{
        width: 150px;
        height: auto;
        /* Sombra dorada para resaltar sobre el fondo oscuro */
        filter: drop-shadow(0 0 30px rgba(212, 175, 55, 0.6));
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }}
    .escudo-img:hover {{ transform: scale(1.05); }}
    
    /* TÍTULOS */
    .main-title {{
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem; 
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 6px;
        margin: 0;
        text-shadow: 0 0 30px rgba(0, 188, 212, 0.5); /* Resplandor azul cian */
        line-height: 1;
        text-align: center;
    }}
    
    .sub-title {{
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        color: #D4AF37; /* DORADO POLICIAL */
        letter-spacing: 4px;
        margin-top: 15px;
        text-transform: uppercase;
        font-weight: 500;
        border-top: 2px solid rgba(212, 175, 55, 0.3);
        padding-top: 15px;
        width: 70%;
        text-align: center;
    }}

    /* --- BOTONES: GRID UNIFORME 1x4 --- */
    div.stButton > button {{
        background: linear-gradient(180deg, rgba(30, 40, 50, 0.95), rgba(15, 20, 25, 0.98)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 15px !important;
        color: #fff !important;
        
        /* UNIFORMIDAD TOTAL DE TAMAÑO */
        width: 100% !important;
        height: 150px !important;      
        min-height: 150px !important;
        max-height: 150px !important;
        
        display: flex !important;
        flex-direction: column !important; /* Icono arriba, Texto abajo */
        justify-content: center !important;
        align-items: center !important;
        padding: 10px !important;
        gap: 10px;

        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        white-space: normal !important;
        text-align: center !important;
        
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.4) !important;
    }}

    div.stButton > button:hover {{
        transform: translateY(-8px) !important;
        background: linear-gradient(180deg, #1e3c50, #102030) !important;
        border-color: #D4AF37 !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 20px rgba(212, 175, 55, 0.3) !important;
    }}

    /* ICONOS DENTRO DE BOTONES */
    div.stButton > button::before {{
        font-size: 45px;
        filter: grayscale(100%) opacity(0.7);
        transition: 0.3s;
        margin-bottom: 5px;
        display: block;
    }}
    div.stButton > button:hover::before {{ filter: grayscale(0%) opacity(1) drop-shadow(0 0 5px rgba(255,255,255,0.5)); transform: scale(1.1); }}

    /* ASIGNACIÓN DE ICONOS */
    div.row-widget.stButton:nth-of-type(1) button::before {{ content: "📝"; }}
    div.row-widget.stButton:nth-of-type(2) button::before {{ content: "👤"; }}
    div.row-widget.stButton:nth-of-type(3) button::before {{ content: "🤖"; }}
    div.row-widget.stButton:nth-of-type(4) button::before {{ content: "🛡️"; }}

    /* FOOTER */
    .footer-dev {{
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center;
        background: rgba(8, 12, 16, 0.98); border-top: 1px solid #1f2b38; padding: 12px;
        font-family: 'Roboto', monospace; font-size: 11px; color: #546e7a;
        z-index: 9999; letter-spacing: 0.5px;
    }}
    .footer-dev span {{ color: #D4AF37; font-weight: bold; margin: 0 5px; }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

# CABECERA (ESCUDO TRANSPARENTE + TÍTULOS)
# Usamos la nueva URL con el escudo PNG transparente
st.markdown(f"""
    <div class="header-container">
        <img src="{URL_ESCUDO}" class="escudo-img" alt="Escudo PN Transparente">
        <div class="main-title">SIGD DINIC</div>
        <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
    </div>
""", unsafe_allow_html=True)

# GRID DE BOTONES UNIFORMES (4 COLUMNAS x 1 FILA)
c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    if st.button("SECRETARIO/A"):
        st.toast("Cargando...", icon="📝")

with c2:
    if st.button("TALENTO HUMANO"):
        st.toast("Accediendo...", icon="👤")

with c3:
    if st.button("GENERADOR DOC."): # Abreviado para encajar mejor
        st.toast("IA Iniciada...", icon="🤖")

with c4:
    if st.button("ADMINISTRACIÓN"):
        st.toast("Panel de Control", icon="🛡️")

# FOOTER DE DESARROLLADOR
st.markdown("""
    <div class="footer-dev">
        VERSIÓN DEL SISTEMA: <span>v9.5 FINAL</span> | 
        DESARROLLADO POR: <span>JSCN</span> | 
        CORREO: <span>cnjstalin@gmail.com</span> | 
        SOPORTE: <span>0996652042</span>
    </div>
""", unsafe_allow_html=True)
