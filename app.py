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

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
VER_SISTEMA = "v57.0 (Matriz Estricta + MultiModel)"
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

st.set_page_config(page_title="SIGD DINIC", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# --- 2. FUNCIONES CRÍTICAS (Extractores y Lógica) ---
def get_hora_ecuador(): 
    return datetime.now(timezone(timedelta(hours=-5)))

def preservar_bordes(cell, fill_obj):
    if cell.border and (cell.border.left.style or cell.border.top.style): new_border = copy(cell.border)
    else:
        thin = Side(border_style="thin", color="000000")
        new_border = Border(top=thin, left=thin, right=thin, bottom=thin)
    cell.border = new_border; cell.fill = fill_obj
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)

def extract_json_safe(text):
    try: return json.loads(text)
    except:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try: 
                data = json.loads(match.group(1))
                if isinstance(data, list) and len(data) > 0: return data[0]
                elif isinstance(data, dict): return data
            except: return {}
        return {}

def limpiar_codigo_prioridad(texto):
    """Regla G7: PN-DIGIN-QX... sin 'Oficio Nro'"""
    if not texto: return ""
    # Busca patrón estricto PN-...
    match = re.search(r"(PN-[\w\-\.]+)", str(texto).upper())
    if match: return match.group(1).strip()
    return str(texto).strip()

def extraer_unidad_f7(texto_codigo):
    """Regla F7: Lo que está entre PN- y -QX"""
    if not texto_codigo: return "DINIC"
    # Busca texto entre PN- y -QX (ej: PN-(DIGIN)-QX -> DIGIN)
    match = re.search(r"PN-[\(]?([A-Z0-9]+)[\)]?-QX", str(texto_codigo).upper())
    if match: return match.group(1).strip()
    return "DINIC"

def determinar_sale_no_sale(destinos_str):
    unidades_externas = ["UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "COMANDO GENERAL", "OTRAS DIRECCIONES"]
    destinos_upper = destinos_str.upper()
    for u in unidades_externas:
        if u in destinos_upper: return "SI"
    return "NO"

# --- 3. GESTIÓN DE MODELOS DE IA (SOLUCIÓN ERROR 404) ---
def configurar_ia_robusta():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return None
    genai.configure(api_key=api_key)
    return True

def invocar_ia_segura(content):
    # Lista de modelos en orden de preferencia (Si falla uno, usa el otro)
    modelos_a_probar = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    
    last_error = ""
    for modelo in modelos_a_probar:
        try:
            model = genai.GenerativeModel(modelo)
            # Intento de generación
            return model.generate_content(content)
        except Exception as e:
            last_error = str(e)
            if "429" in last_error: # Si es saturación, espera un poco y reintenta con el mismo
                time.sleep(2)
                try: return model.generate_content(content)
                except: pass
            continue # Prueba el siguiente modelo
            
    raise Exception(f"No se pudo conectar con ningún modelo de Google. Último error: {last_error}")

# --- 4. LÓGICA DE MATRIZ (COMO EN EL WORD) ---
def generar_fila_matriz(tipo, ia_data, manual_data, usuario_turno, paths_files):
    # Extracción de datos base
    raw_code_in = ia_data.get("recibido_codigo", "")
    cod_in = limpiar_codigo_prioridad(raw_code_in) # Aplica Regla G7
    unidad_f7 = extraer_unidad_f7(raw_code_in)     # Aplica Regla F7
    
    fecha_in = ia_data.get("recibido_fecha", "")
    remitente_nom = ia_data.get("recibido_remitente_nombre", "")
    remitente_car = ia_data.get("recibido_remitente_cargo", "")
    asunto_in = ia_data.get("recibido_asunto", "")
    resumen_in = ia_data.get("recibido_resumen", "")
    
    # Datos de Salida/Respuesta
    dest_out = ia_data.get("respuesta_destinatarios", "") # Regla O7
    raw_code_out = ia_data.get("respuesta_codigo", "")
    cod_out = limpiar_codigo_prioridad(raw_code_out)
    fecha_out = ia_data.get("respuesta_fecha", "")

    # Lógica de Estado
    estado_s7 = "PENDIENTE"
    has_in = True if (paths_files.get("in") or manual_data.get("G")) else False
    has_out = True if (paths_files.get("out") or manual_data.get("P")) else False
    
    if tipo in ["CONOCIMIENTO", "REASIGNADO"]: estado_s7 = "FINALIZADO"
    elif has_in and has_out: estado_s7 = "FINALIZADO"

    str_unidades = manual_data.get("unidades_str", "")
    es_interno = determinar_sale_no_sale(str_unidades)
    if tipo == "CONOCIMIENTO": es_interno = "NO"

    # Estructura Base (Columnas A-Z según Word)
    row = {
        "C": fecha_in,      # C7: Fecha Recibido
        "D": remitente_nom, # D7: Remitente
        "E": remitente_car, # E7: Cargo
        "F": unidad_f7,     # F7: Unidad (PN-X-QX)
        "G": cod_in,        # G7: Codigo (Sin Oficio Nro)
        "H": fecha_in,      # H7: Fecha Recibido
        "I": asunto_in,     # I7: Asunto
        "J": resumen_in,    # J7: Resumen IA
        "K": usuario_turno, # K7: Usuario
        "L": "",            # L7: Variable (Tramite, etc)
        "M": str_unidades,  # M7: Dependencia Destino
        "N": manual_data.get("tipo_doc_salida", ""), # N7: Formato Salida
        "O": "", "P": "", "Q": "", "R": "", "S": estado_s7,
        "T": es_interno, "U": str_unidades, "V": "", "W": "", "X": "", "Y": "", "Z": ""
    }

    # Lógica Específica por Tipo
    if tipo == "TRAMITE NORMAL":
        row["L"] = "" # Según Word: "NO SE REFLEJARA NADA"
        row["O"] = dest_out # O7: Destinatarios del Doc Respuesta
        row["P"] = cod_out  # P7: Codigo Respuesta
        row["Q"] = fecha_out # Q7: Fecha Respuesta
        row["V"] = cod_out
        row["W"] = fecha_out
        row["X"] = fecha_out

    elif tipo == "REASIGNADO":
        row["L"] = "REASIGNADO"
        row["O"] = manual_data.get("reasignado_a", "") # O7: Manual
        row["P"] = "" 
        row["V"] = ""
        row["Q"] = fecha_in; row["W"] = fecha_in; row["X"] = fecha_in

    elif tipo == "GENERADO DESDE DESPACHO":
        row["L"] = "GENERADO DESDE DESPACHO"
        row["D"] = ""; row["E"] = "" # D7, E7 Vacios
        # En Generado, el doc cargado se trata como el output
        row["C"] = fecha_out; row["H"] = fecha_out; row["Q"] = fecha_out; row["W"] = fecha_out; row["X"] = fecha_out
        row["G"] = cod_out; row["P"] = cod_out; row["V"] = cod_out
        row["F"] = extraer_unidad_f7(cod_out)
        row["O"] = dest_out # Destinatarios del doc generado

    elif tipo == "CONOCIMIENTO":
        row["L"] = "CONOCIMIENTO"
        row["M"] = ""; row["O"] = ""; row["P"] = ""; row["U"] = ""; row["V"] = ""
        row["T"] = "NO" # T7: Por defecto NO
        row["Q"] = fecha_in; row["W"] = fecha_in; row["X"] = fecha_in

    if row["S"] == "PENDIENTE":
        for k in ["O", "P", "Q", "V", "W", "X"]: row[k] = ""

    return row

# --- 5. BASES DE DATOS ---
USUARIOS_BASE = {
    "0702870460": {"grado": "SGOS", "nombre": "VILLALTA OCHOA XAVIER BISMARK", "activo": True},
    "1715081731": {"grado": "SGOS", "nombre": "MINDA MINDA FRANCISCO GABRIEL", "activo": True},
    "1723623011": {"grado": "CBOS", "nombre": "CARRILLO NARVAEZ JOHN STALIN", "activo": True}
}
# (Se cargan el resto de archivos JSON igual que antes...)
DB_FILE = "usuarios_db.json"; CONFIG_FILE = "config_sistema.json"; CONTRATOS_FILE = "contratos_legal.json"; LOGS_FILE = "historial_acciones.json"; LISTAS_FILE = "listas_db.json"

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

db_usuarios = cargar_json(DB_FILE, USUARIOS_BASE)
# Fusionar con base si falta
for k,v in USUARIOS_BASE.items(): 
    if k not in db_usuarios: db_usuarios[k] = v

db_contratos = cargar_json(CONTRATOS_FILE, {})
db_logs = cargar_json(LOGS_FILE, [])
if not isinstance(db_logs, list): db_logs = []
db_listas = cargar_json(LISTAS_FILE, {"unidades": ["DINIC"], "reasignados": []})

config_sistema = cargar_json(CONFIG_FILE, {"pass_universal": "DINIC2026", "pass_th": "THDINIC123", "base_historica": 1258, "consultas_ia_global": 0})

def registrar_accion(usuario, accion, detalle=""):
    ahora = get_hora_ecuador().strftime("%Y-%m-%d %H:%M:%S")
    db_logs.insert(0, {"fecha": ahora, "usuario": usuario, "accion": accion, "detalle": detalle})
    guardar_json(LOGS_FILE, db_logs)

def guardar_nueva_entrada_lista(tipo, valor):
    if valor and valor not in db_listas[tipo]:
        db_listas[tipo].append(valor); guardar_json(LISTAS_FILE, db_listas)
        if tipo == "unidades": st.session_state.lista_unidades = db_listas["unidades"]
        if tipo == "reasignados": st.session_state.lista_reasignados = db_listas["reasignados"]

# --- 6. VARIABLES DE SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "" 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 
if 'user_id' not in st.session_state: st.session_state.user_id = ""
if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'edit_index' not in st.session_state: st.session_state.edit_index = None 
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'active_module' not in st.session_state: st.session_state.active_module = 'secretario'
if 'lista_unidades' not in st.session_state: st.session_state.lista_unidades = db_listas.get("unidades", [])
if 'lista_reasignados' not in st.session_state: st.session_state.lista_reasignados = db_listas.get("reasignados", [])

# Persistencia F5
token = st.query_params.get("token", None)
if token and not st.session_state.logged_in and token in db_usuarios:
    st.session_state.logged_in = True; st.session_state.user_id = token; st.session_state.user_role = "admin" if token == ADMIN_USER else "user"
    st.session_state.usuario_turno = f"{db_usuarios[token]['grado']} {db_usuarios[token]['nombre']}"

sistema_activo = configurar_ia_robusta()

# ==============================================================================
#  INTERFAZ GRÁFICA
# ==============================================================================

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h2 style='text-align:center; color:#0E2F44;'>ACCESO SIGD DINIC</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuario:"); p = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("ENTRAR"):
                if u == ADMIN_USER and p == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True; st.session_state.user_role = "admin"; st.session_state.user_id = u
                    st.session_state.usuario_turno = "Administrador"
                    st.query_params["token"] = u; st.rerun()
                elif u in db_usuarios and p == config_sistema["pass_universal"]:
                    st.session_state.logged_in = True; st.session_state.user_role = "user"; st.session_state.user_id = u
                    st.session_state.usuario_turno = f"{db_usuarios[u]['grado']} {db_usuarios[u]['nombre']}"
                    st.query_params["token"] = u; st.rerun()
                else: st.error("Acceso denegado")

else:
    with st.sidebar:
        st.info(f"👤 {st.session_state.usuario_turno}")
        if st.button("📝 SECRETARIO/A"): st.session_state.active_module = 'secretario'; st.rerun()
        if st.button("🧠 ASESOR IA"): st.session_state.active_module = 'asesor'; st.rerun()
        if st.button("🛡️ ADMIN"): st.session_state.active_module = 'admin'; st.rerun()
        if st.button("🔒 SALIR"): st.session_state.logged_in = False; st.query_params.clear(); st.rerun()

    if st.session_state.active_module == 'secretario':
        st.markdown("<h1 style='color:#0E2F44;'>Módulo Gestión Documental</h1>", unsafe_allow_html=True)
        
        # Panel de Métricas y Configuración Rápida
        with st.expander("⚙️ Opciones de Matriz y Respaldo"):
            c1, c2 = st.columns(2)
            if c1.button("Descargar Respaldo JSON"):
                st.download_button("Bajar JSON", json.dumps(st.session_state.registros), "respaldo.json")
            uploaded_matriz = c2.file_uploader("Cargar Matriz Maestra (.xlsx)", type=["xlsx"])
            if uploaded_matriz: 
                with open("matriz_maestra.xlsx", "wb") as f: f.write(uploaded_matriz.getbuffer())
                st.success("Matriz cargada")

        # Formulario de Ingreso
        st.markdown("---")
        c_form1, c_form2 = st.columns([1, 2])
        
        with c_form1:
            tipo_proc = st.selectbox("Tipo de Trámite:", ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"])
            tipo_salida = st.selectbox("Formato Salida:", ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL"])
            
            # Unidades
            unidades = st.multiselect("Destino (Unidad):", st.session_state.lista_unidades)
            nueva_unidad = st.text_input("Agregar Unidad:")
            if nueva_unidad: unidades.append(nueva_unidad.upper())
            str_unidades = ", ".join(unidades)
            
            reasignado_a = ""
            if tipo_proc == "REASIGNADO":
                reasignado_a = st.text_input("Reasignado A (Grado y Nombre):").upper()

        with c_form2:
            d_in = None; d_out = None
            if tipo_proc == "TRAMITE NORMAL":
                c_in, c_out = st.columns(2)
                d_in = c_in.file_uploader("1. Doc RECIBIDO (PDF)", type=["pdf"])
                d_out = c_out.file_uploader("2. Doc RESPUESTA (PDF)", type=["pdf"])
            elif tipo_proc in ["REASIGNADO", "CONOCIMIENTO"]:
                d_in = st.file_uploader("1. Doc RECIBIDO (PDF)", type=["pdf"])
            elif tipo_proc == "GENERADO DESDE DESPACHO":
                d_out = st.file_uploader("2. Doc GENERADO (PDF)", type=["pdf"])

        if st.button("PROCESAR DOCUMENTO", type="primary"):
            if not sistema_activo:
                st.error("⚠️ Error: Configura tu API Key en Secrets.")
            elif (tipo_proc == "TRAMITE NORMAL" and (not d_in and not d_out)):
                st.warning("Suba al menos un documento.")
            else:
                with st.spinner("🤖 Leyendo documento con IA Policial..."):
                    try:
                        paths = {"in":None, "out":None}; files_ia = []
                        
                        if d_in:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(d_in.getvalue()); paths["in"] = t.name
                            files_ia.append(genai.upload_file(paths["in"], display_name="DocRecibido"))
                        
                        if d_out:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t: t.write(d_out.getvalue()); paths["out"] = t.name
                            files_ia.append(genai.upload_file(paths["out"], display_name="DocRespuesta"))

                        # --- PROMPT INGENIERIZADO SEGÚN WORD ---
                        prompt = """
                        Actúa como experto en gestión documental de la Policía Nacional del Ecuador (DINIC).
                        Analiza los documentos adjuntos y extrae la información ESTRICTAMENTE según estas reglas:

                        1. CÓDIGO (G7/P7): Busca en la esquina superior derecha. Formato: 'Oficio Nro. PN-XXX...'. Extrae TODO el código tal cual.
                        2. UNIDAD (F7): Del código extraído, saca SOLO lo que está entre 'PN-' y '-QX'.
                        3. DESTINATARIOS (O7) - REGLA DE ORO:
                           - Busca la sección 'PARA:'.
                           - Extrae SOLO Grados y Nombres (Ej: 'Sgos. Juan Piguave').
                           - ¡IGNORA CARGOS! No pongas 'Jefe de...', 'Director...', etc.
                           - Si hay múltiples, sepáralos por comas.
                           - Si es Trámite Normal, extrae del Documento de Respuesta.
                           - Si es Generado, extrae del Documento Generado.
                        4. REMITENTE (D7): Busca 'DE:' o la firma al final. Grado y Nombre.

                        Devuelve SOLO este JSON:
                        {
                            "recibido_fecha": "DD/MM/AAAA",
                            "recibido_remitente_nombre": "Texto",
                            "recibido_remitente_cargo": "Texto",
                            "recibido_codigo": "Texto",
                            "recibido_asunto": "Texto",
                            "recibido_resumen": "Resumen corto",
                            "respuesta_destinatarios": "Texto (Nombres sin cargos)",
                            "respuesta_codigo": "Texto",
                            "respuesta_fecha": "DD/MM/AAAA"
                        }
                        """
                        
                        res = invocar_ia_segura([prompt, *files_ia])
                        data_ia = extract_json_safe(res.text.replace("```json", "").replace("```", ""))
                        
                        # Generar Fila
                        manual_data = {"unidades_str": str_unidades, "tipo_doc_salida": tipo_salida, "reasignado_a": reasignado_a, "G": True if d_in else False, "P": True if d_out else False}
                        row = generar_fila_matriz(tipo_proc, data_ia, manual_data, st.session_state.usuario_turno, paths)
                        
                        st.session_state.registros.append(row)
                        if nueva_unidad: guardar_nueva_entrada_lista("unidades", nueva_unidad)
                        if reasignado_a: guardar_nueva_entrada_lista("reasignados", reasignado_a)
                        
                        st.success("✅ Documento Procesado Correctamente")
                        
                    except Exception as e: st.error(f"Error Técnico: {e}")

        # Visualización de Registros
        if st.session_state.registros:
            st.markdown("### Registros del Turno")
            df = pd.DataFrame(st.session_state.registros)
            st.dataframe(df)
            
            # Descargar Excel
            if st.button("📥 Descargar Matriz Final"):
                if os.path.exists("matriz_maestra.xlsx"):
                    wb = load_workbook("matriz_maestra.xlsx")
                    ws = wb.active
                    start_row = ws.max_row + 1
                    for r in st.session_state.registros:
                        # Mapeo exacto A=1, B=2, ...
                        ws.cell(row=start_row, column=3, value=r["C"]) # C7
                        ws.cell(row=start_row, column=4, value=r["D"]) # D7
                        ws.cell(row=start_row, column=5, value=r["E"]) # E7
                        ws.cell(row=start_row, column=6, value=r["F"]) # F7
                        ws.cell(row=start_row, column=7, value=r["G"]) # G7
                        ws.cell(row=start_row, column=8, value=r["H"])
                        ws.cell(row=start_row, column=9, value=r["I"])
                        ws.cell(row=start_row, column=10, value=r["J"])
                        ws.cell(row=start_row, column=11, value=r["K"])
                        ws.cell(row=start_row, column=12, value=r["L"])
                        ws.cell(row=start_row, column=13, value=r["M"])
                        ws.cell(row=start_row, column=14, value=r["N"])
                        ws.cell(row=start_row, column=15, value=r["O"]) # O7
                        ws.cell(row=start_row, column=16, value=r["P"])
                        ws.cell(row=start_row, column=17, value=r["Q"])
                        ws.cell(row=start_row, column=19, value=r["S"])
                        ws.cell(row=start_row, column=20, value=r["T"])
                        ws.cell(row=start_row, column=21, value=r["U"])
                        ws.cell(row=start_row, column=22, value=r["V"])
                        start_row += 1
                    
                    out = io.BytesIO()
                    wb.save(out)
                    st.download_button("Descargar Excel", out.getvalue(), "Matriz_Llenada.xlsx")
                else:
                    st.error("Primero carga la Matriz Maestra en la configuración.")

    elif st.session_state.active_module == 'admin':
        st.write("Panel de Administrador (Mantenimiento de Usuarios)")
