import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import re
import time
import io  # <--- ¡ESTA ERA LA LIBRERÍA QUE FALTABA!
import pandas as pd
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(
    page_title="S.I.G.D. DINIC - OFICIAL",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        background-color: #0E2F44;
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 3px solid #D4AF37;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        border: 1px solid #dcdcdc;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        color: white;
    }
    div.stButton > button { width: 100%; font-weight: bold; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE ESTADO ---
if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 
if 'edit_index' not in st.session_state: st.session_state.edit_index = None 
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'consultas_ia' not in st.session_state: st.session_state.consultas_ia = 0
if 'modelo_nombre' not in st.session_state: st.session_state.modelo_nombre = None

# --- 3. AUTENTICACIÓN Y CONEXIÓN INTELIGENTE ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🚨 ERROR: No se encontró la API KEY en Secrets.")
        st.stop()
        
    genai.configure(api_key=api_key)
    
    # LÓGICA DE AUTO-DETECCIÓN (La que funcionó en la prueba)
    if not st.session_state.modelo_nombre:
        try:
            listado = genai.list_models()
            for m in listado:
                if 'flash' in m.name and 'generateContent' in m.supported_generation_methods:
                    st.session_state.modelo_nombre = m.name
                    break
            if not st.session_state.modelo_nombre:
                st.session_state.modelo_nombre = "gemini-1.5-flash" # Fallback
        except:
            st.session_state.modelo_nombre = "gemini-1.5-flash"

    # Conexión al modelo detectado
    model = genai.GenerativeModel(st.session_state.modelo_nombre)
    sistema_activo = True

except Exception as e:
    st.error(f"⚠️ Error de Conexión: {e}")
    sistema_activo = False

# --- 4. FUNCIONES AUXILIARES ---

def limpiar_codigo(texto):
    if not texto: return ""
    match = re.search(r"(PN-.*)", str(texto))
    return match.group(1).strip() if match else str(texto).replace("Oficio Nro.", "").strip()

def extraer_unidad(texto):
    if not texto: return ""
    match = re.search(r"PN-(.*?)-QX", str(texto))
    return match.group(1) if match else "DINIC"

def preservar_bordes(cell, fill_obj):
    original_border = copy(cell.border)
    cell.fill = fill_obj
    if original_border:
        cell.border = original_border
    else:
        thin = Side(border_style="thin", color="000000")
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

def invocar_ia_segura(content):
    """Función blindada con reintentos"""
    max_retries = 3
    for i in range(max_retries):
        try:
            return model.generate_content(content)
        except Exception as e:
            if "429" in str(e):
                time.sleep(2)
                continue
            else:
                raise e
    raise Exception("Sistema saturado. Intente de nuevo.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown("### 👮‍♂️ CONTROL DE MANDO")
    
    if st.session_state.modelo_nombre:
        st.caption(f"🟢 Conectado: {st.session_state.modelo_nombre}")

    st.caption("OFICIAL DE TURNO")
    nombre_input = st.text_input("Grado y Nombre:", value=st.session_state.usuario_turno)
    if nombre_input: st.session_state.usuario_turno = nombre_input
    
    fecha_turno = st.date_input("Fecha Operación:", value=datetime.now())

    st.markdown("---")
    st.markdown("### 💾 RESPALDO")
    
    if st.session_state.registros:
        json_str = json.dumps(st.session_state.registros, default=str)
        st.download_button("⬇️ Bajar Backup (JSON)", json_str, file_name="backup_dinic.json", mime="application/json", type="primary")
    
    uploaded_backup = st.file_uploader("⬆️ Restaurar Backup", type=['json'])
    if uploaded_backup:
        try:
            data = json.load(uploaded_backup)
            st.session_state.registros = data
            st.session_state.docs_procesados_hoy = len(data) # Actualizar contador
            st.success("¡Restaurado!")
            st.rerun()
        except: st.error("Archivo corrupto")

    st.markdown("---")
    st.caption("MATRIZ BASE")
    if os.path.exists("matriz_maestra.xlsx"):
        st.success("✅ Matriz Cargada")
        if st.button("Cambiar Matriz"): os.remove("matriz_maestra.xlsx"); st.rerun()
    else:
        up_m = st.file_uploader("Sube Matriz .xlsx", type=['xlsx'])
        if up_m:
            with open("matriz_maestra.xlsx", "wb") as f: f.write(up_m.getbuffer())
            st.rerun()

# ==============================================================================
# ÁREA PRINCIPAL
# ==============================================================================
st.markdown(f'<div class="main-header"><h1>S.I.G.D. - DINIC v26.1</h1><h3>Sistema Oficial de Gestión Documental</h3></div>', unsafe_allow_html=True)

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><h3>📥 {st.session_state.docs_procesados_hoy}</h3><p>Docs Turno Actual</p></div>", unsafe_allow_html=True)
with c2:
    total_historico = 1258 + len(st.session_state.registros)
    st.markdown(f"<div class='metric-card'><h3>📈 {total_historico}</h3><p>Total Histórico</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h3>🧠 {st.session_state.consultas_ia}</h3><p>Consultas Estratégicas</p></div>", unsafe_allow_html=True)

st.write("") 

if sistema_activo:
    tab1, tab2, tab3 = st.tabs(["📊 GESTOR DE MATRIZ", "🕵️‍♂️ ASESOR ESTRATÉGICO", "🛡️ ADMIN (Lunes)"])

    # --- PESTAÑA 1: GESTOR ---
    with tab1:
        is_editing = st.session_state.edit_index is not None
        idx_edit = st.session_state.edit_index
        registro_a_editar = st.session_state.registros[idx_edit] if is_editing else None

        if is_editing:
            st.warning(f"✏️ EDITANDO REGISTRO #{idx_edit + 1}")
            if st.button("❌ CANCELAR EDICIÓN"):
                st.session_state.edit_index = None
                st.rerun()
        else:
            st.info("🆕 NUEVO REGISTRO")

        col1, col2 = st.columns([1, 2])
        with col1:
            val_tipo = registro_a_editar['L'] if (is_editing and registro_a_editar['L']) else "TRAMITE NORMAL"
            if val_tipo == "": val_tipo = "TRAMITE NORMAL"
            tipo_proceso = st.selectbox("Tipo Gestión:", 
                ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"],
                index=["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"].index(val_tipo)
            )
            val_salida = registro_a_editar['N'] if (is_editing and registro_a_editar['N']) else "QUIPUX ELECTRONICO"
            tipo_doc_salida = st.selectbox("Formato Salida:", 
                ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"],
                index=["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"].index(val_salida) if val_salida else 0
            )

        with col2:
            doc_entrada = None
            doc_salida = None
            if tipo_proceso == "TRAMITE NORMAL":
                c1_in, c2_out = st.columns(2)
                lbl_in = "1. Doc RECIBIDO (Opcional si editas)" if is_editing else "1. Doc RECIBIDO"
                doc_entrada = c1_in.file_uploader(lbl_in, type=['pdf'], key="in_main")
                lbl_out = "2. Doc RESPUESTA (Subir para FINALIZAR)" 
                doc_salida = c2_out.file_uploader(lbl_out, type=['pdf'], key="out_main")
            elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
                doc_entrada = st.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_single")
            elif tipo_proceso == "GENERADO DESDE DESPACHO":
                doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_single")

        btn_text = "🔄 ACTUALIZAR" if is_editing else "➕ AGREGAR"
        
        if st.button(btn_text, type="primary"):
            if not os.path.exists("matriz_maestra.xlsx"):
                st.error("❌ Falta Matriz Base (Cargar en menú lateral).")
            else:
                process = False
                if tipo_proceso == "TRAMITE NORMAL":
                    if is_editing: process = True
                    elif doc_entrada or doc_salida: process = True
                elif doc_entrada or doc_salida: process = True
                
                if process:
                    with st.spinner(f"🤖 Procesando con {st.session_state.modelo_nombre}..."):
                        try:
                            paths = []
                            path_in, path_out = None, None
                            if doc_entrada:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                    t.write(doc_entrada.getvalue()); path_in = t.name; paths.append(t.name)
                            if doc_salida:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                    t.write(doc_salida.getvalue()); path_out = t.name; paths.append(t.name)

                            # SUBIDA DE ARCHIVOS A LA IA
                            files_ia = []
                            if path_in: files_ia.append(genai.upload_file(path_in, display_name="In"))
                            if path_out: files_ia.append(genai.upload_file(path_out, display_name="Out"))

                            data = {}
                            if files_ia:
                                prompt = """
                                Extrae datos exactos en formato JSON estricto.
                                1. NOMBRES: "GRADO + NOMBRE COMPLETO".
                                2. CÓDIGOS: Completos.
                                3. MAPEO: UCAP, UNDECOF, UDAR, DIGIN, DNATH, DINIC DAOP/DCOP/DSOP/PLANF/FINA/JURID.
                                
                                JSON:
                                {
                                    "fecha_recepcion": "DD/MM/AAAA",
                                    "remitente_grado_nombre": "Texto",
                                    "remitente_cargo": "Texto",
                                    "codigo_completo_entrada": "Texto",
                                    "asunto_entrada": "Texto",
                                    "resumen_breve": "Texto",
                                    "cargo_destinatario_mapeado": "Texto",
                                    "destinatario_grado_nombre": "Texto",
                                    "codigo_completo_salida": "Texto",
                                    "fecha_salida": "DD/MM/AAAA"
                                }
                                """
                                res = invocar_ia_segura([prompt, *files_ia])
                                data = json.loads(res.text.replace("```json", "").replace("```", ""))

                            final_data = registro_a_editar.copy() if is_editing else {}
                            def get_val(key_ia, key_row): return data.get(key_ia) if data.get(key_ia) else final_data.get(key_row, "")

                            cod_in = limpiar_codigo(get_val("codigo_completo_entrada", "G"))
                            unidad_f7 = extraer_unidad(get_val("codigo_completo_entrada", "G"))
                            
                            tiene_entrada = True if (path_in or (is_editing and final_data.get("G"))) else False
                            tiene_
