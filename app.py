import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import io
import re
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(
    page_title="S.I.G.D. DINIC",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        background-color: #0E2F44;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #D4AF37;
    }
    .main-header h1 { color: white; margin: 0; font-family: 'Arial Black', sans-serif; }
    .main-header h3 { color: #f0f0f0; margin: 0; font-weight: normal; }
    div.stButton > button { width: 100%; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE ESTADO ---
if 'registros' not in st.session_state: st.session_state.registros = [] 
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = "" 

# --- 3. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error crítico: No se detectan credenciales en Secrets.")
    sistema_activo = False

# --- 4. FUNCIONES DE LIMPIEZA ---
def limpiar_codigo(texto):
    """Deja solo el código PN-... eliminando 'Oficio Nro.', etc."""
    if not texto: return ""
    match = re.search(r"(PN-.*)", str(texto))
    if match:
        return match.group(1).strip()
    return str(texto).replace("Oficio Nro.", "").replace("Memorando Nro.", "").replace("Circular Nro.", "").strip()

def extraer_unidad_exacta(codigo_completo):
    """Extrae lo que está entre 'PN-' y '-QX'."""
    if not codigo_completo: return ""
    match = re.search(r"PN-(.*?)-QX", str(codigo_completo))
    if match:
        return match.group(1)
    return "DINIC" 

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown("### 👮‍♂️ PANEL DE CONTROL")
    
    st.caption("DATOS DE TURNO")
    nombre_input = st.text_input("Grado y Nombre:", value=st.session_state.usuario_turno)
    if nombre_input: st.session_state.usuario_turno = nombre_input

    fecha_turno = st.date_input("Fecha Operación:", value=datetime.now())
    
    st.markdown("---")
    st.caption("CONFIGURACIÓN MATRIZ")
    RUTA_MATRIZ = "matriz_maestra.xlsx"
    
    if os.path.exists(RUTA_MATRIZ):
        st.success("✅ Matriz Base Cargada")
        if st.button("🔄 Actualizar Matriz Base"):
            os.remove(RUTA_MATRIZ)
            st.rerun()
    else:
        uploaded_template = st.file_uploader("Sube Matriz Formato (.xlsx)", type=['xlsx'])
        if uploaded_template:
            with open(RUTA_MATRIZ, "wb") as f:
                f.write(uploaded_template.getbuffer())
            st.rerun()

    st.markdown("---")
    st.metric("Expedientes en Cola", len(st.session_state.registros))
    if st.button("🗑️ Limpiar Cola"):
        st.session_state.registros = []
        st.rerun()

# ==============================================================================
# ÁREA PRINCIPAL
# ==============================================================================
st.markdown("""
    <div class="main-header">
        <h1>S.I.G.D. - DINIC</h1>
        <h3>Sistema de Gestión Documental Inteligente</h3>
    </div>
""", unsafe_allow_html=True)

if sistema_activo:
    tab1, tab2 = st.tabs(["📊 GESTOR DE MATRIZ", "🕵️‍♂️ ASESOR ESTRATÉGICO"])

    # --- PESTAÑA 1: GESTOR DE MATRIZ ---
    with tab1:
        st.markdown("#### 📥 Procesamiento de Documentación")
        col_vars, col_uploads = st.columns([1, 2])
        
        with col_vars:
            st.info("1. Configuración")
            tipo_proceso = st.selectbox("Tipo Gestión:", ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"])
            tipo_doc_salida = st.selectbox("Formato Salida:", ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"])

        with col_uploads:
            st.info("2. Expediente Digital")
            doc_entrada = None
            doc_salida = None
            
            if tipo_proceso == "TRAMITE NORMAL":
                c1, c2 = st.columns(2)
                doc_entrada = c1.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_n")
                doc_salida = c2.file_uploader("2. Doc RESPUESTA", type=['pdf'], key="out_n")
            elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
                doc_entrada = st.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_s")
            elif tipo_proceso == "GENERADO DESDE DESPACHO":
                doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_s")

        st.write("---")
        if st.button("⚡ PROCESAR Y AGREGAR", type="primary"):
            if not os.path.exists(RUTA_MATRIZ):
                st.error("❌ Falta cargar la Matriz Base en el menú lateral.")
            else:
                listo = False
                if tipo_proceso == "TRAMITE NORMAL" and (doc_entrada or doc_salida): listo = True
                if tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"] and doc_entrada: listo = True
                if tipo_proceso == "GENERADO DESDE DESPACHO" and doc_salida: listo = True
                
                if listo:
                    with st.spinner("🤖 Analizando Grados, Nombres y Unidades..."):
                        try:
                            # 1. Temporales
                            paths = []
                            path_in, path_out = None, None
                            if doc_entrada:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                    t.write(doc_entrada.getvalue()); path_in = t.name; paths.append(t.name)
                            if doc_salida:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                                    t.write(doc_salida.getvalue()); path_out = t.name; paths.append(t.name)

                            # 2. IA Config
                            files_ia = []
                            if path_in: files_ia.append(genai.upload_file(path_in, display_name="In"))
                            if path_out: files_ia.append(genai.upload_file(path_out, display_name="Out"))
                            
                            model = genai.GenerativeModel('gemini-flash-latest')

                            # 3. PROMPT ACTUALIZADO (GRADOS EXACTOS)
                            prompt = f"""
                            Extrae datos exactos para Matriz Policial en JSON.
                            
                            INSTRUCCIONES DE EXTRACCIÓN:
                            1. **NOMBRES (CRÍTICO):** Extrae SIEMPRE "GRADO + NOMBRE COMPLETO".
                               - Correcto: "GraD. Willian Roberth Villarroel Trujillo"
                               - Correcto: "Sbte. Denisse Katherine Analuisa Acosta"
                               - Incorrecto: "Willian Villarroel" (Falta grado y segundo nombre).
                            
                            2. **CÓDIGOS:** Extrae el código completo (Ej: PN-DIGIN-QX...).
                            
                            3. **MAPEO CARGOS:**
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
                            
                            JSON ESPERADO:
                            {{
                                "fecha_recepcion": "DD/MM/AAAA",
                                "remitente_grado_nombre": "Grado y Nombre Completo",
                                "remitente_cargo": "Texto",
                                "codigo_completo_entrada": "Texto",
                                "asunto_entrada": "Texto",
                                "resumen_breve": "Texto",
                                "cargo_destinatario_mapeado": "Texto",
                                "destinatario_grado_nombre": "Grado y Nombre Completo",
                                "codigo_completo_salida": "Texto",
                                "fecha_salida": "DD/MM/AAAA"
                            }}
                            """
                            res = model.generate_content([prompt, *files_ia])
                            data = json.loads(res.text.replace("```json", "").replace("```", ""))

                            # 4. LÓGICA PYTHON
                            
                            # Códigos limpios
                            cod_in = limpiar_codigo(data.get("codigo_completo_entrada", ""))
                            cod_out = limpiar_codigo(data.get("codigo_completo_salida", ""))

                            # Unidad F7 (Lógica PN-...-QX)
                            unidad_f7 = extraer_unidad_exacta(data.get("codigo_completo_entrada", ""))

                            # Estado S7
                            estado_s7 = "PENDIENTE"
                            if (doc_entrada and doc_salida) or tipo_proceso != "TRAMITE NORMAL":
                                estado_s7 = "FINALIZADO"

                            # Variables
                            texto_l7 = tipo_proceso if tipo_proceso != "TRAMITE NORMAL" else ""
                            es_externo = "SI" if data["cargo_destinatario_mapeado"] in ["UDAR", "UNDECOF", "UCAP", "DIGIN", "DNATH"] else "NO"
                            fecha_base = data["fecha_recepcion"] if data["fecha_recepcion"] else data["fecha_salida"]

                            # Construcción Fila
                            row = {
                                "C": data["fecha_recepcion"], 
                                "D": data["remitente_grado_nombre"], # NOMBRE CON GRADO
                                "E": data["remitente_cargo"],
                                "F": unidad_f7, 
                                "G": cod_in, 
                                "H": data["fecha_recepcion"],
                                "I": data["asunto_entrada"], 
                                "J": data["resumen_breve"], 
                                "K": st.session_state.usuario_turno, 
                                "L": texto_l7, 
                                "M": data["cargo_destinatario_mapeado"], 
                                "N": tipo_doc_salida, 
                                "O": data["destinatario_grado_nombre"], # NOMBRE CON GRADO
                                "P": cod_out,
                                "Q": data["fecha_salida"], "R": "", 
                                "S": estado_s7, "T": es_externo, 
                                "U": data["cargo_destinatario_mapeado"], 
                                "V": cod_out,
                                "W": data["fecha_salida"], "X": data["fecha_salida"]
                            }

                            # EXCEPCIONES DE NEGOCIO
                            if tipo_proceso == "GENERADO DESDE DESPACHO":
                                row["D"] = ""; row["E"] = ""; row["F"] = "DINIC"
                                row["C"] = data["fecha_salida"]; row["H"] = data["fecha_salida"]
                                row["S"] = "FINALIZADO"
                            elif tipo_proceso == "REASIGNADO":
                                row["P"] = ""; row["V"] = ""
                                for c in ["Q", "W", "X"]: row[c] = fecha_base
                            elif tipo_proceso == "CONOCIMIENTO":
                                for c in ["M", "N", "O", "P", "S", "T", "U", "V"]: row[c] = ""
                                for c in ["Q", "W", "X"]: row[c] = fecha_base

                            st.session_state.registros.append(row)
                            st.success(f"✅ Registro Agregado: {cod_in}")
                            for p in paths: os.remove(p)

                        except Exception as e:
                            st.error(f"Error Técnico: {e}")

        # TABLA Y DESCARGA
        if st.session_state.registros:
            st.markdown("#### 📋 Expedientes Listos")
            st.dataframe(pd.DataFrame(st.session_state.registros))
            
            if os.path.exists(RUTA_MATRIZ):
                if st.button("📥 DESCARGAR EXCEL (FORMATO PROTEGIDO)"):
                    try:
                        wb = load_workbook(RUTA_MATRIZ)
                        sheet_name = next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])
                        ws = wb[sheet_name]
                        
                        start_row = 7
                        while ws.cell(row=start_row, column=1).value is not None:
                            start_row += 1
                        
                        # Colores Semáforo
                        green_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
                        red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

                        for i, reg in enumerate(st.session_state.registros):
                            r = start_row + i
                            
                            def w(c, v): ws.cell(row=r, column=c).value = v
                            
                            w(1, i + 1)
                            w(3, reg["C"]); w(4, reg["D"]); w(5, reg["E"])
                            w(6, reg["F"]); w(7, reg["G"]); w(8, reg["H"])
                            w(9, reg["I"]); w(10, reg["J"]); w(11, reg["K"])
                            w(12, reg["L"]); w(13, reg["M"]); w(14, reg["N"])
                            w(15, reg["O"]); w(16, reg["P"]); w(17, reg["Q"])
                            
                            # Semáforo S7
                            cell_s = ws.cell(row=r, column=19)
                            cell_s.value = reg["S"]
                            if reg["S"] == "FINALIZADO": cell_s.fill = green_fill
                            elif reg["S"] == "PENDIENTE": cell_s.fill = red_fill
                            
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
                        st.error(f"Error Generando Excel: {e}")

    # --- PESTAÑA 2: ASESOR ---
    with tab2:
        st.info("🧠 Asistente de Redacción")
        up_asesor = st.file_uploader("Sube documento (PDF)", type=['pdf'])
        if up_asesor and st.button("ANALIZAR DOCUMENTO"):
            with st.spinner("Generando estrategia..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                        t.write(up_asesor.getvalue()); p_as = t.name
                    f_as = genai.upload_file(p_as, display_name="Consulta")
                    model = genai.GenerativeModel('gemini-flash-latest')
                    prompt = "Actúa como Ayudantía DINIC. Analiza PDF. 1. Diagnóstico. 2. Decisión (Digin/Unidad). 3. Borrador Quipux."
                    res = model.generate_content([prompt, f_as])
                    st.markdown(res.text)
                    os.remove(p_as)
                except Exception as e: st.error(e)
