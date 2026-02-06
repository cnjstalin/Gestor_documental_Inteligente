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

# --- 2. GESTIÓN DE ESTADO (MEMORIA) ---
if 'registros' not in st.session_state:
    st.session_state.registros = [] # Cola de registros

if 'usuario_turno' not in st.session_state:
    st.session_state.usuario_turno = "" # Persistencia del nombre

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
    st.title("Sistema DINIC v12.1")
    
    st.markdown("### 👮‍♂️ Configuración de Turno")
    
    # PUNTO 1: CAMPO PERSISTENTE
    nombre_input = st.text_input("Grado y Nombre del Encargado:", value=st.session_state.usuario_turno)
    if nombre_input:
        st.session_state.usuario_turno = nombre_input # Guardar en memoria

    # PUNTO 4: FECHA DE TURNO
    fecha_turno = st.date_input("Fecha de Turno:", value=datetime.now())
    
    st.write("---")
    st.metric("Registros en Cola", len(st.session_state.registros))
    
    if st.button("🗑️ Borrar Lista y Empezar de Cero"):
        st.session_state.registros = []
        st.rerun()

# ==============================================================================
# LÓGICA PRINCIPAL: GESTOR DE MATRIZ INTELIGENTE
# ==============================================================================
st.title("📊 Gestor de Matriz Automatizado")
st.markdown("### Carga de Documentos y Generación de Registros")

if sistema_activo:
    # --- MENÚ DE VARIABLES (PUNTO 2 Y 11) ---
    col_config, col_docs = st.columns([1, 2])
    
    with col_config:
        st.info("1. Configuración del Trámite")
        tipo_proceso = st.selectbox(
            "Variable de Proceso (Col L):",
            ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"]
        )
        
        tipo_doc_salida = st.selectbox(
            "Tipo Documento Salida (Col N):",
            ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"]
        )

    # --- CARGA DE ARCHIVOS SEGÚN LÓGICA (PUNTO 11) ---
    with col_docs:
        st.info("2. Carga de Documentos")
        doc_entrada = None
        doc_salida = None
        
        if tipo_proceso == "TRAMITE NORMAL":
            c1, c2 = st.columns(2)
            doc_entrada = c1.file_uploader("1. Doc RECEPTADO", type=['pdf'], key="in_norm")
            doc_salida = c2.file_uploader("2. Doc RESPUESTA", type=['pdf'], key="out_norm")
            
        elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
            doc_entrada = st.file_uploader("1. Doc RECEPTADO (Único requerido)", type=['pdf'], key="in_single")
            
        elif tipo_proceso == "GENERADO DESDE DESPACHO":
            doc_salida = st.file_uploader("2. Doc GENERADO (Único requerido)", type=['pdf'], key="out_single")

    # --- BOTÓN AGREGAR A LISTA (PUNTO 3) ---
    st.write("---")
    if st.button("➕ AGREGAR A LA LISTA"):
        # Validación de subida
        listo_para_procesar = False
        if tipo_proceso == "TRAMITE NORMAL" and (doc_entrada or doc_salida): listo_para_procesar = True
        if tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"] and doc_entrada: listo_para_procesar = True
        if tipo_proceso == "GENERADO DESDE DESPACHO" and doc_salida: listo_para_procesar = True
        
        if listo_para_procesar:
            with st.spinner("Analizando documentos, extrayendo entidades y aplicando reglas..."):
                try:
                    # 1. Gestión de Temporales
                    paths = []
                    path_in, path_out = None, None
                    
                    if doc_entrada:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                            t.write(doc_entrada.getvalue())
                            path_in, _ = t.name, paths.append(t.name)
                    
                    if doc_salida:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                            t.write(doc_salida.getvalue())
                            path_out, _ = t.name, paths.append(t.name)

                    # 2. Carga a IA
                    files_ia = []
                    if path_in: files_ia.append(genai.upload_file(path_in, display_name="In"))
                    if path_out: files_ia.append(genai.upload_file(path_out, display_name="Out"))
                    
                    # --- CORRECCIÓN DEL NOMBRE DEL MODELO AQUÍ ---
                    model = genai.GenerativeModel('gemini-flash-latest') 
                    # ---------------------------------------------

                    # 3. PROMPT EXACTO PARA TUS REGLAS
                    prompt = f"""
                    Extrae datos documentales para llenar una matriz Policial en formato JSON.
                    
                    REGLAS DE EXTRACCIÓN:
                    1. **Unidad Origen (Col F):** Mira el código del documento (Ej: PN-DIGIN-QX -> DIGIN).
                    2. **Mapeo de Cargos (Col M/U):**
                       - "Jefe... Eficiencia..." -> UCAP
                       - "Jefe... Financiero..." -> UNDECOF
                       - "Jefe... Aduaneros..." -> UDAR
                       - "DIRECTOR GENERAL..." -> DIGIN
                       - "DIRECTOR... TALENTO HUMANO..." -> DNATH
                       - "Jefe Apoyo Operativo DINIC" -> DINIC DAOP
                       - "Jefe Coord Operacional DINIC" -> DINIC DCOP
                       - "Jefe Soporte Operativo DINIC" -> DINIC DSOP
                       - "Jefe Planificación DINIC" -> DINIC PLANF
                       - "Jefa Financiero DINIC" -> DINIC FINA
                       - "Analista Juridico DINIC" -> DINIC JURID
                    3. **Fechas:** Formato DD/MM/AAAA.

                    JSON REQUERIDO:
                    {{
                        "fecha_recepcion": "DD/MM/AAAA",
                        "remitente_nombre": "Texto",
                        "remitente_cargo": "Texto",
                        "codigo_documento_origen": "Texto completo PN-XYZ...",
                        "numero_oficio_entrada": "Solo numeros/letras finales",
                        "asunto_entrada": "Texto",
                        "resumen_breve": "Resumen IA",
                        "cargo_destinatario_mapeado": "Texto mapeado",
                        "destinatario_nombre": "Texto",
                        "numero_oficio_salida": "Solo numeros/letras finales",
                        "fecha_salida": "DD/MM/AAAA"
                    }}
                    """
                    
                    res = model.generate_content([prompt, *files_ia])
                    data = json.loads(res.text.replace("```json", "").replace("```", ""))
                    
                    # 4. LÓGICA DE NEGOCIO (PYTHON PURO)
                    
                    # A. Extracción Unidad (Col F)
                    unidad_f7 = ""
                    if data.get("codigo_documento_origen"):
                        parts = data["codigo_documento_origen"].split("-")
                        if len(parts) > 1: unidad_f7 = parts[1] # Toma lo del medio (DIGIN, UDAR)

                    # B. Estado (Col S)
                    estado_s7 = "PENDIENTE"
                    # Si hay 2 docs o es un trámite que finaliza en sí mismo
                    if (doc_entrada and doc_salida) or tipo_proceso in ["REASIGNADO", "CONOCIMIENTO", "GENERADO DESDE DESPACHO"]:
                        estado_s7 = "FINALIZADO"

                    # C. Texto Variable (Col L)
                    texto_l7 = tipo_proceso if tipo_proceso != "TRAMITE NORMAL" else ""

                    # D. Lógica Interno/Externo (Col T)
                    # Si va a Unidades o DIGIN es SI (Externo a la oficina), si es Deptos es NO
                    es_externo = "SI" if data["cargo_destinatario_mapeado"] in ["UDAR", "UNDECOF", "UCAP", "DIGIN", "DNATH"] else "NO"
                    
                    # E. Fechas Referencia
                    fecha_base = data["fecha_recepcion"] if data["fecha_recepcion"] else data["fecha_salida"]

                    # --- CONSTRUCCIÓN DE LA FILA (DICCIONARIO) ---
                    # Inicializamos con datos "ideales" y luego limpiamos según variable
                    row = {
                        "C": data["fecha_recepcion"], "D": data["remitente_nombre"], "E": data["remitente_cargo"],
                        "F": unidad_f7, "G": data["numero_oficio_entrada"], "H": data["fecha_recepcion"],
                        "I": data["asunto_entrada"], "J": data["resumen_breve"], 
                        "K": st.session_state.usuario_turno, # Col K (Tu nombre)
                        "L": texto_l7, # Col L (Variable)
                        "M": data["cargo_destinatario_mapeado"], "N": tipo_doc_salida, 
                        "O": data["destinatario_nombre"], "P": data["numero_oficio_salida"],
                        "Q": data["fecha_salida"], "R": "", # Col R vacía
                        "S": estado_s7, "T": es_externo, 
                        "U": data["cargo_destinatario_mapeado"], "V": data["numero_oficio_salida"],
                        "W": data["fecha_salida"], "X": data["fecha_salida"],
                        "Y": "", "Z": ""
                    }

                    # --- APLICACIÓN DE EXCEPCIONES (PUNTO 11) ---
                    
                    if tipo_proceso == "REASIGNADO":
                        # P y V vacíos
                        row["P"] = ""
                        row["V"] = ""
                        # Fechas salida = Fecha entrada
                        for col in ["Q", "W", "X"]: row[col] = fecha_base

                    elif tipo_proceso == "CONOCIMIENTO":
                        # M hasta X vacíos (EXCEPTO FECHAS Q, W, X)
                        cols_vacias = ["M", "N", "O", "P", "S", "T", "U", "V"]
                        for col in cols_vacias: row[col] = ""
                        # Fechas
                        for col in ["Q", "W", "X"]: row[col] = fecha_base

                    elif tipo_proceso == "GENERADO DESDE DESPACHO":
                        # D y E vacíos, F fijo DINIC
                        row["D"] = ""
                        row["E"] = ""
                        row["F"] = "DINIC"
                        # Fechas entrada = Fecha salida
                        row["C"] = data["fecha_salida"]
                        row["H"] = data["fecha_salida"]

                    # Agregar a Cola
                    st.session_state.registros.append(row)
                    st.success("✅ Registro agregado a la lista")
                    
                    # Limpieza
                    for p in paths: os.remove(p)

                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Sube el documento requerido para este tipo de trámite.")

    # --- VISUALIZACIÓN Y DESCARGA (PUNTO 3 Y 4) ---
    if len(st.session_state.registros) > 0:
        st.write("---")
        st.subheader("📋 Registros Listos para Matriz")
        st.dataframe(pd.DataFrame(st.session_state.registros))
        
        st.subheader("📥 Generar Excel")
        plantilla = st.file_uploader("Sube TU Matriz Formato (.xlsx)", type=['xlsx'], key="plantilla")
        
        if plantilla and st.button("🚀 DESCARGAR MATRIZ LLENA"):
            try:
                wb = load_workbook(plantilla)
                # Buscar hoja CONTROL (o usar la primera activa)
                sheet_name = next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])
                ws = wb[sheet_name]
                
                # Buscar Fila 7 o siguiente vacía
                start_row = 7
                while ws.cell(row=start_row, column=1).value is not None:
                    start_row += 1
                
                # Escribir registros
                for i, reg in enumerate(st.session_state.registros):
                    r = start_row + i
                    # Columna A (Contador)
                    ws.cell(row=r, column=1, value=i + 1)
                    # Columna B vacía
                    
                    # Mapeo según tu CSV (Columna C=3, Z=26)
                    ws.cell(row=r, column=3, value=reg["C"])
                    ws.cell(row=r, column=4, value=reg["D"])
                    ws.cell(row=r, column=5, value=reg["E"])
                    ws.cell(row=r, column=6, value=reg["F"])
                    ws.cell(row=r, column=7, value=reg["G"])
                    ws.cell(row=r, column=8, value=reg["H"])
                    ws.cell(row=r, column=9, value=reg["I"])
                    ws.cell(row=r, column=10, value=reg["J"])
                    ws.cell(row=r, column=11, value=reg["K"]) # Usuario
                    ws.cell(row=r, column=12, value=reg["L"]) # Variable
                    ws.cell(row=r, column=13, value=reg["M"])
                    ws.cell(row=r, column=14, value=reg["N"])
                    ws.cell(row=r, column=15, value=reg["O"])
                    ws.cell(row=r, column=16, value=reg["P"])
                    ws.cell(row=r, column=17, value=reg["Q"])
                    # R vacía
                    ws.cell(row=r, column=19, value=reg["S"]) # Estado
                    ws.cell(row=r, column=20, value=reg["T"]) # SI/NO
                    ws.cell(row=r, column=21, value=reg["U"])
                    ws.cell(row=r, column=22, value=reg["V"])
                    ws.cell(row=r, column=23, value=reg["W"])
                    ws.cell(row=r, column=24, value=reg["X"])
                
                # Guardar en memoria
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                
                # Nombre del Archivo (Punto 4)
                f_str = fecha_turno.strftime("%d-%m-%y")
                u_str = st.session_state.usuario_turno.upper()
                fname = f"TURNO {f_str} {u_str}.xlsx"
                
                st.download_button("📥 DESCARGAR EXCEL", data=output, file_name=fname)
                
            except Exception as e:
                st.error(f"Error generando Excel: {e}")
