import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import io
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Integral DINIC", layout="wide", page_icon="👮‍♂️")

# --- 2. GESTIÓN DE ESTADO (MEMORIA TEMPORAL) ---
if 'registros' not in st.session_state:
    st.session_state.registros = [] # Aquí guardaremos la lista de filas

if 'usuario_turno' not in st.session_state:
    st.session_state.usuario_turno = "" # Para recordar el nombre

# --- 3. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error crítico: No se detectan credenciales en Secrets.")
    sistema_activo = False

# --- 4. BARRA LATERAL (CONFIGURACIÓN DE TURNO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.title("Sistema DINIC v11.0")
    
    st.markdown("### 👮‍♂️ Configuración de Turno")
    
    # CAMPO 1: GRADO Y NOMBRE (PERSISTENTE)
    nombre_input = st.text_input("Grado y Nombre del Encargado:", value=st.session_state.usuario_turno)
    if nombre_input:
        st.session_state.usuario_turno = nombre_input # Guardamos en memoria

    # CAMPO 4: FECHA DEL TURNO
    fecha_turno = st.date_input("Fecha de Turno:", value=datetime.now())
    
    st.write("---")
    st.caption(f"Registros en cola: {len(st.session_state.registros)}")
    if st.button("🗑️ Borrar Lista"):
        st.session_state.registros = []
        st.rerun()

# ==============================================================================
# LÓGICA PRINCIPAL: GESTOR DE MATRIZ INTELIGENTE
# ==============================================================================
st.title("📊 Gestor de Matriz Automatizado")
st.markdown("### Carga de Documentos y Generación de Registros")

if sistema_activo:
    # --- A. MENÚ DE VARIABLES (PUNTO 2) ---
    col_var, col_doc = st.columns([1, 2])
    
    with col_var:
        tipo_proceso = st.selectbox(
            "Seleccione Variable de Proceso:",
            ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"]
        )
        
        tipo_doc_salida = st.selectbox(
            "Tipo Documento Salida (N7):",
            ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"]
        )

    # --- B. CARGA DE ARCHIVOS SEGÚN VARIABLE ---
    with col_doc:
        doc_entrada = None
        doc_salida = None
        
        # Lógica de visualización de uploaders
        if tipo_proceso in ["TRAMITE NORMAL"]:
            c1, c2 = st.columns(2)
            doc_entrada = c1.file_uploader("1. Doc RECEPTADO", type=['pdf'], key="in_normal")
            doc_salida = c2.file_uploader("2. Doc RESPUESTA", type=['pdf'], key="out_normal")
            
        elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
            doc_entrada = st.file_uploader("1. Doc RECEPTADO", type=['pdf'], key="in_single")
            st.info(f"Modo {tipo_proceso}: Solo se requiere documento de entrada.")
            
        elif tipo_proceso == "GENERADO DESDE DESPACHO":
            doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_single")
            st.info("Modo Generado: Solo se requiere documento de salida.")

    # --- C. BOTÓN DE AGREGAR A LA LISTA (PUNTO 3) ---
    if st.button("➕ AGREGAR A LA LISTA"):
        # Validaciones
        valid = False
        if tipo_proceso == "TRAMITE NORMAL" and (doc_entrada or doc_salida): valid = True # Al menos uno para pendiente
        if tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"] and doc_entrada: valid = True
        if tipo_proceso == "GENERADO DESDE DESPACHO" and doc_salida: valid = True
        
        if valid:
            with st.spinner("Procesando con IA y aplicando reglas de negocio..."):
                try:
                    # 1. Guardar Temporales
                    paths = []
                    path_in = None
                    path_out = None
                    
                    if doc_entrada:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                            t.write(doc_entrada.getvalue())
                            path_in = t.name
                            paths.append(t.name)
                    
                    if doc_salida:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                            t.write(doc_salida.getvalue())
                            path_out = t.name
                            paths.append(t.name)

                    # 2. Configurar Modelo
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    archivos_ia = []
                    
                    if path_in: archivos_ia.append(genai.upload_file(path_in, display_name="Entrada"))
                    if path_out: archivos_ia.append(genai.upload_file(path_out, display_name="Salida"))

                    # 3. PROMPT MAESTRO (CON TODAS LAS REGLAS DEL PUNTO 10 y 11)
                    prompt = f"""
                    Actúa como Analista Documental Policial. Extrae datos para JSON.
                    
                    VARIABLE SELECCIONADA: {tipo_proceso}
                    
                    INSTRUCCIONES DE EXTRACCIÓN:
                    1. UNIDAD ORIGEN (F7): Busca en el código del documento (Ej: PN-DIGIN-QX -> DIGIN).
                    2. CARGO DESTINATARIO (M7/U7): Mapea EXACTAMENTE así:
                       - "Jefe de la Unidad... Eficiencia..." -> UCAP
                       - "Jefe de la Unidad... Financiero..." -> UNDECOF
                       - "Jefe de la Unidad... Aduaneros..." -> UDAR
                       - "DIRECTOR GENERAL DE INVESTIGACIÓN" -> DIGIN
                       - "DIRECTOR NACIONAL... TALENTO HUMANO..." -> DNATH
                       - "Jefe de Apoyo Operativo... DINIC" -> DINIC DAOP
                       - "Jefe de Coordinación Operacional..." -> DINIC DCOP
                       - "Jefe de Soporte Operativo..." -> DINIC DSOP
                       - "Jefe de Planificación..." -> DINIC PLANF
                       - "Jefa del Financiero..." -> DINIC FINA
                       - "Analista Juridico..." -> DINIC JURID
                       *(Ignora "Subrogante" para el mapeo)*.
                    
                    3. ESTADO (S7): 
                       - Si hay 2 documentos -> "FINALIZADO"
                       - Si solo hay 1 -> "PENDIENTE" (Excepto si es Reasignado/Conocimiento/Generado que son finalizados per se).
                    
                    4. DESTINO INTERNO/EXTERNO (T7):
                       - Si va a Deptos DINIC -> "NO"
                       - Si va a Unidades/DIGIN -> "SI"

                    DEVUELVE UN JSON CON ESTOS CAMPOS (Usa "" si no encuentras):
                    {{
                        "fecha_recepcion": "DD/MM/AAAA",
                        "remitente_nombre": "Texto",
                        "remitente_cargo": "Texto",
                        "codigo_origen_completo": "PN-XYZ-QX...",
                        "doc_recepcion_numero": "Solo el código sin 'Oficio Nro'",
                        "asunto_recepcion": "Texto",
                        "resumen_ia": "Resumen ejecutivo",
                        "cargo_destinatario_mapeado": "Texto mapeado (UCAP, etc)",
                        "destinatario_nombre": "Texto",
                        "doc_respuesta_numero": "Solo el código",
                        "fecha_respuesta": "DD/MM/AAAA"
                    }}
                    """
                    
                    response = model.generate_content([prompt, *archivos_ia])
                    data = json.loads(response.text.replace("```json", "").replace("```", ""))

                    # 4. POST-PROCESAMIENTO (REGLAS DE PYTHON)
                    
                    # Regla F7 (Extracción Unidad)
                    unidad_origen = ""
                    if data["codigo_origen_completo"]:
                        parts = data["codigo_origen_completo"].split("-")
                        if len(parts) > 1: unidad_origen = parts[1] # Toma lo que está entre PN y QX

                    # Regla S7 (Estado Pendiente/Finalizado)
                    estado = "FINALIZADO"
                    if tipo_proceso == "TRAMITE NORMAL" and not doc_salida:
                        estado = "PENDIENTE"
                    
                    # Regla K7 (Usuario Turno)
                    usuario = st.session_state.usuario_turno
                    
                    # Regla L7 (Variable)
                    variable_texto = tipo_proceso if tipo_proceso != "TRAMITE NORMAL" else ""

                    # Reglas Específicas de Variables (Punto 11)
                    fecha_ref = data["fecha_recepcion"] if data["fecha_recepcion"] else data["fecha_respuesta"]
                    
                    # Inicialización de campos
                    row_data = {
                        "C": data["fecha_recepcion"], "D": data["remitente_nombre"], "E": data["remitente_cargo"],
                        "F": unidad_origen, "G": data["doc_recepcion_numero"], "H": data["fecha_recepcion"],
                        "I": data["asunto_recepcion"], "J": data["resumen_ia"], "K": usuario,
                        "L": variable_texto, 
                        "M": data["cargo_destinatario_mapeado"], "N": tipo_doc_salida, "O": data["destinatario_nombre"],
                        "P": data["doc_respuesta_numero"], "Q": data["fecha_respuesta"], 
                        "S": estado, 
                        "T": "SI" if data["cargo_destinatario_mapeado"] in ["UDAR", "UNDECOF", "UCAP", "DIGIN"] else "NO",
                        "U": data["cargo_destinatario_mapeado"], "V": data["doc_respuesta_numero"],
                        "W": data["fecha_respuesta"], "X": data["fecha_respuesta"]
                    }

                    # APLICACIÓN DE EXCEPCIONES (Punto 11)
                    if tipo_proceso == "REASIGNADO":
                        row_data["P"] = ""
                        row_data["V"] = ""
                        # Fechas de salida toman fecha de entrada
                        row_data["Q"] = fecha_ref
                        row_data["W"] = fecha_ref
                        row_data["X"] = fecha_ref

                    elif tipo_proceso == "CONOCIMIENTO":
                        # Vaciar M a X (Excepto fechas que toman la de entrada)
                        for col in ["M", "N", "O", "P", "S", "T", "U", "V"]: row_data[col] = ""
                        row_data["Q"] = fecha_ref
                        row_data["W"] = fecha_ref
                        row_data["X"] = fecha_ref
                        
                    elif tipo_proceso == "GENERADO DESDE DESPACHO":
                        row_data["D"] = "" # Remitente vacio
                        row_data["E"] = "" # Cargo vacio
                        row_data["F"] = "DINIC"
                        # Fechas entrada toman fecha salida
                        row_data["C"] = data["fecha_respuesta"]
                        row_data["H"] = data["fecha_respuesta"]

                    # AGREGAR A LA LISTA
                    st.session_state.registros.append(row_data)
                    st.success("✅ Registro Agregado")
                    
                    # Limpieza
                    for p in paths: os.remove(p)

                except Exception as e:
                    st.error(f"Error procesando: {e}")
        else:
            st.warning("Faltan documentos para el tipo de trámite seleccionado.")

    # --- D. PREVISUALIZACIÓN DE LISTA ---
    if st.session_state.registros:
        st.write("---")
        st.subheader("📋 Lista de Registros para Matriz")
        df_preview = pd.DataFrame(st.session_state.registros)
        st.dataframe(df_preview)

        # --- E. DESCARGA FINAL ---
        st.write("---")
        st.subheader("📥 Descargar Matriz Final")
        plantilla = st.file_uploader("Sube tu Matriz Vacía (.xlsx) para llenar", type=['xlsx'], key="plantilla_final")
        
        if plantilla and st.button("🚀 GENERAR ARCHIVO EXCEL"):
            try:
                wb = load_workbook(plantilla)
                # Buscar hoja CONTROL
                sheet_name = next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])
                ws = wb[sheet_name]
                
                # Encontrar inicio (Fila 7 según instrucciones)
                start_row = 7
                # Si hay datos previos, buscar la siguiente vacía
                while ws.cell(row=start_row, column=1).value is not None:
                    start_row += 1
                
                # Escribir registros
                for idx, reg in enumerate(st.session_state.registros):
                    fila = start_row + idx
                    
                    # Mapeo Directo (Columna A=1, B=2...)
                    ws.cell(row=fila, column=1, value=idx + 1)      # A: Contador
                    # B Vacia
                    ws.cell(row=fila, column=3, value=reg["C"])     # C: Fecha Rec
                    ws.cell(row=fila, column=4, value=reg["D"])     # D: Remitente
                    ws.cell(row=fila, column=5, value=reg["E"])     # E: Cargo
                    ws.cell(row=fila, column=6, value=reg["F"])     # F: Unidad
                    ws.cell(row=fila, column=7, value=reg["G"])     # G: Doc Num
                    ws.cell(row=fila, column=8, value=reg["H"])     # H: Fecha
                    ws.cell(row=fila, column=9, value=reg["I"])     # I: Asunto
                    ws.cell(row=fila, column=10, value=reg["J"])    # J: Resumen
                    ws.cell(row=fila, column=11, value=reg["K"])    # K: Usuario
                    ws.cell(row=fila, column=12, value=reg["L"])    # L: Variable
                    ws.cell(row=fila, column=13, value=reg["M"])    # M: Mapeo Cargo
                    ws.cell(row=fila, column=14, value=reg["N"])    # N: Tipo Doc
                    ws.cell(row=fila, column=15, value=reg["O"])    # O: Destinatario
                    ws.cell(row=fila, column=16, value=reg["P"])    # P: Doc Salida
                    ws.cell(row=fila, column=17, value=reg["Q"])    # Q: Fecha
                    # R Vacia
                    ws.cell(row=fila, column=19, value=reg["S"])    # S: Estado
                    ws.cell(row=fila, column=20, value=reg["T"])    # T: SI/NO
                    ws.cell(row=fila, column=21, value=reg["U"])    # U: Mapeo
                    ws.cell(row=fila, column=22, value=reg["V"])    # V: Doc Salida
                    ws.cell(row=fila, column=23, value=reg["W"])    # W: Fecha
                    ws.cell(row=fila, column=24, value=reg["X"])    # X: Fecha
                
                # Guardar
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                
                # Nombre del Archivo (Punto 4)
                fecha_str = fecha_turno.strftime("%d-%m-%y")
                nombre_archivo = f"TURNO {fecha_str} {st.session_state.usuario_turno}.xlsx".upper()
                
                st.download_button(
                    label="📥 DESCARGAR EXCEL FINAL",
                    data=output,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"Error generando excel: {e}")

else:
    st.info("Por favor configura tu API KEY en Secrets.")
