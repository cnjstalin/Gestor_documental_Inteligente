import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import re
import time
import io
import random
import pandas as pd
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
NOMBRE_SISTEMA = "SIGD-DINIC Sistema Oficial de Gestión Documental"
VER_SISTEMA = "v26.5"

st.set_page_config(
    page_title=NOMBRE_SISTEMA,
    layout="wide",
    page_icon="📂",
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
    /* Ajuste visual para el Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
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

# Listas de Memoria
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

def frases_curiosas():
    frases = [
        "☕ Preparando café digital...",
        "🐢 Más rápido que un oficio en físico...",
        "🤖 La IA está leyendo (esperemos que entienda la letra)...",
        "🕵️‍♂️ Descifrando códigos secretos...",
        "🚀 Calibrando satélites de la DINIC...",
        "📂 Archivando en el ciberespacio...",
        "👮‍♂️ Solicitando autorización al sistema..."
    ]
    return random.choice(frases)

def limpiar_codigo(texto):
    if not texto: return ""
    # Prioridad 1: Buscar patrón exacto PN-XXXX-QX
    match = re.search(r"(PN-[A-Z0-9]+-QX(?:-\d+)?)", str(texto), re.IGNORECASE)
    if match: return match.group(1).strip().upper()
    
    # Prioridad 2: Buscar palabra Oficio Nro
    match2 = re.search(r"(?:Oficio|Memorando).*?(PN-.*)", str(texto), re.IGNORECASE)
    if match2: return match2.group(1).strip().upper()

    return str(texto).strip()

def extraer_unidad_f7(texto_codigo):
    # Extrae lo que está entre PN- y -QX
    if not texto_codigo: return "DINIC"
    match = re.search(r"PN-([A-Z]+)-QX", str(texto_codigo).upper())
    if match:
        return match.group(1)
    # Si no encuentra patrón estándar, intenta buscar siglas comunes
    unidades = ["UCAP", "UNDECOF", "UDAR", "DIGIN", "DNATH", "DAOP"]
    for u in unidades:
        if u in str(texto_codigo).upper(): return u
    return "DINIC" 

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

# --- 5. SIDEBAR (PANEL DE CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown("### 👮‍♂️ CONTROL DE MANDO")
    
    # SECCIÓN 1: DATOS
    st.markdown("#### 1. Datos del Oficial")
    nombre_input = st.text_input("Grado y Nombre:", value=st.session_state.usuario_turno)
    if nombre_input: st.session_state.usuario_turno = nombre_input
    fecha_turno = st.date_input("Fecha Operación:", value=datetime.now())

    st.markdown("---")
    
    # SECCIÓN 2: ACCIONES
    st.markdown("#### 2. Acciones")
    if st.button("🗑️ NUEVO TURNO (Borrar Todo)", type="primary"):
        st.session_state.registros = []
        st.session_state.docs_procesados_hoy = 0
        st.session_state.edit_index = None
        st.rerun()

    st.markdown("---")
    
    # SECCIÓN 3: MATRIZ
    st.markdown("#### 3. Base de Datos")
    if os.path.exists("matriz_maestra.xlsx"):
        st.success("✅ Matriz Cargada")
        if st.button("🔄 Cambiar Archivo Base"): os.remove("matriz_maestra.xlsx"); st.rerun()
    else:
        up_m = st.file_uploader("Cargar Matriz .xlsx", type=['xlsx'])
        if up_m:
            with open("matriz_maestra.xlsx", "wb") as f: f.write(up_m.getbuffer())
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
            default_units = []
            
            # Pre-llenado
            if is_editing and registro_a_editar['M']:
                prev_units = registro_a_editar['M'].split(", ")
                default_units = [u for u in prev_units if u in opciones_unidades]

            # Widget Multiselect
            unidades_selected = st.multiselect("Seleccione Unidad(es):", opciones_unidades, default=default_units)
            
            # Opciones extra
            col_ning, col_otra = st.columns(2)
            chk_ninguna = col_ning.checkbox("NINGUNA (Solo Conocimiento)")
            chk_otra = col_otra.checkbox("✍️ OTRA (Agregar)")
            
            input_otra_unidad = ""
            if chk_otra:
                input_otra_unidad = st.text_input("Nueva Unidad (Siglas):").upper()

            # Lógica final de unidades
            lista_final_unidades = []
            if chk_ninguna:
                lista_final_unidades = [] 
            else:
                lista_final_unidades = unidades_selected.copy()
                if input_otra_unidad: lista_final_unidades.append(input_otra_unidad)

            str_unidades_final = ", ".join(lista_final_unidades)
            # ===============================

            # === LÓGICA REASIGNADO (DESTINATARIO) ===
            destinatario_reasignado_final = ""
            if tipo_proceso == "REASIGNADO":
                st.markdown("---")
                st.markdown("👤 **DESTINATARIO REASIGNADO**")
                
                # Lista combinada
                opciones_reasig = ["SELECCIONAR..."] + st.session_state.lista_reasignados + ["✍️ NUEVO DESTINATARIO"]
                
                idx_rea = 0 
                if is_editing and registro_a_editar.get("O") in st.session_state.lista_reasignados:
                         idx_rea = opciones_reasig.index(registro_a_editar["O"])

                sel_reasig = st.selectbox("Historial Destinatarios:", opciones_reasig, index=idx_rea)
                
                # Input Manual siempre visible si se elige nuevo o si se quiere sobrescribir
                val_manual = ""
                if is_editing and registro_a_editar.get("O") and registro_a_editar.get("O") not in st.session_state.lista_reasignados:
                    val_manual = registro_a_editar.get("O")

                input_manual_reasig = st.text_input("Escribir Grado y Nombre:", value=val_manual)
                
                if sel_reasig == "✍️ NUEVO DESTINATARIO" or input_manual_reasig:
                    destinatario_reasignado_final = input_manual_reasig.upper()
                elif sel_reasig != "SELECCIONAR...":
                    destinatario_reasignado_final = sel_reasig
            # ========================================

        # --- COLUMNA DERECHA: ARCHIVOS ---
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
        
        # --- BOTÓN DE PROCESAMIENTO ---
        if st.button(btn_text, type="primary"):
            if not os.path.exists("matriz_maestra.xlsx"):
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
                        frase = frases_curiosas()
                        msg_carga = f"⏳ AGREGANDO A LA LISTA UN MOMENTO POR FAVOR...\n\n👀 {frase}"
                        
                        with st.spinner(msg_carga):
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

                                # --- PROMPT AJUSTADO ---
                                prompt = """
                                Extrae datos en JSON estricto.
                                1. DESTINATARIOS (MUY IMPORTANTE): Identifica a TODOS los destinatarios (Para). Extrae GRADO y NOMBRE de CADA UNO. 
                                   Formato obligatorio: "Grado Nombre Apellido, Grado Nombre Apellido, Grado Nombre Apellido". 
                                   NO pongas solo uno si hay varios. Sepáralos por comas.
                                2. CODIGO: Busca el código principal tipo "PN-XYZ-QX-202X". Si no hay, busca "Oficio Nro.".
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
                                unidad_f7 = extraer_unidad_f7(cod_in)
                                
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
                                    any_internal = any(u in str_unidades_final for u in unidades_internas)
                                    es_interno = "SI" if any_internal else "NO"

                                # CONSTRUCCION ROW BASE
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
                                    "X": get_val("fecha_salida", "X")
                                }

                                # REGLAS ESPECÍFICAS
                                if tipo_proceso == "GENERADO DESDE DESPACHO":
                                    # Forzar que el código sea el mismo en G, P y V
                                    # Intentamos tomar el mejor código detectado (salida o entrada)
                                    best_code = cod_out if len(cod_out) > 5 else cod_in
                                    best_unit = extraer_unidad_f7(best_code)
                                    
                                    row["D"]=""; row["E"]=""; row["F"]= best_unit # Antes DINIC, ahora intenta extraer
                                    row["G"]=best_code; row["P"]=best_code; row["V"]=best_code
                                    row["C"]=row["Q"]; row["H"]=row["Q"]
                                
                                elif tipo_proceso == "REASIGNADO":
                                    row["P"]=""; row["V"]=""
                                    for k in ["Q","W","X"]: row[k] = row["C"]
                                    if destinatario_reasignado_final:
                                        row["O"] = destinatario_reasignado_final
                                    # Asegurar F7
                                    row["F"] = extraer_unidad_f7(row["G"])

                                elif tipo_proceso == "CONOCIMIENTO":
                                    row["M"]=""; row["U"]=""; row["T"]="NO"; row["S"]="FINALIZADO"
                                    for k in ["N","O","P","V"]: row[k] = ""
                                    for k in ["Q","W","X"]: row[k] = row["C"]

                                # Limpieza final PENDIENTE
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
                                    st.success("✅ Agregado")

                                for p in paths: os.remove(p)
                                st.rerun()

                            except Exception as e: st.error(f"Error Técnico: {e}")
                    else: st.warning("⚠️ Sube documento.")

        # --- VISUALIZACIÓN LISTA Y PREVIEW ---
        if st.session_state.registros:
            st.markdown("---")
            st.markdown("#### 📋 Cola de Trabajo")
            
            # 1. MINI MATRIZ DE PREVISUALIZACIÓN (FILA ÚNICA)
            if len(st.session_state.registros) > 0:
                st.caption("👁️ Previsualización de Registro Seleccionado:")
                indices = [f"#{i+1} | {r['G']}" for i, r in enumerate(st.session_state.registros)]
                sel_idx = st.selectbox("Seleccionar Registro:", range(len(st.session_state.registros)), format_func=lambda x: indices[x], index=len(st.session_state.registros)-1, label_visibility="collapsed")
                
                reg_prev = st.session_state.registros[sel_idx]
                df_prev = pd.DataFrame([reg_prev])
                # Columnas clave para mostrar
                cols_order = ["C","F","G","M","O","P","S","T"]
                df_show = df_prev[[c for c in cols_order if c in df_prev.columns]]
                st.dataframe(df_show, hide_index=True, use_container_width=True)

            st.write("")

            # 2. LISTA DE TARJETAS
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

            # --- DESCARGA DIRECTA (SIN DOBLE CLIC) ---
            if os.path.exists("matriz_maestra.xlsx"):
                try:
                    # Generamos el archivo en memoria ANTES de pintar el botón
                    wb = load_workbook("matriz_maestra.xlsx")
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

                    out_buffer = io.BytesIO()
                    wb.save(out_buffer)
                    out_buffer.seek(0)
                    
                    f_str = fecha_turno.strftime("%d-%m-%y")
                    u_str = st.session_state.usuario_turno.upper()
                    
                    st.download_button(
                        label="📥 DESCARGAR EXCEL FINAL",
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
st.caption(f"{VER_SISTEMA} | Powered by: John Stalin Carrillo Narvaez | cnjstalin@gmail.com | 0996652042 |")
