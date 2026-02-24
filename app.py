import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==============================================================================
# 1. CONFIGURACIÓN Y ESTILOS
# ==============================================================================
VER_SISTEMA = "v46.0 - Matrix"
ADMIN_PASS = "9994915010022"

st.set_page_config(page_title="SIGD DINIC", layout="wide", page_icon="🛡️", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #f8f9fa; color: #1a1a1a; font-family: 'Inter', sans-serif; }
    [data-testid="stHeader"] {background: rgba(0,0,0,0); border-bottom: none;}
    .sec-header { background: #0E2F44; color: #D4AF37; padding: 12px 20px; border-radius: 8px 8px 0 0; font-weight: 700; font-size: 0.85rem; letter-spacing: 1px; border-left: 5px solid #D4AF37; text-transform: uppercase; }
    .sec-body { background: white; padding: 25px; border-radius: 0 0 8px 8px; border: 1px solid #e1e4e8; border-top: none; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    div.row-widget.stButton > button { background: white !important; color: #0E2F44 !important; border: 1px solid #dee2e6 !important; border-left: 8px solid #0E2F44 !important; height: 70px !important; width: 100% !important; border-radius: 10px !important; font-weight: 700 !important; text-align: left !important; padding-left: 25px !important; transition: all 0.3s ease !important; }
    div.row-widget.stButton > button:hover { border-left: 8px solid #D4AF37 !important; transform: translateX(5px); box-shadow: 2px 4px 8px rgba(0,0,0,0.1) !important; }
    </style>
""", unsafe_allow_html=True)

# --- Estado de la App ---
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'df_nomina' not in st.session_state: st.session_state.df_nomina = None

def nav(page):
    st.session_state.page = page
    st.rerun()

@st.cache_data
def cargar_nomina():
    if os.path.exists("nomina de acceso.xlsx - Hoja1.csv"):
        try:
            return pd.read_csv("nomina de acceso.xlsx - Hoja1.csv")
        except: pass
    return None

# ==============================================================================
# 2. PANTALLAS DEL SISTEMA
# ==============================================================================
def mostrar_landing():
    st.markdown(f'<div style="text-align:center; padding: 40px 0;"><h1 style="color:#0E2F44; font-weight:800; margin-bottom:0;">SIGD DINIC</h1><p style="color:#D4AF37; font-weight:700; letter-spacing:4px; margin-top:0;">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("📂 GESTIÓN DOCUMENTAL (SECRETARÍA)"): nav("secretario")
        if st.button("📊 DASHBOARD TALENTO HUMANO"): nav("th")
        if st.button("📝 GENERADOR DE DOCUMENTOS"): nav("generador")
        if st.button("🛡️ PANEL DE ADMINISTRACIÓN"): nav("admin")

def mostrar_secretario():
    c1, c2 = st.columns([1, 5])
    with c1: 
        if st.button("⬅ VOLVER"): nav("landing")
    with c2: st.subheader("📂 GESTOR DOCUMENTAL")
    st.info("Módulo en construcción. Volver a Dashboard TH para continuar pruebas.")

def mostrar_admin():
    if st.button("⬅ VOLVER"): nav("landing")
    st.title("🛡️ ADMINISTRACIÓN")
    if st.text_input("Contraseña Maestra:", type="password") == ADMIN_PASS: st.success("Acceso Concedido")

# ==============================================================================
# 3. MÓDULO TALENTO HUMANO (CON FILTROS Y MAPA)
# ==============================================================================
def mostrar_th():
    c1, c2 = st.columns([1, 5])
    with c1: 
        if st.button("⬅ VOLVER"): nav("landing")
    with c2:
        st.markdown(f'<div style="background:#0E2F44; padding:10px; border-radius:8px; color:white; font-weight:bold; height:50px; display:flex; align-items:center;">📊 DASHBOARD ANALÍTICO - TALENTO HUMANO</div>', unsafe_allow_html=True)

    # Inicializar datos por primera vez si existe el archivo local
    if st.session_state.df_nomina is None:
        st.session_state.df_nomina = cargar_nomina()

    # Carga manual
    with st.expander("📁 CARGAR / ACTUALIZAR MATRIZ DE DATOS"):
        archivo = st.file_uploader("Suba su matriz (Excel .xlsx o CSV)", type=["xlsx", "csv"])
        if archivo:
            try:
                df_nuevo = pd.read_excel(archivo) if archivo.name.endswith('.xlsx') else pd.read_csv(archivo)
                st.session_state.df_nomina = df_nuevo
                st.success("✅ Datos cargados en memoria exitosamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al leer archivo: {e}")

    df = st.session_state.df_nomina

    if df is not None and not df.empty:
        df.columns = df.columns.str.upper() # Normalizar columnas
        df_filtered = df.copy()

        st.markdown('<div class="sec-header">🔍 FILTROS GLOBALES DINÁMICOS</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-body">', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        
        if 'GRADO' in df.columns:
            with f1:
                grados = st.multiselect("Grado:", options=sorted(df['GRADO'].dropna().unique()))
                if grados: df_filtered = df_filtered[df_filtered['GRADO'].isin(grados)]
                
        if 'PROVINCIA' in df.columns:
            with f2:
                provs = st.multiselect("Provincia:", options=sorted(df['PROVINCIA'].dropna().unique()))
                if provs: df_filtered = df_filtered[df_filtered['PROVINCIA'].isin(provs)]
                
        with f3:
            search = st.text_input("Buscar Apellido / C.C:")
            if search:
                mask = df_filtered.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                df_filtered = df_filtered[mask]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-header">ANÁLISIS Y DESPLIEGUE</div>', unsafe_allow_html=True)
        g1, g2 = st.columns([1, 1])
        
        with g1:
            st.metric("Personal Encontrado", f"{len(df_filtered)} / {len(df)}")
            if 'GRADO' in df_filtered.columns:
                fig_bar = px.histogram(df_filtered, x='GRADO', title="Distribución por Grado", color_discrete_sequence=['#0E2F44'])
                st.plotly_chart(fig_bar, use_container_width=True)
                
        with g2:
            if 'LATITUD' in df_filtered.columns and 'LONGITUD' in df_filtered.columns:
                fig_map = px.scatter_mapbox(
                    df_filtered, lat="LATITUD", lon="LONGITUD", 
                    hover_name="APELLIDOS Y NOMBRES" if 'APELLIDOS Y NOMBRES' in df_filtered.columns else None,
                    zoom=5.5, center={"lat": -1.8312, "lon": -78.1834}, mapbox_style="carto-positron"
                )
                fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("⚠️ Sin columnas LATITUD y LONGITUD en el archivo. Mapa desactivado.")

        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.info("ℹ️ Cargue la matriz de datos en el panel superior para activar el dashboard.")

# ==============================================================================
# 4. ROUTER
# ==============================================================================
if st.session_state.page == 'landing': mostrar_landing()
elif st.session_state.page == 'secretario': mostrar_secretario()
elif st.session_state.page == 'th': mostrar_th()
elif st.session_state.page == 'admin': mostrar_admin()
elif st.session_state.page == 'generador': st.info("Módulo Generador"); nav("landing")
