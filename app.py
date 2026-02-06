import streamlit as st
import google.generativeai as genai
import tempfile
import os
import json
import io
import re
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL ---
st.set_page_config(
    page_title="S.I.G.D. DINIC",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (PARA QUE PAREZCA UN SISTEMA REAL) ---
st.markdown("""
    <style>
    /* Encabezado Institucional */
    .main-header {
        background-color: #0E2F44; /* Azul Policial */
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #D4AF37; /* Dorado */
    }
    .main-header h1 {
        color: white;
        font-family: 'Arial Black', sans-serif;
        margin: 0;
    }
    .main-header h3 {
        color: #f0f0f0;
        margin: 0;
        font-weight: normal;
    }
    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
    }
    /* Botones */
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE ESTADO (MEMORIA) ---
if 'registros' not in st.session_state:
    st.session_state.registros = [] 

if 'usuario_turno' not in st.session_state:
    st.session_state.usuario_turno = "" 

# --- 3. AUTENTICACIÓN ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    sistema_activo = True
except Exception:
    st.error("⚠️ Error crítico: No se detectan credenciales en Secrets.")
    sistema_activo = False

# --- 4. BARRA LATERAL (PANEL DE CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=80)
    st.markdown("### 👮‍♂️ PANEL DE MANDO")
    
    # Configuración de Usuario
    st.markdown("---")
    st.caption("DATOS DEL RESPONSABLE")
    nombre_input = st.text_input("Grado y Nombre:", value=st.session_state.usuario_turno, placeholder="Ej: Cbos. John Carrillo")
    if nombre_input:
        st.session_state.usuario_turno = nombre_input

    fecha_turno = st.date_input("Fecha de Operación:", value=datetime.now())
    
    st.markdown("---")
    
    # Gestión de la Matriz Maestra (PERSISTENCIA)
    st.caption("CONFIGURACIÓN DEL SISTEMA")
    RUTA_MATRIZ_MAESTRA = "matriz_maestra.xlsx"
    
    if os.path.exists(RUTA_MATRIZ_MAESTRA):
        st.success("✅ Matriz Maestra Cargada")
        if st.button("🔄 Cambiar Matriz Base"):
            os.remove(RUTA_MATRIZ_MAESTRA)
            st.rerun()
    else:
        st.warning("⚠️ Sistema sin Matriz Base")
        uploaded_template = st.file_uploader("Sube la Matriz Formato (.xlsx)", type=['xlsx'])
        if uploaded_template:
            with open(RUTA_MATRIZ_MAESTRA, "wb") as f:
                f.write(uploaded_template.getbuffer())
            st.success("Matriz guardada en el sistema.")
            st.rerun()

    st.markdown("---")
    st.metric("Expedientes en Cola", len(st.session_state.registros))
    if st.button("🗑️ Limpiar Cola"):
        st.session_state.registros = []
        st.rerun()

# ==============================================================================
# ÁREA PRINCIPAL
# ==============================================================================

# Encabezado Visual
st.markdown("""
    <div class="main-header">
        <h1>S.I.G.D. - DINIC</h1>
        <h3>Sistema Inteligente de Gestión Documental</h3>
    </div>
""", unsafe_allow_html=True)

if sistema_activo:
    # NAVEGACIÓN POR PESTAÑAS
    tab1, tab2 = st.tabs(["📊 GESTOR DE MATRIZ (ERP)", "🕵️‍♂️ ASESOR ESTRATÉGICO (IA)"])

    # ==========================================================================
    # PESTAÑA 1: GESTOR DE MATRIZ (REGISTRO AUTOMÁTICO)
    # ==========================================================================
    with tab1:
        st.markdown("#### 📥 Ingreso y Procesamiento de Documentación")
        
        # 1. Configuración del Trámite
        col_vars, col_uploads = st.columns([1, 2])
        
        with col_vars:
            st.info("⚙️ Parámetros del Trámite")
            tipo_proceso = st.selectbox(
                "Tipo de Gestión:",
                ["TRAMITE NORMAL", "REASIGNADO", "GENERADO DESDE DESPACHO", "CONOCIMIENTO"]
            )
            
            tipo_doc_salida = st.selectbox(
                "Formato de Salida:",
                ["QUIPUX ELECTRONICO", "DOCPOL ELECTRONICO", "FISICO", "DIGITAL", "OTRO"]
            )

        # 2. Carga de Documentos
        with col_uploads:
            st.info("📂 Expediente Digital")
            doc_entrada = None
            doc_salida = None
            
            if tipo_proceso == "TRAMITE NORMAL":
                c1, c2 = st.columns(2)
                doc_entrada = c1.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_norm")
                doc_salida = c2.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_norm")
            elif tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"]:
                doc_entrada = st.file_uploader("1. Doc RECIBIDO", type=['pdf'], key="in_single")
            elif tipo_proceso == "GENERADO DESDE DESPACHO":
                doc_salida = st.file_uploader("2. Doc GENERADO", type=['pdf'], key="out_single")

        # 3. Botón de Procesamiento
        st.write("---")
        if st.button("⚡ PROCESAR Y AGREGAR A MATRIZ", type="primary"):
            # Validaciones
            if not os.path.exists(RUTA_MATRIZ_MAESTRA):
                st.error("❌ Primero debes subir la Matriz Formato en la Barra Lateral.")
            else:
                listo = False
                if tipo_proceso == "TRAMITE NORMAL" and (doc_entrada or doc_salida): listo = True
                if tipo_proceso in ["REASIGNADO", "CONOCIMIENTO"] and doc_entrada: listo = True
                if tipo_proceso == "GENERADO DESDE DESPACHO" and doc_salida: listo = True
                
                if listo:
                    with st.spinner("🤖 La IA está leyendo el documento y protegiendo el formato Excel..."):
                        try:
                            # -- PROCESAMIENTO IA --
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

                            files_ia = []
                            if path_in: files_ia.append(genai.upload_file(path_in, display_name="In"))
                            if path_out: files_ia.append(genai.upload_file(path_out, display_name="Out"))
                            
                            model = genai.GenerativeModel('gemini-flash-latest')

                            prompt = f"""
                            Extrae datos para Matriz Policial en JSON.
                            
                            REGLAS CRÍTICAS:
                            1. **Código Origen:** Extrae COMPLETO (Ej: Oficio Nro. PN-DIGIN-QX-2025-001-OF).
                            2. **Unidad:** Solo extrae las siglas.
                            3. **Mapeo de Cargos (Col M/U):**
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
                                "remitente_nombre": "Texto",
                                "remitente_cargo": "Texto",
                                "codigo_completo_entrada": "Texto",
                                "numero_solo_entrada": "Texto",
                                "asunto_entrada": "Texto",
                                "resumen_breve": "Texto",
                                "cargo_destinatario_mapeado": "Texto",
                                "destinatario_nombre": "Texto",
                                "numero_solo_salida": "Texto",
                                "fecha_salida": "DD/MM/AAAA"
                            }}
                            """
                            res = model.generate_content([prompt, *files_ia])
                            data = json.loads(res.text.replace("```json", "").replace("```", ""))

                            # -- LÓGICA DE NEGOCIO --
                            
                            # Unidad (F7)
                            unidad_f7 = ""
                            if data.get("codigo_completo_entrada"):
                                match = re.search(r"PN-([A-Z0-9]+)-", data["codigo_completo_entrada"])
                                if match: unidad_f7 = match.group(1)
                                else:
                                    parts = data["codigo_completo_entrada"].replace("Oficio Nro. ", "").split("-")
                                    if len(parts) > 1: unidad_f7 = parts[1]

                            # Estado (S7)
                            estado_s7 = "PENDIENTE"
                            if (doc_entrada and doc_salida) or tipo_proceso != "TRAMITE NORMAL":
                                estado_s7 = "FINALIZADO"

                            # Variable (L7)
                            texto_l7 = tipo_proceso if tipo_proceso != "TRAMITE NORMAL" else ""

                            # Externo (T7)
                            es_externo = "SI" if data["cargo_destinatario_mapeado"] in ["UDAR", "UNDECOF", "UCAP", "DIGIN", "DNATH"] else "NO"

                            # Fechas
                            fecha_base = data["fecha_recepcion"] if data["fecha_recepcion"] else data["fecha_salida"]

                            # Construcción Fila
                            row = {
                                "C": data["fecha_recepcion"], "D": data["remitente_nombre"], "E": data["remitente_cargo"],
                                "F": unidad_f7, "G": data["numero_solo_entrada"], "H": data["fecha_recepcion"],
                                "I": data["asunto_entrada"], "J": data["resumen_breve"], 
                                "K": st.session_state.usuario_turno, "L": texto_l7, 
                                "M": data["cargo_destinatario_mapeado"], "N": tipo_doc_salida, 
                                "O": data["destinatario_nombre"], "P": data["numero_solo_salida"],
                                "Q": data["fecha_salida"], "R": "", 
                                "S": estado_s7, "T": es_externo, 
                                "U": data["cargo_destinatario_mapeado"], "V": data["numero_solo_salida"],
                                "W": data["fecha_salida"], "X": data["fecha_salida"]
                            }

                            # EXCEPCIONES
                            if tipo_proceso == "GENERADO DESDE DESPACHO":
                                row["D"] = ""
                                row["E"] = ""
                                row["F"] = "DINIC" # FORCE DINIC
                                row["C"] = data["fecha_salida"]
                                row["H"] = data["fecha_salida"]
                                row["S"] = "FINALIZADO"

                            elif tipo_proceso == "REASIGNADO":
                                row["P"] = ""
                                row["V"] = ""
                                for col in ["Q", "W", "X"]: row[col] = fecha_base

                            elif tipo_proceso == "CONOCIMIENTO":
                                for col in ["M", "N", "O", "P", "S", "T", "U", "V"]: row[col] = ""
                                for col in ["Q", "W", "X"]: row[col] = fecha_base

                            st.session_state.registros.append(row)
                            st.success(f"✅ Documento '{data.get('numero_solo_entrada') or 'GENERADO'}' agregado a la cola.")
                            
                            for p in paths: os.remove(p)

                        except Exception as e:
                            st.error(f"Error Técnico: {e}")
                else:
                    st.warning("⚠️ Faltan documentos para el trámite seleccionado.")

        # 4. Tabla y Descarga
        if st.session_state.registros:
            st.markdown("#### 📋 Expedientes Listos")
            st.dataframe(pd.DataFrame(st.session_state.registros))
            
            if os.path.exists(RUTA_MATRIZ_MAESTRA):
                if st.button("📥 DESCARGAR EXCEL FINAL (CON FORMATO)", type="secondary"):
                    try:
                        wb = load_workbook(RUTA_MATRIZ_MAESTRA)
                        sheet_name = next((s for s in wb.sheetnames if "CONTROL" in s.upper()), wb.sheetnames[0])
                        ws = wb[sheet_name]
                        
                        start_row = 7
                        while ws.cell(row=start_row, column=1).value is not None:
                            start_row += 1
                        
                        for i, reg in enumerate(st.session_state.registros):
                            r = start_row + i
                            # FUNCIÓN DE ESCRITURA SEGURA (SOLO VALORES)
                            def w(c, v): 
                                ws.cell(row=r, column=c).value = v
                            
                            w(1, i + 1)
                            w(3, reg["C"]); w(4, reg["D"]); w(5, reg["E"])
                            w(6, reg["F"]); w(7, reg["G"]); w(8, reg["H"])
                            w(9, reg["I"]); w(10, reg["J"]); w(11, reg["K"])
                            w(12, reg["L"]); w(13, reg["M"]); w(14, reg["N"])
                            w(15, reg["O"]); w(16, reg["P"]); w(17, reg["Q"])
                            w(19, reg["S"]); w(20, reg["T"]); w(21, reg["U"])
                            w(22, reg["V"]); w(23, reg["W"]); w(24, reg["X"])

                        output = io.BytesIO()
                        wb.save(output)
                        output.seek(0)
                        
                        f_str = fecha_turno.strftime("%d-%m-%y")
                        u_str = st.session_state.usuario_turno.upper()
                        fname = f"TURNO {f_str} {u_str}.xlsx"
                        
                        st.download_button("💾 Guardar Archivo", data=output, file_name=fname, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        
                    except Exception as e:
                        st.error(f"Error al generar archivo: {e}")
            else:
                st.error("Falta Matriz Base.")

    # ==========================================================================
    # PESTAÑA 2: ASESOR ESTRATÉGICO (EL CEREBRO IA)
    # ==========================================================================
    with tab2:
        st.markdown("#### ⚖️ Consulta Táctica y Redacción de Documentos")
        st.caption("Sube un PDF para recibir orientación sobre jerarquía y borradores de respuesta.")
        
        uploaded_asesor = st.file_uploader("Sube el documento a analizar (PDF)", type=['pdf'], key="asesor_up")
        
        if uploaded_asesor and st.button("🧠 ANALIZAR SITUACIÓN"):
            with st.spinner("El Estado Mayor Digital está analizando..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
                        t.write(uploaded_asesor.getvalue())
                        path_asesor = t.name
                    
                    file_asesor = genai.upload_file(path_asesor, display_name="Consulta")
                    model = genai.GenerativeModel('gemini-flash-latest')
                    
                    prompt_asesor = """
                    Actúa como JEFE DE AYUDANTÍA DINIC.
                    Analiza el PDF y genera:
                    1. DIAGNÓSTICO: ¿Qué piden? ¿Quién lo pide? (DIGIN vs Unidades).
                    2. DECISIÓN: ¿Elevamos a DIGIN (Oficio) o disponemos a Unidades (Memo)? ¿Por qué?
                    3. REDACCIÓN: El borrador exacto para Quipux.
                    
                    Usa formato Markdown elegante.
                    """
                    
                    res_asesor = model.generate_content([prompt_asesor, file_asesor])
                    st.markdown(res_asesor.text)
                    
                    os.remove(path_asesor)
                except Exception as e:
                    st.error(f"Error en Asesoría: {e}")
