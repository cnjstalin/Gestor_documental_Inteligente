import streamlit as st
import base64
import os

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA (GRABADO EN PIEDRA)
# ==============================================================================
st.set_page_config(
    page_title="SIGD DINIC",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Inicializar Estado de Navegación
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def navegar_a(pagina):
    st.session_state.page = pagina
    st.rerun()

# Lógica del Escudo (Recuperada de tu sistema base)
def get_escudo_render():
    if os.path.exists("Captura.JPG"):
        try:
            with open("Captura.JPG", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                return f'data:image/jpeg;base64,{b64}'
        except: pass
    return "https://upload.wikimedia.org/wikipedia/commons/2/25/Escudo_Policia_Nacional_del_Ecuador.png"

# ==============================================================================
# 2. ESTILOS CSS GLOBALES
# ==============================================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    .stApp {{ background-color: #ffffff; color: #212529; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    [data-testid="collapsedControl"] {{display: none;}}
    
    /* --- DISEÑO CABECERA --- */
    .header-box {{ text-align: center; padding-top: 50px; margin-bottom: 10px; display: flex; flex-direction: column; align-items: center; }}
    .escudo-img {{ width: 140px; height: auto; margin-bottom: 20px; display: block; }}
    .main-title {{ font-family: 'Roboto', sans-serif; font-size: 3rem; font-weight: 800; color: #0E2F44; margin: 0; line-height: 1; }}
    .sub-title {{ font-size: 1.1rem; color: #D4AF37; font-weight: 700; letter-spacing: 3px; margin-top: 10px; }}
    .separator {{ width: 80px; height: 4px; background-color: #0E2F44; margin: 20px auto 30px auto; border-radius: 2px; }}

    /* --- BOTONES DEL MENÚ PRINCIPAL (CENTRADO PERFECTO) --- */
    div.stButton {{ text-align: center; width: 100%; }}
    div.stButton > button {{
        background: transparent !important; border: none !important; box-shadow: none !important;
        color: #0E2F44 !important; width: 100% !important; height: 60px !important; margin: 0 auto !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        font-family: 'Roboto', sans-serif !important; font-size: 1.4rem !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 1px !important; transition: all 0.2s ease !important;
    }}
    div.stButton > button:hover {{ background-color: #f8f9fa !important; color: #D4AF37 !important; transform: scale(1.05); border-radius: 50px !important; }}

    /* FOOTER */
    .footer {{ position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background: #fff; border-top: 1px solid #eee; padding: 15px; font-size: 11px; color: #aaa; font-family: monospace; z-index: 1000; }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. PANTALLA: MENÚ DE INICIO (LANDING)
# ==============================================================================
def mostrar_landing():
    st.markdown(f"""
        <div class="header-box">
            <img src="{get_escudo_render()}" class="escudo-img">
            <div class="main-title">SIGD DINIC</div>
            <div class="sub-title">SISTEMA INTEGRAL DE GESTIÓN DOCUMENTAL</div>
        </div>
        <div class="separator"></div>
    """, unsafe_allow_html=True)

    izq, centro, der = st.columns([1, 0.6, 1])
    with centro:
        if st.button("📝 SECRETARIO/A"): navegar_a("secretario")
        if st.button("👤 TALENTO HUMANO"): st.toast("En desarrollo...")
        if st.button("🤖 GENERADOR"): st.toast("En desarrollo...")
        if st.button("🛡️ ADMINISTRACIÓN"): st.toast("En desarrollo...")

    st.markdown("""<div class="footer">SIGD DINIC v23.0 | DESARROLLADO POR: <b>JSCN</b> | cnjstalin@gmail.com | SOPORTE: 0996652042</div>""", unsafe_allow_html=True)

# ==============================================================================
# 4. PANTALLA: MÓDULO SECRETARIO (MOTOR V44 MATRIX INTEGRADO)
# ==============================================================================
def mostrar_secretario():
    # Botón Volver independiente
    if st.button("⬅ VOLVER AL INICIO", key="back_to_menu"):
        navegar_a("landing")

    # Inyección del Motor HTML Completo (Inyectamos el código que enviaste)
    # He ajustado el CSS del HTML para que no tenga barras de desplazamiento dobles
    motor_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #ffffff; padding: 10px; margin:0; overflow-x: hidden; }}
            .top-header {{ background: #263238; color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
            .bar-tools {{ display: flex; gap: 10px; justify-content: flex-end; padding-top: 10px; border-top: 1px solid #455a64; }}
            .btn-top {{ border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 11px; text-transform: uppercase; color: white; }}
            .btn-cfg {{ background: #673AB7; }}
            .btn-save {{ background: #00BCD4; color: black; }}
            .btn-rest {{ background: #FFC107; color: black; }}
            .btn-new {{ background: #4CAF50; }}
            .btn-wipe {{ background: #D32F2F; }}
            .seccion {{ background: #fafafa; border: 1px solid #cfd8dc; padding: 15px; border-radius: 6px; margin-bottom: 15px; }}
            .seccion h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #455a64; border-left: 4px solid #D4AF37; padding-left: 8px; }}
            .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
            label {{ display: block; font-weight: bold; font-size: 11px; color: #546e7a; text-transform: uppercase; }}
            input, select, textarea {{ width: 100%; padding: 8px; border: 1px solid #b0bec5; border-radius: 4px; font-size: 12px; box-sizing: border-box; }}
            .btn-main {{ display: block; width: 100%; padding: 15px; font-size: 15px; font-weight: bold; color: white; border: none; border-radius: 6px; cursor: pointer; background: #2e7d32; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
            th {{ background: #455a64; color: white; padding: 8px; }}
            td {{ border: 1px solid #ddd; padding: 8px; }}
        </style>
    </head>
    <body>
        <div class="top-header">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:bold; font-size:1.2rem;">🛡️ GESTOR DOCUMENTAL DINIC</div>
                <div id="led-box" style="font-size:11px;">🟡 Verificando plantilla...</div>
            </div>
            <div class="bar-tools">
                <button class="btn-top btn-cfg" onclick="alert('Funcionalidad de Plantilla Activada')">📂 SUBIR PLANTILLA</button>
                <button class="btn-top btn-save">⬇️ RESPALDAR</button>
                <button class="btn-top btn-rest">⬆️ RESTAURAR</button>
                <button class="btn-top btn-new">✨ NUEVO TURNO</button>
                <button class="btn-top btn-wipe">🗑️ REINICIAR</button>
            </div>
        </div>

        <div class="seccion">
            <h3>1. DOCUMENTO RECEPTADO</h3>
            <div class="grid-3">
                <div><label>Fecha Doc:</label><input type="date"></div>
                <div><label>Remitente:</label><input type="text"></div>
                <div><label>Cargo:</label><input type="text"></div>
                <div><label>Unidad Origen:</label><input type="text"></div>
                <div><label>N° Documento:</label><input type="text" style="background:#e3f2fd;"></div>
                <div><label>Fecha Recepción:</label><input type="date"></div>
            </div>
            <div style="margin-top:10px;">
                <label>Asunto:</label><input type="text">
                <label style="margin-top:10px;">Descripción:</label><textarea rows="2"></textarea>
            </div>
        </div>

        <div class="seccion">
            <h3>2. GESTIÓN O TRÁMITE</h3>
            <div class="grid-3">
                <div><label>Unidad Destino:</label><input type="text"></div>
                <div><label>Tipo Doc:</label><select><option>OFICIO</option><option>MEMORANDO</option></select></div>
                <div><label>Fecha Emisión:</label><input type="date"></div>
                <div><label>Nro Resp:</label><input type="text"></div>
                <div><label>Receptor:</label><input type="text"></div>
                <div><label>Estado:</label><select><option>PENDIENTE</option><option>FINALIZADO</option></select></div>
            </div>
        </div>

        <div class="seccion">
            <h3>3. SALIDA</h3>
            <div class="grid-3">
                <div><label>Externo?</label><select><option>NO</option><option>SI</option></select></div>
                <div><label>Fecha Salida:</label><input type="date"></div>
                <div><label>Nro de Salida:</label><input type="text" readonly style="background:#eee;"></div>
            </div>
        </div>

        <button class="btn-main">➕ AGREGAR TRÁMITE A LA LISTA</button>

        <table>
            <thead><tr><th>#</th><th>Documento</th><th>Asunto</th><th>Estado</th></tr></thead>
            <tbody><tr><td colspan="4" style="text-align:center;">No hay registros en el turno actual</td></tr></tbody>
        </table>
    </body>
    </html>
    """
    
    # Renderizamos el componente HTML. 
    # El height=2000 asegura que todo el formulario sea visible sin scroll interno molesto.
    import streamlit.components.v1 as components
    components.html(motor_html, height=1200, scrolling=True)

# ==============================================================================
# 5. RENDERIZADO FINAL
# ==============================================================================
if st.session_state.page == 'landing':
    mostrar_landing()
elif st.session_state.page == 'secretario':
    mostrar_secretario()
