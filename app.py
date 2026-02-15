import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA (FULL WIDE)
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC | Nivel Central",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. ESTILOS CSS MAESTROS (EL NUEVO LOOK)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTAR FUENTE */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Roboto:wght@300;400;700&display=swap');

    /* RESET GENERAL */
    .stApp {
        background: radial-gradient(circle at center, #1a2a3a 0%, #0b1219 100%);
        font-family: 'Roboto', sans-serif;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    /* --- DASHBOARD CENTRAL --- */
    .dashboard-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 40px;
        background-image: 
            linear-gradient(rgba(11, 18, 25, 0.9), rgba(11, 18, 25, 0.9)),
            url("https://www.transparenttextures.com/patterns/cubes.png");
    }

    .hero-section {
        text-align: center;
        margin-bottom: 60px;
        animation: fadeIn 1.5s ease;
    }

    .hero-logo {
        width: 100px;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5));
    }

    .hero-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 0 0 20px rgba(0, 168, 255, 0.6);
        margin: 0;
    }

    .hero-subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.5rem;
        color: #D4AF37; /* Dorado Policial */
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 10px;
        border-top: 1px solid rgba(212, 175, 55, 0.3);
        display: inline-block;
        padding-top: 10px;
    }

    /* GRID DE TARJETAS */
    .card-container {
        display: flex;
        gap: 30px;
        flex-wrap: wrap;
        justify-content: center;
        max-width: 1400px;
        width: 100%;
    }

    /* ESTILO DE LOS BOTONES QUE PARECEN TARJETAS */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        height: 250px !important;
        width: 100% !important;
        min-width: 250px !important;
        border-radius: 15px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1) !important;
    }

    div.stButton > button:hover {
        background: rgba(14, 47, 68, 0.6) !important;
        border-color: #D4AF37 !important;
        transform: translateY(-10px) !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4) !important;
        color: #D4AF37 !important;
    }

    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* EFECTOS DE ANIMACIÓN */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- BOTÓN FLOTANTE HOME --- */
    .floating-home {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }
    .floating-home button {
        height: 60px !important;
        width: 60px !important;
        min-width: 0 !important;
        border-radius: 50% !important;
        background: #D4AF37 !important;
        color: #000 !important;
        font-size: 24px !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.6) !important;
        border: none !important;
    }
    .floating-home button:hover {
        transform: rotate(90deg) !important;
        background: #fff !important;
    }

    /* LOGIN STYLES */
    .login-box {
        background: rgba(11, 18, 25, 0.85);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        text-align: center;
        width: 100%;
        max-width: 400px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HTML DEL MOTOR V44 (AHORA EN DARK MODE REAL)
# ==============================================================================
# He reescrito el CSS interno de este HTML para que coincida con el tema oscuro
HTML_SECRETARIO_DARK = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>GESTOR DARK</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">

    <style>
        /* MODO OSCURO TOTAL */
        body { 
            font-family: 'Roboto', sans-serif; 
            background: transparent; /* Transparente para usar el fondo de Streamlit */
            padding: 20px; 
            color: #e0e0e0; 
            margin: 0; 
            padding-top: 90px;
            padding-bottom: 50px;
        }

        /* HEADER FLOTANTE */
        .top-header { 
            position: fixed; top: 20px; left: 50%; transform: translateX(-50%); width: 95%; max-width: 1600px;
            background: rgba(20, 30, 40, 0.95); 
            backdrop-filter: blur(10px);
            color: white; 
            z-index: 1000; 
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
        }

        .header-title { font-weight: 700; font-size: 18px; letter-spacing: 1px; color: #D4AF37; display: flex; align-items: center; gap: 10px; }
        .header-tools { display: flex; gap: 10px; }

        /* CONTENEDOR PRINCIPAL */
        .container { 
            width: 95%; max-width: 1600px; margin: 0 auto; 
            background: rgba(30, 40, 50, 0.6); 
            padding: 30px; 
            border-radius: 16px; 
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 4px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(5px);
        }

        /* BOTONES MODERNOS */
        button { font-family: 'Roboto', sans-serif; }
        .btn-neon {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.2);
            color: #ccc;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            transition: 0.3s;
        }
        .btn-neon:hover { background: rgba(255,255,255,0.1); color: white; border-color: white; }
        
        .btn-action { background: #D4AF37; color: #000; border: none; box-shadow: 0 0 10px rgba(212, 175, 55, 0.3); }
        .btn-action:hover { background: #fff; box-shadow: 0 0 20px rgba(212, 175, 55, 0.6); }

        .btn-main {
            width: 100%; padding: 15px; margin: 20px 0; border:none; border-radius: 8px;
            font-size: 14px; font-weight: bold; letter-spacing: 1px; cursor: pointer;
            text-transform: uppercase;
        }
        .add { background: linear-gradient(90deg, #2e7d32, #66bb6a); color: white; box-shadow: 0 5px 15px rgba(46, 125, 50, 0.4); }
        .add:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(46, 125, 50, 0.6); }
        .dl { background: linear-gradient(90deg, #0277bd, #29b6f6); color: white; box-shadow: 0 5px 15px rgba(2, 119, 189, 0.4); }

        /* INPUTS OSCUROS */
        label { color: #90a4ae; font-size: 11px; font-weight: 700; margin-bottom: 5px; text-transform: uppercase; display: block; }
        input, select, textarea { 
            width: 100%; padding: 12px; 
            background: #0f161f; 
            border: 1px solid #2c3e50; 
            border-radius: 6px; 
            color: white; font-size: 13px; font-family: 'Roboto', sans-serif;
            box-sizing: border-box; transition: 0.3s;
        }
        input:focus, select:focus, textarea:focus { border-color: #D4AF37; outline: none; box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2); }
        
        /* SECCIONES */
        .seccion { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
        .seccion h3 { color: #fff; margin-top: 0; font-size: 14px; border-left: 3px solid #D4AF37; padding-left: 10px; margin-bottom: 20px; }

        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        .full { grid-column: 1 / -1; }

        /* DROP AREA */
        .drop-area { border: 2px dashed #455a64; background: rgba(0,0,0,0.1); padding: 20px; border-radius: 8px; text-align: center; cursor: pointer; transition: 0.3s; }
        .drop-area:hover { border-color: #D4AF37; background: rgba(212, 175, 55, 0.05); }
        .drop-txt { color: #78909c; font-weight: 600; font-size: 12px; }

        .file-list-box { margin-top: 5px; }
        .file-item { background: #263238; padding: 5px 10px; border-radius: 4px; font-size: 11px; margin-bottom: 2px; display: flex; justify-content: space-between; align-items: center; }

        /* TABLA */
        table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 20px; }
        th { background: #19232d; color: #D4AF37; padding: 12px; text-align: left; font-size: 12px; border-bottom: 2px solid #D4AF37; }
        td { background: #121a21; padding: 10px; border-bottom: 1px solid #263238; font-size: 12px; color: #cfd8dc; }
        
        .status { padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; }
        .st-pend { background: rgba(244, 67, 54, 0.2); color: #ef5350; border: 1px solid #ef5350; }
        .st-ok { background: rgba(102, 187, 106, 0.2); color: #66bb6a; border: 1px solid #66bb6a; }

        /* UTILS */
        .hidden { display: none; }
        .mode-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .mode-btn { padding: 15px; border-radius: 8px; text-align: center; cursor: pointer; border: 1px solid #333; background: #151f28; font-weight: bold; color: #78909c; transition: 0.3s; }
        .mode-btn.active { background: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); border-color: #D4AF37; }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f161f; }
        ::-webkit-scrollbar-thumb { background: #37474f; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #D4AF37; }

        /* AUTOCOMPLETE DARK */
        .ac-box { position: absolute; width: 100%; background: #1e2732; border: 1px solid #455a64; z-index: 999; max-height: 150px; overflow-y: auto; }
        .ac-item { padding: 8px; cursor: pointer; font-size: 12px; color: #b0bec5; border-bottom: 1px solid #263238; }
        .ac-item:hover { background: #D4AF37; color: black; }
        .ac-wrap { position: relative; }

    </style>
</head>
<body>

    <div class="top-header">
        <div class="header-title">🛡️ SIGD DINIC | SECRETARÍA</div>
        <div class="header-tools">
            <button class="btn-neon" onclick="document.getElementById('inPlantilla').click()">📂 Plantilla</button>
            <button class="btn-neon" onclick="guardarRespaldo()">⬇️ Backup</button>
            <button class="btn-neon" onclick="document.getElementById('inRestore').click()">⬆️ Restore</button>
            <span style="border-right: 1px solid rgba(255,255,255,0.2); margin: 0 5px;"></span>
            <button class="btn-neon btn-action" onclick="nuevoTurno()">✨ Nuevo</button>
        </div>
    </div>
    
    <input type="file" id="inPlantilla" class="hidden" accept=".xlsx" onchange="guardarPlantillaDB(this)">
    <input type="file" id="inRestore" class="hidden" accept=".dinic" onchange="restaurarRespaldo(this)">

    <div class="container">
        <div class="mode-bar">
            <div id="btnModeCopia" class="mode-btn" onclick="toggleMode('COPIA')">⚠️ ES COPIA</div>
            <div id="btnModeGen" class="mode-btn" onclick="toggleMode('GENERADO')">⚙️ GENERADO DESDE DESPACHO</div>
        </div>

        <div id="secCopia" class="seccion hidden" style="border-color: #ff9800;">
            <h3>REGISTRO DE COPIA</h3>
            <div class="grid-3">
                <div class="full"><label>N° Oficio / Memo:</label><input type="text" id="cNum" oninput="cleanPNSync(this)"></div>
                <div class="full">
                    <label>Archivos:</label>
                    <div class="drop-area" id="drop_copy" onclick="document.getElementById('cFile').click()">
                        <div class="drop-txt">📂 Click o Arrastrar</div>
                        <input type="file" id="cFile" multiple class="hidden" onchange="handleFiles(this.files, 'copy')">
                    </div>
                    <div id="list_copy" class="file-list-box"></div>
                </div>
            </div>
        </div>

        <div id="secTramite">
            <div class="seccion">
                <h3>1. RECEPCIÓN</h3>
                <div class="grid-3">
                    <div><label>Fecha Doc:</label><input type="date" id="rFd"></div>
                    <div><label>Remitente:</label><div class="ac-wrap"><input type="text" id="rRem" autocomplete="off"><div id="ac_rRem" class="ac-box"></div></div></div>
                    <div><label>Cargo:</label><div class="ac-wrap"><input type="text" id="rCar" autocomplete="off"><div id="ac_rCar" class="ac-box"></div></div></div>
                    <div><label>Origen:</label><div class="ac-wrap"><input type="text" id="rUni" autocomplete="off"><div id="ac_rUni" class="ac-box"></div></div></div>
                    
                    <div><label style="color:#64b5f6;">N° DOCUMENTO:</label><input type="text" id="rNum" oninput="cleanPNSync(this)" style="background:#0d47a1; border-color:#2962ff; font-weight:bold;"></div>
                    
                    <div><label>Fecha Rec:</label><input type="date" id="rFr"></div>
                    <div class="full"><label>Asunto:</label><input type="text" id="rAsu"></div>
                    <div class="full"><label>Resumen:</label><textarea id="rDes" rows="1"></textarea></div>
                    
                    <div><label>Recibido Por:</label><div class="ac-wrap"><input type="text" id="rRec" autocomplete="off"><div id="ac_rRec" class="ac-box"></div></div></div>
                    
                    <div class="full">
                        <label>Observación Especial:</label>
                        <select id="rObs" onchange="logicObs()">
                            <option value="NINGUNA">NINGUNA</option>
                            <option value="REASIGNADO">REASIGNADO (Finaliza)</option>
                            <option value="GENERADO DESDE DESPACHO">GENERADO DESDE DESPACHO</option>
                            <option value="CONOCIMIENTO PARA MI CORONEL">CONOCIMIENTO (Finaliza)</option>
                            <option value="OTRO">OTRO</option>
                        </select>
                        <input type="text" id="rObsO" class="hidden" placeholder="Especifique" style="margin-top:5px;">
                    </div>
                </div>
                
                <div class="grid-3" style="margin-top:15px;">
                    <div class="full">
                        <div style="display:flex; gap:10px;">
                            <div class="drop-area" style="flex:1; border-color:#0277bd;" id="drop_main" onclick="document.getElementById('rFileMain').click()">
                                <div class="drop-txt" style="color:#0277bd;">📄 PRINCIPAL</div>
                                <input type="file" id="rFileMain" class="hidden" onchange="handleFiles(this.files, 'main')">
                                <div id="list_main" class="file-list-box"></div>
                            </div>
                            <div class="drop-area" style="flex:1; border-color:#2e7d32;" id="drop_anx" onclick="document.getElementById('rFileAnx').click()">
                                <div class="drop-txt" style="color:#2e7d32;">📎 ANEXOS</div>
                                <input type="file" id="rFileAnx" multiple class="hidden" onchange="handleFiles(this.files, 'anx')">
                                <div id="list_anx" class="file-list-box"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="seccion" id="sec3">
                <h3>2. GESTIÓN</h3>
                <div class="grid-3">
                    <div class="full"><label>Pase a:</label><div class="ac-wrap"><input type="text" id="gDes" autocomplete="off"><div id="ac_gDes" class="ac-box"></div></div></div>
                    
                    <div><label>Formato:</label>
                        <select id="gTip" onchange="logicTip()">
                            <option>DOCPOL ELECTRÓNICO</option><option>QUIPUX ELECTRÓNICO</option>
                            <option>FISICO</option><option>DIGITAL</option><option>OTRO</option>
                        </select>
                        <input type="text" id="gTipO" class="hidden">
                    </div>

                    <div><label>Receptor:</label><div class="ac-wrap"><input type="text" id="gRec" autocomplete="off"><div id="ac_gRec" class="ac-box"></div></div></div>
                    
                    <div><label style="color:#64b5f6;">N° RESPUESTA:</label><input type="text" id="gNum" oninput="syncRespuesta()"></div>
                    <div><label>Fecha Emisión:</label><input type="date" id="gFem"></div>
                    <div><label>Estado:</label><input type="text" id="gEst" readonly style="font-weight:bold; text-align:center;"></div>
                    
                    <div class="full">
                        <div class="drop-area" style="border-color:#ad1457;" id="drop_out" onclick="document.getElementById('gFile').click()">
                            <div class="drop-txt" style="color:#ad1457;">📤 OFICIOS GENERADOS / RESPUESTAS</div>
                            <input type="file" id="gFile" multiple class="hidden" onchange="handleFiles(this.files, 'out')">
                        </div>
                        <div id="list_out" class="file-list-box"></div>
                    </div>
                </div>
            </div>

            <div class="seccion" id="sec4">
                <h3>3. CONTROL SALIDA</h3>
                <div class="grid-3">
                    <div><label>Externo?</label><select id="sExt"><option>NO</option><option>SI</option></select></div>
                    <div class="full"><label>Destino Final:</label><input type="text" id="sDes" readonly></div>
                    <div><label>N° Salida:</label><input type="text" id="sNum" readonly></div>
                    <div><label>F. Salida:</label><input type="date" id="sFs"></div>
                    <div><label>F. Recepción:</label><input type="date" id="sFr"></div>
                </div>
            </div>
        </div>

        <button id="btnMain" class="btn-main add" onclick="agregarRegistro()">➕ AGREGAR A LA COLA</button>

        <table>
            <thead><tr><th>#</th><th>DOC ENTRADA</th><th>ASUNTO</th><th>ESTADO</th><th>ACCIÓN</th></tr></thead>
            <tbody id="tablaBody"></tbody>
        </table>

        <button class="btn-main dl" onclick="generarFinal()">📦 DESCARGAR PAQUETE (ZIP + EXCEL)</button>

    </div>

    <script>
        let db, registros=[], editIdx=-1, activeMode='TRAMITE', poolFiles={main:null,anx:[],out:[],copy:[]};
        const MEM={rRem:'m_rem',rCar:'m_car',rUni:'m_uni',rRec:'m_rec',gDes:'m_des',gRec:'m_grec'};

        window.onload=()=>{
            let r=indexedDB.open("DINIC_DARK_DB",1);
            r.onupgradeneeded=e=>{let d=e.target.result;if(!d.objectStoreNames.contains('files'))d.createObjectStore('files');};
            r.onsuccess=e=>{db=e.target.result;};
            setToday(); initAuto(); setupDnD();
            document.getElementById('rFd').addEventListener('input',function(){let v=this.value;if(v)['rFr','gFem','sFs','sFr'].forEach(id=>document.getElementById(id).value=v);});
            logicObs();
        };

        function toggleMode(m){
            activeMode=(activeMode===m)?'TRAMITE':m;
            document.querySelectorAll('.mode-btn').forEach(b=>b.classList.remove('active'));
            if(activeMode!=='TRAMITE') document.getElementById(activeMode==='COPIA'?'btnModeCopia':'btnModeGen').classList.add('active');
            
            document.getElementById('secCopia').classList.add('hidden');
            document.getElementById('secTramite').classList.remove('hidden');
            
            // Reset
            document.querySelectorAll('#secTramite input, #secTramite select, #secTramite textarea').forEach(e=>e.disabled=false);
            
            if(activeMode==='COPIA'){
                document.getElementById('secCopia').classList.remove('hidden');
                document.getElementById('secTramite').classList.add('hidden');
            } else if(activeMode==='GENERADO'){
                ['rRem','rCar','rUni'].forEach(id=>document.getElementById(id).disabled=true);
                document.getElementById('rObs').value="GENERADO DESDE DESPACHO";
                logicObs();
            } else {
                document.getElementById('rObs').value="NINGUNA";
                logicObs();
            }
        }

        function agregarRegistro(){
            try{
                let d=capturar(); if(!d)return;
                if(activeMode!=='COPIA') saveMem(d);
                if(editIdx>-1) registros[editIdx]=d; else registros.push(d);
                alert("✅ Guardado"); reset(); render();
            }catch(e){alert(e);}
        }

        function capturar(){
            if(activeMode==='COPIA'){
                let n=val('cNum'); if(!n) throw "Falta Número";
                return {tipo:'COPIA',num:n,fCopy:[...poolFiles.copy]};
            }
            let o=val('rObs');
            if(o!=='GENERADO DESDE DESPACHO' && !val('rNum')) throw "Falta N° Documento";
            let obsF = o==='OTRO'?val('rObsO'):o;
            let est = val('gNum')?"FINALIZADO":"PENDIENTE";
            if(o.includes("REASIGNADO") || o.includes("CONOCIMIENTO")) est="FINALIZADO";
            
            return {
                tipo:'TRAMITE',
                rFd:val('rFd'), rRem:val('rRem'), rCar:val('rCar'), rUni:val('rUni'),
                rNum:val('rNum'), rFr:val('rFr'), rAsu:val('rAsu'), rDes:val('rDes'), rRec:val('rRec'), rObs:obsF,
                gDes:val('gDes'), gTip:val('gTip'), gRec:val('gRec'), gNum:val('gNum'), gFem:val('gFem'), gEst:est,
                sExt:val('sExt'), sDes:val('sDes'), sNum:val('sNum'), sFs:val('sFs'), sFr:val('sFr'),
                fMain:poolFiles.main, fAnx:[...poolFiles.anx], fOut:[...poolFiles.out]
            };
        }

        function render(){
            let t=document.getElementById('tablaBody'); t.innerHTML="";
            registros.forEach((r,i)=>{
                let tr=document.createElement('tr');
                let css=r.gEst==='FINALIZADO'?'st-ok':'st-pend';
                let txt=r.gEst==='FINALIZADO'?'FINALIZADO':'PENDIENTE';
                if(r.tipo==='COPIA'){ txt="COPIA"; css="status"; }
                
                tr.innerHTML=`
                    <td>${i+1}</td>
                    <td><b>${r.tipo==='COPIA'?r.num:r.rNum}</b></td>
                    <td>${r.tipo==='COPIA'?'COPIA':r.rAsu}</td>
                    <td><span class="status ${css}">${txt}</span></td>
                    <td>
                        <button class="btn-neon" onclick="edit(${i})">✏️</button>
                        <button class="btn-neon" style="color:#ef5350; border-color:#ef5350;" onclick="del(${i})">X</button>
                    </td>
                `;
                t.appendChild(tr);
            });
        }

        function edit(i){
            editIdx=i; let r=registros[i];
            document.getElementById('btnMain').innerText="💾 ACTUALIZAR";
            poolFiles={main:r.fMain,anx:[...r.fAnx],out:[...r.fOut],copy:r.fCopy?[...r.fCopy]:[]};
            
            if(r.tipo==='COPIA'){
                toggleMode('COPIA'); document.getElementById('cNum').value=r.num;
            } else {
                if(r.rObs==='GENERADO DESDE DESPACHO') toggleMode('GENERADO'); else toggleMode('TRAMITE');
                setVal('rFd',r.rFd); setVal('rRem',r.rRem); setVal('rCar',r.rCar); setVal('rUni',r.rUni);
                setVal('rNum',r.rNum); setVal('rFr',r.rFr); setVal('rAsu',r.rAsu); setVal('rDes',r.rDes); setVal('rRec',r.rRec);
                
                let baseObs=['NINGUNA','REASIGNADO','GENERADO DESDE DESPACHO','CONOCIMIENTO PARA MI CORONEL'].includes(r.rObs)?r.rObs:'OTRO';
                document.getElementById('rObs').value=baseObs; logicObs();
                if(baseObs==='OTRO') document.getElementById('rObsO').value=r.rObs;

                setVal('gDes',r.gDes); setVal('gRec',r.gRec); setVal('gNum',r.gNum); setVal('gFem',r.gFem);
                setVal('sExt',r.sExt); setVal('sDes',r.sDes); setVal('sNum',r.sNum); setVal('sFs',r.sFs); setVal('sFr',r.sFr);
            }
            renderFiles();
        }

        function del(i){ if(confirm("¿Borrar?")) { registros.splice(i,1); render(); } }
        
        function reset(){
            editIdx=-1; toggleMode('TRAMITE');
            poolFiles={main:null,anx:[],out:[],copy:[]};
            document.getElementById('btnMain').innerText="➕ AGREGAR A LA COLA";
            document.querySelectorAll('input:not([type=file]),textarea').forEach(e=>e.value="");
            setToday(); renderFiles();
        }

        /* --- LOGICA ARCHIVOS --- */
        function setupDnD(){
            ['drop_main','drop_anx','drop_out','drop_copy'].forEach(id=>{
                let z=document.getElementById(id);
                z.ondragover=e=>{e.preventDefault(); z.style.borderColor='#D4AF37'; z.style.background='rgba(255,255,255,0.05)';};
                z.ondragleave=e=>{e.preventDefault(); z.style.borderColor=''; z.style.background='';};
                z.ondrop=e=>{e.preventDefault(); z.style.borderColor=''; z.style.background=''; handleFiles(e.dataTransfer.files, id.replace('drop_',''));};
            });
        }
        function handleFiles(fls, k){
            let ar=Array.from(fls);
            if(k==='main') poolFiles.main=ar[0]; else poolFiles[k]=poolFiles[k].concat(ar);
            renderFiles();
        }
        function renderFiles(){
            let h=(k,d)=>{ 
                let c=document.getElementById(d); c.innerHTML=""; 
                let arr=k==='main'?(poolFiles.main?[poolFiles.main]:[]):poolFiles[k];
                arr.forEach((f,i)=>{
                    c.innerHTML+=`<div class="file-item"><span>${f.name}</span> <span style="cursor:pointer;color:#ef5350;" onclick="rmFile('${k}',${i})">✖</span></div>`; 
                });
            };
            h('main','list_main'); h('anx','list_anx'); h('out','list_out'); h('copy','list_copy');
        }
        function rmFile(k,i){ if(k==='main') poolFiles.main=null; else poolFiles[k].splice(i,1); renderFiles(); }

        /* --- EXCEL & ZIP --- */
        function generarFinal(){
            if(!registros.length) return alert("Cola vacía");
            let tx=db.transaction(['files'],'readonly');
            tx.objectStore('files').get('plantilla').onsuccess=e=>{
                if(e.target.result) processPkg(e.target.result);
                else alert("⚠️ Falta Plantilla Excel (Subir arriba)");
            };
        }
        async function processPkg(blob){
            let zip=new JSZip(); let wb=new ExcelJS.Workbook();
            await wb.xlsx.load(await blob.arrayBuffer());
            
            let sheet=wb.getWorksheet(1);
            let rowIdx=7, count=1;

            let fRoot=zip.folder("TURNO DIGITAL");
            let fDocs=fRoot.folder("DOCUMENTOS");
            
            registros.forEach(r=>{
                if(r.tipo!=='COPIA'){
                    let row=sheet.getRow(rowIdx);
                    row.getCell(1).value=count;
                    row.getCell(3).value=fmt(r.rFd); row.getCell(4).value=r.rRem; row.getCell(5).value=r.rCar; row.getCell(6).value=r.rUni;
                    row.getCell(7).value=r.rNum; row.getCell(8).value=fmt(r.rFr); row.getCell(9).value=r.rAsu; row.getCell(10).value=r.rDes;
                    row.getCell(11).value=r.rRec; row.getCell(12).value=r.rObs;
                    
                    if(!r.rObs.includes("CONOCIMIENTO")){
                        row.getCell(13).value=r.gDes; row.getCell(14).value=r.gTip; row.getCell(15).value=r.gRec; row.getCell(16).value=r.gNum;
                        row.getCell(17).value=fmt(r.gFem); row.getCell(19).value=r.gEst;
                        row.getCell(20).value=r.sExt; row.getCell(21).value=r.sDes; row.getCell(22).value=r.sNum; 
                        row.getCell(23).value=fmt(r.sFs); row.getCell(24).value=fmt(r.sFr);
                    } else { row.getCell(19).value="FINALIZADO"; }
                    
                    // Colores
                    let c=r.gEst==='FINALIZADO'?'FFA5D6A7':'FFEF9A9A';
                    if(['REASIGNADO','GENERADO DESDE DESPACHO'].some(x=>r.rObs.includes(x))) c='FFCFD8DC';
                    row.getCell(19).fill={type:'pattern',pattern:'solid',fgColor:{argb:c}};
                    row.commit(); rowIdx++; count++;
                    
                    // Archivos
                    let name = r.rObs==='GENERADO DESDE DESPACHO' ? safe(r.gNum) : safe(r.rNum);
                    let fFolder = fDocs.folder(`${count-1}. ${name}`);
                    if(r.fMain) fFolder.file(`MAIN ${name}.${ext(r.fMain.name)}`, r.fMain);
                    r.fAnx.forEach((f,x)=>fFolder.file(`ANX ${x+1}.${ext(f.name)}`,f));
                    r.fOut.forEach((f,x)=>fFolder.file(`RESP ${x+1}.${ext(f.name)}`,f));
                }
            });

            let bXls=await wb.xlsx.writeBuffer();
            fRoot.file("CONTROL.xlsx", bXls);
            let bZip=await zip.generateAsync({type:"blob"});
            saveAs(bZip, "TURNO_DINIC.zip");
        }

        /* --- AUTOCOMPLETE & LOGIC --- */
        function initAuto(){ for(let k in MEM) setupAc(k, MEM[k]); }
        function setupAc(id, key){
            let inp=document.getElementById(id), box=document.getElementById('ac_'+id);
            inp.oninput=()=>{
                let t=inp.value.split(',').pop().trim().toLowerCase();
                let l=JSON.parse(localStorage.getItem(key)||'[]');
                let m=l.filter(x=>x.toLowerCase().includes(t));
                box.innerHTML=m.map(x=>`<div class="ac-item">${x}</div>`).join('');
            };
            box.onclick=e=>{ if(e.target.className==='ac-item'){
                let arr=inp.value.split(','); arr.pop(); arr.push(e.target.innerText); inp.value=arr.join(', ');
                box.innerHTML="";
            }};
        }
        function saveMem(d){
            let add=(k,v)=>{ if(!v)return; let l=JSON.parse(localStorage.getItem(k)||'[]'); if(!l.includes(v))l.push(v); localStorage.setItem(k,JSON.stringify(l)); };
            add(MEM.rRem,d.rRem); add(MEM.rCar,d.rCar); add(MEM.rUni,d.rUni);
            add(MEM.rRec,d.rRec); add(MEM.gDes,d.gDes); add(MEM.gRec,d.gRec);
        }

        /* --- UTILS --- */
        function val(id){return document.getElementById(id).value;}
        function setVal(id,v){document.getElementById(id).value=v;}
        function cleanPNSync(i){ if(i.value.toUpperCase().includes("PN-")) i.value=i.value.toUpperCase().match(/PN-.*/)[0]; }
        function logicObs(){ 
            let o=val('rObs'); document.getElementById('rObsO').classList.toggle('hidden',o!=='OTRO'); 
            if(o.includes('REASIGNADO')||o.includes('CONOCIMIENTO')) document.getElementById('gEst').value='FINALIZADO';
            syncRespuesta();
        }
        function logicTip(){ document.getElementById('gTipO').classList.toggle('hidden',val('gTip')!=='OTRO'); }
        function syncRespuesta(){ 
            let v=val('gNum'); document.getElementById('sNum').value=v; 
            if(!val('rObs').includes('REASIGNADO')) document.getElementById('gEst').value=v?'FINALIZADO':'PENDIENTE';
        }
        function setToday(){ let d=new Date().toISOString().split('T')[0]; ['rFd','rFr','gFem','sFs','sFr'].forEach(id=>document.getElementById(id).value=d); }
        function fmt(d){if(!d)return ""; let p=d.split('-'); return `${p[2]}/${p[1]}/${p[0]}`;}
        function safe(s){return s?s.replace(/[\/\\]/g,'-'):'SN';}
        function ext(n){return n.split('.').pop();}
        function guardarPlantillaDB(i){
            let r=new FileReader(); r.onload=e=>{
                let t=db.transaction(['files'],'readwrite'); t.objectStore('files').put(new Blob([e.target.result]),'plantilla');
                alert("Plantilla Guardada");
            }; r.readAsArrayBuffer(i.files[0]);
        }
    </script>
</body>
</html>
"""

# ==============================================================================
# 4. GESTIÓN DE USUARIOS
# ==============================================================================
USUARIOS_BASE = {"1723623011": "CBOS. CARRILLO JOHN", "ADMIN": "SISTEMA CENTRAL"}
PASS_MASTER = "9994915010022"

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active_page' not in st.session_state: st.session_state.active_page = 'dashboard'
if 'usuario' not in st.session_state: st.session_state.usuario = ""

# ==============================================================================
# 5. LÓGICA DE PÁGINAS
# ==============================================================================
def nav_to(page): st.session_state.active_page = page; st.rerun()

if not st.session_state.logged_in:
    # --- LOGIN GLASSMORPHISM ---
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="login-box" style="margin: 0 auto;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" width="100">
                <h2 style="color:white; font-family:'Rajdhani'; letter-spacing:2px;">ACCESO SIGD</h2>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INGRESAR"):
                if u == "1723623011" and p == PASS_MASTER:
                    st.session_state.logged_in = True; st.session_state.usuario = "ADMINISTRADOR"; st.rerun()
                else: st.error("Acceso Denegado")

else:
    # --- DASHBOARD PRINCIPAL ---
    if st.session_state.active_page == 'dashboard':
        st.markdown(f"""
            <div class="dashboard-wrapper">
                <div class="hero-section">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png" class="hero-logo">
                    <h1 class="hero-title">SIGD DINIC</h1>
                    <div class="hero-subtitle">CENTRO DE MANDO DIGITAL V63.0</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Grid de Botones
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("📝\nSECRETARÍA"): nav_to('secretaria')
        with c2: 
            if st.button("🧠\nASESOR IA"): nav_to('ia')
        with c3: 
            if st.button("👮‍♂️\nTALENTO HUMANO"): nav_to('th')
        with c4: 
            if st.button("🛡️\nADMINISTRACIÓN"): nav_to('admin')
            
        # Botón Salir Discreto
        st.markdown("""<div style="position:fixed; bottom:20px; right:20px;">
            <button style="background:red; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;" onclick="location.reload()">SALIR</button>
        </div>""", unsafe_allow_html=True)

    # --- MÓDULO SECRETARÍA (IFRAME DARK MODE) ---
    elif st.session_state.active_page == 'secretaria':
        # Botón flotante HOME
        st.markdown("""
            <div class="floating-home">
                <button onclick="window.parent.document.querySelector('button[kind=secondary]').click()">🏠</button>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón oculto de Streamlit para volver
        if st.button("Volver Dashboard", key="back_sec", type="secondary"): nav_to('dashboard')

        # Iframe Full Screen sin scrollbar
        components.html(HTML_SECRETARIO_DARK, height=1300, scrolling=True)

    # --- OTROS MÓDULOS ---
    elif st.session_state.active_page == 'ia':
        st.title("🧠 Módulo IA"); st.info("En construcción..."); 
        if st.button("Volver"): nav_to('dashboard')

    elif st.session_state.active_page == 'th':
        st.title("👮‍♂️ Talento Humano"); st.warning("Área Restringida"); 
        if st.button("Volver"): nav_to('dashboard')
        
    elif st.session_state.active_page == 'admin':
        st.title("🛡️ Admin"); st.write(USUARIOS_BASE); 
        if st.button("Volver"): nav_to('dashboard')
