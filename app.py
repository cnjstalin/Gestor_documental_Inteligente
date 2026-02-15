import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# Credenciales Maestras
ADMIN_USER = "1723623011"
ADMIN_PASS_MASTER = "9994915010022"

# Estilos CSS para Streamlit
st.markdown("""
    <style>
    .main-header { background-color: #0E2F44; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #D4AF37; }
    .login-container { max-width: 400px; margin: auto; padding: 40px; background-color: #ffffff; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #0E2F44; }
    div.stButton > button { width: 100%; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CÓDIGO HTML INCRUSTADO (TU MOTOR V44)
# ==============================================================================
# Pegamos aquí tu código HTML tal cual, dentro de una variable de texto.
HTML_SECRETARIO_V44 = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GESTOR DOCUMENTAL DINIC - V44 MATRIX FIX</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>

    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #eceff1; padding: 20px; color: #333; padding-top: 20px; padding-bottom: 60px; }
        .container { max-width: 100%; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        
        /* HEADER - Ajustado para iframe */
        .top-header { position: sticky; top: 0; left: 0; width: 100%; background: #263238; color: white; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border-radius: 8px 8px 0 0; margin-bottom: 20px;}
        .bar-main { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; border-bottom: 1px solid #455a64; }
        .bar-tools { background: #37474f; padding: 8px 20px; display: flex; gap: 10px; align-items: center; justify-content: flex-end; flex-wrap: wrap;}

        /* LED */
        .led-box { font-size: 11px; display: flex; align-items: center; gap: 5px; background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px; }
        .led { width: 8px; height: 8px; border-radius: 50%; background: #f44336; box-shadow: 0 0 5px #f44336; }
        .led.on { background: #00e676; box-shadow: 0 0 5px #00e676; }

        /* BOTONES TOP */
        .btn-top { border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 11px; text-transform: uppercase; transition: 0.2s; }
        .btn-cfg { background: #5e35b1; color: white; }
        .btn-save { background: #00acc1; color: white; }
        .btn-rest { background: #ffca28; color: #333; }
        .btn-new { background: #4caf50; color: white; }
        .btn-wipe { background: #b71c1c; color: white; margin-left: 10px; border: 1px solid #ff8a80; }
        .btn-top:hover { filter: brightness(1.2); transform: translateY(-1px); }

        /* BARRA DE MODOS */
        .mode-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .mode-btn { padding: 10px; border-radius: 6px; cursor: pointer; text-align: center; font-weight: bold; border: 2px solid transparent; transition: 0.3s; opacity: 0.7; }
        .mode-btn:hover { opacity: 1; transform: translateY(-2px); }
        .mode-copy { background: #fff3e0; color: #e65100; border-color: #ffe0b2; }
        .mode-copy.active { background: #ffe0b2; border-color: #e65100; opacity: 1; box-shadow: 0 0 8px rgba(230, 81, 0, 0.4); }
        .mode-gen { background: #e0f7fa; color: #006064; border-color: #b2ebf2; }
        .mode-gen.active { background: #b2ebf2; border-color: #006064; opacity: 1; box-shadow: 0 0 8px rgba(0, 96, 100, 0.4); }

        /* SECCIONES */
        .seccion { background: #fafafa; border: 1px solid #cfd8dc; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
        .seccion h3 { margin: 0 0 10px 0; font-size: 14px; color: #455a64; border-left: 4px solid #607d8b; padding-left: 8px; }
        
        /* GRID */
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .full { grid-column: 1 / -1; }

        /* INPUTS */
        label { display: block; font-weight: bold; font-size: 11px; color: #546e7a; margin-bottom: 3px; text-transform: uppercase; }
        input, select, textarea { width: 100%; padding: 8px; border: 1px solid #b0bec5; border-radius: 4px; font-size: 12px; box-sizing: border-box; }
        input[readonly] { background: #e0e0e0; color: #555; cursor: not-allowed; }
        input:disabled, select:disabled, textarea:disabled { background: #cfd8dc; color: #78909c; cursor: not-allowed; border-color: #cfd8dc; }

        /* AUTOCOMPLETE */
        .ac-wrap { position: relative; }
        .ac-box { position: absolute; top: 100%; left: 0; width: 100%; background: white; border: 1px solid #90a4ae; z-index: 999; max-height: 200px; overflow-y: auto; display: none; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .ac-item { padding: 8px; font-size: 12px; cursor: pointer; border-bottom: 1px solid #eee; }
        .ac-item:hover { background: #e3f2fd; color: #0d47a1; font-weight: bold; }

        /* ARCHIVOS */
        .drop-area { border: 2px dashed #90a4ae; padding: 15px; text-align: center; border-radius: 6px; cursor: pointer; background: white; transition: 0.2s; margin-bottom: 5px; position: relative; }
        .drop-area.dragover { border-color: #00e676; background: #e8f5e9; transform: scale(1.02); }
        .drop-area.disabled { background: #eceff1; border-color: #cfd8dc; cursor: not-allowed; opacity: 0.6; pointer-events: none; }
        .drop-txt { font-weight: bold; color: #0277bd; font-size: 11px; pointer-events: none; }
        
        .file-list-box { max-height: 120px; overflow-y: auto; border: 1px solid #b0bec5; padding: 5px; background: #fff; border-radius: 4px; }
        .file-item { display: flex; justify-content: space-between; align-items: center; font-size: 10px; margin-bottom: 2px; background: #f1f8e9; padding: 4px; border-radius: 3px; border-bottom: 1px solid #eee; }
        .btn-del-file { background: #ff5252; color: white; border: none; border-radius: 3px; width: 20px; height: 20px; font-size: 10px; cursor: pointer; margin-left: 5px; font-weight:bold; }
        .btn-del-file:hover { background: #d32f2f; }

        /* BOTONES ACCIÓN */
        .btn-main { display: block; width: 100%; padding: 12px; font-size: 15px; font-weight: bold; color: white; border: none; border-radius: 6px; cursor: pointer; margin: 20px 0; transition: background 0.3s; }
        .btn-add { background: #2e7d32; }
        .btn-update { background: #f57f17; color: white; box-shadow: 0 4px 10px rgba(245, 127, 23, 0.4); }
        .btn-down { background: #01579b; }

        /* TABLA */
        table { width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 10px; }
        thead { background: #455a64; color: white; }
        th, td { padding: 6px 10px; border: 1px solid #cfd8dc; text-align: left; }
        .row-copia { background: #fff3e0; color: #e65100; font-weight: bold; }
        .row-pend { background: #ffebee; color: #b71c1c; }
        .row-ok { background: #e8f5e9; color: #1b5e20; }
        .act-btn { border: none; padding: 3px 8px; border-radius: 3px; cursor: pointer; font-weight: bold; font-size: 10px; margin-right: 4px; }
        .act-edit { background: #ffeb3b; color: #333; }
        .act-del { background: #ef5350; color: white; }

        #loader { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(255,255,255,0.9); z-index: 2000; text-align: center; padding-top: 20%; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #78909c; border-top: 1px solid #ddd; padding-top: 10px; }
    </style>
</head>
<body>

    <div id="loader">
        <div style="font-size:40px;">⏳</div>
        <h3 id="loadText" style="color:#37474f;">Procesando...</h3>
    </div>

    <div class="top-header">
        <div class="bar-main">
            <div style="font-size:16px; font-weight:bold;">🛡️ GESTOR DOCUMENTAL DINIC</div>
            <div class="led-box">
                <span id="led" class="led"></span>
                <span id="ledTxt">Verificando plantilla...</span>
            </div>
        </div>
        <div class="bar-tools">
            <button class="btn-top btn-cfg" onclick="triggerUpload()">📂 SUBIR PLANTILLA</button>
            <input type="file" id="inPlantilla" accept=".xlsx" style="display:none" onchange="guardarPlantillaDB(this)">
            
            <button class="btn-top btn-save" onclick="guardarRespaldo()">⬇️ RESPALDAR</button>
            <button class="btn-top btn-rest" onclick="document.getElementById('inRestore').click()">⬆️ RESTAURAR</button>
            <input type="file" id="inRestore" accept=".dinic" style="display:none" onchange="restaurarRespaldo(this)">
            
            <span style="border-left:1px solid #aaa; height:20px; margin:0 5px;"></span>
            
            <button class="btn-top btn-new" onclick="nuevoTurno()">✨ NUEVO TURNO</button>
            <button class="btn-top btn-wipe" onclick="borrarTodo()">🗑️ REINICIAR</button>
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

        <div id="secCopia" style="display:none; background:#fff3e0; padding:15px; border-radius:6px; margin-bottom:15px; border:1px solid #ffb74d;">
            <div class="grid-3">
                <div class="full"><label>N° Documento Copia:</label><input type="text" id="cNum" oninput="cleanPNSync(this)"></div>
                <div class="full">
                    <label>📂 ANEXOS COPIA (Arrastre o Click):</label>
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
                <h3>2. DOCUMENTO RECEPTADO</h3>
                <div class="grid-3">
                    <div><label>Fecha Doc:</label><input type="date" id="rFd"></div>
                    <div><label>Remitente:</label><input type="text" id="rRem" list="l_rem" autocomplete="off"><datalist id="l_rem"></datalist></div>
                    <div><label>Cargo:</label><input type="text" id="rCar" list="l_car" autocomplete="off"><datalist id="l_car"></datalist></div>
                    <div><label>Unidad Origen:</label><input type="text" id="rUni" list="l_uor" autocomplete="off"><datalist id="l_uor"></datalist></div>
                    
                    <div><label>N° Documento:</label><input type="text" id="rNum" oninput="cleanPNSync(this)" style="background:#e3f2fd; font-weight:bold;"></div>
                    
                    <div><label>Fecha Recepción:</label><input type="date" id="rFr"></div>
                    <div class="full"><label>Asunto:</label><input type="text" id="rAsu"></div>
                    <div class="full"><label>Descripción:</label><textarea id="rDes" rows="2"></textarea></div>
                    <div><label>S. Policial Turno:</label><input type="text" id="rRec" list="l_tur" autocomplete="off"><datalist id="l_tur"></datalist></div>
                    <div>
                        <label style="color:#d32f2f;">Observación:</label>
                        <select id="rObs" onchange="logicObs()">
                            <option value="NINGUNA">NINGUNA</option>
                            <option value="REASIGNADO">REASIGNADO</option>
                            <option value="GENERADO DESDE DESPACHO">GENERADO DESDE DESPACHO</option>
                            <option value="CONOCIMIENTO PARA MI CORONEL">CONOCIMIENTO PARA MI CORONEL</option>
                            <option value="OTRO">OTRO/A</option>
                        </select>
                        <input type="text" id="rObsO" style="display:none; margin-top:2px;" placeholder="Especifique">
                    </div>
                    
                    <div class="full" style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; border-top:1px solid #ddd; padding-top:10px;">
                        <div>
                            <label style="color:#1565c0;">📄 DOCUMENTO PRINCIPAL (Solo 1):</label>
                            <div class="drop-area" id="drop_main" onclick="document.getElementById('rFileMain').click()" style="background:#e3f2fd;">
                                <div class="drop-txt">Arrastra Principal aquí o Click</div>
                                <input type="file" id="rFileMain" style="display:none" onchange="handleFiles(this.files, 'main')">
                            </div>
                            <div id="list_main" class="file-list-box"></div>
                        </div>
                        <div>
                            <label style="color:#2e7d32;">📎 ANEXOS (Acumulativo):</label>
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
                <h3>3. GESTIÓN O TRÁMITE</h3>
                <div class="grid-3">
                    <div class="full">
                        <label>Unidad Destino (Comas para varios):</label>
                        <div class="ac-wrap">
                            <input type="text" id="gDes" autocomplete="off" oninput="syncDestino()">
                            <div id="ac_gDes" class="ac-box"></div>
                        </div>
                    </div>
                    <div>
                        <label>Tipo Doc:</label>
                        <select id="gTip" onchange="logicTip()">
                            <option>DOCPOL ELECTRÓNICO</option><option>QUIPUX ELECTRÓNICO</option>
                            <option>FISICO</option><option>DIGITAL</option><option>OTRO</option>
                        </select>
                        <input type="text" id="gTipO" style="display:none; margin-top:2px;">
                    </div>
                    <div>
                        <label>Receptor Respuesta (Comas para varios):</label>
                        <div class="ac-wrap">
                            <input type="text" id="gRec" autocomplete="off">
                            <div id="ac_gRec" class="ac-box"></div>
                        </div>
                    </div>
                    <div><label>Nro Resp:</label><input type="text" id="gNum" oninput="syncRespuesta()"></div>
                    <div><label>Fecha Emisión:</label><input type="date" id="gFem"></div>
                    <div>
                        <label>Estado:</label>
                        <select id="gEst" style="font-weight:bold; pointer-events:none; background:#eee;">
                            <option value="PENDIENTE" style="color:red">🔴 PENDIENTE</option>
                            <option value="FINALIZADO" style="color:green">🟢 FINALIZADO</option>
                        </select>
                    </div>
                    <div class="full">
                        <label style="color:#c2185b;">DOCUMENTOS DE RESPUESTA (Acumulativo):</label>
                        <div class="drop-area" id="drop_out" onclick="document.getElementById('gFile').click()">
                            <div class="drop-txt">Arrastra Respuestas aquí o Click</div>
                            <input type="file" id="gFile" multiple style="display:none" onchange="handleFiles(this.files, 'out')">
                        </div>
                        <div id="list_out" class="file-list-box"></div>
                    </div>
                </div>
            </div>

            <div class="seccion" id="sec4">
                <h3>4. SALIDA</h3>
                <div class="grid-3">
                    <div><label>Externo?</label><select id="sExt"><option>NO</option><option>SI</option></select></div>
                    <div class="full"><label>Destino Final:</label><input type="text" id="sDes" readonly></div>
                    <div><label>NRO DE SALIDA:</label><input type="text" id="sNum" readonly></div>
                    <div><label>Fecha Salida:</label><input type="date" id="sFs"></div>
                    <div><label>Fecha Recepción:</label><input type="date" id="sFr"></div>
                </div>
            </div>
        </div>

        <button id="btnMain" class="btn-main btn-add" onclick="agregarRegistro()">➕ AGREGAR TRÁMITE A LA LISTA</button>

        <table>
            <thead><tr><th width="30">#</th><th>Documento</th><th>Asunto / Obs</th><th>Estado</th><th width="90">Acción</th></tr></thead>
            <tbody id="tablaBody"></tbody>
        </table>

        <button class="btn-main btn-down" onclick="generarFinal()">📦 DESCARGAR (ZIP o EXCEL)</button>

        <div class="footer">
            Soporte Técnico: CARRILLO NARVAEZ JOHN STALIN | CELL 0996652042 | CORREO: cnjstalin@gmail.com
        </div>

    </div>

    <script>
        // --- GLOBALS & DB ---
        let db, registros = [], editIdx = -1;
        let activeMode = 'TRAMITE'; 
        let poolFiles = { main: null, anx: [], out: [], copy: [] };
        const MEM_KEYS = { remitente: 'd_m_rem', cargo: 'd_m_car', u_origen: 'd_m_uor', rec_turno: 'd_m_rtu', u_destinos: 'd_m_ude', rec_respuestas: 'd_m_rre' };

        window.onload = () => {
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
                
                // Bloquear Remitente, Cargo, Unidad
                document.getElementById('rRem').disabled = true;
                document.getElementById('rCar').disabled = true;
                document.getElementById('rUni').disabled = true;
                
                // Fijar Obs
                document.getElementById('rObs').value = "GENERADO DESDE DESPACHO";
                
                // Bloquear subida seccion 3
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
                let zone = document.getElementById(id);
                if(!zone) return;
                
                zone.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); zone.classList.add('dragover'); });
                zone.addEventListener('dragleave', (e) => { e.preventDefault(); e.stopPropagation(); zone.classList.remove('dragover'); });
                zone.addEventListener('drop', (e) => {
                    e.preventDefault(); e.stopPropagation(); zone.classList.remove('dragover');
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
                let datos = capturarDatos(); 
                if (!datos) return; 

                if(activeMode !== 'COPIA') saveMemories(datos);

                if (editIdx > -1) { 
                    registros[editIdx] = datos; 
                    alert("✅ Registro ACTUALIZADO correctamente"); 
                } else { 
                    registros.push(datos); 
                }
                resetForm(); renderTable(); 
            } catch (e) {
                alert("Error: " + e.message); console.error(e);
            }
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
                let est = getVal('gEst');

                // En modo generado, drop_out esta desactivado, asegurarse de limpiar fOut
                let filesOut = (activeMode === 'GENERADO') ? [] : [...poolFiles.out];

                return {
                    tipo: 'TRAMITE',
                    rFd: getVal('rFd'), rRem: getVal('rRem'), rCar: getVal('rCar'), rUni: getVal('rUni'),
                    rNum: getVal('rNum'), rFr: getVal('rFr'), rAsu: getVal('rAsu'),
                    rDes: getVal('rDes'), rRec: getVal('rRec'), rObs: obsVal, 
                    fMain: poolFiles.main, fAnx: [...poolFiles.anx], fOut: filesOut,
                    gDes: getVal('gDes'), gTip: tVal, gRec: getVal('gRec'), gNum: getVal('gNum'),
                    gFem: getVal('gFem'), gEst: est, 
                    sExt: getVal('sExt'), sDes: getVal('sDes'), sNum: getVal('sNum'), sFs: getVal('sFs'), sFr: getVal('sFr')
                };
            }
        }

        function editar(i) {
            editIdx = i; let r = registros[i];
            let btn = document.getElementById('btnMain'); 
            btn.innerHTML = "💾 ACTUALIZAR REGISTRO"; btn.className = "btn-main btn-update";
            
            poolFiles = { main: r.fMain || null, anx: r.fAnx ? [...r.fAnx] : [], out: r.fOut ? [...r.fOut] : [], copy: r.fCopy ? [...r.fCopy] : [] };
            
            if (r.tipo === 'COPIA') {
                activeMode = 'COPIA'; setVal('cNum', r.num);
            } else {
                if (r.rObs === 'GENERADO DESDE DESPACHO') activeMode = 'GENERADO';
                else activeMode = 'TRAMITE';

                setVal('rFd', r.rFd); setVal('rRem', r.rRem); setVal('rCar', r.rCar); setVal('rUni', r.rUni);
                setVal('rNum', r.rNum); setVal('rFr', r.rFr); setVal('rAsu', r.rAsu); setVal('rDes', r.rDes); setVal('rRec', r.rRec);
                
                let baseObs = ['REASIGNADO','GENERADO DESDE DESPACHO','CONOCIMIENTO PARA MI CORONEL','NINGUNA'].includes(r.rObs) ? r.rObs : 'OTRO';
                setVal('rObs', baseObs); 
                if(baseObs==='OTRO') { document.getElementById('rObsO').style.display='block'; setVal('rObsO', r.rObs); }
                
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
                
                if(r.tipo==='COPIA'){ 
                    css="row-copia"; st="COPIA"; num=r.num; 
                } else {
                    num = (r.rObs === 'GENERADO DESDE DESPACHO') ? (r.gNum ? r.gNum : '(SIN NÚMERO)') : r.rNum;
                    if(st==='PENDIENTE'){ css="row-pend"; } else { css="row-ok"; }
                }

                tr.className = css;
                tr.innerHTML = `<td>${i+1}</td><td><b>${num}</b></td><td>${desc}</td><td><span class="badge">${st}</span></td><td><button class="act-btn act-edit" onclick="editar(${i})">✏️</button><button class="act-btn act-del" onclick="borrar(${i})">X</button></td>`;
                tbody.appendChild(tr);
            });
        }

        // --- EXCEL & ZIP LOGIC ---
        function generarFinal() {
            if(registros.length===0) return alert("Vacio."); overlay(true,"Generando...");
            let hasFiles = registros.some(r => r.fMain || (r.fAnx && r.fAnx.length) || (r.fOut && r.fOut.length) || (r.fCopy && r.fCopy.length));
            let tx = db.transaction(['files'], 'readonly');
            tx.objectStore('files').get('plantilla').onsuccess = e => {
                if(e.target.result) {
                    if (hasFiles) procesarZip(e.target.result); else procesarSoloExcel(e.target.result);
                } else { overlay(false); alert("Falta Plantilla."); }
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
                        cc++; 
                        if(fCop && r.fCopy && r.fCopy.length) {
                            let tg = fCop.folder(`${cc}. ${safe(r.num)}`); 
                            r.fCopy.forEach(f => tg.file(f.name, f)); 
                        }
                    } else {
                        ct++;
                        if (r.fMain || (r.fAnx && r.fAnx.length) || (r.fOut && r.fOut.length)) {
                            let suffix = "";
                            if(['REASIGNADO','CONOCIMIENTO PARA MI CORONEL','GENERADO DESDE DESPACHO'].includes(r.rObs)) suffix = " " + r.rObs;
                            let docName = (r.rObs === 'GENERADO DESDE DESPACHO') ? safe(r.gNum) : safe(r.rNum);
                            let folderName = `${ct}. ${docName}${suffix}`;
                            
                            let tg = fTram.folder(folderName);
                            if(r.fMain) tg.file(`${docName} PRINCIPAL.${ext(r.fMain.name)}`, r.fMain);
                            if(r.fAnx) r.fAnx.forEach((f,k)=>tg.file(`${docName} ANEXO ${k+1} ${f.name}`, f));
                            if(r.fOut) r.fOut.forEach((f,k)=>tg.file(`${r.gNum?safe(r.gNum):'RESP'} RESPUESTA ${k+1} ${f.name}`, f));
                        }
                    }
                });

                const buf = await workbook.xlsx.writeBuffer();
                root.file(`${nameRef}.xlsx`, buf); 
                const cnt = await zip.generateAsync({type:"blob"}); 
                saveAs(cnt, `${nameRef}.zip`); overlay(false);

            } catch(e){ overlay(false); alert("Error ZIP: "+e); }
        }

        function fillSheet(workbook) {
            let sheet = workbook.getWorksheet("CONTROL DE GESTIÓN") || workbook.getWorksheet(1);
            
            // LISTA DE OBS QUE PINTAN TODA LA FILA
            const obsGray = ['REASIGNADO', 'GENERADO DESDE DESPACHO', 'CONOCIMIENTO PARA MI CORONEL'];

            // VARIABLES PARA CONTROLAR LA ESCRITURA EN EXCEL (SIN COPIAS)
            let excelRow = 7;
            let order = 1;

            registros.forEach((r) => {
                
                // SI ES COPIA, NO ESCRIBIMOS NADA EN EL EXCEL (PERO SI EN EL ZIP)
                if(r.tipo === 'COPIA') return;

                let row = sheet.getRow(excelRow);
                row.getCell(1).value = order; // Columna A Correlativa

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
                
                // PINTADO CONDICIONAL DE LA FILA
                if(obsGray.includes(r.rObs)) {
                        row.eachCell(c => c.fill={type:'pattern',pattern:'solid',fgColor:{argb:'FFCFD8DC'}});
                } else {
                        // SOLO SEMÁFORO
                        let color = r.gEst === 'PENDIENTE' ? 'FFEF9A9A' : 'FFA5D6A7';
                        row.getCell(19).fill={type:'pattern',pattern:'solid',fgColor:{argb: color}};
                }
                
                row.commit();
                
                // AVANZAMOS EL CONTADOR SOLO SI SE ESCRIBIÓ
                excelRow++;
                order++;
            });
        }

        // --- LOGIC UI & STATUS ---
        function logicObs(){ 
            let o=getVal('rObs');
            document.getElementById('sDes').readOnly=true; 
            document.getElementById('rObsO').style.display='none'; 

            if(o==='REASIGNADO' || o==='CONOCIMIENTO PARA MI CORONEL'){ 
                document.getElementById('gEst').value = "FINALIZADO";
                if(o==='REASIGNADO'){
                    document.getElementById('gNum').disabled=true; document.getElementById('gNum').value=""; 
                    document.getElementById('sNum').disabled=true; document.getElementById('sNum').value=""; 
                } else {
                     document.querySelectorAll('#sec3 input, #sec3 select, #sec4 input, #sec4 select').forEach(e=>e.disabled=true);
                }
            } else if(o==='GENERADO DESDE DESPACHO'){ 
                syncRespuesta();
            } else if(o==='OTRO'){ 
                document.getElementById('rObsO').style.display='block'; 
                syncRespuesta();
            } else {
                syncRespuesta();
            }
        }

        function syncRespuesta() { 
            let o = getVal('rObs');
            if(o === 'REASIGNADO' || o === 'CONOCIMIENTO PARA MI CORONEL') return;
            let inp = document.getElementById('gNum'); cleanPNSync(inp); let val = inp.value.trim(); 
            document.getElementById('sNum').value = val; 
            document.getElementById('gEst').value = val.length > 0 ? "FINALIZADO" : "PENDIENTE";
        }

        // --- BACKUP ---
        async function guardarRespaldo() {
            if(registros.length===0) return alert("Vacio"); overlay(true,"Guardando...");
            const zip = new JSZip();
            let meta = registros.map(r=>{ 
                let c={...r}; 
                c.nMain = r.fMain ? r.fMain.name : null;
                c.nAnx = r.fAnx ? r.fAnx.map(f=>f.name) : [];
                c.nOut = r.fOut ? r.fOut.map(f=>f.name) : [];
                c.nCopy = r.fCopy ? r.fCopy.map(f=>f.name) : [];
                delete c.fMain; delete c.fAnx; delete c.fOut; delete c.fCopy;
                return c; 
            });
            zip.file("data.json", JSON.stringify(meta));
            let ast = zip.folder("assets");
            registros.forEach((r,i)=>{ 
                if(r.fMain) ast.file(`${i}_main`, r.fMain);
                if(r.fAnx) r.fAnx.forEach((f,k)=>ast.file(`${i}_anx_${k}`,f));
                if(r.fOut) r.fOut.forEach((f,k)=>ast.file(`${i}_out_${k}`, f));
                if(r.fCopy) r.fCopy.forEach((f,k)=>ast.file(`${i}_copy_${k}`, f));
            });
            let blob = await zip.generateAsync({type:"blob"});
            saveAs(blob, `RESPALDO ${getNaming()}.dinic`); overlay(false);
        }

        async function restaurarRespaldo(inp) {
            if(!inp.files[0]) return; overlay(true,"Cargando...");
            try {
                let zip = await JSZip.loadAsync(inp.files[0]);
                let meta = JSON.parse(await zip.file("data.json").async("string"));
                registros = [];
                for(let i=0; i<meta.length; i++){
                    let r = meta[i]; 
                    r.fMain = null; r.fAnx = []; r.fOut = []; r.fCopy = [];
                    if(r.nMain) { let b=await zip.file(`assets/${i}_main`).async("blob"); r.fMain=new File([b], r.nMain); }
                    if(r.nAnx) for(let k=0; k<r.nAnx.length; k++) { let b=await zip.file(`assets/${i}_anx_${k}`).async("blob"); r.fAnx.push(new File([b], r.nAnx[k])); }
                    if(r.nOut) for(let k=0; k<r.nOut.length; k++) { let b=await zip.file(`assets/${i}_out_${k}`).async("blob"); r.fOut.push(new File([b], r.nOut[k])); }
                    if(r.nCopy) for(let k=0; k<r.nCopy.length; k++) { let b=await zip.file(`assets/${i}_copy_${k}`).async("blob"); r.fCopy.push(new File([b], r.nCopy[k])); }
                    registros.push(r);
                }
                renderTable(); overlay(false); alert("✅ Restaurado");
            } catch(e){ overlay(false); alert("Error restauración: " + e); console.log(e); } inp.value="";
        }

        // --- UTILS ---
        function triggerUpload(){ document.getElementById('inPlantilla').click(); }
        function guardarPlantillaDB(inp){ if(!inp.files[0])return; overlay(true); let r=new FileReader(); r.onload=e=>{ let b=new Blob([e.target.result],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}); let t=db.transaction(['files'],'readwrite'); t.objectStore('files').put(b,'plantilla'); t.oncomplete=()=>{overlay(false); checkPlantilla(); alert("Plantilla Guardada");}; }; r.readAsArrayBuffer(inp.files[0]); }
        function checkPlantilla(){ if(!db)return; db.transaction(['files'],'readonly').objectStore('files').get('plantilla').onsuccess=e=>{ document.getElementById('led').className=e.target.result?"led on":"led"; document.getElementById('ledTxt').innerText=e.target.result?"Plantilla Lista":"Falta Plantilla"; }; }
        function nuevoTurno(){ if(confirm("¿Nuevo turno? Se limpia la lista.")){ registros=[]; renderTable(); resetForm(); } }
        function borrarTodo(){ if(confirm("¿Seguro? Borrará todo.")){ localStorage.clear(); location.reload(); } }
        
        function resetForm(){ 
            editIdx=-1; 
            activeMode='TRAMITE';
            poolFiles={main:null,anx:[],out:[],copy:[]}; 
            document.getElementById('btnMain').innerText="➕ AGREGAR TRÁMITE A LA LISTA"; 
            document.getElementById('btnMain').className="btn-main btn-add"; 
            document.querySelectorAll('input:not([type=file]), textarea').forEach(i=>i.value=""); 
            setToday(); 
            applyModeUI(); 
            document.querySelectorAll('.file-list-box').forEach(d=>d.innerHTML="");
            document.querySelectorAll('.ac-box').forEach(s=>s.style.display='none'); 
        }

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
        function overlay(s,t){ document.getElementById('loader').style.display=s?'block':'none'; if(t)document.getElementById('loadText').innerText=t; }
        
        // --- MEMORY ---
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
# 3. FUNCIONES AUXILIARES DE PYTHON (Gestión de Usuarios)
# ==============================================================================
def get_hora_ecuador(): 
    return datetime.now(timezone(timedelta(hours=-5)))

def get_logo_html(width="120px"):
    return f'<img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" style="width:{width}; margin-bottom:15px;">'

# Simulación de Base de Datos de Usuarios
USUARIOS_BASE = {
    "0702870460": {"grado": "SGOS", "nombre": "VILLALTA OCHOA XAVIER BISMARK", "activo": True},
    "1715081731": {"grado": "SGOS", "nombre": "MINDA MINDA FRANCISCO GABRIEL", "activo": True},
    "1723623011": {"grado": "CBOS", "nombre": "CARRILLO NARVAEZ JOHN STALIN", "activo": True}
}
DB_FILE = "usuarios_db.json"

def cargar_usuarios():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return USUARIOS_BASE
    return USUARIOS_BASE

db_usuarios = cargar_usuarios()

# ==============================================================================
# 4. GESTIÓN DE SESIÓN
# ==============================================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = ""
if 'usuario_turno' not in st.session_state: st.session_state.usuario_turno = ""
if 'active_module' not in st.session_state: st.session_state.active_module = 'secretario'

# ==============================================================================
# 5. INTERFAZ PRINCIPAL
# ==============================================================================

if not st.session_state.logged_in:
    # --- PANTALLA DE LOGIN ---
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="login-container">{get_logo_html()}<h2 style='color:#0E2F44; margin-bottom: 5px;'>ACCESO SIGD DINIC</h2><p style='color: gray; margin-top: 0;'>Sistema Oficial de Gestión Documental</p></div>""", unsafe_allow_html=True)
        with st.form("login_form"):
            usuario_input = st.text_input("Usuario (Cédula):").strip()
            pass_input = st.text_input("Contraseña:", type="password").strip()
            
            if st.form_submit_button("INGRESAR AL SISTEMA", type="primary"):
                # Lógica Admin
                if usuario_input == ADMIN_USER and pass_input == ADMIN_PASS_MASTER:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.session_state.usuario_turno = "ADMINISTRADOR PRINCIPAL"
                    st.rerun()
                # Lógica Usuario Normal
                elif usuario_input in db_usuarios:
                    user_data = db_usuarios[usuario_input]
                    # Contraseña genérica para usuarios (ajustar según necesidad)
                    if pass_input == "DINIC2026": 
                        st.session_state.logged_in = True
                        st.session_state.user_role = "user"
                        st.session_state.usuario_turno = f"{user_data['grado']} {user_data['nombre']}"
                        st.rerun()
                    else:
                        st.error("🚫 Contraseña incorrecta.")
                else:
                    st.error("🚫 Usuario no autorizado.")

else:
    # --- SISTEMA AUTENTICADO ---
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png", width=100)
        st.markdown("### 👮‍♂️ CONTROL DE MANDO")
        
        if st.session_state.user_role == "admin":
            st.info("🛡️ MODO ADMIN ACTIVADO")
            
        st.write(f"👤 **{st.session_state.usuario_turno}**")
        st.caption(f"📅 Fecha: {get_hora_ecuador().strftime('%Y-%m-%d')}")
        
        st.markdown("---")
        st.markdown("### 📂 MÓDULOS")
        
        if st.button("📝 SECRETARIO/A", use_container_width=True, type="primary" if st.session_state.active_module == 'secretario' else "secondary"): 
            st.session_state.active_module = 'secretario'; st.rerun()
            
        if st.button("🧠 ASESOR INTELIGENTE", use_container_width=True, type="primary" if st.session_state.active_module == 'asesor' else "secondary"): 
            st.session_state.active_module = 'asesor'; st.rerun()
            
        if st.button("👤 TALENTO HUMANO", use_container_width=True, type="primary" if st.session_state.active_module == 'th' else "secondary"): 
            st.session_state.active_module = 'th'; st.rerun()
            
        if st.session_state.user_role == "admin":
            if st.button("🛡️ ADMINISTRADOR", use_container_width=True, type="primary" if st.session_state.active_module == 'admin' else "secondary"): 
                st.session_state.active_module = 'admin'; st.rerun()
        
        st.markdown("---")
        if st.button("🔒 CERRAR SESIÓN"): 
            st.session_state.logged_in = False
            st.rerun()

    # --- LÓGICA DE MÓDULOS ---

    # 1. MÓDULO SECRETARIO (MOTOR V44 INCRUSTADO)
    if st.session_state.active_module == 'secretario':
        # Renderizamos el HTML/JS puro. 
        # height=1200 asegura que se vea todo sin doble scroll molesto.
        components.html(HTML_SECRETARIO_V44, height=1200, scrolling=True)

    # 2. MÓDULO ASESOR (Placeholder para futura re-integración o lógica simple)
    elif st.session_state.active_module == 'asesor':
        st.title("🧠 Asesor Inteligente")
        st.info("Este módulo está en mantenimiento para optimización de IA.")
        # Aquí puedes volver a poner tu código de Gemini cuando lo ajustemos

    # 3. MÓDULO TALENTO HUMANO
    elif st.session_state.active_module == 'th':
        st.title("👤 Talento Humano")
        st.warning("Área restringida. Ingrese credenciales de TH.")
        # Aquí iría la lógica de TH

    # 4. MÓDULO ADMIN
    elif st.session_state.active_module == 'admin':
        st.title("🛡️ Panel de Administrador")
        st.write("Gestión de Usuarios y Logs del Sistema.")
        st.dataframe(pd.DataFrame.from_dict(db_usuarios, orient='index'))
