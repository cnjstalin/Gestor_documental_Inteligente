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
VER_SISTEMA = "v38.0"
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- 2. BASES DE DATOS ---
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

UNIDADES_DEFAULT = [
    "DINIC", "SOPORTE OPERATIVO", "APOYO OPERATIVO", "PLANIFICACION", 
    "JURIDICO", "COMUNICACION", "ANALISIS DE INFORMACION", "COORDINACION OPERACIONAL", 
    "FINANCIERO", "UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "DAOP", "DCOP", "DSOP"
]

DB_FILE = "usuarios_db.json"
CONFIG_FILE = "config_sistema.json"
CONTRATOS_FILE = "contratos_legal.json"
LOGS_FILE = "historial_acciones.json"
LISTAS_FILE = "listas_db.json"

# FUNCIONES DE CARGA/GUARDADO
def cargar_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except: return default
    return default

def guardar_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f)
    except: pass

def inicializar_usuarios_seguros():
    usuarios_finales = USUARIOS_BASE.copy()
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                usuarios_locales = json.load(f)
                if isinstance(usuarios_locales, dict):
                    usuarios_finales.update(usuarios_locales)
        except: pass
    guardar_json(DB_FILE, usuarios_finales)
    return usuarios_finales

def cargar_listas_desplegables():
    datos = cargar_json(LISTAS_FILE, {"unidades": UNIDADES_DEFAULT, "reasignados": []})
    if not isinstance(datos, dict): datos = {"unidades": UNIDADES_DEFAULT, "reasignados": []}
    for u in UNIDADES_DEFAULT:
        if u not in datos["unidades"]: datos["unidades"].append(u)
    return datos

def guardar_nueva_entrada_lista(tipo, valor):
    datos = cargar_listas_desplegables()
    if valor and valor not in datos[tipo]:
        datos[tipo].append(valor)
        guardar_json(LISTAS_FILE, datos)
        if tipo == "unidades": st.session_state.lista_unidades = datos["unidades"]
        if tipo == "reasignados": st.session_state.lista_reasignados = datos["reasignados"]

# CARGA INICIAL
config_sistema = cargar_json(CONFIG_FILE, {"pass_universal": "DINIC2026", "pass_th": "THDINIC123", "base_historica": 1258, "consultas_ia_global": 0})
db_usuarios = inicializar_usuarios_seguros()
db_contratos = cargar_json(CONTRATOS_FILE, {})
db_logs = cargar_json(LOGS_FILE, [])
if not isinstance(db_logs, list): db_logs = []
db_listas = cargar_listas_desplegables()

if 'lista_unidades' not in st.session_state: st.session_state.lista_unidades = db_listas["unidades"]
if 'lista_reasignados' not in st.session_state: st.session_state.lista_reasignados = db_listas["reasignados"]

# --- 3. FUNCIONES ---
def get_hora_ecuador(): return datetime.now(timezone(timedelta(hours=-5)))

def registrar_accion(usuario, accion, detalle=""):
    ahora = get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_log = {"fecha": ahora, "usuario": usuario, "accion": accion, "detalle": detalle}
    global db_logs
    db_logs.insert(0, nuevo_log)
    guardar_json(LOGS_FILE, db_logs)

def incrementar_contador_ia():
    config_sistema["consultas_ia_global"] = config_sistema.get("consultas_ia_global", 0) + 1
    guardar_json(CONFIG_FILE, config_sistema)

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
        if diferencia < 2: return "🟢 EN LÍNEA"
        elif diferencia < 10: return "🟡 AUSENTE"
        else: return "🔴 DESCONECTADO"
    except: return "🔴 ERROR"

def get_ultima_accion_usuario(nombre_usuario):
    if not isinstance(db_logs, list): return "---"
    for log in db_logs:
        if log.get('usuario') == nombre_usuario:
            fecha = log.get('fecha', '').split(' ')
            hora = fecha[1] if len(fecha) > 1 else ""
            return f"{log.get('accion')} ({hora})"
    return "---"

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

def get_logo_html(width="120px"):
    img_path = "Captura.JPG"
    if os.path.exists(img_path):
        b64 = get_img_as_base64(img_path)
        return f'<img src="data:image/jpeg;base64,{b64}" style="width:{width}; margin-bottom:15px;">'
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" style="width:{width}; margin-bottom:15px;">'

# --- CODIGO DEL GENERADOR POLICIAL (HTML) ---
def get_generador_policial_html():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Generador Policial</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1e1e1e; margin: 0; display: flex; height: 100vh; overflow: hidden; color: #eee; }
        .sidebar { width: 350px; background: #252526; display: flex; flex-direction: column; border-right: 1px solid #333; z-index: 100; box-shadow: 2px 0 10px rgba(0,0,0,0.5); padding: 10px; overflow-y: auto; }
        .header-app { background: linear-gradient(90deg, #003366, #00509e); padding: 10px; text-align: center; border-bottom: 2px solid #00acc1; margin-bottom: 10px; border-radius: 5px; }
        .header-app h2 { margin: 0; font-size: 14px; color: white; text-transform: uppercase; letter-spacing: 1px; }
        .group { margin-bottom: 15px; background: #333; padding: 10px; border-radius: 4px; border: 1px solid #444; }
        .group-title { font-size: 11px; color: #00acc1; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 4px; }
        label { display: block; font-size: 11px; margin-bottom: 3px; color: #ccc; }
        input, select, textarea { width: 100%; padding: 6px; background: #1e1e1e; border: 1px solid #555; color: white; border-radius: 3px; font-size: 12px; box-sizing: border-box; }
        .preview-wrapper { flex: 1; background: #525659; display: flex; justify-content: center; padding: 20px; overflow-y: auto; }
        #hoja-a4 { background: white; width: 210mm; min-height: 296mm; padding: 20mm; box-shadow: 0 0 15px rgba(0,0,0,0.5); color: black; font-family: 'Arial', sans-serif; display: flex; flex-direction: column; box-sizing: border-box; }
        .meta-data { text-align: right; font-weight: bold; font-size: 11pt; margin-bottom: 20px; }
        .body-text { font-size: 12pt; text-align: justify; line-height: 1.5; margin-bottom: 40px; white-space: pre-wrap; }
        .firma-section { margin-top: auto; }
        .btn-main { width: 100%; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; color: white; margin-top: 5px; }
        .btn-blue { background: #00509e; } 
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="header-app"><h2>Generador Policial</h2></div>
        <div class="group">
            <div class="group-title">Configuración</div>
            <label>Tipo Documento</label>
            <select id="docType" onchange="updateView()">
                <option value="MEMORANDO">MEMORANDO</option>
                <option value="OFICIO">OFICIO</option>
            </select>
            <label>Numeración</label>
            <input type="text" id="inpNum" value="PN-DINIC-TH-2026-0048-M" oninput="updateView()">
            <label>Fecha</label>
            <input type="text" id="inpFecha" oninput="updateView()">
            <label>Asunto</label>
            <input type="text" id="inpAsunto" value="ASUNTO DEL DOCUMENTO" oninput="updateView()">
        </div>
        <div class="group">
            <div class="group-title">Contenido</div>
            <label>Cuerpo del Documento</label>
            <div id="editor" contenteditable="true" style="min-height:100px; background:#1e1e1e; border:1px solid #555; padding:5px; font-size:12px;" oninput="updateView()">Escriba aquí el contenido...</div>
        </div>
        <div class="group">
            <div class="group-title">Firmas</div>
            <label>Nombre Firma</label>
            <input type="text" id="inpFirmaNombre" value="NOMBRE APELLIDO" oninput="updateView()">
            <label>Cargo</label>
            <input type="text" id="inpFirmaCargo" value="CARGO POLICIAL" oninput="updateView()">
        </div>
        <button class="btn-main btn-blue" onclick="genPDF()">DESCARGAR PDF</button>
    </div>
    <div class="preview-wrapper">
        <div id="hoja-a4">
            <div class="meta-data">
                <div id="view-num">Memorando Nro...</div>
                <div id="view-fecha">Quito...</div>
            </div>
            <div style="font-weight:bold; margin-bottom:20px;">
                <div>PARA: <span id="view-para">[DESTINATARIO]</span></div>
                <div>ASUNTO: <span id="view-asunto">...</span></div>
            </div>
            <div class="body-text" id="view-cuerpo"></div>
            <div class="firma-section">
                <p>Atentamente,</p>
                <p style="font-weight:bold;">DIOS, PATRIA Y LIBERTAD</p>
                <br><br><br>
                <div id="view-firma-nombre" style="font-weight:bold;">NOMBRE</div>
                <div id="view-firma-cargo">CARGO</div>
            </div>
        </div>
    </div>
    <script>
        function getAutoDate() {
            const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
            const hoy = new Date();
            return `Quito, ${hoy.getDate()} de ${meses[hoy.getMonth()]} de ${hoy.getFullYear()}`;
        }
        document.getElementById('inpFecha').value = getAutoDate();
        function updateView() {
            document.getElementById('view-num').innerText = document.getElementById('inpNum').value;
            document.getElementById('view-fecha').innerText = document.getElementById('inpFecha').value;
            document.getElementById('view-asunto').innerText = document.getElementById('inpAsunto').value;
            document.getElementById('view-cuerpo').innerHTML = document.getElementById('editor').innerHTML;
            document.getElementById('view-firma-nombre').innerText = document.getElementById('inpFirmaNombre').value;
            document.getElementById('view-firma-cargo').innerText = document.getElementById('inpFirmaCargo').value;
        }
        function genPDF() {
            const element = document.getElementById('hoja-a4');
            html2pdf().from(element).save('documento_policial.pdf');
        }
        updateView();
    </script>
</body>
</html>
    """

# --- ESTILOS ---
st.markdown("""
    <style>
    .main-header { background-color: #0E2F44; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #D4AF37; }
    .main-header h1 { margin: 0; font-size: 2.5rem; font-weight: 800; }
    .main-header h3 { margin: 5px 0 0 0; font-size: 1.2rem; font-style: italic; color: #e0e0e0; }
    .metric-card { background-color: #f8f9fa !important; border-radius: 10px; padding: 15px; text-align: center; border: 1px solid #dee2e6; }
    .metric-card h3 { color: #0E2F44 !important; font-size: 2rem; margin: 0; font-weight: 800; }
    .metric-card p { color: #555555 !important; font-size: 1rem; margin: 0; font-weight: 600; }
    .login-container { max-width: 400px; margin: auto; padding: 40px; background-color: #ffffff; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #0E2F44; }
    .legal-warning { background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; color: #856404; font-weight: bold; margin-bottom: 15px; }
    div.stButton > button { width: 100%; font-weight: bold; border-radius: 5px; }
    .admin-badge { background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px; border: 2px solid #b02a37; }
    </style>
""", unsafe_allow_html=True)

# --- 4. VARIABLES DE SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "" 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 
if 'user_id' not in st.session_state: st.session_state.user_id = ""
if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'edit_index' not in st.session_state: st.session_state.edit_index = None 
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'consultas_ia' not in st.session_state: st.session_state.consultas_ia = 0
if 'genai_model' not in st.session_state: st.session_state.genai_model = None
if 'active_module' not in st.session_state: st.session_state.active_module = 'secretario'
if 'th_unlocked' not in st.session_state: st.session_state.th_unlocked = False

# --- 5. CONFIGURACIÓN IA ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        if not st.session_state.genai_model:
            model_name = "gemini-1.5-flash"
            try:
                listado = genai.list_models()
                names = [m.name for m in listado if 'generateContent' in m.supported_generation_methods]
                if any('flash' in n for n in names): model_name = next(n for n in names if 'flash' in n)
            except: pass
            st.session_state.genai_model = genai.GenerativeModel(model_name)
        sistema_activo = True
    else: sistema_activo = False
except: sistema_activo = False

def frases_curiosas():
    frases = ["¿Sabías que? El primer virus se llamó Creeper.", "¿Sabías que? La seguridad es responsabilidad de todos.", "¿Sabías que? Tu contraseña es tu llave digital.", "¿Sabías que? La IA procesa, tú decides.", "¿Sabías que? Un escritorio limpio mejora la productividad."]
    return random.choice(frases)

# --- FUNCIÓN DE LIMPIEZA DE CÓDIGO ---
def extract_json_safe(text):
    try: return json.loads(text)
    except:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try: 
                data = json.loads(match.group())
                if isinstance(data, list) and len(data) > 0: return data[0]
                elif isinstance(data, dict): return data
            except: return {}
        return {}

def limpiar_codigo_prioridad(texto):
    if not texto: return ""
    match = re.search(r"(PN-[\w\-\(\)\.]+)", str(texto).upper())
    if match: 
        codigo = match.group(1).strip()
        codigo = re.sub(r'-(OF|M|MEM|OFICIO|MEMORANDO)$', '', codigo)
        return codigo
    match2 = re.search(r"(?:OFICIO|MEMORANDO).*?(PN-.*)", str(texto), re.IGNORECASE)
    if match2: return match2.group(1).strip().upper()
    return str(texto).strip()

def extraer_unidad_f7(texto_codigo):
    if not texto_codigo: return "DINIC"
    match = re.search(r"PN-(.+?)-QX", str(texto_codigo), re.IGNORECASE)
    if match:
        unidad = match.group(1).strip().upper()
        unidad = unidad.replace('(', '').replace(')', '')
        return unidad
    return "DINIC"

def determinar_sale_no_sale(destinos_str):
    unidades_externas = ["UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "COMANDO GENERAL", "OTRAS DIRECCIONES"]
    destinos_upper = destinos_str.upper()
    for u in unidades_externas:
        if u in destinos_upper: return "SI"
    return "NO"

def invocar_ia_segura(content):
    if not st.session_state.genai_model: raise Exception("IA no configurada")
    max_retries = 3
    for i in range(max_retries):
        try: return st.session_state.genai_model.generate_content(content)
        except Exception as e:
            if "429" in str(e): time.sleep(2); continue
            else: raise e
    raise Exception("Sistema saturado.")

def preservar_bordes(cell, fill_obj):
    original_border = copy(cell.border)
    cell.fill = fill_obj
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)
    if original_border: cell.border = original_border
    else:
        thin = Side(border_style="thin", color="000000")
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

# --- ENCAPSULAMIENTO DE MATRIZ V38 ---
def generar_fila_matriz(tipo, ia_data, manual_data, usuario_turno, paths_files):
    # 1. EXTRACCIÓN Y LIMPIEZA
    raw_code_in = ia_data.get("codigo_entrada", "")
    cod_in = limpiar_codigo_prioridad(raw_code_in)
    unidad_f7 = extraer_unidad_f7(cod_in)
    
    # DATOS DE IA (SEPARADOS POR DOC)
    dest_salida = ia_data.get("destinatarios_salida", "")
    
    raw_code_out = ia_data.get("codigo_salida", "")
    cod_out = limpiar_codigo_prioridad(raw_code_out)
    
    fecha_ia_in = ia_data.get("fecha_recepcion", "")
    fecha_ia_out = ia_data.get("fecha_salida", "")
    
    # ESTADO (S7)
    estado_s7 = "PENDIENTE"
    has_in = True if (paths_files.get("in") or manual_data.get("G")) else False
    has_out = True if (paths_files.get("out") or manual_data.get("P")) else False
    if tipo in ["CONOCIMIENTO", "REASIGNADO", "GENERADO DESDE DESPACHO"]: estado_s7 = "FINALIZADO"
    elif has_in and has_out: estado_s7 = "FINALIZADO"

    str_unidades = manual_data.get("unidades_str", "")
    es_interno = determinar_sale_no_sale(str_unidades)
    if tipo == "CONOCIMIENTO": es_interno = "NO"

    # ROW BASE
    row = {
        "C": fecha_ia_in, # C7: Fecha Doc Entrada
        "D": ia_data.get("remitente_grado_nombre", ""), # D7
        "E": ia_data.get("remitente_cargo", ""), # E7
        "F": unidad_f7, # F7
        "G": cod_in, # G7
        "H": fecha_ia_in, # H7
        "I": ia_data.get("asunto_entrada", ""), # I7
        "J": ia_data.get("resumen_entrada", ""), # J7
        "K": usuario_turno, # K7
        "L": "", # L7
        "M": str_unidades, # M7
        "N": manual_data.get("tipo_doc_salida", ""), # N7
        "O": "", # O7 (Se llena según lógica)
        "P": cod_out, # P7
        "Q": fecha_ia_out, # Q7
        "R": "", # R7
        "S": estado_s7, # S7
        "T": es_interno, # T7
        "U": str_unidades, # U7
        "V": cod_out, # V7
        "W": fecha_ia_out, # W7
        "X": fecha_ia_out, # X7
        "Y": "", "Z": ""
    }

    # --- REGLAS BLINDADAS POR TIPO ---
    if tipo == "TRAMITE NORMAL":
        row["L"] = ""
        # O7: Destinatarios del Doc Respuesta (IA)
        row["O"] = dest_salida
    
    elif tipo == "REASIGNADO":
        row["L"] = "REASIGNADO"
        # P7, V7 VACIAS
        row["P"] = ""; row["V"] = ""
        # O7: Manual
        if manual_data.get("reasignado_a"): row["O"] = manual_data.get("reasignado_a")
        # Fechas Q,W,X = H
        row["Q"] = row["H"]; row["W"] = row["H"]; row["X"] = row["H"]

    elif tipo == "GENERADO DESDE DESPACHO":
        row["L"] = "GENERADO DESDE DESPACHO"
        # D7, E7 VACIAS
        row["D"] = ""; row["E"] = ""
        # Fechas salida mandan
        f_gen = fecha_ia_out if fecha_ia_out else fecha_ia_in
        row["C"] = f_gen; row["H"] = f_gen; row["Q"] = f_gen; row["W"] = f_gen; row["X"] = f_gen
        # Codigo único
        code_final = cod_out if cod_out else cod_in
        row["G"] = code_final; row["P"] = code_final; row["V"] = code_final
        row["F"] = extraer_unidad_f7(code_final)
        # O7: Destinatarios del Doc Respuesta (IA)
        row["O"] = dest_salida

    elif tipo == "CONOCIMIENTO":
        row["L"] = "CONOCIMIENTO"
        # M,O,P,U,V VACIAS
        row["M"] = ""; row["O"] = ""; row["P"] = ""; row["U"] = ""; row["V"] = ""
        row["T"] = "NO"
        row["Q"] = row["C"]; row["W"] = row["C"]; row["X"] = row["C"]

    # Limpieza PENDIENTES
    if row["S"] == "PENDIENTE":
        for k in ["O", "P", "Q", "V", "W", "X"]: row[k] = ""

    return row

# ==============================================================================
#  LOGIN
# ==============================================================================

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="login-container">{get_logo_html()}<h2 style='color:#0E2F44; margin-bottom: 5px;'>ACCESO SIGD DINIC</h2><p style='color: gray; margin-top: 0;'>Sistema Oficial de Gestión Documental</p></div>""", unsafe_allow_html=True)
        with st.form("login_form"):
            usuario_input = st.text_input("Usuario (Cédula):").strip()
            pass_input = st.text_input("Contraseña:", type="password").strip()
            if st.form_submit_button("INGRESAR AL SISTEMA", type="primary"):
                if usuario_input == ADMIN_USER and pass_input == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.session_state.user_id = usuario_input
                    admin_data = db_usuarios.get(ADMIN_USER, {"grado": "CBOS.", "nombre": "CARRILLO NARVAEZ JOHN STALIN"})
                    st.session_state.usuario_turno = f"{admin_data['grado']} {admin_data['nombre']}"
                    st.success("✅ Acceso Concedido: ADMINISTRADOR")
                    registrar_accion(st.session_state.usuario_turno, "INICIO SESIÓN ADMIN")
                    actualizar_presencia(usuario_input)
                    st.rerun()
                elif usuario_input in db_usuarios:
                    user_data = db_usuarios[usuario_input]
                    if pass_input == config_sistema["pass_universal"]:
                        if user_data["activo"]:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "user"
                            st.session_state.user_id = usuario_input
                            st.session_state.usuario_turno = f"{user_data['grado']} {user_data['nombre']}"
                            st.success(f"✅ Bienvenido: {st.session_state.usuario_turno}")
                            registrar_accion(st.session_state.usuario_turno, "INICIO SESIÓN USUARIO")
                            actualizar_presencia(usuario_input)
                            st.rerun()
                        else: st.error("🚫 Usuario inactivo.")
                    else: st.error("🚫 Contraseña incorrecta.")
                else: st.error("🚫 Usuario no autorizado.")

else:
    actualizar_presencia(st.session_state.user_id)
    with st.sidebar:
        if os.path.exists("Captura.JPG"): st.image("Captura.JPG", use_container_width=True)
        else: st.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png", width=100)
        st.markdown("### 👮‍♂️ CONTROL DE MANDO")
        if st.session_state.user_role == "admin": st.markdown("""<div class="admin-badge">🛡️ MODO ADMINISTRADOR<br><span style="font-size: 0.8em; font-weight: normal;">CONTROL TOTAL</span></div>""", unsafe_allow_html=True)
        st.info(f"👤 **{st.session_state.usuario_turno}**")
        fecha_turno = st.date_input("Fecha Operación:", value=get_hora_ecuador().date())
        st.markdown("---"); st.markdown("### 📂 MÓDULOS")
        if st.button("📝 SECRETARIO/A", use_container_width=True, type="primary" if st.session_state.active_module == 'secretario' else "secondary"): st.session_state.active_module = 'secretario'; st.rerun()
        if st.button("🧠 ASESOR INTELIGENTE", use_container_width=True, type="primary" if st.session_state.active_module == 'asesor' else "secondary"): st.session_state.active_module = 'asesor'; st.rerun()
        if st.button("👤 TALENTO HUMANO", use_container_width=True, type="primary" if st.session_state.active_module == 'th' else "secondary"): st.session_state.active_module = 'th'; st.rerun()
        if st.button("🛡️ ADMINISTRADOR", use_container_width=True, type="primary" if st.session_state.active_module == 'admin' else "secondary"): st.session_state.active_module = 'admin'; st.rerun()
        st.markdown("---")
        if st.button("🔒 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()

    if st.session_state.active_module == 'secretario':
        st.markdown(f'''<div class="main-header"><h1>SIGD DINIC</h1><h3>Módulo Secretario/a - Gestión Documental</h3></div>''', unsafe_allow_html=True)
        base_h = config_sistema.get("base_historica", 1258)
        total_d = base_h + len(st.session_state.registros)
        total_ia = config_sistema.get("consultas_ia_global", 0) + st.session_state.consultas_ia
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><h3>📥 {st.session_state.docs_procesados_hoy}</h3><p>Docs Turno Actual</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>📈 {total_d}</h3><p>Total Histórico</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h3>🧠 {total_ia}</h3><p>Consultas IA (Global)</p></div>", unsafe_allow_html=True)
        
        with st.expander("⚙️ CONFIGURACIÓN Y RESPALDO RÁPIDO"):
            c_conf1, c_conf2 = st.columns(2)
            with c_conf1:
                if st.session_state.registros: st.download_button("⬇️ RESPALDO JSON", json.dumps(st.session_state.registros, default=str), "backup_sigd.json", "application/json")
                up_bk = st.file_uploader("⬆️ RESTAURAR JSON", type=['json'])
                if up_bk: 
                    try: 
                        st.session_state.registros = json.load(up_bk); st.session_state.docs_procesados_hoy = len(st.session_state.registros); st.success("¡Restaurado!"); time.sleep(1); st.rerun()
                    except: st.error("Error archivo.")
            with c_conf2:
                if os.path.exists("matriz_maestra.xlsx"):
                    st.success("✅ Matriz Cargada")
                    if st.button("🔄 Cambiar Matriz"): os.remove("matriz_maestra.xlsx"); st.rerun()
                else:
                    up_m = st.file_uploader("Cargar Matriz .xlsx", type=['xlsx'])
                    if up_m: 
                        with open("matriz_maestra.xlsx", "wb") as f: f.write(up_m.getbuffer())
                        st.rerun()
        st.write("")

        if sistema_activo:
            is_edit = st.session_state.edit_index is not None
            idx_edit = st.session_state.edit_index
            reg_edit = st.session_state.registros[idx_edit] if is_edit else None
            
            if is_edit: st.warning(f"✏️ EDITANDO #{idx_edit + 1}"); 
            else: st.info("🆕 NUEVO REGISTRO")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                v_tipo = reg_edit['L'] if (is_edit and reg_edit['L']) else "TRAMITE NORMAL"
                if not v_tipo: v_tipo = "TRAMITE NORMAL"
                tipo_proc = st.selectbox("Tipo Gestión:", ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"], index=["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"].index(v_tipo))
                v_sal = reg_edit['N'] if (is_edit and reg_edit['N']) else "QUIPUX ELECTRONICO"
                tipo_doc = st.selectbox("Formato Salida:", ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"], index=["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"].index(v_sal) if v_sal else 0)
                
                st.markdown("---"); st.caption("🏢 DEPENDENCIA/as DE DESTINO")
                opts_u = sorted(st.session_state.lista_unidades)
                def_u = [u for u in (reg_edit['M'].split(", ") if is_edit and reg_edit['M'] else []) if u in opts_u]
                u_sel = st.multiselect("Seleccione:", opts_u, default=def_u)
                chk_no = st.checkbox("NINGUNA")
                chk_ot = st.checkbox("✍️ OTRA")
                in_ot = st.text_input("Nueva:") if chk_ot else ""
                list_u = u_sel.copy()
                if in_ot: list_u.append(in_ot.upper())
                str_u = ", ".join(list_u) if not chk_no else ""
                
                dest_reasig = ""
                if tipo_proc == "REASIGNADO":
                    st.markdown("---"); st.markdown("👤 **DESTINATARIO REASIGNADO**")
                    opts_r = ["SELECCIONAR..."] + sorted(st.session_state.lista_reasignados) + ["✍️ NUEVO"]
                    idx_r = opts_r.index(reg_edit["O"]) if (is_edit and reg_edit.get("O") in opts_r) else 0
                    sel_r = st.selectbox("Historial:", opts_r, index=idx_r)
                    in_r_man = st.text_input("Grado y Nombre:", value=reg_edit.get("O","") if is_edit else "")
                    if sel_r == "✍️ NUEVO" or in_r_man: dest_reasig = in_r_man.upper()
                    elif sel_r != "SELECCIONAR...": dest_reasig = sel_r

            with col2:
                d_in = None; d_out = None
                if tipo_proc == "TRAMITE NORMAL":
                    c_in, c_out = st.columns(2)
                    d_in = c_in.file_uploader("1. Doc RECIBIDO", ['pdf'])
                    d_out = c_out.file_uploader("2. Doc RESPUESTA", ['pdf'])
                elif tipo_proc in ["REASIGNADO", "CONOCIMIENTO"]:
                    d_in = st.file_uploader("1. Doc RECIBIDO", ['pdf'])
                elif tipo_proc == "GENERADO DESDE DESPACHO":
                    d_out = st.file_uploader("2. Doc GENERADO", ['pdf'])

            if st.button("🔄 ACTUALIZAR" if is_edit else "➕ AGREGAR", type="primary"):
                if not os.path.exists("matriz_maestra.xlsx"): st.error("❌ Falta Matriz.")
                else:
                    process = False
                    if tipo_proc == "TRAMITE NORMAL": process = True if (is_edit or d_in or d_out) else False
                    elif d_in or d_out: process = True
                    
                    if process:
                        with st.spinner(f"⏳ PROCESANDO... {frases_curiosas()}"):
                            try:
                                paths = {"in":None, "out":None}
                                if d_in:
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(d_in.getvalue()); paths["in"] = t.name
                                if d_out:
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(d_out.getvalue()); paths["out"] = t.name
                                
                                files_ia = []
                                if paths["in"]: files_ia.append(genai.upload_file(paths["in"], display_name="In"))
                                if paths["out"]: files_ia.append(genai.upload_file(paths["out"], display_name="Out"))
                                
                                prompt = """
                                ANÁLISIS DOCUMENTAL POLICIAL (DOS ARCHIVOS: ENTRADA Y SALIDA).
                                Distingue claramente entre el documento recibido (antecedente) y el generado (respuesta).

                                DEL DOCUMENTO DE RESPUESTA (DOC 2 - SALIDA):
                                1. DESTINATARIOS (Campo O): Busca la sección 'PARA:' o bajo 'ASUNTO:'. Extrae GRADO y NOMBRE de todos.
                                   - ¡CRÍTICO!: NO incluyas cargos. NO pongas al firmante (Remitente). Separa con comas.
                                2. CÓDIGO (Campo P): Esquina superior derecha (Ej: Oficio Nro. PN-...). Extrae el código completo.
                                3. FECHA SALIDA (Campo Q): Fecha del documento.

                                DEL DOCUMENTO RECIBIDO (DOC 1 - ENTRADA):
                                4. REMITENTE (Campo D): Quien firma.
                                5. CÓDIGO ENTRADA (Campo G): Esquina superior derecha.
                                6. RESUMEN (Campo J): Breve síntesis.

                                JSON ESTRICTO:
                                {
                                    "fecha_recepcion": "DD/MM/AAAA",
                                    "remitente_grado_nombre": "Texto",
                                    "remitente_cargo": "Texto",
                                    "codigo_entrada": "Texto",
                                    "asunto_entrada": "Texto",
                                    "resumen_entrada": "Texto",
                                    "destinatarios_salida": "Texto (Solo Grado y Nombre, comas)",
                                    "codigo_salida": "Texto",
                                    "fecha_salida": "DD/MM/AAAA"
                                }
                                """
                                data_ia = {}
                                if files_ia:
                                    res = invocar_ia_segura([prompt, *files_ia])
                                    txt_clean = res.text.replace("```json", "").replace("```", "")
                                    data_ia = extract_json_safe(txt_clean)
                                
                                final_d = reg_edit.copy() if is_edit else {}
                                man_data = {"unidades_str": str_u, "tipo_doc_salida": tipo_doc, "reasignado_a": dest_reasig, "G": final_d.get("G",""), "P": final_d.get("P","")}
                                row = generar_fila_matriz(tipo_proc, data_ia, man_data, st.session_state.usuario_turno, paths)
                                if in_ot: guardar_nueva_entrada_lista("unidades", in_ot)
                                if dest_reasig: guardar_nueva_entrada_lista("reasignados", dest_reasig)
                                if is_edit: st.session_state.registros[idx_edit] = row; st.session_state.edit_index = None; st.success("✅ Actualizado"); registrar_accion(st.session_state.usuario_turno, f"EDITÓ {row['G']}")
                                else: st.session_state.registros.append(row); st.session_state.docs_procesados_hoy += 1; st.success("✅ Agregado"); registrar_accion(st.session_state.usuario_turno, f"NUEVO {row['G']}")
                                if paths["in"]: os.remove(paths["in"])
                                if paths["out"]: os.remove(paths["out"])
                                st.rerun()
                            except Exception as e: st.error(f"Error: {e}")
                    else: st.warning("⚠️ Sube documento.")

            if st.session_state.registros:
                st.markdown("#### 📋 Cola de Trabajo")
                if len(st.session_state.registros)>0:
                    inds = [f"#{i+1} | {r['G']} | {r['L']}" for i,r in enumerate(st.session_state.registros)]
                    s_idx = st.selectbox("Ver:", range(len(st.session_state.registros)), format_func=lambda x: inds[x], index=len(st.session_state.registros)-1)
                    st.dataframe(pd.DataFrame([st.session_state.registros[s_idx]]), hide_index=True)
                
                for i, r in enumerate(st.session_state.registros):
                    bg = "#e8f5e9" if r["S"]=="FINALIZADO" else "#ffebee"
                    with st.container():
                        st.markdown(f"<div style='background:{bg}; padding:10px; border-left:5px solid {'green' if r['S']=='FINALIZADO' else 'red'}; margin-bottom:5px; border-radius:5px;'><b>#{i+1}</b> | <b>{r['G']}</b> | {r['L']}</div>", unsafe_allow_html=True)
                        c_e, c_d = st.columns([1,1])
                        if c_e.button("✏️", key=f"e{i}"): st.session_state.edit_index = i; st.rerun()
                        if c_d.button("🗑️", key=f"d{i}"): st.session_state.registros.pop(i); st.session_state.docs_procesados_hoy = max(0, st.session_state.docs_procesados_hoy-1); st.rerun()
                
                if os.path.exists("matriz_maestra.xlsx"):
                    try:
                        wb = load_workbook("matriz_maestra.xlsx"); ws = wb[next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])]
                        start_row = 7
                        while ws.cell(row=start_row, column=1).value is not None: start_row += 1
                        gf = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
                        rf = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                        for i, r in enumerate(st.session_state.registros):
                            rw = start_row + i
                            def w(c,v): ws.cell(row=rw, column=c).value = v
                            w(1, i+1); w(2, ""); w(3, r["C"]); w(4, r["D"]); w(5, r["E"]); w(6, r["F"]); w(7, r["G"]); w(8, r["H"]); w(9, r["I"]); w(10, r["J"]); w(11, r["K"]); w(12, r["L"]); w(13, r["M"]); w(14, r["N"]); w(15, r["O"]); w(16, r["P"]); w(17, r["Q"]); w(18, "")
                            cs = ws.cell(row=rw, column=19); cs.value = r["S"]
                            if r["S"]=="FINALIZADO": preservar_bordes(cs, gf)
                            else: preservar_bordes(cs, rf)
                            w(20, r["T"]); w(21, r["U"]); w(22, r["V"]); w(23, r["W"]); w(24, r["X"]); w(25, ""); w(26, "")
                            for c_idx in range(1, 27): 
                                cell = ws.cell(row=rw, column=c_idx)
                                if c_idx != 19: preservar_bordes(cell, PatternFill(fill_type=None))
                        out = io.BytesIO(); wb.save(out); out.seek(0)
                        fn = f"TURNO {fecha_turno.strftime('%d-%m-%y')} {st.session_state.usuario_turno.upper()}.xlsx"
                        st.download_button("📥 DESCARGAR MATRIZ FINAL", out, fn, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
                    except Exception as e: st.error(f"Error Excel: {e}")

    elif st.session_state.active_module == 'asesor':
        st.markdown("### 🧠 Asesor Inteligente")
        if st.session_state.user_id not in db_contratos:
            st.warning("⚠️ Acepte los términos.")
            with st.expander("📜 TÉRMINOS Y CONDICIONES"):
                if st.button("✅ ACEPTAR Y FIRMAR"):
                    db_contratos[st.session_state.user_id] = {"fecha": get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S"), "foto": "", "usuario": st.session_state.usuario_turno}
                    guardar_json(CONTRATOS_FILE, db_contratos); st.rerun()
        else:
            st.markdown("""<div class="legal-warning">⚠️ AVISO LEGAL: Uso referencial.</div>""", unsafe_allow_html=True)
            if st.session_state.user_id in db_contratos:
                st.download_button("📜 Descargar Contrato", generar_html_contrato(db_usuarios.get(st.session_state.user_id,{}),""), "Contrato.html", "text/html")
            up_as = st.file_uploader("Sube PDF", ['pdf'])
            if up_as and st.button("ANALIZAR"):
                with st.spinner("Analizando..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(up_as.getvalue()); p = t.name
                        f = genai.upload_file(p, display_name="Consulta")
                        res = invocar_ia_segura(["Actúa como JEFE. Dame Diagnóstico, Criterio y Extracto.", f])
                        st.markdown(res.text)
                        st.session_state.consultas_ia += 1; incrementar_contador_ia()
                        os.remove(p)
                    except Exception as e: st.error(str(e))

    elif st.session_state.active_module == 'th':
        if not st.session_state.th_unlocked:
            st.markdown("### 👤 Talento Humano"); pwd = st.text_input("Contraseña:", type="password")
            if st.button("Ingresar"): 
                if pwd == config_sistema.get("pass_th", "THDINIC123"): st.session_state.th_unlocked = True; st.rerun()
                else: st.error("Incorrecto")
        else:
            components.html(get_generador_policial_html(), height=800, scrolling=True)
            if st.button("Cerrar"): st.session_state.th_unlocked = False; st.rerun()

    elif st.session_state.active_module == 'admin':
        st.markdown("### 🛡️ ADMINISTRADOR"); pwd = st.text_input("Contraseña Maestra:", type="password")
        if st.session_state.user_role == "admin" and pwd == ADMIN_PASS_MASTER:
            t1, t2, t3, t4 = st.tabs(["Monitor", "Contratos", "Historial", "Config"])
            with t1:
                data = [{"Usuario": f"{v['grado']} {v['nombre']}", "Estado": get_estado_usuario(k)} for k,v in db_usuarios.items()]
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            with t2:
                if db_contratos:
                    for k, v in db_contratos.items():
                        c1, c2, c3 = st.columns([2,1,1])
                        c1.write(f"{v['usuario']} ({v['fecha']})")
                        c2.download_button("⬇️", generar_html_contrato(db_usuarios.get(k,{}), v["foto"]), f"C_{k}.html", key=f"dl_{k}")
                        if c3.button("🗑️", key=f"del_{k}"): del db_contratos[k]; guardar_json(CONTRATOS_FILE, db_contratos); st.rerun()
                else: st.info("Vacío")
            with t3: st.dataframe(pd.DataFrame(db_logs), use_container_width=True)
            with t4:
                st.caption("Contadores"); val = st.number_input("Consultas IA:", value=config_sistema.get("consultas_ia_global",0))
                if st.button("Guardar IA"): config_sistema["consultas_ia_global"]=val; guardar_json(CONFIG_FILE, config_sistema); st.success("OK")
