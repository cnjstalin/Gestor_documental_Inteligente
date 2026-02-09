import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import re
import time
import io
# import base64  <-- Eliminar importación de base64 ya que no se usará la cámara
import random
import pandas as pd
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
NOMBRE_SISTEMA = "Sistema de Gestión Documental" # <-- Nombre cambiado
VER_SISTEMA = "v26.5"

st.set_page_config(
    page_title=NOMBRE_SISTEMA,
    layout="wide",
    page_icon="📂", # <-- Icono cambiado a algo más acorde
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
    /* Ajuste para multiselect */
    .stMultiSelect span {
        background-color: #D4AF37 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE ESTADO ---
if 'registros' not in st.session_state: st.session_state.registros = []
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = ""
if 'edit_index' not in st.session_state: st.session_state.edit_index = None
if 'docs_procesados_hoy' not in st.session_state: st.session_state.docs_procesados_hoy = 0
if 'consultas_ia' not in st.session_state: st.session_state.consultas_ia = 0
if 'modelo_nombre' not in st.session_state: st.session_state.modelo_nombre = None

# Memoria Inteligente
if 'lista_unidades' not in st.session_state:
    st.session_state.lista_unidades = ["DINIC", "UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "DAOP", "DCOP", "DSOP", "PLANF", "FINA", "JURID"]
if 'lista_reasignados' not in st.session_state:
    st.session_state.lista_reasignados = []

# --- 3. CONEXIÓN INTELIGENTE ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🚨 ERROR: No se encontró la API KEY en Secrets.")
        st.stop()
    genai.configure(api_key=api_key)

    if not st.session_state.modelo_nombre:
        try:
            listado = genai.list_models()
            found = False
            for m in listado:
                if 'flash' in m.name and 'generateContent' in m.supported_generation_methods:
                    st.session_state.modelo_nombre = m.name
                    found = True
                    break
            if not found: st.session_state.modelo_nombre = "gemini-1.5-flash"
        except: st.session_state.modelo_nombre = "gemini-1.5-flash"
    model = genai.GenerativeModel(st.session_state.modelo_nombre)
    sistema_activo = True
except Exception as e:
    st.error(f"⚠️ Error de Conexión: {e}")
    sistema_activo = False

# --- 4. FUNCIONES ---

def frases_carga():
    frases = [
        "☕ Preparando el café virtual...",
        "🚀 Calibrando satélites de la DINIC...",
        "🕵️‍♂️ Descifrando jeroglíficos...",
        "🤖 La IA está leyendo (esperemos que no se aburra)...",
        "📂 Archivando en la nube...",
        "👮‍♂️ Solicitando permiso al General...",
        "🐢 Más rápido que un trámite físico..."
    ]
    return random.choice(frases)

def limpiar_codigo(texto):
    if not texto: return ""
    # Priorizar formato PN-XXXX-QX
    match = re.search(r"(PN-[A-Z0-9]+-QX-?\d*)", str(texto), re.IGNORECASE)
    if match: return match.group(1).strip().upper()
    # Si no, buscar Oficio Nro
    match2 = re.search(r"Nro\.\s*([\w-]+)", str(texto), re.IGNORECASE)
    return match2.group(1).strip() if match2 else str(texto).strip()

def extraer_unidad_f7(texto_codigo):
    # Intenta sacar la unidad del código PN-UNIDAD-QX
    if not texto_codigo: return "DINIC"
    match = re.search(r"PN-([A-Z]+)-", str(texto_codigo).upper())
    if match:
        return match.group(1)
    return "DINIC" # Default si no encuentra patrón

def preservar_bordes(cell, fill_obj):
    original_border = copy(cell.border)
    cell.fill = fill_obj
    if original_border: cell.border = original_border
    else:
        thin = Side(border_style="thin", color="000000")
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

def invocar_ia_segura(content):
    max_retries = 3
    for i in range(max_retries):
        try: return model.generate_content(content)
        except Exception as e:
            if "429" in str(e): time.sleep(2); continue
            else: raise e
    raise Exception("Sistema saturado.")

# --- 5. SIDEBAR (PANEL LATERAL REORGANIZADO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown(f"## {NOMBRE_SISTEMA}") # <-- Nombre principal actualizado

    st.markdown("---")
    st.markdown("### 📋 Datos del Oficial")

    # Inputs para datos del oficial (no son acciones, se quedan como inputs)
    nombre_input = st.text_input("Grado y Nombre:", value=st.session_state.usuario_turno)
    if nombre_input: st.session_state.usuario_turno = nombre_input
    fecha_turno = st.date_input("Fecha Operación:", value=datetime.now())

    st.markdown("---")
    st.markdown("### 🛠️ Acciones de Turno")

    # Botón para nuevo turno, ahora en una sección de acciones
    if st.button("🗑️ NUEVO TURNO (Borrar Todo)", type="primary", use_container_width=True):
        st.session_state.registros = []
        st.session_state.docs_procesados_hoy = 0
        st.session_state.edit_index = None
        # st.session_state.lista_unidades = ... # (Opcional: reiniciar listas)
        # st.session_state.lista_reasignados = [] # (Opcional: reiniciar listas)
        st.rerun()

    st.markdown("---")
    st.markdown("### 📂 Gestión de Matriz Base")

    matriz_path = "matriz_maestra.xlsx"
    if os.path.exists(matriz_path):
        st.success("✅ Matriz Cargada")
        # Botón para cambiar la matriz
        if st.button("🔄 Cambiar Matriz Base", use_container_width=True):
            os.remove(matriz_path)
            st.rerun()
    else:
        # El uploader no puede ser un botón simple, pero está en la sección de gestión
        up_m = st.file_uploader("Cargar Matriz .xlsx", type=['xlsx'])
        if up_m:
            with open(matriz_path, "wb") as f: f.write(up_m.getbuffer())
            st.rerun()

# --- ÁREA PRINCIPAL ---
st.markdown(f'<div class="main-header"><h1>{NOMBRE_SISTEMA}</h1></div>', unsafe_allow_html=True)

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

        # --- COLUMNA IZQUIERDA: PARÁMETROS ---
        with col1:
            val_tipo = registro_a_editar['L'] if (is_editing and registro_a_editar['L']) else "TRAMITE NORMAL"
            if not val_tipo: val_tipo = "TRAMITE NORMAL"
            tipo_proceso = st.selectbox("Tipo Gestión:",
                ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"],
                index=["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"].index(val_tipo)
            )

            val_salida = registro_a_editar['N'] if (is_editing and registro_a_editar['N']) else "QUIPUX ELECTRONICO"
            tipo_doc_salida = st.selectbox("Formato Salida:",
                ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"],
                index=["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"].index(val_salida) if val_salida else 0
            )

            # === MULTI-SELECCIÓN UNIDADES ===
            st.markdown("---")
            st.caption("🏢 DEPENDENCIA/as DE DESTINO")

            opciones_unidades = sorted(st.session_state.lista_unidades)

            # Pre-llenado si es edición
            default_units = []
            if is_editing and registro_a_editar['M']:
                prev_units = registro_a_editar['M'].split(", ")
                default_units = [u for u in prev_units if u in opciones_unidades]

            # Widget Multiselect
            unidades_selected = st.multiselect("Seleccione Unidad(es):", opciones_unidades, default=default_units)

            # Opciones extra: NINGUNA y OTRA
            chk_ninguna = st.checkbox("NINGUNA (Solo Conocimiento)")
            chk_otra = st.checkbox("✍️ OTRA (Agregar Nueva)")

            input_otra_unidad = ""
            if chk_otra:
                input_otra_unidad = st.text_input("Nueva Unidad (Siglas):").upper()

            # Lógica final de unidades
            lista_final_unidades = []
            if chk_ninguna:
                lista_final_unidades = [] # Vacio para Excel
            else:
                lista_final_unidades = unidades_selected.copy()
                if input_otra_unidad: lista_final_unidades.append(input_otra_unidad)

            str_unidades_final = ", ".join(lista_final_unidades)
            # ===============================

            # === LÓGICA REASIGNADO (DESTINATARIO) ===
            destinatario_reasignado_final = ""
            if tipo_proceso == "REASIGNADO":
                st.markdown("---")
                st.caption("👤 DESTINATARIO REASIGNADO")
                opciones_reasig = ["SELECCIONAR..."] + st.session_state.lista_reasignados + ["✍️ NUEVO DESTINATARIO"]

                idx_rea = 0
                # Intentar recuperar si editamos
                if is_editing and registro_a_editar.get("O"):
                    if registro_a_editar["O"] in st.session_state.lista_reasignados:
                         idx_rea = opciones_reasig.index(registro_a_editar["O"])

                sel_reasig = st.selectbox("A quién se reasigna:", opciones_reasig, index=idx_rea)

                if sel_reasig == "✍️ NUEVO DESTINATARIO":
                    destinatario_reasignado_final = st.text_input("Grado y Nombre Completo:").upper()
                elif sel_reasig != "SELECCIONAR...":
                    destinatario_reasignado_final = sel_reasig
            # ========================================

        # --- COLUMNA DERECHA: ARCHIVOS ---
        with col2:
            doc_entrada = None
            doc_salida = None

            # Uploaders según tipo
            if tipo_proceso == "TRAMITE NORMAL":
                c1_in, c2_out = st.columns(2)
                doc_entrada = c1_in.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_main")
                doc_salida = c2_out.file_uploader("2. Doc RESPUESTA", type=['pdf'], key="out_main")
            elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
                doc_entrada = st.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_s")
            elif tipo_proceso == "GENERADO DESDE DESPACHO":
                doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_s")

            # --- SECCIÓN DE CÁMARA ELIMINADA ---
            # Se ha eliminado el bloque de st.camera_input y la lógica asociada
            # como se solicitó.
            # ------------------------------------

        btn_text = "🔄 ACTUALIZAR" if is_editing else "➕ AGREGAR"

        # --- BOTÓN DE PROCESAMIENTO ---
        if st.button(btn_text, type="primary"):
            if not os.path.exists(matriz_maestra.xlsx"):
                st.error("❌ Falta Matriz Base.")
            else:
                # Validaciones
                valid_units = True
                if tipo_proceso != "CONOCIMIENTO" and not str_unidades_final and not chk_ninguna:
                    st.warning("⚠️ Seleccione al menos una Dependencia de Destino.")
                    valid_units = False

                if valid_units:
                    process = False
                    if tipo_proceso == "TRAMITE NORMAL": process = True if (is_editing or doc_entrada or doc_salida) else False
                    elif doc_entrada or doc_salida: process = True

                    if process:
                        frase = frases_carga()
                        with st.spinner(f"⏳ AGREGANDO A LA LISTA UN MOMENTO POR FAVOR... \n\n👀 Dato: {frase}"):
                            try:
                                # Guardar temporales
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

                                # --- PROMPT ACTUALIZADO ---
                                prompt = """
                                Extrae datos en JSON estricto.
                                1. DESTINATARIOS (IMPORTANTE): Identifica TODOS los destinatarios del documento. Si hay varios, pon sus GRADOS y NOMBRES completos separados por coma. Ejemplo: "Crnl. Juan Perez, Mayo. Luis Silva".
                                2. CODIGO: Busca el código principal del oficio (Header o Asunto). Prioridad: "Oficio Nro. PN-..." o códigos similares.
                                3. FECHAS: DD/MM/AAAA.

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

                                # --- LÓGICA DE CAMPOS ---
                                # Código Entrada y Unidad F7
                                raw_code_in = get_val("codigo_completo_entrada", "G")
                                cod_in = limpiar_codigo(raw_code_in)
                                unidad_f7 = extraer_unidad_f7(cod_in) # Usar regex sobre el código extraído

                                # Destinatarios (Col O)
                                dest_ia = get_val("destinatarios_todos", "O")

                                # Código Salida
                                raw_code_out = get_val("codigo_completo_salida", "P")
                                cod_out = limpiar_codigo(raw_code_out)

                                # Estado S7
                                estado_s7 = "PENDIENTE"
                                if tipo_proceso == "CONOCIMIENTO": estado_s7 = "FINALIZADO"
                                elif tipo_proceso != "TRAMITE NORMAL": estado_s7 = "FINALIZADO"
                                elif (path_in or final_data.get("G")) and (path_out or final_data.get("P")): estado_s7 = "FINALIZADO"

                                # Actualizar Memorias (Unidades y Reasignados)
                                if input_otra_unidad and input_otra_unidad not in st.session_state.lista_unidades:
                                    st.session_state.lista_unidades.append(input_otra_unidad)
                                if destinatario_reasignado_final and destinatario_reasignado_final not in st.session_state.lista_reasignados:
                                    st.session_state.lista_reasignados.append(destinatario_reasignado_final)

                                # Columna T (Sale/No Sale)
                                unidades_internas = ["UDAR","UNDECOF","UCAP","DIGIN","DNATH","DINIC"]
                                es_interno = "NO"
                                if tipo_proceso == "CONOCIMIENTO":
                                    es_interno = "NO"
                                else:
                                    # Si alguna de las unidades seleccionadas es interna, ponemos SI (o lógica custom)
                                    # Asumiremos SI si va a una unidad productora interna
                                    any_internal = any(u in str_unidades_final for u in unidades_internas)
                                    es_interno = "SI" if any_internal else "NO"

                                # CONSTRUCCION ROW
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
                                    "L": tipo_proceso if tipo_proceso != "TRAMITE NORMAL" else "",
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
                                    # "FOTO_EVIDENCIA": foto_b64 <-- Campo de foto eliminado del registro
                                }

                                # REGLAS ESPECÍFICAS POR TIPO
                                if tipo_proceso == "GENERADO DESDE DESPACHO":
                                    code_gen = limpiar_codigo(get_val("codigo_completo_salida", "P"))
                                    if len(code_gen) < 5: code_gen = limpiar_codigo(get_val("codigo_completo_entrada", "G"))
                                    
                                    row["D"]=""; row["E"]=""; row["F"]="DINIC"
                                    row["G"]=code_gen; row["P"]=code_gen; row["V"]=code_gen
                                    row["C"]=row["Q"]; row["H"]=row["Q"]

                                elif tipo_proceso == "REASIGNADO":
                                    row["P"]=""; row["V"]=""
                                    for k in ["Q","W","X"]: row[k] = row["C"]
                                    if destinatario_reasignado_final:
                                        row["O"] = destinatario_reasignado_final

                                elif tipo_proceso == "CONOCIMIENTO":
                                    row["M"]=""; row["U"]=""; row["T"]="NO"; row["S"]="FINALIZADO"
                                    for k in ["N","O","P","V"]: row[k] = ""
                                    for k in ["Q","W","X"]: row[k] = row["C"]

                                # Limpieza final si PENDIENTE
                                if row["S"] == "PENDIENTE":
                                    for k in ["N", "O", "P", "Q", "V", "W", "X"]: row[k] = ""

                                # GUARDAR
                                if is_editing:
                                    st.session_state.registros[idx_edit] = row
                                    st.session_state.edit_index = None
                                    st.success("✅ Actualizado")
                                else:
                                    st.session_state.registros.append(row)
                                    st.session_state.docs_procesados_hoy += 1
                                    st.success("✅ Agregado a la lista")

                                for p in paths: os.remove(p)
                                st.rerun()

                            except Exception as e: st.error(f"Error Técnico: {e}")
                    else: st.warning("⚠️ Sube documento.")

        # --- VISUALIZACIÓN LISTA Y PREVIEW ---
        if st.session_state.registros:
            st.markdown("---")
            st.markdown("#### 📋 Cola de Trabajo")

            # Selector para ver preview (por defecto el último)
            indices = [f"Reg #{i+1} | {r['G']}" for i, r in enumerate(st.session_state.registros)]
            sel_preview = st.selectbox("👁️ Previsualizar Registro en Matriz:", range(len(st.session_state.registros)), format_func=lambda x: indices[x], index=len(st.session_state.registros)-1)

            # MOSTRAR MINI MATRIZ DEL SELECCIONADO
            reg_prev = st.session_state.registros[sel_preview]
            df_prev = pd.DataFrame([reg_prev])
            # Ordenar columnas para visualización amigable
            cols_order = ["C","D","F","G","I","M","O","P","S","T"]
            df_show = df_prev[[c for c in cols_order if c in df_prev.columns]]
            st.dataframe(df_show, hide_index=True)

            # LISTADO COMPLETO
            for i, reg in enumerate(st.session_state.registros):
                bg = "#e8f5e9" if reg["S"] == "FINALIZADO" else "#ffebee"
                bc = "green" if reg["S"] == "FINALIZADO" else "red"
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: {bg}; padding: 10px; border-left: 5px solid {bc}; margin-bottom: 5px; border-radius: 5px;">
                        <b>#{i+1}</b> | <b>{reg['G']}</b> | {reg['D']} <br>
                        Destino: <b>{reg['M']}</b> | Estado: <b>{reg['S']}</b>
                    </div>""", unsafe_allow_html=True)
                    c_edit, c_del = st.columns([1, 1])
                    if c_edit.button("✏️ EDITAR", key=f"e_{i}"): st.session_state.edit_index = i; st.rerun()
                    if c_del.button("🗑️ BORRAR", key=f"d_{i}"):
                        st.session_state.registros.pop(i)
                        st.session_state.docs_procesados_hoy = max(0, st.session_state.docs_procesados_hoy - 1)
                        if st.session_state.edit_index == i: st.session_state.edit_index = None
                        st.rerun()

            # --- DESCARGA DIRECTA ---
            # Preparamos el buffer
            if os.path.exists(matriz_maestra.xlsx"):
                try:
                    wb = load_workbook(matriz_maestra.xlsx")
                    ws = wb[next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])]
                    start_row = 7
                    while ws.cell(row=start_row, column=1).value is not None: start_row += 1

                    gf = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
                    rf = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

                    for i, reg in enumerate(st.session_state.registros):
                        r = start_row + i
                        def w(c, v): ws.cell(row=r, column=c).value = v
                        w(1, i+1); w(3, reg["C"]); w(4, reg["D"]); w(5, reg["E"])
                        w(6, reg["F"]); w(7, reg["G"]); w(8, reg["H"]); w(9, reg["I"])
                        w(10, reg["J"]); w(11, reg["K"]); w(12, reg["L"]); w(13, reg["M"])
                        w(14, reg["N"]); w(15, reg["O"]); w(16, reg["P"]); w(17, reg["Q"])
                        cell_s = ws.cell(row=r, column=19); cell_s.value = reg["S"]
                        if reg["S"]=="FINALIZADO": preservar_bordes(cell_s, gf)
                        elif reg["S"]=="PENDIENTE": preservar_bordes(cell_s, rf)
                        w(20, reg["T"]); w(21, reg["U"]); w(22, reg["V"]); w(23, reg["W"]); w(24, reg["X"])

                    out = io.BytesIO()
                    wb.save(out); out.seek(0)
                    f_str = fecha_turno.strftime("%d-%m-%y")
                    u_str = st.session_state.usuario_turno.upper()

                    st.download_button(
                        label="📥 DESCARGAR EXCEL FINAL",
                        data=out,
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
                    prompt_asesor = "Actúa como JEFE DE AYUDANTÍA. Dame Diagnóstico, Decisión y Redacción."
                    res = invocar_ia_segura([prompt_asesor, f_as])
                    st.markdown(res.text)
                    st.session_state.consultas_ia += 1
                    os.remove(p_as)
                except Exception as e: st.error(f"Error: {e}")

    # --- TAB 3: ADMIN ---
    with tab3:
        st.info("🔐 Solo Lunes 08:30")

# FOOTER
st.markdown("---")
st.caption(f"{NOMBRE_SISTEMA} | {VER_SISTEMA} | Powered by: John Stalin Carrillo Narvaez | cnjstalin@gmail.com | 0996652042 |")
