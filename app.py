import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import io
import re
import pandas as pd
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(
    page_title="S.I.G.D. DINIC PRO",
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
if 'edit_index' not in st.session_state: st.session_state.edit_index = None # Para saber qué estamos editando

# --- 3. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error crítico: No se detectan credenciales.")
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
    """Aplica color sin borrar los bordes existentes."""
    original_border = copy(cell.border)
    cell.fill = fill_obj
    # Re-aplicar bordes originales (si existen) o poner bordes finos por defecto
    if original_border:
        cell.border = original_border
    else:
        thin = Side(border_style="thin", color="000000")
        cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

# --- 5. BARRA LATERAL (RESPALDO Y CONFIG) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown("### 👮‍♂️ CONTROL DE MANDO")
    
    st.caption("RESPONSABLE DEL TURNO")
    nombre_input = st.text_input("Grado y Nombre:", value=st.session_state.usuario_turno)
    if nombre_input: st.session_state.usuario_turno = nombre_input
    
    fecha_turno = st.date_input("Fecha Operación:", value=datetime.now())

    st.markdown("---")
    st.markdown("### 💾 SISTEMA DE RESPALDO")
    
    # Descargar Backup
    if st.session_state.registros:
        json_str = json.dumps(st.session_state.registros, default=str)
        st.download_button(
            "⬇️ Descargar Copia de Seguridad (JSON)",
            json_str,
            file_name=f"backup_dinic_{datetime.now().strftime('%H%M')}.json",
            mime="application/json",
            type="primary"
        )
    
    # Restaurar Backup
    uploaded_backup = st.file_uploader("⬆️ Restaurar Copia", type=['json'])
    if uploaded_backup:
        try:
            data = json.load(uploaded_backup)
            st.session_state.registros = data
            st.success("¡Registros restaurados!")
            st.rerun()
        except:
            st.error("Archivo corrupto")

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
st.markdown('<div class="main-header"><h1>S.I.G.D. - DINIC v17.0</h1><h3>Gestión de Matriz con Edición y Respaldo</h3></div>', unsafe_allow_html=True)

if sistema_activo:
    # Determinamos si estamos editando o creando nuevo
    is_editing = st.session_state.edit_index is not None
    idx_edit = st.session_state.edit_index
    
    registro_a_editar = st.session_state.registros[idx_edit] if is_editing else None

    # TÍTULO DINÁMICO
    if is_editing:
        st.warning(f"✏️ ESTÁS EDITANDO EL REGISTRO #{idx_edit + 1} - {registro_a_editar['G']}")
        if st.button("❌ CANCELAR EDICIÓN"):
            st.session_state.edit_index = None
            st.rerun()
    else:
        st.info("🆕 NUEVO REGISTRO")

    # --- FORMULARIO DE INGRESO ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("##### ⚙️ Configuración")
        # Si editamos, mantenemos los valores previos o permitimos cambiar
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
        st.markdown("##### 📂 Carga de Documentos")
        doc_entrada = None
        doc_salida = None
        
        if is_editing:
            st.success("ℹ️ Sube el documento faltante para completar el registro.")
        
        # LÓGICA DE UPLOADS
        if tipo_proceso == "TRAMITE NORMAL":
            c1, c2 = st.columns(2)
            # En edición, si ya hay datos de entrada, avisamos que es opcional resubirlo
            lbl_in = "1. Doc RECIBIDO (Re-subir si desea cambiar)" if is_editing else "1. Doc RECIBIDO"
            doc_entrada = c1.file_uploader(lbl_in, type=['pdf'], key="in_main")
            
            lbl_out = "2. Doc RESPUESTA (Subir para FINALIZAR)" 
            doc_salida = c2.file_uploader(lbl_out, type=['pdf'], key="out_main")
            
        elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
            doc_entrada = st.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_single")
            
        elif tipo_proceso == "GENERADO DESDE DESPACHO":
            doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_single")

    # --- BOTÓN DE ACCIÓN ---
    btn_text = "🔄 ACTUALIZAR REGISTRO" if is_editing else "➕ AGREGAR A LA LISTA"
    
    if st.button(btn_text, type="primary"):
        if not os.path.exists("matriz_maestra.xlsx"):
            st.error("❌ Falta Matriz Base.")
        else:
            # Validar si procesamos
            process = False
            if tipo_proceso == "TRAMITE NORMAL":
                if is_editing: process = True # En edición permitimos cualquier cambio
                elif doc_entrada or doc_salida: process = True
            elif doc_entrada or doc_salida: process = True
            
            if process:
                with st.spinner("🤖 Procesando con IA y aplicando reglas de negocio..."):
                    try:
                        # 1. Guardar Temporales
                        paths = []
                        path_in, path_out = None, None
                        
                        if doc_entrada:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                t.write(doc_entrada.getvalue()); path_in = t.name; paths.append(t.name)
                        if doc_salida:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                t.write(doc_salida.getvalue()); path_out = t.name; paths.append(t.name)

                        # 2. IA Extracción
                        model = genai.GenerativeModel('gemini-flash-latest')
                        files_ia = []
                        if path_in: files_ia.append(genai.upload_file(path_in, display_name="In"))
                        if path_out: files_ia.append(genai.upload_file(path_out, display_name="Out"))

                        data = {}
                        if files_ia:
                            prompt = """
                            Extrae datos exactos para Matriz Policial JSON.
                            1. NOMBRES: Extrae "GRADO + NOMBRE COMPLETO".
                            2. CÓDIGOS: Completos (Ej: PN-DIGIN-QX...).
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
                            res = model.generate_content([prompt, *files_ia])
                            data = json.loads(res.text.replace("```json", "").replace("```", ""))

                        # 3. MERGE DE DATOS (SI ES EDICIÓN)
                        # Si estamos editando, usamos los datos viejos como base y sobrescribimos con los nuevos que traiga la IA
                        final_data = registro_a_editar.copy() if is_editing else {}
                        
                        # Helpers
                        def get_val(key_ia, key_row, default=""):
                            # Si la IA trajo dato, úsalo. Si no, usa el que ya estaba (si editamos). Si no, vacío.
                            val_ia = data.get(key_ia)
                            val_old = final_data.get(key_row, "")
                            return val_ia if val_ia else val_old

                        # LÓGICA DE UNIDAD
                        cod_in = limpiar_codigo(get_val("codigo_completo_entrada", "G"))
                        unidad_f7 = extraer_unidad(get_val("codigo_completo_entrada", "G"))
                        
                        # ESTADO DEL REGISTRO
                        tiene_entrada = True if (path_in or (is_editing and final_data.get("G"))) else False
                        tiene_salida = True if (path_out or (is_editing and final_data.get("P"))) else False
                        
                        estado_s7 = "PENDIENTE"
                        if tipo_proceso != "TRAMITE NORMAL":
                            estado_s7 = "FINALIZADO"
                        elif tiene_entrada and tiene_salida:
                            estado_s7 = "FINALIZADO"

                        # Construcción del Registro Nuevo/Actualizado
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
                            "M": get_val("cargo_destinatario_mapeado", "M"),
                            "N": tipo_doc_salida,
                            "O": get_val("destinatario_grado_nombre", "O"),
                            "P": limpiar_codigo(get_val("codigo_completo_salida", "P")),
                            "Q": get_val("fecha_salida", "Q"),
                            "R": "",
                            "S": estado_s7,
                            "T": "SI" if get_val("cargo_destinatario_mapeado", "M") in ["UDAR","UNDECOF","UCAP","DIGIN","DNATH"] else "NO",
                            "U": get_val("cargo_destinatario_mapeado", "U"),
                            "V": limpiar_codigo(get_val("codigo_completo_salida", "V")),
                            "W": get_val("fecha_salida", "W"),
                            "X": get_val("fecha_salida", "X")
                        }

                        # REGLA DE CAMPOS VACIOS SI ES PENDIENTE (TRAMITE NORMAL)
                        if estado_s7 == "PENDIENTE":
                            for k in ["M", "N", "O", "P", "Q", "T", "U", "V", "W", "X"]:
                                row[k] = ""
                        
                        # EXCEPCIONES FIJAS
                        if tipo_proceso == "GENERADO DESDE DESPACHO":
                            row["D"]=""; row["E"]=""; row["F"]="DINIC"
                            row["C"]=row["Q"]; row["H"]=row["Q"]
                        elif tipo_proceso == "REASIGNADO":
                            row["P"]=""; row["V"]=""
                            fecha_base = row["C"]
                            for k in ["Q","W","X"]: row[k] = fecha_base
                        elif tipo_proceso == "CONOCIMIENTO":
                            for k in ["M","N","O","P","S","T","U","V"]: row[k] = ""
                            fecha_base = row["C"]
                            for k in ["Q","W","X"]: row[k] = fecha_base

                        # GUARDAR
                        if is_editing:
                            st.session_state.registros[idx_edit] = row
                            st.session_state.edit_index = None # Salir modo edición
                            st.success("✅ Registro Actualizado Correctamente")
                        else:
                            st.session_state.registros.append(row)
                            st.success("✅ Registro Agregado a la Lista")

                        for p in paths: os.remove(p)
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("⚠️ Sube al menos un documento.")

    # --- LISTA Y ACCIONES ---
    if st.session_state.registros:
        st.markdown("---")
        st.markdown("#### 📋 Expedientes en Cola")
        
        # Tabla Custom
        for i, reg in enumerate(st.session_state.registros):
            bg_color = "#e8f5e9" if reg["S"] == "FINALIZADO" else "#ffebee"
            border_color = "green" if reg["S"] == "FINALIZADO" else "red"
            
            with st.container():
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 10px; border-left: 5px solid {border_color}; margin-bottom: 5px; border-radius: 5px;">
                    <b>#{i+1}</b> | <b>{reg['G']}</b> | {reg['D']} <br>
                    <span class="status-badge" style="background-color: {border_color};">{reg['S']}</span> 
                    Salida: {reg['P'] if reg['P'] else '---'}
                </div>
                """, unsafe_allow_html=True)
                
                c_edit, c_del = st.columns([1, 1])
                if c_edit.button("✏️ EDITAR", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
                if c_del.button("🗑️ BORRAR", key=f"del_{i}"):
                    st.session_state.registros.pop(i)
                    if st.session_state.edit_index == i: st.session_state.edit_index = None
                    st.rerun()

        st.markdown("---")
        if st.button("📥 DESCARGAR MATRIZ FINAL (EXCEL)", type="primary"):
            if os.path.exists("matriz_maestra.xlsx"):
                try:
                    wb = load_workbook("matriz_maestra.xlsx")
                    sheet_name = next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])
                    ws = wb[sheet_name]
                    
                    start_row = 7
                    while ws.cell(row=start_row, column=1).value is not None: start_row += 1
                    
                    # Estilos
                    green_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
                    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    
                    for i, reg in enumerate(st.session_state.registros):
                        r = start_row + i
                        
                        def w(c, v): 
                            cell = ws.cell(row=r, column=c)
                            cell.value = v
                            # NO TOCAR BORDES A MENOS QUE HAYA COLOR
                        
                        w(1, i + 1)
                        w(3, reg["C"]); w(4, reg["D"]); w(5, reg["E"])
                        w(6, reg["F"]); w(7, reg["G"]); w(8, reg["H"])
                        w(9, reg["I"]); w(10, reg["J"]); w(11, reg["K"])
                        w(12, reg["L"]); w(13, reg["M"]); w(14, reg["N"])
                        w(15, reg["O"]); w(16, reg["P"]); w(17, reg["Q"])
                        
                        # Columna S con Color y Preservación de Bordes
                        cell_s = ws.cell(row=r, column=19)
                        cell_s.value = reg["S"]
                        if reg["S"] == "FINALIZADO": preservar_bordes(cell_s, green_fill)
                        elif reg["S"] == "PENDIENTE": preservar_bordes(cell_s, red_fill)
                        
                        w(20, reg["T"]); w(21, reg["U"])
                        w(22, reg["V"]); w(23, reg["W"]); w(24, reg["X"])

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)
                    
                    f_str = fecha_turno.strftime("%d-%m-%y")
                    u_str = st.session_state.usuario_turno.upper()
                    fname = f"TURNO {f_str} {u_str}.xlsx"
                    
                    st.download_button("💾 Guardar Archivo", data=output, file_name=fname, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception as e:
                    st.error(f"Error Excel: {e}")
            else:
                st.error("Sube la matriz base primero.")
