import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v7.0", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO DE ALTO IMPACTO (CSS MEJORADO)
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background: #0d1117; }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 3px solid #00d2ff;
    }

    /* Título Sistema */
    .titulo-sidebar {
        font-size: 26px !important;
        font-weight: 900;
        color: #00d2ff;
        text-shadow: 0px 0px 15px #00d2ff;
        text-align: center;
    }

    /* COLOR DE USUARIO (AMARILLO BRILLANTE) */
    .usuario-sidebar {
        font-size: 20px;
        color: #ffda79 !important; 
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 0px 0px 5px #ffda79;
    }

    /* LETRAS DE LOS MENÚS (COLOR INICIAL CIAN) */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #00d2ff !important;
        text-align: left !important;
        width: 100%;
        font-size: 17px !important;
        transition: 0.1s;
    }

    /* EVITAR QUE SE PONGA BLANCO AL HACER CLICK - FORZAR ROJO */
    .stButton > button:focus, 
    .stButton > button:active, 
    .stButton > button:hover,
    .stButton > button:visited {
        color: #ff4d4d !important; /* ROJO NEÓN */
        text-shadow: 0px 0px 15px #ff4d4d !important;
        background-color: transparent !important;
        font-weight: bold !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Títulos de Pantalla Central */
    .titulo-central {
        color: #00d2ff !important;
        font-size: 40px !important;
        font-weight: bold;
    }

    h1, h2, h3, p, span { color: #e6edf3 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS (LECTURA Y LIMPIEZA EXTREMA)
def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        # Limpieza absoluta de nombres de columnas: quita espacios y saltos de línea
        df.columns = [str(c).strip().replace('\\n', '').upper() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 4. LÓGICA DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-central" style="text-align:center;">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_industrial"):
            u_id = st.text_input("🆔 ID USUARIO").strip()
            u_pass = st.text_input("🔑 CONTRASEÑA", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # CARGA DE PERMISOS: Limpia cada celda y nombre de columna
                        fila = valido.iloc[0]
                        st.session_state.permisos = [str(col).strip().upper() for col in fila.index if str(fila[col]).strip() == '1']
                        st.rerun()
                    else: st.error("❌ Acceso Incorrecto")
    st.stop()

# 6. SIDEBAR (MENÚ IZQUIERDO)
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # Estructura de Datos
    areas_data = {
        "COPELAS": ["Registro de Copelas"],
        "CRISOLES": ["Registro de Crisoles"],
        "QUEMA": ["Quema de Crisoles", "Quema de Copelas"],
        "EMBALAJE": ["Embalaje de Crisoles", "Embalaje de Copelas"],
        "LIMPIEZA": ["Limpieza de Crisoles", "Limpieza de Copelas"],
        "MEZCLA": ["Mezcla de Crisoles", "Mezcla de Copelas", "Control de Mermas"],
        "ZARANDA": ["Zaranda", "Martillo", "Rodillo", "Preparacion"],
        "MOLINO": ["Arcilla", "Mexicana", "Reciclaje", "Crisol", "Otros Materiales"],
        "ALMACEN": ["Kardex", "Inventario", "Despachos"],
        "HISTORIAL": ["Registros Generales"],
        "USUARIO": ["Gestión de Usuarios"],
        "MANTENIMIENTO": ["Control de Mantenimiento"],
        "OBSERVACION": ["Registros Observaciones"]
    }

    for area, opciones in areas_data.items():
        # Verificamos permiso asegurando que coincida exactamente con el nombre de la columna
        if area in st.session_state.permisos:
            with st.expander(f"📦 {area}"):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. PANEL CENTRAL
if st.session_state.sub_modulo:
    st.markdown(f'<p class="titulo-central">📍 {st.session_state.sub_modulo}</p>', unsafe_allow_html=True)
    st.divider()
    st.write(f"Módulo activo: **{st.session_state.sub_modulo}**")
    
    if st.button("⬅ VOLVER AL MENÚ"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h1 style='color:#00d2ff;'>SISTEMA INDUSTRIAL</h1><p>Panel de Control Activo</p></div>", unsafe_allow_html=True)
