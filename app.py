import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import io
from openpyxl import load_workbook # Librería para editar Excel sin romper formato
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Integral DINIC", layout="wide", page_icon="👮‍♂️")

# --- 2. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error crítico: No se detectan credenciales en Secrets.")
    sistema_activo = False

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.title("Sistema DINIC v10.0")
    st.success("🟢 Módulo Matriz Exacta")
    
    modo = st.radio(
        "Seleccione Módulo:",
        ["🕵️‍♂️ Asesor Estratégico", "📊 Llenado de Matriz"]
    )

# ==============================================================================
# MÓDULO 1: ASESOR (El mismo cerebro de antes)
# ==============================================================================
if modo == "🕵️‍♂️ Asesor Estratégico":
    st.title("🛡️ Asesoría de Despacho")
    st.markdown("### Análisis y Redacción Táctica")
    if sistema_activo:
        uploaded_file = st.file_uploader("Sube el expediente (PDF)", type=['pdf'])
        if uploaded_file and st.button("⚖️ Analizar"):
            with st.spinner("Procesando..."):
                # (Aquí va la lógica de redacción que ya tenías aprobada)
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        path = tmp.name
                    f_up = genai.upload_file(path, display_name="Doc")
                    model = genai.GenerativeModel('gemini-flash-latest')
                    prompt = """
                    Actúa como Asesor DINIC. Analiza el documento y decide:
                    1. Flujo (Cascada/Elevación).
                    2. Redacta texto Quipux (Oficio o Memo).
                    Dame la respuesta directa para copiar.
                    """
                    res = model.generate_content([prompt, f_up])
                    st.markdown(res.text)
                    os.remove(path)
                except Exception as e:
                    st.error(f"Error: {e}")

# ==============================================================================
# MÓDULO 2: LLENADO DE MATRIZ (LÓGICA NUEVA)
# ==============================================================================
elif modo == "📊 Llenado de Matriz":
    st.title("📊 Actualizador de Matriz Institucional")
    st.markdown("### Inyección de datos en tu Formato Excel")
    st.info("Sube los documentos y TU matriz vacía. El sistema llenará la siguiente fila disponible.")

    col1, col2, col3 = st.columns(3)
    with col1:
        doc_in = st.file_uploader("1. Doc ENTRADA (PDF)", type=['pdf'], key="in")
    with col2:
        doc_out = st.file_uploader("2. Doc SALIDA (PDF)", type=['pdf'], key="out")
    with col3:
        # AQUÍ SUBES TU ARCHIVO ORIGINAL
        plantilla = st.file_uploader("3. Tu Matriz (.xlsx)", type=['xlsx'], key="xls")

    if doc_in and doc_out and plantilla and st.button("🚀 Llenar Matriz"):
        with st.spinner("Extrayendo datos e inyectándolos en tu Excel..."):
            try:
                # A. Guardar Temporales
                files_del = []
                def save_tmp(u_file):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                        t.write(u_file.getvalue())
                        files_del.append(t.name)
                        return t.name
                
                p_in = save_tmp(doc_in)
                p_out = save_tmp(doc_out)

                # B. IA Extrae Datos
                model = genai.GenerativeModel('gemini-flash-latest')
                u_in = genai.upload_file(p_in, display_name="In")
                u_out = genai.upload_file(p_out, display_name="Out")

                prompt_json = """
                Extrae los datos de estos documentos para una matriz de gestión policial.
                Devuelve SOLO un JSON con estas claves exactas:
                {
                    "fecha_ingreso": "DD/MM/AAAA",
                    "remitente": "Nombre del que firma entrada",
                    "cargo": "Cargo del que firma",
                    "entidad": "Unidad de origen",
                    "doc_entrada": "Nro de Oficio/Memo de entrada",
                    "asunto": "Resumen del asunto",
                    "doc_salida": "Nro de Oficio/Memo generado (Salida)",
                    "fecha_salida": "DD/MM/AAAA",
                    "destinatario": "A quien va dirigido el de salida",
                    "observacion": "Acción realizada (Derivado a TH, Archivo, etc)"
                }
                """
                response = model.generate_content([prompt_json, u_in, u_out])
                clean_json = response.text.replace("```json", "").replace("```", "")
                data = json.loads(clean_json)

                # C. EDICIÓN DEL EXCEL (OPENPYXL)
                # 1. Cargamos tu archivo en memoria
                wb = load_workbook(plantilla)
                
                # 2. Seleccionamos la hoja correcta
                # Buscamos la hoja que tenga "CONTROL" o usamos la primera activa
                sheet_name = next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])
                ws = wb[sheet_name]

                # 3. Encontrar la primera fila vacía (Saltando el encabezado)
                # Asumimos que el encabezado ocupa las primeras 6-7 filas según tu CSV
                start_row = 7 
                while ws.cell(row=start_row, column=3).value is not None: # Chequeamos col C (Fecha)
                    start_row += 1
                
                current_row = start_row

                # 4. Mapeo de Columnas (Según tu CSV "CONTROL DE GESTIÓN")
                # Si ves que cae en la columna equivocada, cambia el número aquí:
                
                # Columna C (3): FECHA INGRESO
                ws.cell(row=current_row, column=3, value=data["fecha_ingreso"])
                
                # Columna D (4): REMITENTE
                ws.cell(row=current_row, column=4, value=data["remitente"])
                
                # Columna E (5): CARGO
                ws.cell(row=current_row, column=5, value=data["cargo"])
                
                # Columna F (6): ENTIDAD
                ws.cell(row=current_row, column=6, value=data["entidad"])
                
                # Columna G (7): N° DOC ENTRADA
                ws.cell(row=current_row, column=7, value=data["doc_entrada"])
                
                # Columna I (9): ASUNTO
                ws.cell(row=current_row, column=9, value=data["asunto"])
                
                # --- ZONA DE SALIDA ---
                
                # Columna L (12): OBSERVACIÓN (Aprox, ajusta si es necesario)
                ws.cell(row=current_row, column=12, value=data["observacion"]) 

                # Columna R (18): N° DOC RESPUESTA
                ws.cell(row=current_row, column=18, value=data["doc_salida"]) 
                
                # Columna U (21): DESTINO
                ws.cell(row=current_row, column=21, value=data["destinatario"])
                
                # Columna W (23): FECHA SALIDA
                ws.cell(row=current_row, column=23, value=data["fecha_salida"])

                # 5. Guardar en memoria para descargar
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)

                st.success(f"✅ Matriz Actualizada en Fila {current_row}")
                st.write(f"Hoja detectada: {sheet_name}")
                
                st.download_button(
                    label="📥 Descargar Matriz Llena",
                    data=output,
                    file_name="MATRIZ_ACTUALIZADA_DINIC.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Limpieza
                for f in files_del: os.remove(f)

            except Exception as e:
                st.error(f"Error técnico: {e}")
