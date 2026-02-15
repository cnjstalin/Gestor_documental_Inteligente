import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==============================================================================
# 1. CONFIGURACIÓN INMERSIVA (FULL SCREEN)
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC | Plataforma Central",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed" # Ocultamos la barra lateral por defecto
)

# ==============================================================================
# 2. ESTILOS CSS AVANZADOS (EL EFECTO "PÁGINA WEB")
# ==============================================================================
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit para look "Web Propia" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;} /* Oculta la flecha del sidebar */
    
    /* Eliminar márgenes excesivos para usar toda la pantalla */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    /* ESTILOS DEL DASHBOARD (MENÚ PRINCIPAL) */
    .dashboard-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        padding: 50px 20px;
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); /* Fondo elegante */
        min-height: 100vh;
        color: white;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #cfd8dc;
        margin-bottom: 50px;
        font-weight: 300;
    }

    /* TARJETAS DE MÓDULOS */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 30px;
        width: 100%;
        max-width: 1200px;
    }

    .card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        border-color: #fff;
    }

    .card-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        display: block;
    }

    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: white;
    }

    .card-desc {
        font-size: 0.9rem;
        color: #b0bec5;
    }
    
    /* BOTÓN DE RETORNO (Flotante) */
    .btn-home {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #0E2F44;
        color: white;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        z-index: 9999;
        font-weight: bold;
        border: 2px solid #D4AF37;
        cursor: pointer;
    }
    .btn-home:hover {
        background-color: #1a4f70;
    }

    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HTML DEL MOTOR V44 (OPTIMIZADO PARA INTEGRACIÓN PERFECTA)
# ==============================================================================
HTML_SECRETARIO_V44 = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GESTOR DOCUMENTAL DINIC</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <style>
        /* Ajuste para que parezca nativo: Fondo blanco y padding superior controlado */
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f7fa; padding: 20px; color: #333; padding-top: 100px; padding-bottom: 60px; margin: 0; }
        
        /* Contenedor fluido para aprovechar ancho completo */
        .container { width: 95%; max-width: 1600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
        
        /* HEADER FIJO ESTILIZADO */
        .top-header { position: fixed; top: 0; left: 0; width: 100%; background: #0E2F44; color: white; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        .bar-main { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .bar-tools { background: #0a2333; padding: 10px 30px; display: flex; gap: 15px; align-items: center; justify-content: flex-end; flex-wrap: wrap; }

        /* LED */
        .led-box { font-size: 12px; display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); }
        .led { width: 10px; height: 10px; border-radius: 50%; background: #f44336; box-shadow: 0 0 8px #f44336; transition: 0.3s; }
        .led.on { background: #00e676; box-shadow: 0 0 8px #00e676; }

        /* BOTONES TOP */
        .btn-top { border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 11px; text-transform: uppercase; transition: 0.2s; letter-spacing: 0.5px; }
        .btn-cfg { background: #3949ab; color: white; }
        .btn-save { background: #00acc1; color: white; }
        .btn-rest { background: #ffb300; color: #333; }
        .btn-new { background: #43a047; color: white; }
        .btn-wipe { background: #c62828; color: white; margin-left: 15px; }
        .btn-top:hover { filter: brightness(1.15); transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.2); }

        /* BARRA DE MODOS */
        .mode-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
        .mode-btn { padding: 15px; border-radius: 8px; cursor: pointer; text-align: center; font-weight: bold; border: 2px solid transparent; transition: 0.3s; opacity: 0.8; font-size: 14px; }
        .mode-btn:hover { opacity: 1; transform: translateY(-2px); }
        .mode-copy { background: #fff8e1; color: #ff6f00; border-color: #ffecb3; }
        .mode-copy.active { background: #ffecb3; border-color: #ff6f00; opacity: 1; box-shadow: 0 4px 10px rgba(255, 111, 0, 0.2); }
        .mode-gen { background: #e0f7fa; color: #006064; border-color: #b2ebf2; }
        .mode-gen.active { background: #b2ebf2; border-color: #006064; opacity: 1; box-shadow: 0 4px 10px rgba(0, 96, 100, 0.2); }

        /* SECCIONES Y FORMULARIOS */
        .seccion { background: #fafafa; border: 1px solid #e0e0e0; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .seccion h3 { margin: 0 0 15px 0; font-size: 15px; color: #455a64; border-left: 5px solid #0E2F44; padding-left: 10px; text-transform: uppercase; }
        
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        .full { grid-column: 1 / -1; }

        label { display: block; font-weight: 700; font-size: 11px; color: #546e7a; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #cfd8dc; border-radius: 6px; font-size: 13px; box-sizing: border-box; transition: 0.2s; background: #fff; }
        input:focus, select:focus, textarea:focus { border-color: #0E2F44; outline: none; box-shadow: 0 0 0 3px rgba(14, 47, 68, 0.1); }
        
        /* ARCHIVOS MEJORADOS */
        .drop-area { border: 2px dashed #b0bec5; padding: 20px; text-align: center; border-radius: 8px; cursor: pointer; background: #fcfcfc; transition: 0.2s; margin-bottom: 5px; }
        .drop-area:hover { border-color: #0E2F44; background: #eceff1; }
        .drop-txt { font-weight: bold; color: #0E2F44; font-size: 12px; pointer-events: none; }
        
        .file-list-box { max-height: 150px; overflow-y: auto; border: 1px solid #eceff1; padding: 5px; background: #fff; border-radius: 6px; }
        .file-item { display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-bottom: 4px; background: #f5f5f5; padding: 6px 10px; border-radius: 4px; }
        
        /* TABLA MODERNA */
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 15px; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0; }
        thead { background: #0E2F44; color: white; }
        th { padding: 12px 15px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        td { padding: 10px 15px; border-bottom: 1px solid #f0f0f0; font-size: 12px; background: white; }
        tr:last-child td { border-bottom: none; }
        
        .row-grey td { color: #555; }
        .row-pend td { background: #ffebee !important; color: #c62828; font-weight: 500; }
        .row-ok td { background: #e8f5e9 !important; color: #2e7d32; font-weight: 500; }

        /* FOOTER */
        .footer { text-align: center; margin-top: 40px; font-size: 11px; color: #90a4ae; border-top: 1px solid #eee; padding-top: 20px; }
        
        /* BOTONES GRANDES */
        .btn-main { display: block; width: 100%; padding: 15px; font-size: 14px; font-weight: 800; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 25px 0; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.2s; }
        .btn-add { background: linear-gradient(to right, #2e7d32, #43a047); }
        .btn-add:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(46, 125, 50, 0.3); }
        .btn-down { background: linear-gradient(to right, #0E2F44, #1a4f70); }
        
    </style>
</head>
<body>
    <div id="loader" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(255,255,255,0.9); z-index:2000; display:flex; justify-content:center; align-items:center; flex-direction:column;">
        <div style="font-size:50px;">🛡️</div>
        <h3 id="loadText" style="color:#0E2F44; margin-top:10px;">Procesando...</h3>
    </div>

    <div class="top-header">
        <div class="bar-main">
            <div style="font-size:18px; font-weight:800; letter-spacing:1px;">🛡️ SIGD DINIC | SECRETARÍA</div>
            <div class="led-box">
                <span id="led" class="led"></span>
                <span id="ledTxt">Verificando plantilla...</span>
            </div>
        </div>
        <div class="bar-tools">
            <button class="btn-top btn-cfg" onclick="triggerUpload()">📂 Plantilla Excel</button>
            <input type="file" id="inPlantilla" accept=".xlsx" style="display:none" onchange="guardarPlantillaDB(this)">
            
            <button class="btn-top btn-save" onclick="guardarRespaldo()">⬇️ Respaldar Turno</button>
            <button class="btn-top btn-rest" onclick="document.getElementById('inRestore').click()">⬆️ Restaurar</button>
            <input type="file" id="inRestore" accept=".dinic" style="display:none" onchange="restaurarRespaldo(this)">
            
            <span style="border-left:1px solid rgba(255,255,255,0.2); height:20px; margin:0 5px;"></span>
            
            <button class="btn-top btn-new" onclick="nuevoTurno()">✨ Nuevo</button>
            <button class="btn-top btn-wipe" onclick="borrarTodo()">🗑️ Reset</button>
        </div>
    </div>

    <div class="container">
        <div class="mode-bar">
            <div id="btnModeCopia" class="mode-btn mode-copy" onclick="toggleMode('COPIA')">
                ⚠️ ¿EL DOCUMENTO ES UNA COPIA?
                <br><span style="font-size:10px;">(Click para activar)</span>
            </div>
            <div id="btnModeGen" class="mode-btn mode-gen" onclick="toggleMode('GENERADO')">
                ⚙️ ¿GENERADO DESDE DESPACHO?
                <br><span style="font-size:10px;">(Click para activar)</span>
            </div>
        </div>

        <div id="secCopia" style="display:none; background:#fff3e0; padding:20px; border-radius:8px; margin-bottom:20px; border:1px solid #ffb74d;">
            <div class="grid-3">
                <div class="full"><label>N° Documento Copia:</label><input type="text" id="cNum" oninput="cleanPNSync(this)"></div>
                <div class="full">
                    <label>📂 ANEXOS COPIA:</label>
                    <div class="drop-area" id="drop_copy" onclick="document.getElementById('cFile').click()">
                        <div class="drop-txt">Arrastra archivos aquí o haz click</div>
                        <input type="file" id="cFile" multiple style="display:none" onchange="handleFiles(this.files, 'copy')">
                    </div>
                    <div id="list_copy" class="file-list-box"></div>
                </div>
            </div>
        </div>

        <div id="secTramite">
            <div class="seccion">
                <h3>1. DATOS DE RECEPCIÓN</h3>
                <div class="grid-3">
                    <div><label>Fecha Doc:</label><input type="date" id="rFd"></div>
                    <div><label>Remitente:</label><input type="text" id="rRem" list="l_rem" autocomplete="off"><datalist id="l_rem"></datalist></div>
                    <div><label>Cargo:</label><input type="text" id="rCar" list="l_car" autocomplete="off"><datalist id="l_car"></datalist></div>
                    <div><label>Unidad Origen:</label><input type="text" id="rUni" list="l_uor" autocomplete="off"><datalist id="l_uor"></datalist></div>
                    
                    <div><label>N° Documento:</label><input type="text" id="rNum" oninput="cleanPNSync(this)" style="background:#e3f2fd; font-weight:bold; border:1px solid #2196f3;"></div>
                    
                    <div><label>Fecha Recepción:</label><input type="date" id="rFr"></div>
                    <div class="full"><label>Asunto:</label><input type="text" id="rAsu"></div>
                    <div class="full"><label>Descripción / Resumen:</label><textarea id="rDes" rows="2"></textarea></div>
                    <div><label>S. Policial Turno:</label><input type="text" id="rRec" list="l_tur" autocomplete="off"><datalist id="l_tur"></datalist></div>
                    <div>
                        <label style="color:#d32f2f;">Observación Especial:</label>
                        <select id="rObs" onchange="logicObs()">
                            <option value="NINGUNA">NINGUNA</option>
                            <option value="REASIGNADO">REASIGNADO</option>
                            <option value="GENERADO DESDE DESPACHO">GENERADO DESDE DESPACHO</option>
                            <option value="CONOCIMIENTO PARA MI CORONEL">CONOCIMIENTO PARA MI CORONEL</option>
                            <option value="OTRO">OTRO/A</option>
                        </select>
                        <input type="text" id="rObsO" style="display:none; margin-top:5px;" placeholder="Especifique observación">
                    </div>
                    
                    <div class="full" style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; border-top:1px solid #eee; padding-top:15px; margin-top:10px;">
                        <div>
                            <label style="color:#1565c0;">📄 DOCUMENTO PRINCIPAL (Solo 1):</label>
                            <div class="drop-area" id="drop_main" onclick="document.getElementById('rFileMain').click()" style="background:#e3f2fd; border-color:#90caf9;">
                                <div class="drop-txt">Arrastra Principal aquí o Click</div>
                                <input type="file" id="rFileMain" style="display:none" onchange="handleFiles(this.files, 'main')">
                            </div>
                            <div id="list_main" class="file-list-box"></div>
                        </div>
                        <div>
                            <label style="color:#2e7d32;">📎 ANEXOS (Varios):</label>
                            <div class="drop-area" id="drop_anx" onclick="document.getElementById('rFileAnx').click()">
                                <div class="drop-txt">Arrastra Anexos aquí o Click</div>
                                <input type="file" id="rFileAnx" multiple style="display:none" onchange="handleFiles(this.files, 'anx')">
                            </div>
                            <div id="list_anx" class="file-list-box"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="seccion" id="sec3">
                <h3>2. GESTIÓN Y RESPUESTA</h3>
                <div class="grid-3">
                    <div class="full">
                        <label>Unidad Destino (Separar con comas):</label>
                        <div class="ac-wrap">
                            <input type="text" id="gDes" autocomplete="off" oninput="syncDestino()" placeholder="Ej: UCAP, UNDECOF...">
                            <div id="ac_gDes" class="ac-box"></div>
                        </div>
                    </div>
                    <div>
                        <label>Tipo Doc. Salida:</label>
                        <select id="gTip" onchange="logicTip()">
                            <option>DOCPOL ELECTRÓNICO</option><option>QUIPUX ELECTRÓNICO</option>
                            <option>FISICO</option><option>DIGITAL</option><option>OTRO</option>
                        </select>
                        <input type="text" id="gTipO" style="display:none; margin-top:5px;">
                    </div>
                    <div>
                        <label>Receptor Respuesta (Nombres):</label>
                        <div class="ac-wrap">
                            <input type="text" id="gRec" autocomplete="off">
                            <div id="ac_gRec" class="ac-box"></div>
                        </div>
                    </div>
                    <div><label>Nro. Documento Respuesta:</label><input type="text" id="gNum" oninput="syncRespuesta()" placeholder="PN-DINIC..."></div>
                    <div><label>Fecha Emisión:</label><input type="date" id="gFem"></div>
                    <div>
                        <label>Estado del Trámite:</label>
                        <select id="gEst" style="font-weight:bold; pointer-events:none; background:#f5f5f5;">
                            <option value="PENDIENTE" style="color:red">🔴 PENDIENTE</option>
                            <option value="FINALIZADO" style="color:green">🟢 FINALIZADO</option>
                        </select>
                    </div>
                    <div class="full">
                        <label style="color:#c2185b;">DOCUMENTOS DE RESPUESTA / OFICIOS (Varios):</label>
                        <div class="drop-area" id="drop_out" onclick="document.getElementById('gFile').click()">
                            <div class="drop-txt">Arrastra Respuestas aquí o Click</div>
                            <input type="file" id="gFile" multiple style="display:none" onchange="handleFiles(this.files, 'out')">
                        </div>
                        <div id="list_out" class="file-list-box"></div>
                    </div>
                </div>
            </div>

            <div class="seccion" id="sec4">
                <h3>3. CONTROL DE SALIDA</h3>
                <div class="grid-3">
                    <div><label>¿Trámite Externo?</label><select id="sExt"><option>NO</option><option>SI</option></select></div>
                    <div class="full"><label>Destino Final (Automático):</label><input type="text" id="sDes" readonly style="background:#eee;"></div>
                    <div><label>NRO DE SALIDA (Automático):</label><input type="text" id="sNum" readonly style="background:#eee;"></div>
                    <div><label>Fecha Salida:</label><input type="date" id="sFs"></div>
                    <div><label>Fecha Recepción:</label><input type="date" id="sFr"></div>
                </div>
            </div>
        </div>

        <button id="btnMain" class="btn-main btn-add" onclick="agregarRegistro()">➕ AGREGAR TRÁMITE A LA COLA</button>

        <h3 style="margin-top:40px; border-bottom:2px solid #0E2F44; padding-bottom:10px;">📋 COLA DE TRABAJO (Turno Actual)</h3>
        <table>
            <thead><tr><th width="40">#</th><th>Documento</th><th>Asunto / Obs</th><th>Estado</th><th width="100">Acciones</th></tr></thead>
            <tbody id="tablaBody"></tbody>
        </table>

        <button class="btn-main btn-down" onclick="generarFinal()">📦 DESCARGAR PAQUETE FINAL (ZIP + EXCEL)</button>

        <div class="footer">
            SISTEMA INTEGRADO DE GESTIÓN DOCUMENTAL - DINIC 2026 | Desarrollado por John Rotot
        </div>
    </div>

    <script>
        // --- GLOBALS & DB ---
        let db, registros = [], editIdx = -1;
        let activeMode = 'TRAMITE'; 
        let poolFiles = { main: null, anx: [], out: [], copy: [] };
        const MEM_KEYS = { remitente: 'd_m_rem', cargo: 'd_m_car', u_origen: 'd_m_uor', rec_turno: 'd_m_rtu', u_destinos: 'd_m_ude', rec_respuestas: 'd_m_rre' };

        window.onload = () => {
            document.getElementById('loader').style.display='none'; // Ocultar loader inicial por si acaso
            let r = indexedDB.open("DINIC_V44_MATRIX", 1);
            r.onupgradeneeded = e => { let d = e.target.result; if(!d.objectStoreNames.contains('files')) d.createObjectStore('files'); };
            r.onsuccess = e => { db = e.target.result; checkPlantilla(); };
            
            setToday(); loadMemories();
            setupAuto('gDes', 'mem_u_destinos'); setupAuto('gRec', 'mem_rec_respuestas');
            setupDnD(); 
            
            document.getElementById('rFd').addEventListener('input', function(){ 
                let v = this.value; if(v) ['rFr','gFem','sFs','sFr'].forEach(id => document.getElementById(id).value = v); 
            });
        };

        // --- MANEJO DE MODOS ---
        function toggleMode(mode) {
            if (activeMode === mode) activeMode = 'TRAMITE'; else activeMode = mode;
            applyModeUI();
        }

        function applyModeUI() {
            document.getElementById('btnModeCopia').className = "mode-btn mode-copy";
            document.getElementById('btnModeGen').className = "mode-btn mode-gen";
            document.getElementById('secCopia').style.display = 'none';
            document.getElementById('secTramite').style.display = 'block';

            // Reset habilitaciones
            document.querySelectorAll('#secTramite input, #secTramite select, #secTramite textarea').forEach(e => e.disabled = false);
            document.getElementById('rObs').disabled = false;
            document.getElementById('drop_out').classList.remove('disabled');

            if (activeMode === 'COPIA') {
                document.getElementById('btnModeCopia').className += " active";
                document.getElementById('secCopia').style.display = 'block';
                document.getElementById('secTramite').style.display = 'none';
            
            } else if (activeMode === 'GENERADO') {
                document.getElementById('btnModeGen').className += " active";
                document.getElementById('rRem').disabled = true;
                document.getElementById('rCar').disabled = true;
                document.getElementById('rUni').disabled = true;
                document.getElementById('rObs').value = "GENERADO DESDE DESPACHO";
                document.getElementById('drop_out').classList.add('disabled');
                logicObs();
            } else {
                document.getElementById('rObs').value = "NINGUNA";
                logicObs();
            }
        }

        // --- DRAG & DROP & FILES ---
        function setupDnD() {
            ['drop_copy', 'drop_main', 'drop_anx', 'drop_out'].forEach(id => {
                let zone = document.getElementById(id); if(!zone) return;
                zone.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); zone.style.background='#e3f2fd'; });
                zone.addEventListener('dragleave', (e) => { e.preventDefault(); e.stopPropagation(); zone.style.background=''; });
                zone.addEventListener('drop', (e) => {
                    e.preventDefault(); e.stopPropagation(); zone.style.background='';
                    if(zone.classList.contains('disabled')) return;
                    let type = id.replace('drop_', ''); 
                    handleFiles(e.dataTransfer.files, type);
                });
            });
        }

        function handleFiles(files, type) {
            let arr = Array.from(files);
            if(type === 'main') poolFiles.main = arr[0];
            else poolFiles[type] = poolFiles[type].concat(arr);
            renderFiles();
        }

        function removeFile(type, index) {
            if(confirm("¿Quitar este archivo?")) {
                if(type === 'main') poolFiles.main = null;
                else poolFiles[type].splice(index, 1);
                renderFiles();
            }
        }

        function renderFiles() {
            let divM = document.getElementById('list_main'); divM.innerHTML = "";
            if(poolFiles.main) {
                divM.innerHTML = `<div class="file-item"><span>📄 PRINCIPAL: ${poolFiles.main.name}</span> <button class="btn-del-file" onclick="removeFile('main',0)">✖</button></div>`;
            }
            const renderList = (type, divId, prefix) => {
                let div = document.getElementById(divId); div.innerHTML = "";
                poolFiles[type].forEach((f, i) => {
                    div.innerHTML += `<div class="file-item"><span>${prefix} ${i+1}: ${f.name}</span> <button class="btn-del-file" onclick="removeFile('${type}',${i})">✖</button></div>`;
                });
            };
            renderList('anx', 'list_anx', '📎 ANEXO');
            renderList('out', 'list_out', '📤 SALIDA');
            renderList('copy', 'list_copy', '📂 COPIA');
        }

        // --- CORE: AGREGAR / EDITAR ---
        function agregarRegistro() {
            try {
                let datos = capturarDatos(); if (!datos) return; 
                if(activeMode !== 'COPIA') saveMemories(datos);
                if (editIdx > -1) { registros[editIdx] = datos; alert("✅ Registro ACTUALIZADO"); } 
                else { registros.push(datos); }
                resetForm(); renderTable(); 
            } catch (e) { alert("Error: " + e.message); console.error(e); }
        }

        function capturarDatos() {
            if (activeMode === 'COPIA') {
                let num = getVal('cNum'); if (!num) { alert("Falta N° Copia"); return null; }
                return { tipo: 'COPIA', num: num, fCopy: [...poolFiles.copy], obs: 'COPIA' };
            } else {
                let obs = getVal('rObs');
                if (obs !== 'GENERADO DESDE DESPACHO' && !getVal('rNum')) { alert("Falta N° Documento de Entrada"); return null; }
                let obsVal = obs === 'OTRO' ? getVal('rObsO') : obs;
                let tVal = getVal('gTip') === 'OTRO' ? getVal('gTipO') : getVal('gTip');
                let filesOut = (activeMode === 'GENERADO') ? [] : [...poolFiles.out];
                return {
                    tipo: 'TRAMITE',
                    rFd: getVal('rFd'), rRem: getVal('rRem'), rCar: getVal('rCar'), rUni: getVal('rUni'),
                    rNum: getVal('rNum'), rFr: getVal('rFr'), rAsu: getVal('rAsu'),
                    rDes: getVal('rDes'), rRec: getVal('rRec'), rObs: obsVal, 
                    fMain: poolFiles.main, fAnx: [...poolFiles.anx], fOut: filesOut,
                    gDes: getVal('gDes'), gTip: tVal, gRec: getVal('gRec'), gNum: getVal('gNum'),
                    gFem: getVal('gFem'), gEst: getVal('gEst'), 
                    sExt: getVal('sExt'), sDes: getVal('sDes'), sNum: getVal('sNum'), sFs: getVal('sFs'), sFr: getVal('sFr')
                };
            }
        }

        function editar(i) {
            editIdx = i; let r = registros[i];
            let btn = document.getElementById('btnMain'); btn.innerHTML = "💾 ACTUALIZAR REGISTRO"; btn.style.background = "#f57f17";
            poolFiles = { main: r.fMain || null, anx: r.fAnx ? [...r.fAnx] : [], out: r.fOut ? [...r.fOut] : [], copy: r.fCopy ? [...r.fCopy] : [] };
            
            if (r.tipo === 'COPIA') {
                activeMode = 'COPIA'; setVal('cNum', r.num);
            } else {
                if (r.rObs === 'GENERADO DESDE DESPACHO') activeMode = 'GENERADO'; else activeMode = 'TRAMITE';
                setVal('rFd', r.rFd); setVal('rRem', r.rRem); setVal('rCar', r.rCar); setVal('rUni', r.rUni);
                setVal('rNum', r.rNum); setVal('rFr', r.rFr); setVal('rAsu', r.rAsu); setVal('rDes', r.rDes); setVal('rRec', r.rRec);
                let baseObs = ['REASIGNADO','GENERADO DESDE DESPACHO','CONOCIMIENTO PARA MI CORONEL','NINGUNA'].includes(r.rObs) ? r.rObs : 'OTRO';
                setVal('rObs', baseObs); if(baseObs==='OTRO') { document.getElementById('rObsO').style.display='block'; setVal('rObsO', r.rObs); }
                setVal('gDes', r.gDes); 
                let baseTip = ['DOCPOL ELECTRÓNICO','QUIPUX ELECTRÓNICO','FISICO','DIGITAL'].includes(r.gTip) ? r.gTip : 'OTRO';
                setVal('gTip', baseTip); if(baseTip==='OTRO') { document.getElementById('gTipO').style.display='block'; setVal('gTipO', r.gTip); }
                setVal('gRec', r.gRec); setVal('gNum', r.gNum); setVal('gFem', r.gFem); setVal('gEst', r.gEst);
                setVal('sExt', r.sExt); setVal('sDes', r.sDes); setVal('sNum', r.sNum); setVal('sFs', r.sFs); setVal('sFr', r.sFr);
            }
            applyModeUI(); renderFiles(); window.scrollTo(0,0);
        }

        function borrar(i) { if(confirm("¿Eliminar?")) { registros.splice(i, 1); renderTable(); } }

        function renderTable() {
            let tbody = document.getElementById('tablaBody'); tbody.innerHTML = "";
            registros.forEach((r, i) => {
                let tr = document.createElement('tr');
                let css="row-grey", desc=r.tipo==='COPIA'?'COPIA':r.rAsu, num, st=r.gEst;
                if(r.tipo==='COPIA'){ css="row-copia"; st="COPIA"; num=r.num; } else {
                    num = (r.rObs === 'GENERADO DESDE DESPACHO') ? (r.gNum ? r.gNum : '(SIN NÚMERO)') : r.rNum;
                    if(st==='PENDIENTE'){ css="row-pend"; } else { css="row-ok"; }
                }
                tr.className = css;
                tr.innerHTML = `<td>${i+1}</td><td><b>${num}</b></td><td>${desc}</td><td>${st}</td><td><button style="margin-right:5px;cursor:pointer;" onclick="editar(${i})">✏️</button><button style="cursor:pointer;color:red;" onclick="borrar(${i})">❌</button></td>`;
                tbody.appendChild(tr);
            });
        }

        function generarFinal() {
            if(registros.length===0) return alert("Vacio."); overlay(true,"Generando...");
            let hasFiles = registros.some(r => r.fMain || (r.fAnx && r.fAnx.length) || (r.fOut && r.fOut.length) || (r.fCopy && r.fCopy.length));
            let tx = db.transaction(['files'], 'readonly');
            tx.objectStore('files').get('plantilla').onsuccess = e => {
                if(e.target.result) { if (hasFiles) procesarZip(e.target.result); else procesarSoloExcel(e.target.result); } 
                else { overlay(false); alert("⚠️ Falta Plantilla Excel. Subela arriba."); }
            };
        }

        async function procesarSoloExcel(blob) {
            try {
                const workbook = new ExcelJS.Workbook(); await workbook.xlsx.load(await blob.arrayBuffer());
                fillSheet(workbook);
                saveAs(new Blob([await workbook.xlsx.writeBuffer()]), `${getNaming()}.xlsx`); overlay(false);
            } catch(e) { overlay(false); alert("Error Excel: "+e); }
        }

        async function procesarZip(blob) {
            try {
                const zip = new JSZip(); const workbook = new ExcelJS.Workbook();
                await workbook.xlsx.load(await blob.arrayBuffer());
                fillSheet(workbook);
                let nameRef = getNaming();
                let root = zip.folder(nameRef);
                let fTram = root.folder("DOCUMENTACION RECIBIDA");
                let fCop = registros.some(r=>r.tipo==='COPIA') ? root.folder("COPIAS") : null;
                let ct=0, cc=0;

                registros.forEach((r, idx) => {
                    if(r.tipo === 'COPIA') {
                        cc++; if(fCop && r.fCopy) { let tg = fCop.folder(`${cc}. ${safe(r.num)}`); r.fCopy.forEach(f => tg.file(f.name, f)); }
                    } else {
                        ct++;
                        if (r.fMain || (r.fAnx && r.fAnx.length) || (r.fOut && r.fOut.length)) {
                            let suffix = ['REASIGNADO','CONOCIMIENTO PARA MI CORONEL','GENERADO DESDE DESPACHO'].includes(r.rObs) ? " " + r.rObs : "";
                            let docName = (r.rObs === 'GENERADO DESDE DESPACHO') ? safe(r.gNum) : safe(r.rNum);
                            let folderName = `${ct}. ${docName}${suffix}`;
                            let tg = fTram.folder(folderName);
                            if(r.fMain) tg.file(`${docName} PRINCIPAL.${ext(r.fMain.name)}`, r.fMain);
                            if(r.fAnx) r.fAnx.forEach((f,k)=>tg.file(`${docName} ANEXO ${k+1} ${f.name}`, f));
                            if(r.fOut) r.fOut.forEach((f,k)=>tg.file(`${r.gNum?safe(r.gNum):'RESP'} RESPUESTA ${k+1} ${f.name}`, f));
                        }
                    }
                });
                const buf = await workbook.xlsx.writeBuffer(); root.file(`${nameRef}.xlsx`, buf); 
                const cnt = await zip.generateAsync({type:"blob"}); saveAs(cnt, `${nameRef}.zip`); overlay(false);
            } catch(e){ overlay(false); alert("Error ZIP: "+e); }
        }

        function fillSheet(workbook) {
            let sheet = workbook.getWorksheet("CONTROL DE GESTIÓN") || workbook.getWorksheet(1);
            let excelRow = 7, order = 1;
            registros.forEach((r) => {
                if(r.tipo === 'COPIA') return;
                let row = sheet.getRow(excelRow); row.getCell(1).value = order;
                let obs = r.rObs==='NINGUNA'?"":r.rObs;
                let fd=fmtD(r.rFd), fr=fmtD(r.rFr), fe=fmtD(r.gFem), fs=fmtD(r.sFs), frs=fmtD(r.sFr);
                if(r.rObs === 'GENERADO DESDE DESPACHO') { row.getCell(11).value=r.rRec; row.getCell(12).value=obs; }
                else {
                    row.getCell(3).value=fd; row.getCell(4).value=r.rRem; row.getCell(5).value=r.rCar; row.getCell(6).value=r.rUni;
                    row.getCell(7).value=r.rNum; row.getCell(8).value=fr; row.getCell(9).value=r.rAsu; row.getCell(10).value=r.rDes;
                    row.getCell(11).value=r.rRec; row.getCell(12).value=obs;
                }
                if(r.rObs !== 'CONOCIMIENTO PARA MI CORONEL') {
                    row.getCell(13).value=r.gDes; row.getCell(14).value=r.gTip; row.getCell(15).value=r.gRec; row.getCell(16).value=r.gNum;
                    row.getCell(17).value=fe; row.getCell(19).value=r.gEst; row.getCell(20).value=r.sExt; row.getCell(21).value=r.sDes;
                    row.getCell(22).value=r.sNum; row.getCell(23).value=fs; row.getCell(24).value=frs;
                } else { row.getCell(19).value="FINALIZADO"; }
                
                if(['REASIGNADO', 'GENERADO DESDE DESPACHO', 'CONOCIMIENTO PARA MI CORONEL'].includes(r.rObs)) {
                    row.eachCell(c => c.fill={type:'pattern',pattern:'solid',fgColor:{argb:'FFCFD8DC'}});
                } else {
                    let color = r.gEst === 'PENDIENTE' ? 'FFEF9A9A' : 'FFA5D6A7';
                    row.getCell(19).fill={type:'pattern',pattern:'solid',fgColor:{argb: color}};
                }
                row.commit(); excelRow++; order++;
            });
        }

        // --- UTILS ---
        function logicObs(){ 
            let o=getVal('rObs');
            document.getElementById('sDes').readOnly=true; 
            document.getElementById('rObsO').style.display='none'; 
            if(o==='REASIGNADO' || o==='CONOCIMIENTO PARA MI CORONEL'){ 
                document.getElementById('gEst').value = "FINALIZADO";
                if(o==='REASIGNADO'){ document.getElementById('gNum').disabled=true; document.getElementById('sNum').disabled=true; } 
                else { document.querySelectorAll('#sec3 input, #sec3 select, #sec4 input, #sec4 select').forEach(e=>e.disabled=true); }
            } else if(o==='GENERADO DESDE DESPACHO' || o==='OTRO'){ 
                if(o==='OTRO') document.getElementById('rObsO').style.display='block'; syncRespuesta();
            } else syncRespuesta();
        }
        function syncRespuesta() { 
            let o = getVal('rObs'); if(o === 'REASIGNADO' || o === 'CONOCIMIENTO PARA MI CORONEL') return;
            let val = document.getElementById('gNum').value.trim(); 
            document.getElementById('sNum').value = val; 
            document.getElementById('gEst').value = val.length > 0 ? "FINALIZADO" : "PENDIENTE";
        }
        async function guardarRespaldo() {
            if(registros.length===0) return alert("Vacio"); overlay(true,"Guardando...");
            const zip = new JSZip();
            let meta = registros.map(r=>{ 
                let c={...r}; 
                c.nMain=r.fMain?r.fMain.name:null; c.nAnx=r.fAnx?r.fAnx.map(f=>f.name):[]; c.nOut=r.fOut?r.fOut.map(f=>f.name):[]; c.nCopy=r.fCopy?r.fCopy.map(f=>f.name):[]; 
                delete c.fMain; delete c.fAnx; delete c.fOut; delete c.fCopy; return c; 
            });
            zip.file("data.json", JSON.stringify(meta));
            let ast = zip.folder("assets");
            registros.forEach((r,i)=>{ 
                if(r.fMain) ast.file(`${i}_main`, r.fMain); if(r.fAnx) r.fAnx.forEach((f,k)=>ast.file(`${i}_anx_${k}`,f)); if(r.fOut) r.fOut.forEach((f,k)=>ast.file(`${i}_out_${k}`, f)); if(r.fCopy) r.fCopy.forEach((f,k)=>ast.file(`${i}_copy_${k}`, f));
            });
            let blob = await zip.generateAsync({type:"blob"}); saveAs(blob, `RESPALDO ${getNaming()}.dinic`); overlay(false);
        }
        async function restaurarRespaldo(inp) {
            if(!inp.files[0]) return; overlay(true,"Cargando...");
            try {
                let zip = await JSZip.loadAsync(inp.files[0]);
                let meta = JSON.parse(await zip.file("data.json").async("string"));
                registros = [];
                for(let i=0; i<meta.length; i++){
                    let r = meta[i]; r.fMain=null; r.fAnx=[]; r.fOut=[]; r.fCopy=[];
                    if(r.nMain) { let b=await zip.file(`assets/${i}_main`).async("blob"); r.fMain=new File([b], r.nMain); }
                    if(r.nAnx) for(let k=0; k<r.nAnx.length; k++) { let b=await zip.file(`assets/${i}_anx_${k}`).async("blob"); r.fAnx.push(new File([b], r.nAnx[k])); }
                    if(r.nOut) for(let k=0; k<r.nOut.length; k++) { let b=await zip.file(`assets/${i}_out_${k}`).async("blob"); r.fOut.push(new File([b], r.nOut[k])); }
                    if(r.nCopy) for(let k=0; k<r.nCopy.length; k++) { let b=await zip.file(`assets/${i}_copy_${k}`).async("blob"); r.fCopy.push(new File([b], r.nCopy[k])); }
                    registros.push(r);
                }
                renderTable(); overlay(false); alert("✅ Restaurado");
            } catch(e){ overlay(false); alert("Error restauración: " + e); console.log(e); } inp.value="";
        }
        function triggerUpload(){ document.getElementById('inPlantilla').click(); }
        function guardarPlantillaDB(inp){ if(!inp.files[0])return; overlay(true); let r=new FileReader(); r.onload=e=>{ let b=new Blob([e.target.result],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}); let t=db.transaction(['files'],'readwrite'); t.objectStore('files').put(b,'plantilla'); t.oncomplete=()=>{overlay(false); checkPlantilla(); alert("Plantilla Guardada");}; }; r.readAsArrayBuffer(inp.files[0]); }
        function checkPlantilla(){ if(!db)return; db.transaction(['files'],'readonly').objectStore('files').get('plantilla').onsuccess=e=>{ document.getElementById('led').className=e.target.result?"led on":"led"; document.getElementById('ledTxt').innerText=e.target.result?"Plantilla Lista":"Falta Plantilla"; }; }
        function nuevoTurno(){ if(confirm("¿Nuevo turno?")){ registros=[]; renderTable(); resetForm(); } }
        function borrarTodo(){ if(confirm("¿Seguro?")){ localStorage.clear(); location.reload(); } }
        function resetForm(){ editIdx=-1; activeMode='TRAMITE'; poolFiles={main:null,anx:[],out:[],copy:[]}; document.getElementById('btnMain').innerText="➕ AGREGAR TRÁMITE A LA COLA"; document.querySelectorAll('input:not([type=file]), textarea').forEach(i=>i.value=""); setToday(); applyModeUI(); document.querySelectorAll('.file-list-box').forEach(d=>d.innerHTML=""); }
        function getNaming(){ let p=registros.find(r=>r.tipo==='TRAMITE'); return p?`TURNO ${p.rFd} ${p.rRec}`:"TURNO DINIC"; }
        function getVal(id){ return document.getElementById(id).value; }
        function setVal(id,v){ document.getElementById(id).value=v; }
        function cleanPNSync(input) { let val = input.value; if(val.toUpperCase().includes("PN-")) { let match = val.match(/PN-.*/i); if(match) input.value = match[0].toUpperCase(); } }
        function syncDestino() { document.getElementById('sDes').value = document.getElementById('gDes').value; }
        function logicTip(){ document.getElementById('gTipO').style.display=getVal('gTip')==='OTRO'?'block':'none'; }
        function setToday(){ const d=new Date().toISOString().split('T')[0]; ['rFd','rFr','gFem','sFs','sFr'].forEach(id=>document.getElementById(id).value=d); }
        function fmtD(i){ if(!i)return""; const[y,m,d]=i.split('-'); return `${d}/${m}/${y}`; }
        function safe(s){ return s?s.replace(/[\/\\]/g,'-'):'SN'; }
        function ext(n){ return n.split('.').pop(); }
        function overlay(s,t){ document.getElementById('loader').style.display=s?'flex':'none'; if(t)document.getElementById('loadText').innerText=t; }
        function saveMemories(d) { saveS('mem_remitente', d.rRem); saveS('mem_cargo', d.rCar); saveS('mem_u_origen', d.rUni); saveS('mem_rec_turno', d.rRec); saveM('mem_u_destinos', d.gDes); saveM('mem_rec_respuestas', d.gRec); }
        function saveS(k, v) { if(!v) return; let l = safeParse(localStorage.getItem(MEM_KEYS[k.replace('mem_','')])); if(!l.includes(v)){ l.push(v); localStorage.setItem(MEM_KEYS[k.replace('mem_','')], JSON.stringify(l)); loadMemories(); } }
        function saveM(k, v) { if(!v) return; let p = v.split(',').map(s=>s.trim()).filter(s=>s); let l = safeParse(localStorage.getItem(MEM_KEYS[k.replace('mem_','')])); p.forEach(x=>{ if(!l.includes(x)) l.push(x); }); localStorage.setItem(MEM_KEYS[k.replace('mem_','')], JSON.stringify(l)); }
        function loadMemories() { ['mem_remitente','mem_cargo','mem_u_origen','mem_rec_turno'].forEach(id=>{ let l = safeParse(localStorage.getItem(MEM_KEYS[id.replace('mem_','')])); let el = document.getElementById(id==='mem_remitente'?'l_rem': id==='mem_cargo'?'l_car': id==='mem_u_origen'?'l_uor': 'l_tur'); if(el) el.innerHTML = l.map(x=>`<option value="${x}">`).join(''); }); }
        function setupAuto(id, memKey) { const inp = document.getElementById(id); const box = document.getElementById('ac_' + id); const key = MEM_KEYS[memKey.replace('mem_','')]; function showSuggestions() { let val = inp.value, parts = val.split(','), term = parts[parts.length - 1].trim().toLowerCase(); let list = safeParse(localStorage.getItem(key)); let matches = term === '' ? list : list.filter(item => item.toLowerCase().includes(term)); if (matches.length > 0) { box.innerHTML = matches.map(item => `<div class="ac-item">${item}</div>`).join(''); box.style.display = 'block'; box.querySelectorAll('.ac-item').forEach(div => { div.onclick = function() { parts[parts.length - 1] = " " + this.innerText; inp.value = parts.join(',') + ", "; box.style.display = 'none'; inp.focus(); inp.dispatchEvent(new Event('input')); }; }); } else box.style.display = 'none'; } inp.addEventListener('input', showSuggestions); inp.addEventListener('focus', showSuggestions); document.addEventListener('click', function(e) { if (e.target !== inp && e.target !== box && !box.contains(e.target)) box.style.display = 'none'; }); }
        function safeParse(str) { try { return JSON.parse(str) || []; } catch(e) { return []; } }
    </script>
</body>
</html>
"""

# ==============================================================================
# 4. GESTIÓN DE USUARIOS Y SESIÓN
# ==============================================================================
USUARIOS_BASE = {
    "1723623011": {"grado": "CBOS", "nombre": "CARRILLO NARVAEZ JOHN STALIN", "activo": True},
    "ADMIN": {"grado": "ADMIN", "nombre": "SISTEMA CENTRAL", "activo": True}
}
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active_page' not in st.session_state: st.session_state.active_page = 'dashboard'
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = ""

# ==============================================================================
# 5. LÓGICA DE NAVEGACIÓN
# ==============================================================================

def ir_a(pagina):
    st.session_state.active_page = pagina
    st.rerun()

def get_hora_ecuador():
    return datetime.now(timezone(timedelta(hours=-5)))

# ==============================================================================
# 6. INTERFAZ: LOGIN O DASHBOARD
# ==============================================================================

if not st.session_state.logged_in:
    # --- PANTALLA DE LOGIN MINIMALISTA ---
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png", width=100)
        st.markdown("### SIGD DINIC | ACCESO SEGURO")
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ENTRAR", type="primary"):
                if u == ADMIN_USER and p == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True
                    st.session_state.usuario_turno = "ADMINISTRADOR"
                    st.rerun()
                else:
                    st.error("Acceso denegado")
else:
    # --- SISTEMA CENTRAL ---
    
    # PÁGINA 1: DASHBOARD (LANDING PAGE)
    if st.session_state.active_page == 'dashboard':
        st.markdown(f"""
            <div class="dashboard-container">
                <div class="hero-title">SIGD DINIC</div>
                <div class="hero-subtitle">Sistema Integrado de Gestión Documental - Nivel Central</div>
                
                <div class="card-grid">
                    <div class="card" onclick="document.getElementById('btn_sec').click()">
                        <span class="card-icon">📝</span>
                        <div class="card-title">Secretaría</div>
                        <div class="card-desc">Gestión de Trámites, Matriz V44 y Archivo Digital</div>
                    </div>

                    <div class="card" onclick="document.getElementById('btn_ia').click()">
                        <span class="card-icon">🧠</span>
                        <div class="card-title">Asesor IA</div>
                        <div class="card-desc">Análisis de Documentos y Consultas Inteligentes</div>
                    </div>

                    <div class="card" onclick="document.getElementById('btn_th').click()">
                        <span class="card-icon">👮‍♂️</span>
                        <div class="card-title">Talento Humano</div>
                        <div class="card-desc">Partes, Sanciones y Gestión de Personal</div>
                    </div>
                    
                    <div class="card" onclick="document.getElementById('btn_adm').click()">
                        <span class="card-icon">🛡️</span>
                        <div class="card-title">Administración</div>
                        <div class="card-desc">Auditoría, Usuarios y Logs del Sistema</div>
                    </div>
                </div>
                
                <div style="margin-top: 50px; opacity: 0.7;">
                    Usuario: {st.session_state.usuario_turno} | {get_hora_ecuador().strftime('%Y-%m-%d')}
                    <br>
                    <button style="background:none; border:none; color: #ef5350; cursor:pointer; margin-top:10px;" onclick="location.reload()">Cerrar Sesión</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones invisibles para conectar el HTML click con Python
        # (Truco para que el diseño CSS controle la lógica de Streamlit)
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("Ir a Secretaría", key="btn_sec"): ir_a('secretaria')
        with c2: 
            if st.button("Ir a IA", key="btn_ia"): ir_a('asesor')
        with c3: 
            if st.button("Ir a TH", key="btn_th"): ir_a('th')
        with c4: 
            if st.button("Ir a Admin", key="btn_adm"): ir_a('admin')

    # PÁGINA 2: MÓDULO SECRETARÍA (FULL SCREEN REAL)
    elif st.session_state.active_page == 'secretaria':
        # Botón flotante para volver (inyectado en CSS arriba .btn-home)
        st.markdown('<a href="#" class="btn-home" onclick="document.getElementById(\'btn_back\').click()">🏠 MENÚ</a>', unsafe_allow_html=True)
        # Botón oculto real que ejecuta el regreso
        if st.button("Volver", key="btn_back", help="Volver al menú"): ir_a('dashboard')
        
        # EL COMPONENTE HTML OCUPA TODO
        # height=3000 y scrolling=False es el truco para "No Scrollbar interna"
        components.html(HTML_SECRETARIO_V44, height=3000, scrolling=False)

    # PÁGINA 3: MÓDULO ASESOR
    elif st.session_state.active_page == 'asesor':
        st.markdown('<a href="#" class="btn-home" onclick="document.getElementById(\'btn_back\').click()">🏠 MENÚ</a>', unsafe_allow_html=True)
        if st.button("Volver", key="btn_back"): ir_a('dashboard')
        
        st.title("🧠 Módulo de Inteligencia Artificial")
        st.info("Sistema en Mantenimiento. Integrando Gemini 2.0 Flash...")

    # PÁGINA 4: MÓDULO TH
    elif st.session_state.active_page == 'th':
        st.markdown('<a href="#" class="btn-home" onclick="document.getElementById(\'btn_back\').click()">🏠 MENÚ</a>', unsafe_allow_html=True)
        if st.button("Volver", key="btn_back"): ir_a('dashboard')
        
        st.title("👮‍♂️ Talento Humano")
        st.warning("Área Restringida.")

    # PÁGINA 5: ADMIN
    elif st.session_state.active_page == 'admin':
        st.markdown('<a href="#" class="btn-home" onclick="document.getElementById(\'btn_back\').click()">🏠 MENÚ</a>', unsafe_allow_html=True)
        if st.button("Volver", key="btn_back"): ir_a('dashboard')
        
        st.title("🛡️ Panel de Control")
        st.dataframe(pd.DataFrame.from_dict(USUARIOS_BASE, orient='index'))
