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
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
VER_SISTEMA = "v27.1"
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# FUNCIÓN PARA IMAGEN EN LOGIN (BASE64)
def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Intentar cargar el escudo para el login
img_path = "Captura.JPG"
img_base64 = ""
if os.path.exists(img_path):
    img_base64 = f"data:image/jpeg;base64,{get_img_as_base64(img_path)}"
else:
    # Fallback si no está la imagen
    img_base64 = "https://cdn-icons-png.flaticon.com/512/9370/9370308.png"

st.markdown(f"""
    <style>
    .main-header {{
        background-color: #0E2F44;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #D4AF37;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .main-header h1 {{ margin: 0; font-size: 2.5rem; font-weight: 800; }}
    .main-header h3 {{ margin: 5px 0 0 0; font-size: 1.2rem; font-style: italic; color: #e0e0e0; }}
    .metric-card {{
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .login-container {{
        max-width: 400px;
        margin: auto;
        padding: 40px;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #0E2F44;
    }}
    .login-logo {{
        width: 120px;
        margin-bottom: 20px;
    }}
    div.stButton > button {{ width: 100%; font-weight: bold; border-radius: 5px; }}
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE ESTADO ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "" 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 

if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'edit_index' not in st.session_state: st.session_state.edit_index = None 
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'consultas_ia' not in st.session_state: st.session_state.consultas_ia = 0
if 'modelo_nombre' not in st.session_state: st.session_state.modelo_nombre = None

if 'lista_unidades' not in st.session_state: 
    st.session_state.lista_unidades = [
        "DINIC", "SOPORTE OPERATIVO", "APOYO OPERATIVO", "PLANIFICACION", 
        "JURIDICO", "COMUNICACION", "ANALISIS DE INFORMACION", "COORDINACION OPERACIONAL", 
        "FINANCIERO", "UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "DAOP", "DCOP", "DSOP"
    ]
if 'lista_reasignados' not in st.session_state: st.session_state.lista_reasignados = []

# --- 2.1 BASE DE DATOS DE USUARIOS (QUEMADA/HARDCODED) ---
DB_FILE = "usuarios_db.json"
CONFIG_FILE = "config_sistema.json"

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {"pass_universal": "DINIC2026"}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def guardar_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f)

def inicializar_db_usuarios():
    # 1. Intentar cargar archivo local si existe (persistencia)
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    
    # 2. SI NO EXISTE ARCHIVO, USAR LISTA FIJA (DEL CSV ORIGINAL)
    # Esto garantiza que funcione en cualquier navegador nuevo
    users = {
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
    
    # Guardar esta lista base en el archivo JSON
    with open(DB_FILE, 'w') as f:
        json.dump(users, f)
    return users

def guardar_db_usuarios(users):
    with open(DB_FILE, 'w') as f:
        json.dump(users, f)

config_sistema = cargar_config()
db_usuarios = inicializar_db_usuarios()

# --- 3. CONEXIÓN INTELIGENTE ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: st.warning("⚠️ Sin API Key (Offline).")
    else:
        genai.configure(api_key=api_key)
        if not st.session_state.modelo_nombre: st.session_state.modelo_nombre = "gemini-1.5-flash"
        model = genai.GenerativeModel(st.session_state.modelo_nombre)
    sistema_activo = True
except: sistema_activo = True

# --- 4. FUNCIONES AUXILIARES ---
def frases_curiosas():
    frases = [
        "¿Sabías que? El primer virus informático se creó en 1971 y se llamaba Creeper.",
        "¿Sabías que? La seguridad de la información es responsabilidad de todos.",
        "¿Sabías que? Tu contraseña es la llave de tu identidad digital.",
        "¿Sabías que? La IA procesa datos, pero tú tomas las decisiones.",
        "¿Sabías que? Un escritorio limpio mejora la productividad.",
        "¿Sabías que? El phishing es la técnica más común de robo de datos."
    ]
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
    if 'model' not in globals(): raise Exception("IA no configurada")
    max_retries = 3
    for i in range(max_retries):
        try: return model.generate_content(content)
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

# ==============================================================================
#  LÓGICA DE LOGIN
# ==============================================================================

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Aquí inyectamos la imagen Base64 del escudo
        st.markdown(f"""
        <div class="login-container">
            <img src="{img_base64}" class="login-logo">
            <h2 style='color:#0E2F44;'>ACCESO SIGD DINIC</h2>
            <p>Sistema Oficial de Gestión Documental</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario_input = st.text_input("Usuario (Cédula):", placeholder="Ingrese su número de cédula")
            pass_input = st.text_input("Contraseña:", type="password", placeholder="••••••••")
            
            submit_login = st.form_submit_button("INGRESAR AL SISTEMA", type="primary")
            
            if submit_login:
                # 1. CASO ADMINISTRADOR
                if usuario_input == ADMIN_USER and pass_input == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.session_state.usuario_turno = "ADMINISTRADOR DEL SISTEMA"
                    st.success("✅ Acceso Concedido: ADMINISTRADOR")
                    st.rerun()
                
                # 2. CASO USUARIO NORMAL
                elif usuario_input in db_usuarios:
                    user_data = db_usuarios[usuario_input]
                    if pass_input == config_sistema["pass_universal"]:
                        if user_data["activo"]:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "user"
                            st.session_state.usuario_turno = f"{user_data['grado']} {user_data['nombre']}"
                            st.success(f"✅ Bienvenido: {st.session_state.usuario_turno}")
                            st.rerun()
                        else:
                            st.error("🚫 Usuario inactivo. Contacte al Administrador.")
                    else:
                        st.error("🚫 Contraseña incorrecta.")
                
                else:
                    st.error("🚫 Usuario no encontrado en la base de datos.")

else:
    # ==============================================================================
    #  SISTEMA PRINCIPAL (LOGUEADO)
    # ==============================================================================
    with st.sidebar:
        # Mostrar el mismo escudo en el sidebar
        if os.path.exists("Captura.JPG"):
            st.image("Captura.JPG", use_container_width=True)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=100)
        
        st.markdown("### 👮‍♂️ CONTROL DE MANDO")
        
        # 1. PERSONA DE TURNO
        st.info(f"👤 **{st.session_state.usuario_turno}**")
        st.caption(f"Rol: {st.session_state.user_role.upper()}")
        fecha_turno = st.date_input("Fecha Operación:", value=datetime.now())

        st.markdown("---")
        
        # 2. ACCIONES
        if st.button("🗑️ NUEVO TURNO (Limpiar)", type="primary"):
            st.session_state.registros = []
            st.session_state.docs_procesados_hoy = 0
            st.session_state.edit_index = None
            st.rerun()

        st.markdown("---")
        
        # 3. RESPALDO
        if st.session_state.registros:
            json_str = json.dumps(st.session_state.registros, default=str)
            st.download_button("⬇️ DESCARGAR RESPALDO SIGD", json_str, file_name="backup_sigd.json", mime="application/json")
        
        uploaded_backup = st.file_uploader("⬆️ RESTAURAR RESPALDO SIGD", type=['json'])
        if uploaded_backup:
            try:
                data = json.load(uploaded_backup)
                st.session_state.registros = data
                st.session_state.docs_procesados_hoy = len(data)
                st.success("¡Backup Restaurado!")
                time.sleep(1)
                st.rerun()
            except: st.error("Archivo corrupto.")

        st.markdown("---")
        
        # 4. BASE DE DATOS
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
            st.session_state.user_role = ""
            st.session_state.usuario_turno = ""
            st.rerun()

    # --- ÁREA PRINCIPAL ---
    st.markdown(f'''
    <div class="main-header">
        <h1>SIGD DINIC</h1>
        <h3>Sistema de Gestión Documental</h3>
    </div>
    ''', unsafe_allow_html=True)

    # DASHBOARD
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
                            msg_carga = f"⏳ AGREGANDO A LA LISTA UN MOMENTO POR FAVOR...\n\n👀 {frase}"
                            with st.spinner(msg_carga):
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
                                    
                                    JSON:
                                    {
                                        "fecha_recepcion": "DD/MM/AAAA",
                                        "remitente_grado_nombre": "Texto",
                                        "remitente_cargo": "Texto",
                                        "codigo_completo_entrada": "Texto",
                                        "asunto_entrada": "Texto",
                                        "resumen_breve": "Texto",
                                        "destinatarios_todos": "Texto con comas", 
                                        "codigo_completo_salida": "Texto",
                                        "fecha_salida": "DD/MM/AAAA"
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
                                        "C": get_val("fecha_recepcion", "C"),
                                        "D": get_val("remitente_grado_nombre", "D"),
                                        "E": get_val("remitente_cargo", "E"),
                                        "F": unidad_f7,
                                        "G": cod_in,
                                        "H": get_val("fecha_recepcion", "H"),
                                        "I": get_val("asunto_entrada", "I"),
                                        "J": get_val("resumen_breve", "J"),
                                        "K": st.session_state.usuario_turno,
                                        "L": "",
                                        "M": str_unidades_final,
                                        "N": tipo_doc_salida,
                                        "O": dest_ia, 
                                        "P": cod_out,
                                        "Q": get_val("fecha_salida", "Q"),
                                        "R": "",
                                        "S": estado_s7,
                                        "T": es_interno,
                                        "U": str_unidades_final,
                                        "V": cod_out,
                                        "W": get_val("fecha_salida", "W"),
                                        "X": get_val("fecha_salida", "X"),
                                        "Y": "", "Z": ""
                                    }

                                    if tipo_proceso == "TRAMITE NORMAL": row["L"] = ""
                                    elif tipo_proceso == "REASIGNADO":
                                        row["L"] = "REASIGNADO"
                                        row["P"] = row["G"]; row["V"] = row["P"]
                                        row["Q"] = row["H"]; row["W"] = row["H"]; row["X"] = row["H"]
                                        if destinatario_reasignado_final: row["O"] = destinatario_reasignado_final
                                        if destinatario_reasignado_final and destinatario_reasignado_final not in st.session_state.lista_reasignados:
                                            st.session_state.lista_reasignados.append(destinatario_reasignado_final)

                                    elif tipo_proceso == "GENERADO DESDE DESPACHO":
                                        row["L"] = "GENERADO DESDE DESPACHO"
                                        fecha_gen = get_val("fecha_salida", "Q")
                                        row["C"]=fecha_gen; row["H"]=fecha_gen; row["Q"]=fecha_gen; row["W"]=fecha_gen; row["X"]=fecha_gen
                                        row["D"] = ""; row["E"] = ""
                                        if not cod_out and cod_in: cod_out = cod_in
                                        row["G"] = cod_out; row["P"] = cod_out; row["V"] = cod_out
                                        row["F"] = extraer_unidad_f7(cod_out)

                                    elif tipo_proceso == "CONOCIMIENTO":
                                        row["L"] = "CONOCIMIENTO"
                                        row["M"] = ""; row["U"] = ""; row["O"] = ""
                                        row["P"] = ""; row["V"] = ""; row["T"] = "NO"
                                        row["Q"] = row["C"]; row["W"] = row["C"]; row["X"] = row["C"]

                                    if row["S"] == "PENDIENTE":
                                        for k in ["O", "P", "Q", "V", "W", "X"]: row[k] = ""

                                    if input_otra_unidad and input_otra_unidad not in st.session_state.lista_unidades:
                                        st.session_state.lista_unidades.append(input_otra_unidad)

                                    if is_editing:
                                        st.session_state.registros[idx_edit] = row
                                        st.session_state.edit_index = None
                                        st.success("✅ Actualizado")
                                    else:
                                        st.session_state.registros.append(row)
                                        st.session_state.docs_procesados_hoy += 1
                                        st.success("✅ Agregado")

                                    for p in paths: os.remove(p)
                                    st.rerun()

                                except Exception as e: st.error(f"Error Técnico: {e}")
                        else: st.warning("⚠️ Sube documento.")

            if st.session_state.registros:
                st.markdown("---")
                st.markdown("#### 📋 Cola de Trabajo")
                if len(st.session_state.registros) > 0:
                    st.caption("👁️ Previsualización:")
                    indices = [f"#{i+1} | {r.get('G','')} | {r.get('L','')}" for i, r in enumerate(st.session_state.registros)]
                    sel_idx = st.selectbox("Seleccionar Registro:", range(len(st.session_state.registros)), format_func=lambda x: indices[x], index=len(st.session_state.registros)-1, label_visibility="collapsed")
                    reg_prev = st.session_state.registros[sel_idx]
                    df_prev = pd.DataFrame([reg_prev])
                    cols_order = ["C","F","G","L","M","O","P","S","T"]
                    df_show = df_prev[[c for c in cols_order if c in df_prev.columns]]
                    st.dataframe(df_show, hide_index=True, use_container_width=True)

                for i, reg in enumerate(st.session_state.registros):
                    bg = "#e8f5e9" if reg["S"] == "FINALIZADO" else "#ffebee"
                    bc = "green" if reg["S"] == "FINALIZADO" else "red"
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: {bg}; padding: 10px; border-left: 5px solid {bc}; margin-bottom: 5px; border-radius: 5px;">
                            <b>#{i+1}</b> | <b>{reg.get('G','')}</b> <br>
                            Tipo: <b>{reg.get('L') if reg.get('L') else 'NORMAL'}</b> | Destino: {reg.get('M','')}
                        </div>""", unsafe_allow_html=True)
                        c_edit, c_del = st.columns([1, 1])
                        if c_edit.button("✏️ EDITAR", key=f"e_{i}"): st.session_state.edit_index = i; st.rerun()
                        if c_del.button("🗑️ BORRAR", key=f"d_{i}"):
                            st.session_state.registros.pop(i)
                            st.session_state.docs_procesados_hoy = max(0, st.session_state.docs_procesados_hoy - 1)
                            if st.session_state.edit_index == i: st.session_state.edit_index = None
                            st.rerun()

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
                            w(1, i+1); w(2, "")
                            w(3, reg["C"]); w(4, reg["D"]); w(5, reg["E"])
                            w(6, reg["F"]); w(7, reg["G"]); w(8, reg["H"]); w(9, reg["I"])
                            w(10, reg["J"]); w(11, reg["K"]); w(12, reg["L"]); w(13, reg["M"])
                            w(14, reg["N"]); w(15, reg["O"]); w(16, reg["P"]); w(17, reg["Q"])
                            w(18, "")
                            cell_s = ws.cell(row=r, column=19); cell_s.value = reg["S"]
                            if reg["S"]=="FINALIZADO": preservar_bordes(cell_s, gf)
                            elif reg["S"]=="PENDIENTE": preservar_bordes(cell_s, rf)
                            w(20, reg["T"]); w(21, reg["U"]); w(22, reg["V"]); w(23, reg["W"]); w(24, reg["X"])
                            w(25, ""); w(26, "")
                            for col_idx in range(1, 27):
                                cell = ws.cell(row=r, column=col_idx)
                                if col_idx != 19: preservar_bordes(cell, PatternFill(fill_type=None))

                        out_buffer = io.BytesIO()
                        wb.save(out_buffer)
                        out_buffer.seek(0)
                        f_str = fecha_turno.strftime("%d-%m-%y")
                        u_str = st.session_state.usuario_turno.upper()
                        st.download_button(
                            label="📥 DESCARGAR MATRIZ FINAL",
                            data=out_buffer,
                            file_name=f"TURNO {f_str} {u_str}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary"
                        )
                    except Exception as e: st.error(f"Error generando Excel: {e}")

        # --- TAB 2: ASESOR ---
        with tab2:
            st.markdown("#### 🧠 Consultor de Despacho (IA)")
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
                    
                    st.markdown("---")
                    st.markdown("#### 1. Gestión de Usuarios")
                    
                    df_users = pd.DataFrame.from_dict(db_usuarios, orient='index')
                    st.dataframe(df_users, use_container_width=True)
                    
                    c_add, c_del = st.columns(2)
                    with c_add:
                        st.caption("Agregar Usuario")
                        new_ced = st.text_input("Cédula:")
                        new_grado = st.text_input("Grado:")
                        new_nom = st.text_input("Nombres:")
                        if st.button("Guardar Usuario"):
                            if new_ced and new_grado and new_nom:
                                db_usuarios[new_ced] = {"grado": new_grado, "nombre": new_nom, "activo": True}
                                guardar_db_usuarios(db_usuarios)
                                st.success("Usuario agregado.")
                                st.rerun()
                            else:
                                st.warning("Complete los datos.")
                    
                    with c_del:
                        st.caption("Eliminar/Desactivar Usuario")
                        del_ced = st.selectbox("Seleccione Cédula:", options=list(db_usuarios.keys()))
                        if st.button("Eliminar Usuario"):
                            if del_ced in db_usuarios:
                                del db_usuarios[del_ced]
                                guardar_db_usuarios(db_usuarios)
                                st.success("Usuario eliminado.")
                                st.rerun()
                                
                    st.markdown("---")
                    st.markdown("#### 2. Configuración")
                    new_pass_univ = st.text_input("Cambiar Contraseña Universal (Usuarios):", value=config_sistema["pass_universal"])
                    if st.button("Actualizar Contraseña Universal"):
                        config_sistema["pass_universal"] = new_pass_univ
                        guardar_config(config_sistema)
                        st.success("Contraseña Universal Actualizada.")
                        
                else:
                    st.info("Ingrese contraseña maestra para ver opciones sensibles.")
            else:
                st.error("ACCESO DENEGADO. Módulo solo para Administrador.")

# FOOTER
st.markdown("---")
st.caption(f"{VER_SISTEMA} | Powered by: John Stalin Carrillo Narvaez | cnjstalin@gmail.com | 0996652042 |")
