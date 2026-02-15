import streamlit as st
import base64
import os
from datetime import date

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

if 'page' not in st.session_state: st.session_state.page = 'landing'

def navegar_a(pagina):
    st.session_state.page = pagina
    st.rerun()

# ==============================================================================
# 2. RECURSOS (ESCUDO)
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
# 3. ESTILOS CSS MAESTROS
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    /* GLOBAL */
    .stApp { background-color: #f4f6f8; color: #2c3e50; font-family: 'Roboto', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 98% !important; }

    /* --- ESTILOS LANDING PAGE --- */
    .header-box { text-align: center; padding-top: 40px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; }
    .escudo-img { width: 130px; height: auto; margin-bottom: 20px; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.1)); }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #0E2F44; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
    .sub-title { font-size: 1rem; color: #D4AF37; font-weight: 700; letter-spacing: 3px; margin-top: 5px; border-bottom: 2px solid #e1e4e8; padding-bottom: 20px; width: 100%; text-align: center; }
    
    /* --- BARRA DE HERRAMIENTAS (TOOLBAR) --- */
    .toolbar-container {
        background-color: #263238; padding: 10px; border-radius: 8px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* Botones de Herramientas */
    div.stButton > button.btn-tool {
        border: none !important; color: white !important; font-weight: 700 !important; font-size: 0.8rem !important;
        padding: 0.5rem 0.8rem !important; border-radius: 5px !important; text-transform: uppercase !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important; height: 45px !important;
    }
    
    /* Botón Atrás Especial */
    .btn-back-style {
        background-color: #f4f6f8 !important; color: #0E2F44 !important; border: 1px solid #0E2F44 !important;
        font-weight: bold !important; border-radius: 5px !important;
    }

    /* Estilos Secciones Formulario */
    .sec-header { background-color: #0E2F44; color: white; padding: 8px 15px; border-radius: 5px 5px 0 0; font-weight: 600; font-size: 0.9rem; margin-top: 15px; border-left: 5px solid #D4AF37; }
    .sec-body { background-color: white; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    
    label { color: #37474f !important; font-weight: 700 !important; font-size: 0.85rem !important; }

    /* Footer */
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 10px; font-size: 11px; color: #aaa; font-family: monospace; z-index:999; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LANDING PAGE
# ==============================================================================
def mostrar_landing():
    st.markdown(f"""
        <div class="header-box">
            {get_escudo_html()}
            <div class="main-title">SIGD DINIC</div>
            <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
        </div>
    """, unsafe_allow_html=True)

    izq, centro, der = st.columns([1, 0.8, 1])
    with centro:
        st.markdown("""<style>
            div.row-widget.stButton > button {
                background-color: #ffffff !important; color: #0E2F44 !important; border: 1px solid #e1e4e8 !important;
                border-left: 8px solid #0E2F44 !important; border-radius: 8px !important; width: 100% !important; height: 80px !important;
                margin-bottom: 20px !important; font-size: 1.2rem !important; font-weight: 700 !important; text-transform: uppercase !important;
            }
            div.row-widget.stButton > button:hover { border-left: 8px solid #D4AF37 !important; transform: translateX(5px); }
        </style>""", unsafe_allow_html=True)

        if st.button("📝 SECRETARIO/A"): navegar_a("secretario")
        if st.button("👤 TALENTO HUMANO"): st.toast("En desarrollo...")
        if st.button("🤖 GENERADOR"): st.toast("En desarrollo...")
        if st.button("🛡️ ADMINISTRACIÓN"): st.toast("En desarrollo...")

    st.markdown("""<div class="footer">SIGD DINIC v22.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042</div>""", unsafe_allow_html=True)

# ==============================================================================
# 5. MÓDULO SECRETARIO
# ==============================================================================
def mostrar_secretario():
    # BARRA SUPERIOR (Atrás + Título + Herramientas)
    
    # Fila Superior: Botón Atrás y Título
    c_back, c_title, c_filler = st.columns([1, 4, 3])
    with c_back:
        if st.button("⬅ ATRÁS", key="btn_back_home"):
            navegar_a("landing")
    
    # Barra de Herramientas (Toolbar Estilo Imagen)
    st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
    
    col_bar_left, col_bar_right = st.columns([1, 2.5])
    
    with col_bar_left:
        st.markdown(f"""
            <div style="background:#263238; padding:10px; border-radius:8px; color:white; font-weight:bold; height:50px; display:flex; align-items:center;">
                <span style="font-size:20px; margin-right:10px;">🛡️</span> GESTOR DOCUMENTAL DINIC
            </div>
        """, unsafe_allow_html=True)

    with col_bar_right:
        b1, b2, b3, b4, b5 = st.columns(5)
        
        # Inyección de estilos de color por botón
        b1.markdown("""<style>div.stButton > button[key="btn_up"] { background-color: #673AB7 !important; color:white !important; }</style>""", unsafe_allow_html=True)
        with b1: st.button("📂 PLANTILLA", key="btn_up")

        b2.markdown("""<style>div.stButton > button[key="btn_bak"] { background-color: #00BCD4 !important; color:black !important; }</style>""", unsafe_allow_html=True)
        with b2: st.button("⬇ RESPALDAR", key="btn_bak")

        b3.markdown("""<style>div.stButton > button[key="btn_res"] { background-color: #FFC107 !important; color:black !important; }</style>""", unsafe_allow_html=True)
        with b3: st.button("⬆ RESTAURAR", key="btn_res")

        b4.markdown("""<style>div.stButton > button[key="btn_new"] { background-color: #4CAF50 !important; color:white !important; }</style>""", unsafe_allow_html=True)
        with b4: st.button("✨ NUEVO", key="btn_new")

        b5.markdown("""<style>div.stButton > button[key="btn_rst"] { background-color: #D32F2F !important; color:white !important; }</style>""", unsafe_allow_html=True)
        with b5: 
            if st.button("🗑️ REINICIAR", key="btn_rst"):
                st.warning("Datos del turno limpiados.")

    # --- FORMULARIO ---
    st.markdown('<div class="sec-header">1. DOCUMENTO RECEPTADO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1.5])
        with c1: st.date_input("FECHA DOC:", value=date.today(), key="f1")
        with c2: st.text_input("REMITENTE:", key="f2")
        with c3: st.text_input("CARGO:", key="f3")
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1: st.text_input("UNIDAD ORIGEN:", key="f4")
        with c2: st.text_input("N° DOCUMENTO (PN):", key="f5")
        with c3: st.date_input("FECHA RECEPCIÓN:", value=date.today(), key="f6")
        st.text_input("ASUNTO:", key="f7")
        st.text_area("DESCRIPCIÓN:", height=60, key="f8")
        c1, c2 = st.columns([2, 1])
        with c1: st.text_input("S. POLICIAL TURNO:", key="f9")
        with c2: st.selectbox("OBSERVACIÓN:", ["NINGUNA", "URGENTE", "RESERVADO"], key="f10")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-header">2. GESTIÓN / TRÁMITE</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("UNIDAD DESTINO:", key="f11")
        with c2: st.selectbox("TIPO DOC:", ["OFICIO", "MEMORANDO", "PARTE"], key="f12")
        with c3: st.date_input("FECHA EMISIÓN:", key="f13")
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("N° DOC RESPUESTA:", key="f14")
        with c2: st.text_input("RECEPTOR (GRADO/NOMBRE):", key="f15")
        with c3: st.selectbox("ESTADO:", ["PENDIENTE", "FINALIZADO"], key="f16")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-header">3. SALIDA RESPUESTA</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.radio("¿SALE DE DINIC?", ["SI", "NO"], horizontal=True, key="f17")
        with c2: st.text_input("DESTINO FINAL:", key="f18")
        with c3: st.text_input("N° DOC FINAL:", key="f19")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 GUARDAR REGISTRO EN LA BASE DE DATOS", type="primary", use_container_width=True):
        st.success("Registro Almacenado Correctamente")

# ==============================================================================
# 6. ROUTER
# ==============================================================================
if st.session_state.page == 'landing':
    mostrar_landing()
elif st.session_state.page == 'secretario':
    mostrar_secretario()
