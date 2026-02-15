import streamlit as st
import base64
import os
from datetime import date

# Intentamos cargar librerías para los gráficos de TH
try:
    import pandas as pd
    import plotly.express as px
    LIBRERIAS_OK = True
except ImportError:
    LIBRERIAS_OK = False

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL (TU BASE)
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
# 2. RECURSOS (ESCUDO BASE)
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
# 3. ESTILOS CSS MAESTROS (TU DISEÑO ORIGINAL)
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
    
    /* Botones Menú Principal */
    div.row-widget.stButton > button {
        background-color: #ffffff !important; color: #0E2F44 !important; border: 1px solid #e1e4e8 !important;
        border-left: 8px solid #0E2F44 !important; border-radius: 8px !important; width: 100% !important; height: 80px !important;
        margin-bottom: 20px !important; display: flex !important; justify-content: flex-start !important; align-items: center !important;
        padding-left: 30px !important; font-family: 'Roboto', sans-serif !important; font-size: 1.2rem !important;
        font-weight: 700 !important; text-transform: uppercase !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    }
    div.row-widget.stButton > button:hover { border-left: 8px solid #D4AF37 !important; transform: translateX(5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }

    /* --- ESTILOS MÓDULOS --- */
    .sec-header { background-color: #0E2F44; color: white; padding: 8px 15px; border-radius: 5px 5px 0 0; font-weight: 600; font-size: 0.9rem; margin-top: 20px; border-left: 5px solid #D4AF37; }
    .sec-body { background-color: white; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    
    label { color: #37474f !important; font-weight: 700 !important; font-size: 0.8rem !important; margin-bottom: 0px !important; }

    /* Footer */
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 10px; font-size: 11px; color: #aaa; font-family: monospace; z-index:999; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. PANTALLAS (MODULARIZADAS)
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

    st.markdown("""<div class="footer">SIGD DINIC v22.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com | Soporte: 0996652042</div>""", unsafe_allow_html=True)

def mostrar_secretario():
    # Barra de herramientas superior
    c_title, c_tools = st.columns([2, 5])
    with c_title:
         st.markdown(f'<div style="background:#263238; padding:10px; border-radius:8px; color:white; font-weight:bold; display:flex; align-items:center; height:60px;"><span style="font-size:20px; margin-right:10px;">🛡️</span> GESTOR DOCUMENTAL DINIC</div>', unsafe_allow_html=True)
    
    with c_tools:
        b1, b2, b3, b4, b5 = st.columns([1.2, 1, 1, 1.2, 1])
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
            if st.button("🗑️ REINICIAR", key="btn_rst"): navegar_a("landing")

    # Formulario Base Secretario
    st.markdown('<div class="sec-header">1. DOCUMENTO RECEPTADO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1.5])
        with c1: st.date_input("FECHA DOC:", value=date.today())
        with c2: st.text_input("REMITENTE:")
        with c3: st.text_input("CARGO:")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("Formulario de secretaría activo. Use los botones superiores para gestionar la data.")

# ------------------------------------------------------------------------------
# NUEVO: MÓDULO TALENTO HUMANO (Implementado en tu base)
# ------------------------------------------------------------------------------
def mostrar_talento_humano():
    # Encabezado consistente con tu estilo
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("⬅ VOLVER"): navegar_a("landing")
    with col_title:
        st.markdown(f'<div style="background:#0E2F44; padding:10px; border-radius:8px; color:white; font-weight:bold; height:50px; display:flex; align-items:center;"><span style="font-size:20px; margin-right:10px;">👤</span> TALENTO HUMANO - ANALÍTICA DE PERSONAL</div>', unsafe_allow_html=True)

    if not LIBRERIAS_OK:
        st.error("Error: Librerías 'pandas' o 'plotly' no detectadas. Verifique su requirements.txt.")
        return

    # Carga de Matriz
    st.markdown('<div class="sec-header">CARGA DE MATRIZ EXTERNA</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        archivo = st.file_uploader("Suba su archivo de personal (Excel o CSV)", type=["xlsx", "csv"])
        st.markdown('</div>', unsafe_allow_html=True)

    if archivo:
        try:
            df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
            
            # --- DASHBOARD ---
            st.markdown('<div class="sec-header">DASHBOARD E INDICADORES</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="sec-body">', unsafe_allow_html=True)
                
                # Filtros Dinámicos
                st.subheader("🔍 Filtros Dinámicos")
                cols_filtros = st.multiselect("Seleccione columnas para filtrar", df.columns.tolist())
                dff = df.copy()
                if cols_filtros:
                    for col in cols_filtros:
                        valores = st.multiselect(f"Filtrar por {col}", df[col].unique())
                        if valores:
                            dff = dff[dff[col].isin(valores)]
                
                st.divider()

                # Gráficos
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    eje_x = st.selectbox("Eje X para Gráfico de Barras", dff.columns)
                    fig_bar = px.histogram(dff, x=eje_x, title=f"Distribución por {eje_x}", color_discrete_sequence=['#0E2F44'])
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col_g2:
                    eje_pie = st.selectbox("Eje para Gráfico de Pastel", dff.columns, index=min(1, len(dff.columns)-1))
                    fig_pie = px.pie(dff, names=eje_pie, title=f"Distribución de {eje_pie}", hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)

            # --- TABLA DE DATOS ---
            st.markdown('<div class="sec-header">MATRIZ DE DATOS FILTRADA</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="sec-body">', unsafe_allow_html=True)
                st.dataframe(dff, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al procesar la matriz: {e}")
    else:
        st.info("Por favor, suba una matriz de datos para comenzar el análisis visual.")

# ==============================================================================
# 5. ROUTER (ESTRUCTURA BASE)
# ==============================================================================
if st.session_state.page == 'landing':
    mostrar_landing()
elif st.session_state.page == 'secretario':
    mostrar_secretario()
elif st.session_state.page == 'th':
    mostrar_talento_humano()
