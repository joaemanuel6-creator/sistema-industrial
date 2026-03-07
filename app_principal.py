import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v8.0", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO PROFESIONAL (CSS INYECTADO)
st.markdown("""
    <style>
    .stApp { background: #0d1117; }
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 3px solid #00d2ff;
    }
    .titulo-sidebar {
        font-size: 26px !important;
        font-weight: 900;
        color: #00d2ff;
        text-shadow: 0px 0px 15px #00d2ff;
        text-align: center;
    }
    .usuario-sidebar {
        font-size: 20px;
        color: #ffda79 !important; 
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 0px 0px 5px #ffda79;
    }
    /* BOTONES DEL MENÚ */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #00d2ff !important;
        text-align: left !important;
        width: 100%;
        font-size: 17px !important;
        transition: 0.1s;
    }
    /* COLOR ROJO AL HACER CLICK (EVITA EL BLANCO) */
    .stButton > button:focus, .stButton > button:active, .stButton > button:hover {
        color: #ff4d4d !important; 
        text-shadow: 0px 0px 15px #ff4d4d !important;
        background-color: transparent !important;
        font-weight: bold !important;
        outline: none !important;
        box-shadow: none !important;
    }
    .titulo-central {
        color: #00d2ff !important;
        font-size: 40px !important;
        font-weight: bold;
    }
    h1, h2, h3, p, span { color: #e6edf3 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIONES DE LÓGICA DE DATOS
def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- MODULO DE COPELAS (MIGRADO DE TU ARCHIVO .PY) ---
def formulario_copelas(usuario):
    st.markdown('<p class="titulo-central">📝 REGISTRO DE COPELAS</p>', unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            codigo = st.selectbox("C/Producto:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
            cantidad = st.number_input("Cantidad:", min_value=0, step=1)
        with col2:
            material = st.text_input("Material:").upper()
            prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with col3:
            parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 21)])
            fecha = st.date_input("Fecha:", datetime.now())
    
    if st.button("💾 GUARDAR EN DRIVE"):
        st.success(f"Registro exitoso para {usuario}: {codigo}")

# 4. MANEJO DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

# 5. INTERFAZ DE LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-central" style="text-align:center;">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u_id = st.text_input("🆔 ID USUARIO").strip()
            u_pass = st.text_input("🔑 CONTRASEÑA", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        fila = valido.iloc[0]
                        # Filtro estricto para permisos
                        st.session_state.permisos = [str(col).strip().upper() for col in fila.index if str(fila[col]).strip() == '1']
                        st.rerun()
                    else: st.error("❌ Credenciales incorrectas")
    st.stop()

# 6. BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # Estructura de Módulos (Asegúrate que coincidan con tus columnas de Drive)
    areas_data = {
        "COPELAS": ["Registro de Copelas"],
        "CRISOLES": ["Registro de Crisoles"],
        "QUEMA": ["Proceso de Quema"],
        "EMBALAJE": ["Embalaje General"],
        "LIMPIEZA": ["Limpieza de Equipos"],
        "MEZCLA": ["Control de Mezclas"],
        "ZARANDA": ["Zaranda y Martillo"],
        "MOLINO": ["Operación de Molino"],
        "ALMACEN": ["Kardex e Inventario"],
        "HISTORIAL": ["Registros Pasados"],
        "USUARIO": ["Gestión de Usuarios"],
        "MANTENIMIENTO": ["Plan de Mantenimiento"],
        "OBSERVACION": ["Registro de Observaciones"]
    }

    for area, opciones in areas_data.items():
        if area in st.session_state.permisos:
            with st.expander(f"📦 {area}"):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. PANEL CENTRAL (DERECHA)
if st.session_state.sub_modulo:
    # LÓGICA DE APERTURA DE MÓDULOS
    if "Copelas" in st.session_state.sub_modulo:
        formulario_copelas(st.session_state.usuario)
    
    elif "Mantenimiento" in st.session_state.sub_modulo:
        st.markdown('<p class="titulo-central">🛠 MANTENIMIENTO PREVENTIVO</p>', unsafe_allow_html=True)
        st.info("Cargando cronograma de mantenimiento...")

    elif "Observaciones" in st.session_state.sub_modulo:
        st.markdown('<p class="titulo-central">👁 REGISTRO DE OBSERVACIONES</p>', unsafe_allow_html=True)
        st.text_area("Describa la novedad:")

    else:
        st.markdown(f'<p class="titulo-central">📍 {st.session_state.sub_modulo}</p>', unsafe_allow_html=True)
    
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h1 style='color:#00d2ff;'>SISTEMA INDUSTRIAL</h1><p>Panel de Control Activo</p></div>", unsafe_allow_html=True)
