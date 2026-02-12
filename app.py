import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import re
import time
import io
import random
import base64
import pandas as pd
import streamlit.components.v1 as components
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment
from datetime import datetime, timedelta, timezone

# --- 1. CONFIGURACIÓN INICIAL DEL SISTEMA ---
VER_SISTEMA = "v51.0 - PRODUCCIÓN"
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- 2. FUNCIONES DE APOYO (DEFINIDAS AL INICIO PARA EVITAR ERRORES) ---
def get_hora_ecuador(): 
    return datetime.now(timezone(timedelta(hours=-5)))

def preservar_bordes(cell, fill_obj):
    """Mantiene el formato de celdas al escribir en Excel"""
    if cell.border and (cell.border.left.style or cell.border.top.style):
        new_border = copy(cell.border)
    else:
        thin = Side(border_style="thin", color="000000")
        new_border = Border(top=thin, left=thin, right=thin, bottom=thin)
    cell.border = new_border
    cell.fill = fill_obj
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)

def extract_json_safe(text):
    """Extrae JSON de la respuesta de la IA de forma robusta"""
    try: return json.loads(text)
    except:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try: 
                data = json.loads(match.group(1))
                return data[0] if isinstance(data, list) and len(data) > 0 else data
            except: return {}
        return {}

def limpiar_codigo_prioridad(texto):
    if not texto: return ""
    match = re.search(r"(PN-[\w\-\(\)\.]+)", str(texto).upper())
    return match.group(1).strip() if match else str(texto).strip().upper()

def extraer_unidad_f7(texto_codigo):
    if not texto_codigo: return "DINIC"
    match = re.search(r"PN-(.+?)-QX", str(texto_codigo), re.IGNORECASE)
    return match.group(1).strip().upper().replace('(', '').replace(')', '') if match else "DINIC"

def determinar_sale_no_sale(destinos_str):
    unidades_externas = ["UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "COMANDO GENERAL", "OTRAS DIRECCIONES"]
    destinos_upper = destinos_str.upper()
    return "SI" if any(u in destinos_upper for u in unidades_externas) else "NO"

# --- 3. GESTIÓN DE BASES DE DATOS ---
USUARIOS_BASE = {
    "0702870460": {"grado": "SGOS", "nombre": "VILLALTA OCHOA XAVIER BISMARK", "activo": True},
    "1715081731": {"grado": "SGOS", "nombre": "MINDA MINDA FRANCISCO GABRIEL", "activo": True},
    "1720103090": {"grado": "SGOS", "nombre": "ZAPATA NAVAS CHRISTIAN VINICIO", "activo": True},
    "1721117057": {"grado": "CBOP", "nombre": "YANQUI RAMOS MONICA ALEXANDRA", "activo": True},
    "1716555154": {"grado": "CBOP", "nombre": "RUANO ARMAS JAIRO RODRIGO", "activo": True},
    "1721350351": {"grado": "CBOP", "nombre": "LOZADA MORENO EDISON WLADIMIR", "activo": True},
    "1718278060": {"grado": "CBOP", "nombre": "CAIZA AMORES DAVID STALIN", "activo": True},
    "1721308086": {"grado": "CBOP", "nombre": "SISALIMA CASTILLO MARÍA JOSE", "activo": True},
    "1721865986": {"grado": "CBOP", "nombre": "VILLACRES CARRILLO SERGIO ALEJANDRO", "activo": True},
    "1722901152": {"grado": "CBOP", "nombre": "ORTIZ GARZON VANESSA LIZBETH", "activo": True},
    "1725283194": {"grado": "CBOP", "nombre": "RODRIGUEZ ESCOBAR DIEGO ALBERTO", "activo": True},
    "1804621520": {"grado": "CBOP", "nombre": "CHUGCHO CHUGCHO CHRISTIAN ESTUARDO", "activo": True},
    "1723730923": {"grado": "CBOP", "nombre": "ALMEIDA CHUGA LUIS ANDRES", "activo": True},
    "1723248942": {"grado": "CBOS", "nombre": "ALMACHI NACIMBA DARIO RAUL", "activo": True},
    "0401770771": {"grado": "CBOS", "nombre": "MORAN CHILAN EDISON JAVIER", "activo": True},
    "1723623011": {"grado": "CBOS", "nombre": "CARRILLO NARVAEZ JOHN STALIN", "activo": True}
}

UNIDADES_DEFAULT = ["DINIC", "SOPORTE OPERATIVO", "APOYO OPERATIVO", "PLANIFICACION", "JURIDICO", "COMUNICACION", "ANALISIS DE INFORMACION", "COORDINACION OPERACIONAL", "FINANCIERO", "UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "DAOP", "DCOP", "DSOP"]

DB_FILE, CONFIG_FILE, CONTRATOS_FILE, LOGS_FILE, LISTAS_FILE = "usuarios_db.json", "config_sistema.json", "contratos_legal.json", "historial_actions.json", "listas_db.json"

def cargar_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except: return default
    return default

def guardar_json(filepath, data):
    try:
        with open(filepath, 'w') as f: json.dump(data, f)
    except: pass

config_sistema = cargar_json(CONFIG_FILE, {"pass_universal": "DINIC2026", "pass_th": "THDINIC123", "base_historica": 1258, "consultas_ia_global": 0})
db_usuarios = USUARIOS_BASE.copy()
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, 'r') as f: db_usuarios.update(json.load(f))
    except: pass
db_contratos = cargar_json(CONTRATOS_FILE, {})
db_logs = cargar_json(LOGS_FILE, [])
if not isinstance(db_logs, list): db_logs = []
db_listas = cargar_json(LISTAS_FILE, {"unidades": UNIDADES_DEFAULT, "reasignados": []})

# --- 4. PERSISTENCIA Y ESTADO DE SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "" 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 
if 'user_id' not in st.session_state: st.session_state.user_id = ""
if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'edit_index' not in st.session_state: st.session_state.edit_index = None 
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'consultas_ia' not in st.session_state: st.session_state.consultas_ia = 0
if 'active_module' not in st.session_state: st.session_state.active_module = 'secretario'
if 'th_unlocked' not in st.session_state: st.session_state.th_unlocked = False

# Recuperar sesión por URL (F5)
token_url = st.query_params.get("token", None)
if token_url and not st.session_state.logged_in:
    if token_url in db_usuarios and db_usuarios[token_url]["activo"]:
        st.session_state.logged_in = True
        st.session_state.user_id = token_url
        st.session_state.user_role = "admin" if token_url == ADMIN_USER else "user"
        st.session_state.usuario_turno = f"{db_usuarios[token_url]['grado']} {db_usuarios[token_url]['nombre']}"

def registrar_accion(usuario, accion, detalle=""):
    ahora = get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S")
    db_logs.insert(0, {"fecha": ahora, "usuario": usuario, "accion": accion, "detalle": detalle})
    guardar_json(LOGS_FILE, db_logs)

# --- 5. CONFIGURACIÓN IA (INTELIGENTE CON CUENTA PAGADA) ---
sistema_activo = False
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        # Prioridad: Flash 1.5 (Rápido y moderno)
        try:
            st.session_state.genai_model = genai.GenerativeModel("gemini-1.5-flash")
        except:
            st.session_state.genai_model = genai.GenerativeModel("gemini-pro")
        sistema_activo = True
except: sistema_activo = False

def invocar_ia_segura(content):
    if not st.session_state.genai_model: raise Exception("IA no configurada")
    max_retries = 3
    for i in range(max_retries):
        try: return st.session_state.genai_model.generate_content(content)
        except Exception as e:
            if i == max_retries - 1: raise Exception(f"Error de conexión con Google: {str(e)}")
            time.sleep(2)
    return None

# --- 6. DISEÑO PREMIUM ---
st.markdown("""
    <style>
    .main-header { background-color: #0E2F44; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #D4AF37; }
    .metric-card { background-color: #f8f9fa !important; border-radius: 10px; padding: 15px; text-align: center; border: 1px solid #dee2e6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-card h3 { color: #0E2F44 !important; font-size: 2rem; margin: 0; font-weight: 800; }
    .login-container { max-width: 400px; margin: auto; padding: 40px; background-color: #ffffff; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #0E2F44; }
    </style>
""", unsafe_allow_html=True)

# --- 7. LÓGICA DE LOGIN ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f'<div class="login-container"><h2 style="color:#0E2F44;">ACCESO SIGD DINIC</h2><p style="color:gray;">Sistema Oficial v51.0</p></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            u_in = st.text_input("Usuario (Cédula):").strip()
            p_in = st.text_input("Contraseña:", type="password").strip()
            if st.form_submit_button("INGRESAR", type="primary"):
                if u_in == ADMIN_USER and p_in == ADMIN_PASS_MASTER:
                    login_ok = True; st.session_state.user_role = "admin"
                elif u_in in db_usuarios and p_in == config_sistema["pass_universal"]:
                    login_ok = True; st.session_state.user_role = "user"
                else: login_ok = False; st.error("🚫 Error de acceso")
                
                if login_ok:
                    st.session_state.logged_in = True; st.session_state.user_id = u_in
                    st.session_state.usuario_turno = f"{db_usuarios.get(u_in, {'grado':'--','nombre':'Admin'})['grado']} {db_usuarios.get(u_in, {'grado':'--','nombre':'Admin'})['nombre']}"
                    st.query_params["token"] = u_in
                    registrar_accion(st.session_state.usuario_turno, "INICIÓ SESIÓN")
                    st.rerun()
else:
    # --- INTERFAZ PRINCIPAL ---
    with st.sidebar:
        st.markdown("### 👮‍♂️ PANEL DE CONTROL")
        st.info(f"👤 **{st.session_state.usuario_turno}**")
        st.markdown("---")
        if st.button("📝 SECRETARIO/A", use_container_width=True, type="primary" if st.session_state.active_module == 'secretario' else "secondary"): st.session_state.active_module = 'secretario'; st.rerun()
        if st.button("🧠 ASESOR INTELIGENTE", use_container_width=True, type="primary" if st.session_state.active_module == 'asesor' else "secondary"): st.session_state.active_module = 'asesor'; st.rerun()
        if st.button("👤 TALENTO HUMANO", use_container_width=True, type="primary" if st.session_state.active_module == 'th' else "secondary"): st.session_state.active_module = 'th'; st.rerun()
        if st.button("🔒 CERRAR SESIÓN"): st.session_state.logged_in = False; st.query_params.clear(); st.rerun()

    if st.session_state.active_module == 'secretario':
        st.markdown(f'<div class="main-header"><h1>SIGD DINIC</h1><h3>Gestión Documental Estratégica</h3></div>', unsafe_allow_html=True)
        
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><h3>📥 {st.session_state.docs_procesados_hoy}</h3><p>Turno Actual</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>📈 {config_sistema['base_historica'] + len(st.session_state.registros)}</h3><p>Histórico Total</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h3>🚀 FLASH</h3><p>Estado de IA</p></div>", unsafe_allow_html=True)
        
        # Subida y Proceso
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        with col1:
            tipo_gestion = st.selectbox("Tipo de Gestión:", ["TRAMITE NORMAL", "REASIGNADO", "CONOCIMIENTO", "GENERADO DESDE DESPACHO"])
            str_unidades = st.text_input("Dependencia de Destino (Ej: UDAR, DNATH):").upper()
            
        with col2:
            d_in = st.file_uploader("Documento Recibido (PDF)", type=['pdf'])
            d_out = st.file_uploader("Documento de Respuesta (PDF)", type=['pdf']) if tipo_gestion != "CONOCIMIENTO" else None

        if st.button("⚙️ PROCESAR DOCUMENTOS", type="primary"):
            if d_in or d_out:
                with st.spinner("🧠 Analizando documentos con IA Policial..."):
                    try:
                        paths = {"in": None, "out": None}
                        files_ia = []
                        if d_in:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(d_in.getvalue()); paths["in"] = t.name
                            files_ia.append(genai.upload_file(paths["in"]))
                        if d_out:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(d_out.getvalue()); paths["out"] = t.name
                            files_ia.append(genai.upload_file(paths["out"]))
                        
                        prompt = """Analiza los documentos policiales y extrae JSON. 
                        REGLA PARA O7: Busca 'PARA:'. Extrae solo GRADOS y NOMBRES. 
                        ¡PROHIBIDO EXTRAER CARGOS O QUIEN FIRMA AL FINAL!"""
                        
                        res = invocar_ia_segura([prompt, *files_ia])
                        data_ia = extract_json_safe(res.text)
                        
                        # Armar Fila
                        row = {
                            "C": data_ia.get("fecha", ""), "D": data_ia.get("remitente_nombre", ""), 
                            "E": data_ia.get("remitente_cargo", ""), "F": extraer_unidad_f7(data_ia.get("codigo", "")),
                            "G": limpiar_codigo_prioridad(data_ia.get("codigo", "")), "I": data_ia.get("asunto", ""),
                            "J": data_ia.get("resumen", ""), "K": st.session_state.usuario_turno, 
                            "M": str_unidades, "S": "FINALIZADO" if d_out else "PENDIENTE",
                            "O": data_ia.get("destinatarios", ""), "P": data_ia.get("respuesta_codigo", "")
                        }
                        st.session_state.registros.append(row)
                        st.session_state.docs_procesados_hoy += 1
                        st.success("✅ Registro agregado exitosamente.")
                        st.rerun()
                    except Exception as e: st.error(f"Error: {str(e)}")

        # Tabla de trabajo
        if st.session_state.registros:
            st.markdown("### 📋 REGISTROS DEL TURNO")
            st.dataframe(pd.DataFrame(st.session_state.registros), use_container_width=True)
            
            # Descarga de Excel
            if os.path.exists("matriz_maestra.xlsx") and st.button("📥 DESCARGAR MATRIZ (.xlsx)"):
                try:
                    wb = load_workbook("matriz_maestra.xlsx")
                    ws = wb.active
                    for i, r in enumerate(st.session_state.registros):
                        ws.append([i+1, "", r.get("C"), r.get("D"), r.get("E"), r.get("F"), r.get("G")])
                    out = io.BytesIO()
                    wb.save(out)
                    st.download_button("Click para descargar", out.getvalue(), "MATRIZ_DINIC.xlsx")
                except: st.error("Falta archivo matriz_maestra.xlsx")

    elif st.session_state.active_module == 'asesor':
        st.markdown("### 🧠 ASESOR INTELIGENTE")
        u_pdf = st.file_uploader("Sube un documento para análisis táctico", type=['pdf'])
        if u_pdf and st.button("ANALIZAR DOCUMENTO"):
            with st.spinner("Generando diagnóstico policial..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(u_pdf.getvalue()); p = t.name
                f = genai.upload_file(p)
                res = invocar_ia_segura(["Como Jefe Policial, dame: 1. Extracto 2. Diagnóstico 3. Criterio Jurídico.", f])
                st.markdown(res.text)

    elif st.session_state.active_module == 'th':
        st.markdown("### 👤 TALENTO HUMANO - GENERADOR")
        st.info("Generador de documentos DINIC en desarrollo...")
