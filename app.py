import streamlit as st
import base64
import os
from datetime import date

# Intentamos cargar librerías de análisis
try:
    import pandas as pd
    import plotly.express as px
    ANALISIS_LISTO = True
except ImportError:
    ANALISIS_LISTO = False

# ==============================================================================
# 1. CONFIGURACIÓN Y NAVEGACIÓN (EN PIEDRA)
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

# Lógica del Escudo (Captura.JPG)
def get_escudo_html():
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

# ==============================================================================
# 2. ESTILOS CSS MAESTROS
# ==============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    .stApp { background-color: #f4f6f8; color: #2c3e50; font-family: 'Roboto', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 98% !important; }

    /* LANDING PAGE */
    .header-box { text-align: center; padding-top: 40px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; }
    .escudo-img { width: 130px; height: auto; margin-bottom: 20px; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.1)); }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #0E2F44; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
    .sub-title { font-size: 1rem; color: #D4AF37; font-weight: 700; letter-spacing: 3px; margin-top: 5px; border-bottom: 2px solid #e1e4e8; padding-bottom: 20px; width: 100%; text-align: center; }
    
    /* BOTONES LANDING */
    div.row-widget.stButton > button {
        background-color: #ffffff !important; color: #0E2F44 !important; border: 1px solid #e1e4e8 !important;
        border-left: 8px solid #0E2F44 !important; border-radius: 8px !important; width: 100% !important; height: 80px !important;
        margin-bottom: 20px !important; display: flex !important; justify-content: flex-start !important; align-items: center !important;
        padding-left: 30px !important; font-family: 'Roboto', sans-serif !important; font-size: 1.2rem !important;
        font-weight: 700 !important; text-transform: uppercase !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    }
    div.row-widget.stButton > button:hover { border-left: 8px solid #D4AF37 !important; transform: translateX(5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }

    /* SECCIONES FORMULARIO */
    .sec-header { background-color: #0E2F44; color: white; padding: 8px 15px; border-radius: 5px 5px 0 0; font-weight: 600; font-size: 0.9rem; margin-top: 20px; border-left: 5px solid #D4AF37; }
    .sec-body { background-color: white; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 10px; font-size: 11px; color: #aaa; font-family: monospace; z-index:999; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. MÓDULOS DE PANTALLA
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
        if st.button("📝 SECRETARIO/A"): navegar_a("secretario")
        if st.button("👤 TALENTO HUMANO"): navegar_a("th")
        if st.button("🤖 GENERADOR"): st.toast("En desarrollo...")
        if st.button("🛡️ ADMINISTRACIÓN"): st.toast("En desarrollo...")

    st.markdown("""<div class="footer">SIGD DINIC v26.0 | DESARROLLADO POR: <b>JSCN</b> | cnjstalin@gmail.com | SOPORTE: 0996652042</div>""", unsafe_allow_html=True)

def mostrar_secretario():
    c_title, c_tools = st.columns([2, 5])
    with c_title:
         st.markdown(f'<div style="background:#263238; padding:10px; border-radius:8px; color:white; font-weight:bold; display:flex; align-items:center; height:60px;"><span style="font-size:20px; margin-right:10px;">🛡️</span> GESTOR DOCUMENTAL</div>', unsafe_allow_html=True)
    with c_tools:
        b1, b2, b3, b4, b5 = st.columns(5)
        with b1: st.button("📂 PLANTILLA", key="b1")
        with b2: st.button("⬇ RESPALDAR", key="b2")
        with b3: st.button("⬆ RESTAURAR", key="b3")
        with b4: st.button("✨ NUEVO", key="b4")
        with b5: 
            if st.button("🗑️ REINICIAR", key="b5"): navegar_a("landing")

    st.markdown('<div class="sec-header">1. DOCUMENTO RECEPTADO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.date_input("FECHA DOC:")
        with c2: st.text_input("REMITENTE:")
        with c3: st.text_input("CARGO:")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MÓDULO TALENTO HUMANO (BUSINESS INTELLIGENCE)
# ------------------------------------------------------------------------------
def mostrar_th():
    if st.button("⬅ VOLVER AL MENÚ"): navegar_a("landing")
    
    st.markdown(f'<div style="text-align:center;">{get_escudo_html()}</div>', unsafe_allow_html=True)
    st.title("👤 Análisis de Talento Humano")
    
    if not ANALISIS_LISTO:
        st.error("Librerías de análisis no instaladas. Revisa tu requirements.txt")
        return

    # Carga de Matriz
    st.markdown('<div class="sec-header">CARGA DE MATRIZ DE DATOS</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        archivo = st.file_uploader("Suba su archivo Excel o CSV", type=["xlsx", "csv"])
        st.markdown('</div>', unsafe_allow_html=True)

    if archivo:
        df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
        
        # Filtros Dinámicos
        st.sidebar.header("🔍 Filtros Dinámicos")
        cols = st.sidebar.multiselect("Seleccione columnas para filtrar", df.columns.tolist())
        
        filtered_df = df.copy()
        for col in cols:
            val = st.sidebar.multiselect(f"Valores para {col}", df[col].unique())
            if val: filtered_df = filtered_df[filtered_df[col].isin(val)]

        # Visualización
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Registros", len(filtered_df))
        
        st.markdown('<div class="sec-header">VISUALIZACIÓN DE GRÁFICOS</div>', unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            eje_x = st.selectbox("Eje X para Barras", df.columns)
            fig_bar = px.histogram(filtered_df, x=eje_x, title=f"Conteo por {eje_x}", template="plotly_white", color_discrete_sequence=['#0E2F44'])
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_g2:
            eje_pie = st.selectbox("Categoría para Pastel", df.columns, index=min(1, len(df.columns)-1))
            fig_pie = px.pie(filtered_df, names=eje_pie, title=f"Distribución de {eje_pie}", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('<div class="sec-header">TABLA DE DATOS FILTRADOS</div>', unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True)

# ==============================================================================
# 4. ROUTER
# ==============================================================================
if st.session_state.page == 'landing': mostrar_landing()
elif st.session_state.page == 'secretario': mostrar_secretario()
elif st.session_state.page == 'th': mostrar_th()
