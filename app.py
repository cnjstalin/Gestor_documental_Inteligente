# ==============================================================================
# MÓDULO TALENTO HUMANO (DASHBOARD ANALÍTICO AVANZADO)
# ==============================================================================
def mostrar_th():
    c1, c2 = st.columns([1, 5])
    with c1: 
        if st.button("⬅ VOLVER"): nav("landing")
    with c2:
        st.markdown(f'<div style="background:#0E2F44; padding:10px; border-radius:8px; color:white; font-weight:bold; height:50px; display:flex; align-items:center;"><span style="font-size:20px; margin-right:10px;">📊</span> DASHBOARD ANALÍTICO - TALENTO HUMANO</div>', unsafe_allow_html=True)

    # 1. PERSISTENCIA EN MEMORIA (Evita que se borre al salir)
    if 'df_nomina' not in st.session_state:
        st.session_state.df_nomina = cargar_nomina()

    # 2. CARGA DE ARCHIVOS
    with st.expander("📁 CARGAR / ACTUALIZAR MATRIZ DE DATOS"):
        archivo = st.file_uploader("Suba su matriz (Excel .xlsx o CSV)", type=["xlsx", "csv"])
        if archivo:
            try:
                df_nuevo = pd.read_excel(archivo) if archivo.name.endswith('.xlsx') else pd.read_csv(archivo)
                st.session_state.df_nomina = df_nuevo
                st.success("✅ Datos cargados en memoria exitosamente.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al procesar archivo: {e}")

    # Obtenemos el df de la sesión
    df = st.session_state.df_nomina

    if df is not None and not df.empty:
        # Asegurar nombres de columnas en mayúsculas para evitar errores tipográficos
        df.columns = df.columns.str.upper()

        st.markdown('<div class="sec-header">🔍 FILTROS GLOBALES DINÁMICOS</div>', unsafe_allow_html=True)
        
        # 3. LÓGICA DE FILTRADO CRUZADO
        df_filtered = df.copy()
        
        with st.container():
            st.markdown('<div class="sec-body">', unsafe_allow_html=True)
            f1, f2, f3, f4 = st.columns(4)
            
            # Filtro 1: Grado (Si existe la columna)
            if 'GRADO' in df.columns:
                with f1:
                    grados = st.multiselect("Filtrar por Grado:", options=sorted(df['GRADO'].dropna().unique()))
                    if grados: df_filtered = df_filtered[df_filtered['GRADO'].isin(grados)]
            
            # Filtro 2: Provincia/Zona (Si existe la columna)
            col_geo = 'PROVINCIA' if 'PROVINCIA' in df.columns else 'ZONA' if 'ZONA' in df.columns else None
            if col_geo:
                with f2:
                    zonas = st.multiselect(f"Filtrar por {col_geo}:", options=sorted(df[col_geo].dropna().unique()))
                    if zonas: df_filtered = df_filtered[df_filtered[col_geo].isin(zonas)]
            
            # Filtro 3: Unidad (Si existe la columna)
            if 'UNIDAD' in df.columns:
                with f3:
                    unidades = st.multiselect("Filtrar por Unidad:", options=sorted(df['UNIDAD'].dropna().unique()))
                    if unidades: df_filtered = df_filtered[df_filtered['UNIDAD'].isin(unidades)]
            
            # Filtro 4: Búsqueda Libre (Nombres o Cédula)
            with f4:
                search = st.text_input("Buscar Apellido / C.C:")
                if search:
                    mask = df_filtered.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                    df_filtered = df_filtered[mask]
                    
            st.markdown('</div>', unsafe_allow_html=True)

        # 4. MÉTRICAS SINCRONIZADAS AL FILTRO
        st.markdown('<div class="sec-header">KPIs DE PERSONAL</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Personal Encontrado", f"{len(df_filtered)} / {len(df)}")
        if 'GRADO' in df_filtered.columns:
            m2.metric("Grados Representados", df_filtered['GRADO'].nunique())
        m3.metric("Nivel de Filtrado", f"{round((len(df_filtered)/len(df))*100, 1)}%")

        # 5. GRÁFICOS Y MAPA GEOLOCALIZADO
        st.markdown('<div class="sec-header">ANÁLISIS VISUAL Y DESPLIEGUE TERRITORIAL</div>', unsafe_allow_html=True)
        g1, g2 = st.columns([1, 1])
        
        with g1:
            if 'GRADO' in df_filtered.columns:
                fig_bar = px.histogram(df_filtered, x='GRADO', title="Distribución por Grado", color_discrete_sequence=['#0E2F44'], template="plotly_white")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Sin columna 'GRADO' para graficar barras.")
                
        with g2:
            # MAPA DE ECUADOR
            if 'LATITUD' in df_filtered.columns and 'LONGITUD' in df_filtered.columns:
                fig_map = px.scatter_mapbox(
                    df_filtered, 
                    lat="LATITUD", 
                    lon="LONGITUD", 
                    hover_name="APELLIDOS Y NOMBRES" if 'APELLIDOS Y NOMBRES' in df_filtered.columns else None,
                    color="GRADO" if 'GRADO' in df_filtered.columns else None,
                    title="Mapa de Despliegue Operativo",
                    color_discrete_sequence=px.colors.qualitative.Dark24,
                    zoom=5.5, 
                    center={"lat": -1.8312, "lon": -78.1834}, # Centro de Ecuador
                    mapbox_style="carto-positron"
                )
                fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("🗺️ MAPA DESACTIVADO: La matriz cargada no tiene las columnas 'LATITUD' y 'LONGITUD'. Añádalas al Excel para ver el despliegue.")

        # 6. DATAFRAME FINAL
        st.markdown('<div class="sec-header">DATASET FILTRADO</div>', unsafe_allow_html=True)
        st.dataframe(df_filtered, use_container_width=True)

    else:
        st.info("ℹ️ Para activar el dashboard interactivo, primero cargue la matriz de datos en el panel superior.")
