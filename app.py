import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
from datetime import date

# ==============================================================================
# 1. CONFIGURACIÓN INICIAL (GRABADO EN PIEDRA)
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
# 2. RECURSOS Y ESTILOS (GRABADO EN PIEDRA)
# ==============================================================================
def get_escudo_html():
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{b64}" class="escudo-img">'
        except: pass
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="escudo-img">'

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    .stApp { background-color: #f4f6f8; color: #2c3e50; font-family: 'Roboto', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; max-width: 98% !important; }

    /* CABECERA LANDING */
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

    /* ESTILO FORMULARIOS */
    .sec-header { background-color: #0E2F44; color: white; padding: 8px 15px; border-radius: 5px 5px 0 0; font-weight: 600; font-size: 0.9rem; margin-top: 20px; border-left: 5px solid #D4AF37; }
    .sec-body { background-color: white; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 10px; font-size: 11px; color: #aaa; font-family: monospace; z-index:999; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. MÓDULOS DE PANTALLA
# ==============================================================================

def mostrar_landing():
    st.markdown(f'<div class="header-box">{get_escudo_html()}<div class="main-title">SIGD DINIC</div><div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div></div>', unsafe_allow_html=True)
    izq, centro, der = st.columns([1, 0.8, 1])
    with centro:
        if st.button("📝 SECRETARIO/A"): navegar_a("secretario")
        if st.button("👤 TALENTO HUMANO"): navegar_a("talento_humano")
        if st.button("🤖 GENERADOR"): st.toast("En desarrollo...")
        if st.button("🛡️ ADMINISTRACIÓN"): st.toast("En desarrollo...")
    st.markdown("""<div class="footer">SIGD DINIC v24.0 | Desarrollado por: <b>JSCN</b> | cnjstalin@gmail.com</div>""", unsafe_allow_html=True)

def mostrar_secretario():
    if st.button("⬅ VOLVER AL MENÚ"): navegar_a("landing")
    st.markdown('<div class="sec-header">1. DOCUMENTO RECEPTADO</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1.5])
        with c1: st.date_input("FECHA DOC:", value=date.today())
        with c2: st.text_input("REMITENTE:")
        with c3: st.text_input("CARGO:")
        st.markdown('</div>', unsafe_allow_html=True)
    st.info("Módulo de Secretaría configurado según especificaciones previas.")

# ------------------------------------------------------------------------------
# NUEVO: MÓDULO TALENTO HUMANO
# ------------------------------------------------------------------------------
def mostrar_talento_humano():
    # Encabezado del Módulo
    c_btn, c_title = st.columns([1, 4])
    with c_btn:
        if st.button("⬅ VOLVER"): navegar_a("landing")
    with c_title:
        st.markdown(f"""<div style="background:#263238; padding:10px; border-radius:8px; color:white; font-weight:bold; display:flex; align-items:center; height:50px; margin-bottom:20px;"><span style="font-size:20px; margin-right:10px;">👤</span> MÓDULO TALENTO HUMANO - DASHBOARD ANALÍTICO</div>""", unsafe_allow_html=True)

    # Carga de Matriz Externa
    st.markdown('<div class="sec-header">CARGA DE DATOS (MATRIZ EXTERNA)</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Suba su archivo Excel o CSV con la matriz de datos", type=["xlsx", "csv"])
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        try:
            # Lectura de datos
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # --- ZONA DE FILTROS ---
            st.markdown('<div class="sec-header">FILTROS DE BÚSQUEDA</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="sec-body">', unsafe_allow_html=True)
                cols_filtro = st.columns(len(df.columns[:4])) # Filtros para las primeras 4 columnas
                filtered_df = df.copy()
                for i, col in enumerate(df.columns[:4]):
                    with cols_filtro[i]:
                        opciones = ["TODOS"] + sorted(df[col].unique().tolist())
                        sel = st.selectbox(f"Filtrar por {col}", opciones)
                        if sel != "TODOS":
                            filtered_df = filtered_df[filtered_df[col] == sel]
                st.markdown('</div>', unsafe_allow_html=True)

            # --- DASHBOARD VISUAL ---
            st.markdown('<div class="sec-header">ANÁLISIS GRÁFICO</div>', unsafe_allow_html=True)
            c_g1, c_g2 = st.columns(2)
            
            with c_g1:
                # Gráfico de Barras Automático (Primera columna vs Segunda)
                fig1 = px.histogram(filtered_df, x=df.columns[0], color=df.columns[0], title=f"Distribución por {df.columns[0]}", template="plotly_white")
                st.plotly_chart(fig1, use_container_width=True)

            with c_g2:
                # Gráfico de Pastel (Tercera columna)
                fig2 = px.pie(filtered_df, names=df.columns[2] if len(df.columns) > 2 else df.columns[0], title="Composición Porcentual", hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)

            # --- TABLA DE DATOS ---
            st.markdown('<div class="sec-header">REGISTROS FILTRADOS</div>', unsafe_allow_html=True)
            st.dataframe(filtered_df, use_container_width=True)
            
            # Botón Descarga
            st.download_button("📥 Descargar Reporte Filtrado", filtered_df.to_csv(index=False), "reporte_th.csv", "text/csv")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Esperando archivo... Por favor suba la matriz de datos para generar los gráficos.")

# ==============================================================================
# 4. ROUTER
# ==============================================================================
if st.session_state.page == 'landing':
    mostrar_landing()
elif st.session_state.page == 'secretario':
    mostrar_secretario()
elif st.session_state.page == 'talento_humano':
    mostrar_talento_humano()
