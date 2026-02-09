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
import socket
import pandas as pd
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment
from datetime import datetime, timedelta, timezone

# --- 1. CONFIGURACIÓN Y ESTILOS ---
VER_SISTEMA = "v27.6"
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- 2. BASE DE DATOS DE USUARIOS (INCRUSTADA) ---
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

DB_FILE = "usuarios_db.json"
CONFIG_FILE = "config_sistema.json"
CONTRATOS_FILE = "contratos_legal.json"

def cargar_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except: return default
    return default

def guardar_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)

config_sistema = cargar_json(CONFIG_FILE, {"pass_universal": "DINIC2026"})
db_usuarios = cargar_json(DB_FILE, USUARIOS_BASE)
if not db_usuarios: db_usuarios = USUARIOS_BASE
db_contratos = cargar_json(CONTRATOS_FILE, {})

# --- 3. FUNCIONES DE TIEMPO Y LOGO ---
def get_hora_ecuador():
    # UTC - 5
    return datetime.now(timezone(timedelta(hours=-5)))

def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_logo_html(width="120px"):
    img_path = "Captura.JPG"
    if os.path.exists(img_path):
        b64 = get_img_as_base64(img_path)
        return f'<img src="data:image/jpeg;base64,{b64}" style="width:{width}; margin-bottom:15px;">'
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" style="width:{width}; margin-bottom:15px;">'

st.markdown("""
    <style>
    .main-header { background-color: #0E2F44; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #D4AF37; }
    .main-header h1 { margin: 0; font-size: 2.5rem; font-weight: 800; }
    .main-header h3 { margin: 5px 0 0 0; font-size: 1.2rem; font-style: italic; color: #e0e0e0; }
    .metric-card { background-color: #f8f9fa; border-radius: 10px; padding: 15px; text-align: center; border: 1px solid #dee2e6; }
    .login-container { max-width: 400px; margin: auto; padding: 40px; background-color: #ffffff; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #0E2F44; }
    .legal-warning { background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; color: #856404; font-weight: bold; margin-bottom: 15px; }
    div.stButton > button { width: 100%; font-weight: bold; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. GESTIÓN DE SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "" 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 
if 'user_id' not in st.session_state: st.session_state.user_id = ""

if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'edit_index' not in st.session_state: st.session_state.edit_index = None 
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'consultas_ia' not in st.session_state: st.session_state.consultas_ia = 0
if 'genai_model' not in st.session_state: st.session_state.genai_model = None

if 'lista_unidades' not in st.session_state: 
    st.session_state.lista_unidades = [
        "DINIC", "SOPORTE OPERATIVO", "APOYO OPERATIVO", "PLANIFICACION", 
        "JURIDICO", "COMUNICACION", "ANALISIS DE INFORMACION", "COORDINACION OPERACIONAL", 
        "FINANCIERO", "UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "DAOP", "DCOP", "DSOP"
    ]
if 'lista_reasignados' not in st.session_state: st.session_state.lista_reasignados = []

# --- 5. CONFIGURACIÓN IA (AUTO-REPARACIÓN) ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        
        # LÓGICA DE DETECCIÓN AUTOMÁTICA DE MODELO
        if not st.session_state.genai_model:
            model_name = "gemini-pro" # Fallback por defecto
            try:
                # Intentamos listar modelos disponibles para la API KEY
                listado = genai.list_models()
                modelos_disponibles = [m.name for m in listado if 'generateContent' in m.supported_generation_methods]
                
                # Buscamos prioridades
                flash_models = [m for m in modelos_disponibles if 'flash' in m]
                pro_models = [m for m in modelos_disponibles if 'pro' in m and 'vision' not in m] # Vision a veces da error con texto solo
                
                if flash_models:
                    model_name = flash_models[0]
                elif pro_models:
                    model_name = pro_models[0]
                elif modelos_disponibles:
                    model_name = modelos_disponibles[0]
                    
            except Exception as e:
                # Si falla listar, forzamos uno conocido
                model_name = "gemini-1.5-flash"

            st.session_state.genai_model = genai.GenerativeModel(model_name)
            # st.toast(f"IA Conectada: {model_name}") # Debug visual opcional
            
        sistema_activo = True
    else:
        sistema_activo = False
except Exception as e:
    st.error(f"Error Conexión IA: {e}")
    sistema_activo = False

def frases_curiosas():
    frases = ["¿Sabías que? El primer virus se llamó Creeper.", "¿Sabías que? La seguridad es responsabilidad de todos.", "¿Sabías que? Tu contraseña es tu llave digital.", "¿Sabías que? La IA procesa, tú decides.", "¿Sabías que? Un escritorio limpio mejora la productividad."]
    return random.choice(frases)

def limpiar_codigo(texto):
    if not texto: return ""
    match = re.search(r"(PN-[A-Z0-9]+-QX(?:-\d+)?(?:-OF|-MM)?)", str(texto), re.IGNORECASE)
    if match: return match.group(1).strip().upper()
    match2 = re.search(r"(?:Oficio|Memorando).*?(PN-.*)", str(texto), re.IGNORECASE)
    if match2: return match2.group(1).strip().upper()
    return str(texto).strip()

def extraer_unidad_f7(texto_codigo):
    if not texto_codigo: return "DINIC"
    match = re.search(r"PN-([A-Z\s]+)-QX", str(texto_codigo).upper())
    if match: return match.group(1).strip()
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
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    if original_border: cell.border = original_border
    else:
        thin = Side(border_style="thin", color="000000")
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

def generar_html_contrato(datos_usuario, img_b64):
    fecha_hora = get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S")
    logo_b64 = ""
    if os.path.exists("Captura.JPG"):
        logo_b64 = get_img_as_base64("Captura.JPG")
    
    logo_html_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:100px; display:block; margin: 0 auto;">' if logo_b64 else ""

    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 40px; border: 2px solid #000; max-width: 800px; margin: auto;">
        <div style="text-align: center;">
            {logo_html_tag}
            <h2>ACTA DE COMPROMISO Y CONFIDENCIALIDAD<br>USO DEL ASESOR INTELIGENTE SIGD-DINIC</h2>
        </div>
        <br>
        <p><strong>Usuario:</strong> {datos_usuario['grado']} {datos_usuario['nombre']}</p>
        <p><strong>Cédula:</strong> {st.session_state.user_id}</p>
        <p><strong>Fecha y Hora de Aceptación:</strong> {fecha_hora}</p>
        <hr>
        <h3>TÉRMINOS Y CONDICIONES DEL ASESOR INTELIGENTE SIGD</h3>
        <p>Yo, el servidor policial arriba identificado, declaro haber leído, entendido y aceptado las siguientes políticas:</p>
        <ol>
            <li><strong>Naturaleza de Apoyo:</strong> El Asesor Estratégico es una herramienta de Inteligencia Artificial generativa diseñada exclusivamente como apoyo técnico y de consulta. No sustituye el criterio, mando ni decisión del servidor policial.</li>
            <li><strong>Carácter Referencial:</strong> Todo contenido, análisis, extracto o redacción generado por este sistema es estrictamente referencial y tentativo. No constituye un documento oficial ni una orden vinculante hasta que sea revisado y firmado por la autoridad competente.</li>
            <li><strong>Responsabilidad Humana:</strong> El Oficial de Turno o usuario asume la responsabilidad total y exclusiva de verificar, corregir y validar la información antes de plasmarla en sistemas oficiales (Quipux, Partes Web, etc.).</li>
            <li><strong>Verificación Normativa:</strong> Es obligación del usuario contrastar las sugerencias de la IA con la normativa legal vigente (COIP, COESCOP, Reglamentos) para evitar errores jurídicos o de procedimiento.</li>
            <li><strong>Prohibición de Datos Sensibles:</strong> Queda estrictamente prohibido ingresar nombres de fuentes humanas, datos de víctimas protegidas o información clasificada como "SECRETA" que ponga en riesgo operaciones en curso.</li>
            <li><strong>No Vinculante:</strong> Las recomendaciones tácticas (diagnósticos) emitidas por el sistema no tienen validez legal ni administrativa por sí mismas y no eximen de responsabilidad al usuario por acciones tomadas basándose en ellas.</li>
            <li><strong>Posibilidad de Error:</strong> El usuario reconoce que la IA puede incurrir en "alucinaciones" (datos inexactos) y se compromete a realizar el control de calidad de cada párrafo generado.</li>
            <li><strong>Trazabilidad de Uso:</strong> El sistema registra la identidad, fecha y hora del acceso para fines de auditoría y control de gestión de la DINIC.</li>
            <li><strong>Uso Ético:</strong> La herramienta debe utilizarse estrictamente para fines institucionales. Cualquier uso para fines personales o ajenos al servicio será sancionado disciplinariamente.</li>
            <li><strong>Aceptación de Riesgo:</strong> Al ingresar, el usuario declara entender estas limitaciones y libera a la administración del sistema de cualquier responsabilidad por el mal uso de la información generada.</li>
        </ol>
        <br><br>
        <div style="border: 1px dashed #333; padding: 15px; width: fit-content; margin-left: auto;">
            <p style="text-align: center; font-size: 12px; margin-bottom: 5px;"><strong>EVIDENCIA BIOMÉTRICA DE ACEPTACIÓN</strong></p>
            <img src="data:image/png;base64,{img_b64}" style="width: 150px; border: 1px solid #ccc;">
            <p style="font-size: 10px; text-align: center; margin-top: 5px;">Firma Digital: {fecha_hora}</p>
        </div>
    </div>
    """
    return html

# ==============================================================================
#  LOGIN
# ==============================================================================

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-container">
            {get_logo_html()}
            <h2 style='color:#0E2F44; margin-bottom: 5px;'>ACCESO SIGD DINIC</h2>
            <p style='color: gray; margin-top: 0;'>Sistema Oficial de Gestión Documental</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario_input = st.text_input("Usuario (Cédula):").strip()
            pass_input = st.text_input("Contraseña:", type="password").strip()
            if st.form_submit_button("INGRESAR AL SISTEMA", type="primary"):
                # ADMIN
                if usuario_input == ADMIN_USER and pass_input == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.session_state.user_id = usuario_input
                    st.session_state.usuario_turno = "CBOS. JOHN CARRILLO" 
                    st.success("✅ Acceso Concedido: ADMINISTRADOR")
                    st.rerun()
                # USUARIOS
                elif usuario_input in db_usuarios:
                    user_data = db_usuarios[usuario_input]
                    if pass_input == config_sistema["pass_universal"]:
                        if user_data["activo"]:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "user"
                            st.session_state.user_id = usuario_input
                            st.session_state.usuario_turno = f"{user_data['grado']} {user_data['nombre']}"
                            st.success(f"✅ Bienvenido: {st.session_state.usuario_turno}")
                            st.rerun()
                        else: st.error("🚫 Usuario inactivo.")
                    else: st.error("🚫 Contraseña incorrecta.")
                else: st.error("🚫 Usuario no autorizado.")

else:
    # ==============================================================================
    #  SISTEMA PRINCIPAL
    # ==============================================================================
    
    with st.sidebar:
        if os.path.exists("Captura.JPG"): st.image("Captura.JPG", use_container_width=True)
        else: st.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png", width=100)
        
        st.markdown("### 👮‍♂️ CONTROL DE MANDO")
        st.info(f"👤 **{st.session_state.usuario_turno}**")
        
        fecha_turno = st.date_input("Fecha Operación:", value=get_hora_ecuador().date())

        st.markdown("---")
        if st.button("🗑️ NUEVO TURNO (Limpiar)", type="primary"):
            st.session_state.registros = []
            st.session_state.docs_procesados_hoy = 0
            st.rerun()

        st.markdown("---")
        if st.session_state.registros:
            json_str = json.dumps(st.session_state.registros, default=str)
            st.download_button("⬇️ DESCARGAR RESPALDO SIGD", json_str, file_name="backup_sigd.json", mime="application/json")
        
        uploaded_backup = st.file_uploader("⬆️ RESTAURAR RESPALDO SIGD", type=['json'])
        if uploaded_backup:
            try:
                data = json.load(uploaded_backup)
                st.session_state.registros = data
                st.success("¡Backup Restaurado!")
                time.sleep(1)
                st.rerun()
            except: st.error("Archivo corrupto.")

        st.markdown("---")
        if os.path.exists("matriz_maestra.xlsx"):
            st.success("✅ Matriz Cargada")
            if st.button("🔄 Cambiar Matriz"): os.remove("matriz_maestra.xlsx"); st.rerun()
        else:
            up_m = st.file_uploader("Cargar Matriz .xlsx", type=['xlsx'])
            if up_m:
                with open("matriz_maestra.xlsx", "wb") as f: f.write(up_m.getbuffer())
                st.rerun()
        
        st.markdown("---")
        if st.button("🔒 CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown(f'''<div class="main-header"><h1>SIGD DINIC</h1><h3>Sistema de Gestión Documental</h3></div>''', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><h3>📥 {st.session_state.docs_procesados_hoy}</h3><p>Docs Turno Actual</p></div>", unsafe_allow_html=True)
    with c2: 
        hist = 1258 + len(st.session_state.registros)
        st.markdown(f"<div class='metric-card'><h3>📈 {hist}</h3><p>Total Histórico</p></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>🧠 {st.session_state.consultas_ia}</h3><p>Consultas IA</p></div>", unsafe_allow_html=True)
    st.write("")

    if sistema_activo:
        tab1, tab2, tab3 = st.tabs(["📊 GESTOR DE MATRIZ", "🕵️‍♂️ ASESOR", "🛡️ ADMIN"])

        # --- TAB 1: GESTOR ---
        with tab1:
            is_editing = st.session_state.edit_index is not None
            idx_edit = st.session_state.edit_index
            registro_a_editar = st.session_state.registros[idx_edit] if is_editing else None

            if is_editing:
                st.warning(f"✏️ EDITANDO REGISTRO #{idx_edit + 1}")
                if st.button("❌ CANCELAR EDICIÓN"): st.session_state.edit_index = None; st.rerun()
            else: st.info("🆕 NUEVO REGISTRO")

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

                st.markdown("---")
                st.caption("🏢 DEPENDENCIA/as DE DESTINO")
                opciones_unidades = sorted(st.session_state.lista_unidades)
                default_units = []
                if is_editing and registro_a_editar['M']:
                    prev_units = registro_a_editar['M'].split(", ")
                    default_units = [u for u in prev_units if u in opciones_unidades]

                unidades_selected = st.multiselect("Seleccione Unidad(es):", opciones_unidades, default=default_units)
                col_ning, col_otra = st.columns(2)
                chk_ninguna = col_ning.checkbox("NINGUNA")
                chk_otra = col_otra.checkbox("✍️ OTRA")
                
                input_otra_unidad = ""
                if chk_otra: input_otra_unidad = st.text_input("Nueva Unidad:").upper()

                lista_final_unidades = []
                if chk_ninguna: lista_final_unidades = [] 
                else:
                    lista_final_unidades = unidades_selected.copy()
                    if input_otra_unidad: lista_final_unidades.append(input_otra_unidad)
                str_unidades_final = ", ".join(lista_final_unidades)

                destinatario_reasignado_final = ""
                if tipo_proceso == "REASIGNADO":
                    st.markdown("---")
                    st.markdown("👤 **DESTINATARIO REASIGNADO**")
                    opciones_reasig = ["SELECCIONAR..."] + st.session_state.lista_reasignados + ["✍️ NUEVO"]
                    idx_rea = 0 
                    if is_editing and registro_a_editar.get("O") in st.session_state.lista_reasignados:
                            idx_rea = opciones_reasig.index(registro_a_editar["O"])

                    sel_reasig = st.selectbox("Historial:", opciones_reasig, index=idx_rea)
                    val_manual = ""
                    if is_editing and registro_a_editar.get("O") and registro_a_editar.get("O") not in st.session_state.lista_reasignados:
                        val_manual = registro_a_editar.get("O")
                    input_manual_reasig = st.text_input("Grado y Nombre:", value=val_manual)
                    
                    if sel_reasig == "✍️ NUEVO" or input_manual_reasig:
                        destinatario_reasignado_final = input_manual_reasig.upper()
                    elif sel_reasig != "SELECCIONAR...":
                        destinatario_reasignado_final = sel_reasig

            with col2:
                doc_entrada = None
                doc_salida = None
                if tipo_proceso == "TRAMITE NORMAL":
                    c1_in, c2_out = st.columns(2)
                    doc_entrada = c1_in.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_main")
                    doc_salida = c2_out.file_uploader("2. Doc RESPUESTA", type=['pdf'], key="out_main")
                elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
                    doc_entrada = st.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_s")
                elif tipo_proceso == "GENERADO DESDE DESPACHO":
                    doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_s")

            btn_text = "🔄 ACTUALIZAR" if is_editing else "➕ AGREGAR"
            
            if st.button(btn_text, type="primary"):
                if not os.path.exists("matriz_maestra.xlsx"):
                    st.error("❌ Falta Matriz Base.")
                else:
                    valid_units = True
                    if tipo_proceso != "CONOCIMIENTO" and not str_unidades_final and not chk_ninguna:
                        st.warning("⚠️ Seleccione Dependencia de Destino.")
                        valid_units = False
                    
                    if valid_units:
                        process = False
                        if tipo_proceso == "TRAMITE NORMAL": process = True if (is_editing or doc_entrada or doc_salida) else False
                        elif doc_entrada or doc_salida: process = True
                        
                        if process:
                            frase = frases_curiosas()
                            with st.spinner(f"⏳ AGREGANDO A LA LISTA UN MOMENTO POR FAVOR...\n\n👀 {frase}"):
                                try:
                                    paths = []; path_in = None; path_out = None
                                    if doc_entrada:
                                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                            t.write(doc_entrada.getvalue()); path_in = t.name; paths.append(t.name)
                                    if doc_salida:
                                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                            t.write(doc_salida.getvalue()); path_out = t.name; paths.append(t.name)

                                    files_ia = []
                                    if path_in: files_ia.append(genai.upload_file(path_in, display_name="In"))
                                    if path_out: files_ia.append(genai.upload_file(path_out, display_name="Out"))

                                    prompt = """
                                    Extrae datos en JSON estricto.
                                    1. DESTINATARIOS: "Grado Nombre, Grado Nombre". (Todos los 'Para').
                                    2. CODIGO: "PN-XYZ-QX-202X".
                                    3. FECHAS: DD/MM/AAAA.
                                    4. RESUMEN: Breve descripción.
                                    JSON: {
                                        "fecha_recepcion": "DD/MM/AAAA", "remitente_grado_nombre": "Texto", "remitente_cargo": "Texto", "codigo_completo_entrada": "Texto", "asunto_entrada": "Texto", "resumen_breve": "Texto", "destinatarios_todos": "Texto con comas", "codigo_completo_salida": "Texto", "fecha_salida": "DD/MM/AAAA"
                                    }
                                    """
                                    data = {}
                                    if files_ia:
                                        res = invocar_ia_segura([prompt, *files_ia])
                                        txt_clean = res.text.replace("```json", "").replace("```", "")
                                        data = json.loads(txt_clean)

                                    final_data = registro_a_editar.copy() if is_editing else {}
                                    def get_val(key_ia, key_row): return data.get(key_ia) if data.get(key_ia) else final_data.get(key_row, "")

                                    raw_code_in = get_val("codigo_completo_entrada", "G")
                                    cod_in = limpiar_codigo(raw_code_in)
                                    unidad_f7 = extraer_unidad_f7(cod_in)
                                    dest_ia = get_val("destinatarios_todos", "O")
                                    raw_code_out = get_val("codigo_completo_salida", "P")
                                    cod_out = limpiar_codigo(raw_code_out)

                                    estado_s7 = "PENDIENTE"
                                    if tipo_proceso in ["CONOCIMIENTO", "REASIGNADO", "GENERADO DESDE DESPACHO"]: estado_s7 = "FINALIZADO"
                                    elif (path_in or final_data.get("G")) and (path_out or final_data.get("P")): estado_s7 = "FINALIZADO"

                                    es_interno = determinar_sale_no_sale(str_unidades_final)
                                    if tipo_proceso == "CONOCIMIENTO": es_interno = "NO"

                                    row = {
                                        "C": get_val("fecha_recepcion", "C"), "D": get_val("remitente_grado_nombre", "D"), "E": get_val("remitente_cargo", "E"), "F": unidad_f7, "G": cod_in, "H": get_val("fecha_recepcion", "H"), "I": get_val("asunto_entrada", "I"), "J": get_val("resumen_breve", "J"),
                                        "K": st.session_state.usuario_turno, 
                                        "L": "", "M": str_unidades_final, "N": tipo_doc_salida, "O": dest_ia, "P": cod_out, "Q": get_val("fecha_salida", "Q"), "R": "", "S": estado_s7, "T": es_interno, "U": str_unidades_final, "V": cod_out, "W": get_val("fecha_salida", "W"), "X": get_val("fecha_salida", "X"), "Y": "", "Z": ""
                                    }

                                    if tipo_proceso == "TRAMITE NORMAL": row["L"] = ""
                                    elif tipo_proceso == "REASIGNADO":
                                        row["L"] = "REASIGNADO"; row["P"] = row["G"]; row["V"] = row["P"]; row["Q"] = row["H"]; row["W"] = row["H"]; row["X"] = row["H"]
                                        if destinatario_reasignado_final: row["O"] = destinatario_reasignado_final
                                        if destinatario_reasignado_final and destinatario_reasignado_final not in st.session_state.lista_reasignados: st.session_state.lista_reasignados.append(destinatario_reasignado_final)
                                    elif tipo_proceso == "GENERADO DESDE DESPACHO":
                                        row["L"] = "GENERADO DESDE DESPACHO"; fecha_gen = get_val("fecha_salida", "Q"); row["C"]=fecha_gen; row["H"]=fecha_gen; row["Q"]=fecha_gen; row["W"]=fecha_gen; row["X"]=fecha_gen; row["D"] = ""; row["E"] = ""
                                        if not cod_out and cod_in: cod_out = cod_in
                                        row["G"] = cod_out; row["P"] = cod_out; row["V"] = cod_out; row["F"] = extraer_unidad_f7(cod_out)
                                    elif tipo_proceso == "CONOCIMIENTO":
                                        row["L"] = "CONOCIMIENTO"; row["M"] = ""; row["U"] = ""; row["O"] = ""; row["P"] = ""; row["V"] = ""; row["T"] = "NO"; row["Q"] = row["C"]; row["W"] = row["C"]; row["X"] = row["C"]

                                    if row["S"] == "PENDIENTE":
                                        for k in ["O", "P", "Q", "V", "W", "X"]: row[k] = ""

                                    if input_otra_unidad and input_otra_unidad not in st.session_state.lista_unidades:
                                        st.session_state.lista_unidades.append(input_otra_unidad)

                                    if is_editing: st.session_state.registros[idx_edit] = row; st.session_state.edit_index = None; st.success("✅ Actualizado")
                                    else: st.session_state.registros.append(row); st.session_state.docs_procesados_hoy += 1; st.success("✅ Agregado")

                                    for p in paths: os.remove(p)
                                    st.rerun()
                                except Exception as e: st.error(f"Error Técnico: {e}")
                        else: st.warning("⚠️ Sube documento.")

            if st.session_state.registros:
                st.markdown("#### 📋 Cola de Trabajo")
                if len(st.session_state.registros) > 0:
                    indices = [f"#{i+1} | {r.get('G','')} | {r.get('L','')}" for i, r in enumerate(st.session_state.registros)]
                    sel_idx = st.selectbox("Seleccionar Registro:", range(len(st.session_state.registros)), format_func=lambda x: indices[x], index=len(st.session_state.registros)-1, label_visibility="collapsed")
                    st.dataframe(pd.DataFrame([st.session_state.registros[sel_idx]]), hide_index=True, use_container_width=True)

                for i, reg in enumerate(st.session_state.registros):
                    bg = "#e8f5e9" if reg["S"] == "FINALIZADO" else "#ffebee"
                    with st.container():
                        st.markdown(f"""<div style="background-color: {bg}; padding: 10px; border-left: 5px solid {'green' if reg['S']=='FINALIZADO' else 'red'}; margin-bottom: 5px; border-radius: 5px;"><b>#{i+1}</b> | <b>{reg.get('G','')}</b> <br>Tipo: <b>{reg.get('L') if reg.get('L') else 'NORMAL'}</b> | Destino: {reg.get('M','')}</div>""", unsafe_allow_html=True)
                        c_edit, c_del = st.columns([1, 1])
                        if c_edit.button("✏️ EDITAR", key=f"e_{i}"): st.session_state.edit_index = i; st.rerun()
                        if c_del.button("🗑️ BORRAR", key=f"d_{i}"): st.session_state.registros.pop(i); st.session_state.docs_procesados_hoy = max(0, st.session_state.docs_procesados_hoy - 1); st.session_state.edit_index = None; st.rerun()

                if os.path.exists("matriz_maestra.xlsx"):
                    try:
                        wb = load_workbook("matriz_maestra.xlsx")
                        ws = wb[next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])]
                        start_row = 7
                        while ws.cell(row=start_row, column=1).value is not None: start_row += 1
                        gf = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
                        rf = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                        for i, reg in enumerate(st.session_state.registros):
                            r = start_row + i
                            def w(c, v): ws.cell(row=r, column=c).value = v
                            w(1, i+1); w(2, ""); w(3, reg["C"]); w(4, reg["D"]); w(5, reg["E"]); w(6, reg["F"]); w(7, reg["G"]); w(8, reg["H"]); w(9, reg["I"]); w(10, reg["J"]); w(11, reg["K"]); w(12, reg["L"]); w(13, reg["M"]); w(14, reg["N"]); w(15, reg["O"]); w(16, reg["P"]); w(17, reg["Q"]); w(18, "")
                            cell_s = ws.cell(row=r, column=19); cell_s.value = reg["S"]
                            if reg["S"]=="FINALIZADO": preservar_bordes(cell_s, gf)
                            elif reg["S"]=="PENDIENTE": preservar_bordes(cell_s, rf)
                            w(20, reg["T"]); w(21, reg["U"]); w(22, reg["V"]); w(23, reg["W"]); w(24, reg["X"]); w(25, ""); w(26, "")
                            for col_idx in range(1, 27):
                                cell = ws.cell(row=r, column=col_idx)
                                if col_idx != 19: preservar_bordes(cell, PatternFill(fill_type=None))
                        out_buffer = io.BytesIO(); wb.save(out_buffer); out_buffer.seek(0)
                        f_str = fecha_turno.strftime("%d-%m-%y"); u_str = st.session_state.usuario_turno.upper()
                        st.download_button(label="📥 DESCARGAR MATRIZ FINAL", data=out_buffer, file_name=f"TURNO {f_str} {u_str}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
                    except Exception as e: st.error(f"Error Excel: {e}")

        # --- TAB 2: ASESOR (CONTRATOS) ---
        with tab2:
            st.markdown("#### 🧠 Consultor de Despacho (IA)")
            usuario_actual = st.session_state.user_id
            ya_acepto = usuario_actual in db_contratos
            
            if not ya_acepto:
                st.warning("⚠️ **ACCIÓN REQUERIDA:** Debe aceptar los Términos y Condiciones.")
                with st.expander("📜 TÉRMINOS Y CONDICIONES (DECÁLOGO)", expanded=True):
                    politicas = [
                        "Naturaleza de Apoyo: El Asesor Estratégico es una herramienta de Inteligencia Artificial generativa diseñada exclusivamente como apoyo técnico y de consulta. No sustituye el criterio, mando ni decisión del servidor policial.",
                        "Carácter Referencial: Todo contenido, análisis, extracto o redacción generado por este sistema es estrictamente referencial y tentativo. No constituye un documento oficial ni una orden vinculante hasta que sea revisado y firmado por la autoridad competente.",
                        "Responsabilidad Humana: El Oficial de Turno o usuario asume la responsabilidad total y exclusiva de verificar, corregir y validar la información antes de plasmarla en sistemas oficiales (Quipux, Partes Web, etc.).",
                        "Verificación Normativa: Es obligación del usuario contrastar las sugerencias de la IA con la normativa legal vigente (COIP, COESCOP, Reglamentos) para evitar errores jurídicos o de procedimiento.",
                        "Prohibición de Datos Sensibles: Queda estrictamente prohibido ingresar nombres de fuentes humanas, datos de víctimas protegidas o información clasificada como \"SECRETA\" que ponga en riesgo operaciones en curso.",
                        "No Vinculante: Las recomendaciones tácticas (diagnósticos) emitidas por el sistema no tienen validez legal ni administrativa por sí mismas y no eximen de responsabilidad al usuario por acciones tomadas basándose en ellas.",
                        "Posibilidad de Error: El usuario reconoce que la IA puede incurrir en \"alucinaciones\" (datos inexactos) y se compromete a realizar el control de calidad de cada párrafo generado.",
                        "Trazabilidad de Uso: El sistema registra la identidad, fecha y hora del acceso para fines de auditoría y control de gestión de la DINIC.",
                        "Uso Ético: La herramienta debe utilizarse estrictamente para fines institucionales. Cualquier uso para fines personales o ajenos al servicio será sancionado disciplinariamente.",
                        "Aceptación de Riesgo: Al ingresar, el usuario declara entender estas limitaciones y libera a la administración del sistema de cualquier responsabilidad por el mal uso de la información generada."
                    ]
                    checks = []
                    for p in politicas:
                        checks.append(st.checkbox(p))
                    
                    if all(checks):
                        st.success("✅ Términos aceptados. Capture su foto para finalizar.")
                        foto = st.camera_input("Firma Biométrica (Foto)")
                        if foto:
                            b64_foto = base64.b64encode(foto.getvalue()).decode()
                            db_contratos[usuario_actual] = {
                                "fecha": get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S"),
                                "foto": b64_foto,
                                "usuario": st.session_state.usuario_turno
                            }
                            guardar_json(CONTRATOS_FILE, db_contratos)
                            st.balloons()
                            st.success("¡Contrato Firmado!")
                            time.sleep(2)
                            st.rerun()
            else:
                st.markdown("""<div class="legal-warning">⚠️ AVISO LEGAL:<br>Este módulo utiliza Inteligencia Artificial...</div>""", unsafe_allow_html=True)
                if usuario_actual in db_contratos:
                    datos = db_contratos[usuario_actual]
                    u_info = db_usuarios.get(usuario_actual, {"grado":"", "nombre": st.session_state.usuario_turno})
                    html_contrato = generar_html_contrato(u_info, datos["foto"])
                    st.download_button("📜 Descargar Mi Contrato", html_contrato, file_name="Contrato_Uso.html", mime="text/html")

                st.markdown("---")
                up_asesor = st.file_uploader("Sube documento (PDF)", type=['pdf'], key="asesor_up")
                if up_asesor and st.button("ANALIZAR ESTRATEGIA"):
                    with st.spinner("Analizando..."):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                t.write(up_asesor.getvalue()); p_as = t.name
                            f_as = genai.upload_file(p_as, display_name="Consulta")
                            prompt_asesor = """
                            Actúa como JEFE DE AYUDANTÍA DINIC.
                            Tu salida debe tener ESTRICTAMENTE esta estructura:
                            1. 🧐 DIAGNÓSTICO TÉCNICO:
                            - ¿Qué unidad pide?
                            - ¿Cuál es el requerimiento central?
                            2. ⚖️ CRITERIO / DECISIÓN:
                            - ¿Se debe archivar, tramitar internamente o elevar? ¿Por qué?
                            3. ✍️ EXTRACTO TENTATIVO (SOLO TEXTO):
                            - Redacta EXCLUSIVAMENTE el párrafo del cuerpo de respuesta.
                            - SIN encabezados, saludos ni firmas.
                            """
                            res = invocar_ia_segura([prompt_asesor, f_as])
                            st.markdown(res.text)
                            st.session_state.consultas_ia += 1
                            os.remove(p_as)
                        except Exception as e: st.error(f"Error: {e}")

        # --- TAB 3: ADMIN ---
        with tab3:
            st.markdown("### 🛡️ PANEL DE ADMINISTRADOR")
            if st.session_state.user_role == "admin":
                verif_pass = st.text_input("Confirme Contraseña Maestra:", type="password")
                if verif_pass == ADMIN_PASS_MASTER:
                    st.success("ACCESO VERIFICADO")
                    t3_1, t3_2 = st.tabs(["👥 Usuarios", "📜 Contratos Firmados"])
                    with t3_1:
                        st.markdown("#### Gestión de Usuarios")
                        st.dataframe(pd.DataFrame.from_dict(db_usuarios, orient='index'), use_container_width=True)
                        c_add, c_del = st.columns(2)
                        with c_add:
                            st.caption("Agregar Usuario")
                            new_ced = st.text_input("Cédula:")
                            new_grado = st.text_input("Grado:")
                            new_nom = st.text_input("Nombres:")
                            if st.button("Guardar Usuario"):
                                if new_ced and new_grado and new_nom:
                                    db_usuarios[new_ced] = {"grado": new_grado, "nombre": new_nom, "activo": True}
                                    guardar_json(DB_FILE, db_usuarios)
                                    st.success("Usuario agregado.")
                                    st.rerun()
                        with c_del:
                            st.caption("Eliminar Usuario")
                            del_ced = st.selectbox("Seleccione Cédula:", options=list(db_usuarios.keys()))
                            if st.button("Eliminar Usuario"):
                                if del_ced in db_usuarios:
                                    del db_usuarios[del_ced]
                                    guardar_json(DB_FILE, db_usuarios)
                                    st.success("Eliminado.")
                                    st.rerun()
                    with t3_2:
                        st.markdown("#### Repositorio de Contratos")
                        if db_contratos:
                            for ced, data in db_contratos.items():
                                with st.expander(f"{data['usuario']} ({ced}) - {data['fecha']}"):
                                    u_info = db_usuarios.get(ced, {"grado":"", "nombre": data['usuario']})
                                    html_c = generar_html_contrato(u_info, data["foto"])
                                    st.download_button(f"Descargar Contrato {ced}", html_c, file_name=f"Contrato_{ced}.html", mime="text/html")
                        else: st.info("No hay contratos firmados aún.")
                else: st.info("Ingrese contraseña maestra.")
            else: st.error("ACCESO DENEGADO.")

# FOOTER
st.markdown("---")
st.caption(f"{VER_SISTEMA} | Powered by: John Stalin Carrillo Narvaez | cnjstalin@gmail.com | 0996652042 |")
