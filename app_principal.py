import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. ESTILOS CSS PARA LA BARRA LATERAL
st.markdown("""
    <style>
    /* Ajustes para el Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        padding-top: 20px;
    }
    .titulo-sidebar {
        font-size: 28px !important;
        font-weight: 900;
        color: #1E272E;
        line-height: 1;
        margin-bottom: 5px;
    }
    .usuario-sidebar {
        font-size: 18px;
        color: #0083B0;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .area-titulo {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 15px;
    }
    /* Estilo de enlaces de texto en la sidebar */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #4b4b4b !important;
        text-align: left !important;
        padding: 2px 0px !important;
        font-size: 15px !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        color: #0083B0 !important;
        text-decoration: underline !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS
def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 4. LÓGICA DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

# 5. LOGIN (Pantalla Central)
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>SISTEMA INDUSTRIAL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login"):
            u_id = st.text_input("ID de Usuario")
            u_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INGRESAR"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # Cargamos permisos donde el valor sea 1 (Asegúrate que en Excel digan 1)
                        st.session_state.permisos = [col for col in valido.iloc[0].index if str(valido.iloc[0][col]) == '1']
                        st.rerun()
                    else: st.error("Acceso denegado")
    st.stop()

# 6. TODO A LA IZQUIERDA (SIDEBAR)
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">USUARIO: {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 🛠 ÁREAS")

    # Definición de Áreas y Sub-opciones
    areas_data = {
        "COPELAS": ["Registro de Copelas"],
        "CRISOLES": ["Registro de Crisoles"],
        "QUEMA": ["Quema de Crisoles", "Quema de Copelas"],
        "EMBALAJE": ["Embalaje de Crisoles", "Embalaje de Copelas"],
        "LIMPIEZA": ["Limpieza de Crisoles", "Limpieza de Copelas"],
        "MEZCLA": ["Mezcla de Crisoles", "Mezcla de Copelas", "Control de Mermas"],
        "ZARANDA": ["Zaranda", "Martillo", "Rodillo", "Preparacion"],
        "MOLINO": ["Arcilla", "Mexicana", "Reciclaje", "Crisol", "Otros Materiales"],
        "ALMACEN": ["Ingreso Almacén", "Salida Almacén", "Kardex", "Despachos", "Inventario", "Ajuste de Inventario", "Historial Despachos"],
        "HISTORIAL": ["Registros Copelas y Crisoles", "Registros de limpieza de Copelas", "Registro de Limpieza de Crisoles", "Historial de Embalaje", "Registrio de Mezclas", "Zaranda", "Registros del Molino"],
        "USUARIO": ["Registro de Usuario"],
        "MANTENIMIENTO": ["Registro de Mantenimiento"],
        "OBSERVACION": ["Registros Observaciones"]
    }

    # Mostrar Áreas como Expander (Desplegables) en la Sidebar
    for area, opciones in areas_data.items():
        if area in st.session_state.permisos:
            with st.expander(f"📁 {area}"):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. CONTENIDO CENTRAL (DERECHA)
if st.session_state.sub_modulo:
    st.title(f"📍 {st.session_state.sub_modulo}")
    st.write(f"Cargando información del módulo: {st.session_state.sub_modulo}")
    
    # Ejemplo: Si el usuario hace clic en Kardex, mostramos datos
    if "Kardex" in st.session_state.sub_modulo:
        df_datos = leer_hoja_directo("ALMACEN")
        st.dataframe(df_datos, use_container_width=True)
    
    # Botón para limpiar pantalla central
    if st.button("Limpiar Pantalla"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.subheader("Bienvenido al Sistema de Gestión Industrial")
    st.info("Seleccione un área y una opción en el menú de la izquierda para comenzar a trabajar.")
