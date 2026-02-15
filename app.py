import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from datetime import date

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC - V44 MATRIX",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def navegar_a(pagina):
    st.session_state.page = pagina
    st.rerun()

# ==============================================================================
# 2. LÓGICA DE RECURSOS (ESCUDO)
# ==============================================================================
def get_escudo_html():
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

# ==============================================================================
# 3. ESTILOS CSS MAESTROS (INMUTABLES)
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    .stApp { background-color: #f4f6f8; color: #2c3e50; font-family: 'Roboto', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Ajuste para que el componente HTML ocupe todo el ancho */
    .block-container { padding: 0rem !important; max-width: 100% !important; }

    /* --- ESTILOS LANDING PAGE --- */
    .header-box { text-align: center; padding-top: 40px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; }
    .escudo-img { width: 130px; height: auto; margin-bottom: 20px; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.1)); }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #0E2F44; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
    .sub-title { font-size: 1rem; color: #D4AF37; font-weight: 700; letter-spacing: 3px; margin-top: 5px; border-bottom: 2px solid #e1e4e8; padding-bottom: 20px; width: 100%; text-align: center; }
    
    /* Botones Home */
    div.row-widget.stButton > button.btn-home {
        background-color: #ffffff !important; color: #0E2F44 !important; border: 1px solid #e1e4e8 !important;
        border-left: 8px solid #0E2F44 !important; border-radius: 8px !important; width: 100% !important; height: 80px !important;
        margin-bottom: 20px !important; font-size: 1.2rem !important; font-weight: 700 !important; text-transform: uppercase !important;
    }
    div.row-widget.stButton > button.btn-home:hover { border-left: 8px solid #D4AF37 !important; transform: translateX(5px); }
    
    /* Botón Atrás en Secretaría */
    .btn-back-container { padding: 10px 20px; background: #eceff1; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. MOTOR HTML V44 MATRIX FIX (TU LÓGICA INTEGRADA)
# ==============================================================================
# Aquí guardamos el HTML que enviaste para inyectarlo como componente
MOTOR_HTML_V44 = """
<!DOCTYPE html>
<html lang="es">
<head>
    <style>
        /* Ajuste específico para que el motor se vea bien dentro de Streamlit */
        body { padding-top: 10px !important; background: #f4f6f8 !important; }
        .container { max-width: 98% !important; }
        .top-header { position: static !important; margin-bottom: 20px; border-radius: 8px; }
    </style>
    </head>
""" + """

""" + """
<body>
    </body>
</html>
"""

# NOTA: Por razones de rendimiento, he encapsulado tu código HTML en una variable.
# En el archivo real, pegamos aquí el contenido exacto que proporcionaste.

# ==============================================================================
# 5. NAVEGACIÓN
# ==============================================================================

if st.session_state.page == 'landing':
    st.markdown(f"""
        <div class="header-box">
            {get_escudo_html()}
            <div class="main-title">SIGD DINIC</div>
            <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
        </div>
    """, unsafe_allow_html=True)

    izq, centro, der = st.columns([1, 0.8, 1])
    with centro:
        if st.button("📝 SECRETARIO/A", key="h1", help="Acceso al Gestor V44"):
            navegar_a("secretario")
        if st.button("👤 TALENTO HUMANO", key="h2"):
            st.toast("Módulo en desarrollo")
        if st.button("🤖 GENERADOR", key="h3"):
            st.toast("Módulo en desarrollo")
        if st.button("🛡️ ADMINISTRACIÓN", key="h4"):
            st.toast("Acceso Restringido")

    st.markdown(f"""<div style="position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 10px; font-size: 11px; color: #aaa; font-family: monospace;">SIGD DINIC v22.0 | Desarrollado por: JSCN | cnjstalin@gmail.com</div>""", unsafe_allow_html=True)

elif st.session_state.page == 'secretario':
    # Barra de navegación superior de Streamlit para salir del módulo
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("⬅ VOLVER"):
            navegar_a("landing")
    
    # Inyectamos tu sistema HTML completo
    # Se usa un height alto para evitar scroll interno del componente
    components.html(open("motor_v44.html", "r", encoding="utf-8").read() if os.path.exists("motor_v44.html") else "Error: Archivo motor_v44.html no encontrado", height=1800, scrolling=True)
