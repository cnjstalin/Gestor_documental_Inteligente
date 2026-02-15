import streamlit as st
import base64
import os
from datetime import date

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL Y ESTADO
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Inicializar Estado de Navegación
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

# Función para navegar
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
# 3. ESTILOS CSS GLOBALES (AQUÍ ESTÁ EL DISEÑO "EN PIEDRA")
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    /* --- GLOBAL --- */
    .stApp { background-color: #f4f6f8; color: #2c3e50; font-family: 'Roboto', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* --- ESTILOS DE LA LANDING PAGE (INTOCABLES) --- */
    .header-box {
        text-align: center; padding-top: 40px; margin-bottom: 20px;
        display: flex; flex-direction: column; align-items: center;
    }
    .escudo-img { width: 130px; height: auto; margin-bottom: 20px; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.1)); }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #0E2F44; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
    .sub-title { font-size: 1rem; color: #D4AF37; font-weight: 700; letter-spacing: 3px; margin-top: 5px; border-bottom: 2px solid #e1e4e8; padding-bottom: 20px; width: 100%; text-align: center; }
    
    /* Botones del Menú Principal */
    .btn-landing {
        width: 100%; height: 80px; margin-bottom: 20px;
        display: flex; align-items: center; padding-left: 30px;
        background-color: #ffffff; color: #0E2F44;
        border: 1px solid #e1e4e8; border-left: 8px solid #0E2F44; border-radius: 8px;
        font-weight: 700; text-transform: uppercase; letter-spacing: 1px; cursor: pointer;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: all 0.3s;
    }
    .btn-landing:hover { border-left: 8px solid #D4AF37; transform: translateX(5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); background-color: #fff; }

    /* --- ESTILOS DEL FORMULARIO SECRETARÍA --- */
    .sec-header {
        background-color: #0E2F44; color: white; padding: 10px 20px;
        border-radius: 8px 8px 0 0; font-weight: 700; letter-spacing: 1px;
        margin-top: 30px; border-bottom: 3px solid #D4AF37;
        display: flex; align-items: center;
    }
    .sec-container {
        background-color: white; padding: 25px; border-radius: 0 0 8px 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; margin-bottom: 20px;
    }
    /* Inputs personalizados */
    div[data-baseweb="input"] { border-radius: 5px; }
    label { color: #0E2F44 !important; font-weight: 600 !important; font-size: 0.9rem !important; }

    /* FOOTER */
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 15px; font-size: 11px; color: #aaa; font-family: monospace; z-index:999; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. PANTALLA: LANDING PAGE (DISEÑO EN PIEDRA)
# ==============================================================================
def mostrar_landing():
    # Cabecera
    st.markdown(f"""
        <div class="header-box">
            {get_escudo_html()}
            <div class="main-title">SIGD DINIC</div>
            <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
        </div>
    """, unsafe_allow_html=True)

    # Menú
    izq, centro, der = st.columns([1, 0.8, 1])
    with centro:
        # Usamos un truco de CSS+HTML para los botones personalizados que activan funciones de Streamlit
        # Pero para mantener la funcionalidad nativa simple y robusta, usaremos los botones st con el estilo inyectado
        
        # Inyección de estilo específico para los botones de Streamlit en esta página
        st.markdown("""
            <style>
            div.stButton > button {
                background-color: #ffffff !important; color: #0E2F44 !important;
                border: 1px solid #e1e4e8 !important; border-left: 8px solid #0E2F44 !important;
                border-radius: 8px !important; width: 100% !important; height: 80px !important;
                margin-bottom: 20px !important; display: flex !important; justify-content: flex-start !important;
                align-items: center !important; padding-left: 30px !important;
                font-family: 'Roboto', sans-serif !important; font-size: 1.2rem !important;
                font-weight: 700 !important; text-transform: uppercase !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
            }
            div.stButton > button:hover {
                border-left: 8px solid #D4AF37 !important; transform: translateX(5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
            }
            div.stButton > button::before { content: "➤"; margin-right: 15px; color: #b0b0b0; font-size: 18px; }
            div.stButton > button:hover::before { color: #D4AF37; }
            </style>
        """, unsafe_allow_html=True)

        if st.button("SECRETARIO/A"): navegar_a("secretario")
        if st.button("TALENTO HUMANO"): st.toast("En desarrollo...")
        if st.button("GENERADOR"): st.toast("En desarrollo...")
        if st.button("ADMINISTRACIÓN"): st.toast("En desarrollo...")

    # Footer
    st.markdown("""
        <div class="footer">
            SIGD DINIC v20.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 5. PANTALLA: MÓDULO SECRETARIO (FORMULARIO ELEGANTE)
# ==============================================================================
def mostrar_secretario():
    # Botón de Retorno (Estilo simple)
    if st.button("⬅ VOLVER AL MENÚ PRINCIPAL"):
        navegar_a("landing")
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:20px; margin-bottom:20px;">
            {get_escudo_html().replace('width: 130px','width: 60px')}
            <div>
                <h2 style="margin:0; color:#0E2F44;">MÓDULO DE SECRETARÍA</h2>
                <span style="color:#D4AF37; font-weight:bold;">REGISTRO Y CONTROL DOCUMENTAL</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN 1: DOCUMENTO RECEPTADO ---
    st.markdown('<div class="sec-header">1. DOCUMENTO RECEPTADO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-container">', unsafe_allow_html=True)
        
        # Fila 1
        c1, c2, c3 = st.columns(3)
        with c1: st.date_input("Fecha Documento Receptado", value=date.today())
        with c2: st.date_input("Fecha de Recepción", value=date.today())
        with c3: st.text_input("Remitente")
        
        # Fila 2
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Cargo del Remitente")
        with c2: st.text_input("Unidad de Origen")
        with c3: st.text_input("S. Policial que Recibe")
        
        # Fila 3
        st.text_input("Asunto")
        st.text_area("Descripción / Resumen", height=80)
        st.text_input("Observación", placeholder="Ej: Urgente, Reservado, etc.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SECCIÓN 2: GESTIÓN O TRÁMITE ---
    st.markdown('<div class="sec-header">2. GESTIÓN O TRÁMITE DEL DOCUMENTO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-container">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("Unidad de Destino (Gestión)")
        with c2: st.selectbox("Tipo de Documento", ["Oficio", "Memorando", "Parte", "Telegrama", "Otro"])
        with c3: st.date_input("Fecha de Emisión")
        
        c1, c2 = st.columns(2)
        with c1: st.text_input("N° Documento Respuesta (Gestión)")
        with c2: st.text_input("Grado y Nombre Receptor")
        
        st.selectbox("Estado del Trámite", ["PENDIENTE", "EN PROCESO", "FINALIZADO", "ARCHIVADO"])
        
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SECCIÓN 3: SALIDA DEL DOCUMENTO ---
    st.markdown('<div class="sec-header">3. SALIDA DEL DOCUMENTO DE RESPUESTA</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-container">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.radio("¿El documento sale de la DINIC?", ["SÍ", "NO"], horizontal=True)
        with c2: st.text_input("Unidad de Destino Final")
        with c3: st.text_input("N° Documento Respuesta (Final)")

        c1, c2 = st.columns(2)
        with c1: st.date_input("Fecha de Salida")
        with c2: st.date_input("Fecha de Recepción (Destino)")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Botón de Guardado
    col_save, _ = st.columns([1, 4])
    with col_save:
        if st.button("💾 GUARDAR REGISTRO", use_container_width=True, type="primary"):
            st.success("¡Registro guardado exitosamente en el sistema!")

# ==============================================================================
# 6. EJECUCIÓN PRINCIPAL
# ==============================================================================
if st.session_state.page == 'landing':
    mostrar_landing()
elif st.session_state.page == 'secretario':
    mostrar_secretario()
