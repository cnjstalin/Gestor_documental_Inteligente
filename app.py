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

    /* --- ESTILOS LANDING PAGE (CENTRO DE MANDO) --- */
    .header-box { text-align: center; padding-top: 40px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; }
    .escudo-img { width: 130px; height: auto; margin-bottom: 20px; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.1)); }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #0E2F44; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
    .sub-title { font-size: 1rem; color: #D4AF37; font-weight: 700; letter-spacing: 3px; margin-top: 5px; border-bottom: 2px solid #e1e4e8; padding-bottom: 20px; width: 100%; text-align: center; }
    
    .btn-landing {
        width: 100%; height: 80px; margin-bottom: 20px; display: flex; align-items: center; padding-left: 30px;
        background-color: #ffffff; color: #0E2F44; border: 1px solid #e1e4e8; border-left: 8px solid #0E2F44; border-radius: 8px;
        font-weight: 700; text-transform: uppercase; letter-spacing: 1px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: all 0.3s;
    }
    .btn-landing:hover { border-left: 8px solid #D4AF37; transform: translateX(5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); background-color: #fff; }

    /* --- ESTILOS MÓDULO SECRETARÍA --- */
    /* Barra Superior Oscura */
    .toolbar-container {
        background-color: #263238; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .toolbar-title { color: white; font-weight: 700; font-size: 1.2rem; display: flex; align-items: center; gap: 10px; }
    
    /* Botones de Herramientas (Colores Específicos) */
    div.stButton > button.btn-tool {
        border: none !important; color: white !important; font-weight: 700 !important; font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important; border-radius: 5px !important; text-transform: uppercase !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important; transition: transform 0.1s !important; height: auto !important; width: auto !important;
    }
    div.stButton > button.btn-tool:hover { transform: translateY(-2px); filter: brightness(110%); }
    div.stButton > button.btn-tool:active { transform: translateY(0); }

    /* Formulario */
    .sec-header { background-color: #0E2F44; color: white; padding: 8px 15px; border-radius: 5px 5px 0 0; font-weight: 600; font-size: 0.9rem; margin-top: 20px; border-left: 5px solid #D4AF37; }
    .sec-body { background-color: white; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    
    /* Inputs Compactos */
    label { color: #37474f !important; font-weight: 700 !important; font-size: 0.8rem !important; margin-bottom: 0px !important; }
    div[data-baseweb="input"] { background-color: #fff !important; border-color: #cfd8dc !important; }
    div[data-testid="stDateInput"] > div { margin-top: 0px; }

    /* Footer */
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 10px; font-size: 11px; color: #aaa; font-family: monospace; z-index:999; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LANDING PAGE (MENÚ PRINCIPAL)
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
        # Inyectamos estilos específicos para los botones del menú principal (Tarjeta Ejecutiva)
        st.markdown("""
            <style>
            div.row-widget.stButton > button {
                background-color: #ffffff !important; color: #0E2F44 !important; border: 1px solid #e1e4e8 !important;
                border-left: 8px solid #0E2F44 !important; border-radius: 8px !important; width: 100% !important; height: 80px !important;
                margin-bottom: 20px !important; display: flex !important; justify-content: flex-start !important; align-items: center !important;
                padding-left: 30px !important; font-family: 'Roboto', sans-serif !important; font-size: 1.2rem !important;
                font-weight: 700 !important; text-transform: uppercase !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
            }
            div.row-widget.stButton > button:hover { border-left: 8px solid #D4AF37 !important; transform: translateX(5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
            </style>
        """, unsafe_allow_html=True)

        if st.button("📝 SECRETARIO/A"): navegar_a("secretario")
        if st.button("👤 TALENTO HUMANO"): st.toast("En desarrollo...")
        if st.button("🤖 GENERADOR"): st.toast("En desarrollo...")
        if st.button("🛡️ ADMINISTRACIÓN"): st.toast("En desarrollo...")

    st.markdown("""<div class="footer">SIGD DINIC v21.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042</div>""", unsafe_allow_html=True)

# ==============================================================================
# 5. MÓDULO SECRETARIO (INTERFAZ REPLICADA)
# ==============================================================================
def mostrar_secretario():
    # --- BARRA DE HERRAMIENTAS PERSONALIZADA ---
    # Usamos columnas ajustadas para replicar la barra de la imagen
    
    # 1. Título a la izquierda
    # 2. Botones a la derecha
    
    c_title, c_tools = st.columns([2, 5])
    
    with c_title:
         st.markdown(f"""
            <div style="background:#263238; padding:10px; border-radius:8px; color:white; font-weight:bold; display:flex; align-items:center; height:60px;">
                <span style="font-size:20px; margin-right:10px;">🛡️</span> GESTOR DOCUMENTAL DINIC
            </div>
        """, unsafe_allow_html=True)
    
    with c_tools:
        # Contenedor oscuro para los botones
        with st.container():
            st.markdown("""<style>div.stButton > button { height: 45px !important; margin-top: 8px; }</style>""", unsafe_allow_html=True)
            
            # Grid de botones ajustado
            b1, b2, b3, b4, b5 = st.columns([1.2, 1, 1, 1.2, 1])
            
            # Inyección de colores específicos para cada botón
            b1.markdown("""<style>div.stButton > button:first-child { background-color: #673AB7 !important; }</style>""", unsafe_allow_html=True)
            with b1: st.button("📂 SUBIR PLANTILLA", key="btn_up", help="Cargar Excel Base", type="primary")

            b2.markdown("""<style>div.stButton > button:first-child { background-color: #00BCD4 !important; color: black !important; }</style>""", unsafe_allow_html=True)
            with b2: st.button("⬇ RESPALDAR", key="btn_bak", help="Guardar Backup")

            b3.markdown("""<style>div.stButton > button:first-child { background-color: #FFC107 !important; color: black !important; }</style>""", unsafe_allow_html=True)
            with b3: st.button("⬆ RESTAURAR", key="btn_res", help="Cargar Backup")

            # Separador visual vertical (simulado con columna vacía o borde)
            
            b4.markdown("""<style>div.stButton > button:first-child { background-color: #4CAF50 !important; }</style>""", unsafe_allow_html=True)
            with b4: st.button("✨ NUEVO TURNO", key="btn_new", help="Limpiar Todo")

            b5.markdown("""<style>div.stButton > button:first-child { background-color: #D32F2F !important; }</style>""", unsafe_allow_html=True)
            with b5: 
                if st.button("🗑️ REINICIAR", key="btn_rst"): navegar_a("landing")

    # --- FORMULARIO ---
    
    # SECCIÓN 1
    st.markdown('<div class="sec-header">1. DOCUMENTO RECEPTADO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1.5])
        with c1: st.date_input("FECHA DOC:", value=date.today())
        with c2: st.text_input("REMITENTE:")
        with c3: st.text_input("CARGO:")
        
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1: st.text_input("UNIDAD ORIGEN:")
        with c2: st.text_input("N° DOCUMENTO (PN):")
        with c3: st.date_input("FECHA RECEPCIÓN:", value=date.today())
        
        st.text_input("ASUNTO:")
        st.text_area("DESCRIPCIÓN:", height=60)
        
        c1, c2 = st.columns([2, 1])
        with c1: st.text_input("S. POLICIAL TURNO:")
        with c2: st.selectbox("OBSERVACIÓN:", ["NINGUNA", "URGENTE", "RESERVADO"])
        
        st.markdown('</div>', unsafe_allow_html=True)

    # SECCIÓN 2
    st.markdown('<div class="sec-header">2. GESTIÓN / TRÁMITE</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("UNIDAD DESTINO:")
        with c2: st.selectbox("TIPO DOC:", ["OFICIO", "MEMORANDO", "PARTE"])
        with c3: st.date_input("FECHA EMISIÓN:")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("N° DOC RESPUESTA:")
        with c2: st.text_input("RECEPTOR (GRADO/NOMBRE):")
        with c3: st.selectbox("ESTADO:", ["PENDIENTE", "FINALIZADO"])
        st.markdown('</div>', unsafe_allow_html=True)

    # SECCIÓN 3
    st.markdown('<div class="sec-header">3. SALIDA RESPUESTA</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.radio("¿SALE DE DINIC?", ["SI", "NO"], horizontal=True)
        with c2: st.text_input("DESTINO FINAL:")
        with c3: st.text_input("N° DOC FINAL:")
        st.markdown('</div>', unsafe_allow_html=True)

    # Botón Guardar Inferior
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
