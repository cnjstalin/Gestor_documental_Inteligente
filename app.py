import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import io
import re
import time
import pandas as pd
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(
    page_title="S.I.G.D. DINIC - v25.1",
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

# --- 3. AUTENTICACIÓN ---
try:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        st.error("🚨 ERROR: No se encontró la API KEY. Configúrala en los Secrets.")
        st.stop()
        
    genai.configure(api_key=api_key)
    sistema_activo = True

except Exception as e:
    st.error(f"⚠️ Error de Conexión General: {e}")
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

def invocar_ia_todoterreno(content):
    """
    ESTRATEGIA BLINDADA v25.1:
    Prueba una lista de modelos. Si uno falla (404/Error), salta al siguiente.
    Así garantizamos que SIEMPRE funcione, sin importar cambios de Google.
    """
    # Lista de prioridades: El mejor primero, el viejo confiable al final.
    modelos_a_probar = [
        "gemini-1.5-flash",        # La opción rápida y nueva
        "gemini-1.5-flash-latest", # Alias alternativo
        "gemini-1.5-pro",          # Opción potente
        "gemini-1.0-pro",          # Opción anterior
        "gemini-pro"               # La vieja confiable
    ]
    
    ultimo_error = ""

    config = {
        "temperature": 0.1,
        "max_output_tokens": 8192,
    }

    for nombre_modelo in modelos_a_probar:
        try:
            # Intenta configurar el modelo actual de la lista
            model = genai.GenerativeModel(nombre_modelo, generation_config=config)
            
            # Intenta generar (con reintentos por si está saturado 429)
            for i in range(2): 
                try:
                    return model.generate_content(content)
                except Exception as e:
                    if "429" in str(e): # Si está lleno, espera un poco y reintenta
                        time.sleep(2)
                        continue
                    else:
                        raise e # Si es otro error (como 404), lanza la excepción para cambiar de modelo
            
        except Exception as e:
            # Si falla este modelo, guardamos el error y probamos el siguiente de la lista
            ultimo_error = str(e)
            continue # Pasa al siguiente modelo en la lista "modelos_a_probar"
    
    # Si llega aquí es que fallaron TODOS los modelos
    raise Exception(f"⚠️ Error Crítico: No se pudo conectar con NINGÚN modelo de IA. Verifica tu API Key o actualiza requirements.txt. Detalle: {ultimo_error}")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown("### 👮‍♂️ CONTROL DE MANDO")
    
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
st.markdown('<div class="main-header"><h1>S.I.G.D. - DINIC v25.1</h1><h3>Sistema Inteligente de Gestión Documental</h3></div>', unsafe_allow_html=True)

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
                    with st.spinner("🤖 Procesando con IA (Buscando mejor modelo)..."):
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
                                # LLAMADA A LA FUNCIÓN TODOTERRENO
                                res = invocar_ia_todoterreno([prompt, *files_ia])
                                data = json.loads(res.text.replace("```json", "").replace("```", ""))

                            final_data = registro_a_editar.copy() if is_editing else {}
                            def get_val(key_ia, key_row): return data.get(key_ia) if data.get(key_ia) else final_data.get(key_row, "")

                            cod_in = limpiar_codigo(get_val("codigo_completo_entrada", "G"))
                            unidad_f7 = extraer_unidad(get_val("codigo_completo_entrada", "G"))
                            
                            tiene_entrada = True if (path_in or (is_editing and final_data.get("G"))) else False
                            tiene_salida = True if (path_out or (is_editing and final_data.get("P"))) else False
                            
                            estado_s7 = "PENDIENTE"
                            if tipo_proceso != "TRAMITE NORMAL": estado_s7 = "FINALIZADO"
                            elif tiene_entrada and tiene_salida: estado_s7 = "FINALIZADO"

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

                            if estado_s7 == "PENDIENTE":
                                for k in ["M", "N", "O", "P", "Q", "T", "U", "V", "W", "X"]: row[k] = ""
                            
                            if tipo_proceso == "GENERADO DESDE DESPACHO":
                                row["D"]=""; row["E"]=""; row["F"]="DINIC"
                                row["C"]=row["Q"]; row["H"]=row["Q"]
                            elif tipo_proceso == "REASIGNADO":
                                row["P"]=""; row["V"]=""
                                for k in ["Q","W","X"]: row[k] = row["C"]
                            elif tipo_proceso == "CONOCIMIENTO":
                                for k in ["M","N","O","P","S","T","U","V"]: row[k] = ""
                                for k in ["Q","W","X"]: row[k] = row["C"]

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
                else:
                    st.warning("⚠️ Sube documento.")

        if st.session_state.registros:
            st.markdown("#### 📋 Cola de Trabajo")
            for i, reg in enumerate(st.session_state.registros):
                bg = "#e8f5e9" if reg["S"] == "FINALIZADO" else "#ffebee"
                bc = "green" if reg["S"] == "FINALIZADO" else "red"
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: {bg}; padding: 10px; border-left: 5px solid {bc}; margin-bottom: 5px; border-radius: 5px;">
                        <b>#{i+1}</b> | <b>{reg['G']}</b> | {reg['D']} <br>
                        <span class="status-badge" style="background-color: {bc};">{reg['S']}</span> 
                        Salida: {reg['P'] if reg['P'] else '---'}
                    </div>""", unsafe_allow_html=True)
                    c_edit, c_del = st.columns([1, 1])
                    if c_edit.button("✏️ EDITAR", key=f"e_{i}"): st.session_state.edit_index = i; st.rerun()
                    if c_del.button("🗑️ BORRAR", key=f"d_{i}"):
                        st.session_state.registros.pop(i)
                        if st.session_state.edit_index == i: st.session_state.edit_index = None
                        st.rerun()

            if st.button("📥 DESCARGAR EXCEL FINAL", type="primary"):
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
                        st.download_button("💾 Guardar Excel", data=out, file_name=f"TURNO {f_str} {u_str}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    except Exception as e: st.error(f"Error Excel: {e}")

    # --- PESTAÑA 2: ASESOR ---
    with tab2:
        st.markdown("#### 🧠 Consultor de Despacho (IA)")
        st.caption("Analiza documentos complejos y redacta borradores tácticos.")
        up_asesor = st.file_uploader("Sube documento (PDF)", type=['pdf'], key="asesor_up")
        
        if up_asesor and st.button("ANALIZAR ESTRATEGIA"):
            with st.spinner("Analizando jerarquía y redactando..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                        t.write(up_asesor.getvalue()); p_as = t.name
                    
                    f_as = genai.upload_file(p_as, display_name="Consulta")
                    
                    prompt_asesor = """
                    Actúa como JEFE DE AYUDANTÍA DINIC.
                    Analiza:
                    1. DIAGNÓSTICO: ¿Quién pide? ¿Qué pide?
                    2. DECISIÓN: ¿Elevamos a DIGIN o disponemos a Unidades? ¿Por qué?
                    3. REDACCIÓN: El borrador exacto para Quipux.
                    """
                    # LLAMADA A LA FUNCIÓN TODOTERRENO
                    res = invocar_ia_todoterreno([prompt_asesor, f_as])
                    st.markdown(res.text)
                    st.session_state.consultas_ia += 1
                    os.remove(p_as)
                except Exception as e: st.error(f"Error: {e}")

    # --- PESTAÑA 3: ADMIN (NUEVA) ---
    with tab3:
        st.info("🔐 Módulo de Administración y Seguridad")
        st.write("Esta sección está reservada para la gestión de usuarios, claves y roles (Lunes 08:30).")
        st.text_input("Usuario Admin", disabled=True)
        st.text_input("Contraseña", type="password", disabled=True)
        st.button("Ingresar al Panel", disabled=True)

# PIE DE PÁGINA
st.markdown("---")
st.caption("S.I.G.D. - Versión Blindada v25.1 | Powered by Google Gemini")
