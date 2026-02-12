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

# --- 1. CONFIGURACIÓN Y ESTILOS ---
VER_SISTEMA = "v52.0"
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- 2. BASES DE DATOS Y FUNCIONES DE CARGA ---
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

DB_FILE, CONFIG_FILE, CONTRATOS_FILE, LOGS_FILE, LISTAS_FILE = "usuarios_db.json", "config_sistema.json", "contratos_legal.json", "historial_acciones.json", "listas_db.json"

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

# Inicialización de Datos
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

# --- 3. FUNCIONES AUXILIARES ---
def get_hora_ecuador(): return datetime.now(timezone(timedelta(hours=-5)))

def registrar_accion(usuario, accion, detalle=""):
    ahora = get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S")
    db_logs.insert(0, {"fecha": ahora, "usuario": usuario, "accion": accion, "detalle": detalle})
    guardar_json(LOGS_FILE, db_logs)

def actualizar_presencia(cedula_usuario):
    if cedula_usuario in db_usuarios:
        db_usuarios[cedula_usuario]['ultima_actividad'] = get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S")
        guardar_json(DB_FILE, db_usuarios)

def get_estado_usuario(cedula):
    user_data = db_usuarios.get(cedula, {})
    last_seen_str = user_data.get('ultima_actividad')
    if not last_seen_str: return "🔴 DESCONECTADO"
    try:
        last_seen = datetime.strptime(last_seen_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=-5)))
        diferencia = (get_hora_ecuador() - last_seen).total_seconds() / 60
        return "🟢 EN LÍNEA" if diferencia < 5 else "🔴 DESCONECTADO"
    except: return "🔴 ERROR"

def preservar_bordes(cell, fill_obj):
    if cell.border and (cell.border.left.style or cell.border.top.style): new_border = copy(cell.border)
    else:
        thin = Side(border_style="thin", color="000000")
        new_border = Border(top=thin, left=thin, right=thin, bottom=thin)
    cell.border = new_border
    cell.fill = fill_obj
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)

def extract_json_safe(text):
    try: return json.loads(text)
    except:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: return {}
        return {}

# --- 4. PERSISTENCIA F5 (TOKEN URL) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active_module' not in st.session_state: st.session_state.active_module = 'secretario'

token_url = st.query_params.get("token", None)
if token_url and not st.session_state.logged_in:
    if token_url in db_usuarios:
        st.session_state.logged_in = True
        st.session_state.user_id = token_url
        st.session_state.user_role = "admin" if token_url == ADMIN_USER else "user"
        st.session_state.usuario_turno = f"{db_usuarios[token_url]['grado']} {db_usuarios[token_url]['nombre']}"

# --- 5. CONFIGURACIÓN IA ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        st.session_state.genai_model = genai.GenerativeModel("gemini-1.5-flash")
except: pass

def invocar_ia_segura(content):
    try: return st.session_state.genai_model.generate_content(content)
    except: return None

# --- 6. INTERFAZ Y MÓDULOS ---
st.markdown("""<style>.main-header { background-color: #0E2F44; padding: 20px; border-radius: 10px; color: white; text-align: center; border-bottom: 4px solid #D4AF37; }</style>""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    # --- LOGIN ---
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br><h2 style='text-align:center;'>ACCESO SIGD DINIC</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Cédula:").strip()
            p = st.text_input("Clave:", type="password").strip()
            if st.form_submit_button("ENTRAR"):
                if u == ADMIN_USER and p == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True; st.session_state.user_id = u; st.session_state.user_role = "admin"
                elif u in db_usuarios and p == config_sistema["pass_universal"]:
                    st.session_state.logged_in = True; st.session_state.user_id = u; st.session_state.user_role = "user"
                
                if st.session_state.logged_in:
                    st.session_state.usuario_turno = f"{db_usuarios[u]['grado']} {db_usuarios[u]['nombre']}"
                    st.query_params["token"] = u; st.rerun()
else:
    # --- SIDEBAR ---
    actualizar_presencia(st.session_state.user_id)
    with st.sidebar:
        st.info(f"👤 {st.session_state.usuario_turno}")
        if st.button("📝 SECRETARIO/A", use_container_width=True): st.session_state.active_module = 'secretario'; st.rerun()
        if st.button("🧠 ASESOR", use_container_width=True): st.session_state.active_module = 'asesor'; st.rerun()
        if st.button("🛡️ ADMINISTRADOR", use_container_width=True): st.session_state.active_module = 'admin'; st.rerun()
        if st.button("🔒 CERRAR"): st.session_state.logged_in = False; st.query_params.clear(); st.rerun()

    # --- MÓDULO SECRETARIO (RESUMIDO) ---
    if st.session_state.active_module == 'secretario':
        st.markdown('<div class="main-header"><h1>SISTEMA DINIC v52</h1></div>', unsafe_allow_html=True)
        # Aquí va toda su lógica de subir PDF que ya funciona...
        st.write("Módulo de Gestión Documental Activo.")

    # --- MÓDULO ADMINISTRADOR (RESTAURADO AL 100%) ---
    elif st.session_state.active_module == 'admin':
        st.markdown("### 🛡️ PANEL DE CONTROL MAESTRO")
        if st.session_state.user_role == "admin":
            t1, t2, t3, t4 = st.tabs(["📊 Monitor Presencia", "📜 Contratos/Actas", "📑 Historial Logs", "⚙️ Configuración"])
            
            with t1:
                st.markdown("#### Usuarios en Tiempo Real")
                data_p = [{"Grado/Nombre": f"{v['grado']} {v['nombre']}", "Estado": get_estado_usuario(k)} for k,v in db_usuarios.items()]
                st.table(pd.DataFrame(data_p))
            
            with t2:
                st.markdown("#### Actas de Confidencialidad")
                if db_contratos:
                    for k, v in db_contratos.items():
                        st.write(f"✅ {v['usuario']} - {v['fecha']}")
                else: st.info("No hay actas firmadas aún.")
            
            with t3:
                st.markdown("#### Auditoría de Acciones")
                st.dataframe(pd.DataFrame(db_logs), use_container_width=True)
            
            with t4:
                st.markdown("#### Parámetros del Sistema")
                new_pass = st.text_input("Contraseña Universal Usuarios:", value=config_sistema["pass_universal"])
                new_base = st.number_input("Base Histórica Oficios:", value=config_sistema["base_historica"])
                if st.button("Guardar Cambios"):
                    config_sistema["pass_universal"] = new_pass
                    config_sistema["base_historica"] = new_base
                    guardar_json(CONFIG_FILE, config_sistema)
                    st.success("Configuración actualizada.")
        else:
            st.error("Acceso denegado. Solo administradores.")
