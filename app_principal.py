import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v4.0", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO AVANZADO (CSS)
st.markdown("""
    <style>
    /* Fondo Oscuro */
    .stApp {
        background: #101418;
    }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 2px solid #00d2ff;
    }

    /* Títulos */
    .titulo-sidebar {
        font-size: 24px !important;
        font-weight: 900;
        color: #00d2ff;
        text-shadow: 0px 0px 8px #00d2ff;
        text-align: center;
    }

    /* Botón de Acceder (Login) */
    div.stButton > button:first-child {
        background-color: #00d2ff !important;
        color: #101418 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
    }

    /* Enlaces de Submenú (Turquesa Neón) */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #55efc4 !important;
        text-align: left !important;
        width: 100%;
        font-size: 16px !important;
        transition: 0.3s;
    }

    /* Efecto al seleccionar o pasar el mouse (Cambio a Amarillo Neón) */
    .stButton > button:hover, .stButton > button:active, .stButton > button:focus {
        color: #feca57 !important; /* Amarillo Neón */
        text-shadow: 0px 0px 10px #feca57;
        transform: translateX(10px);
        background: transparent !important;
    }

    h1, h2, h3, p, span { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS CON LIMPIEZA TOTAL
def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        # Limpieza profunda: Quitar espacios y pasar a mayúsculas
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 4. LÓGICA DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #00d2ff !important;'>SISTEMA INDUSTRIAL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u_id = st.text_input("ID DE USUARIO").strip()
            u_pass = st.text_input("CONTRASEÑA", type="password").strip()
            if st.form_submit_button("ACCEDER AL SISTEMA"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # CARGA DE PERMISOS: Limpiamos cada nombre de columna para que coincida
                        fila = valido.iloc[0]
                        st.session_state.permisos = [str(col).strip().upper() for col in fila.index if str(fila[col]) == '1']
                        st.rerun()
                    else: st.error("Error en ID o Clave")
    st.stop()

# 6. SIDEBAR
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>👤 {st.session_state.usuario}</p>", unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # Lista de áreas EXACTA para que coincida con tus permisos
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
        "USUARIO": ["Registro de Nuevo Usuario"],
        "MANTENIMIENTO": ["Plan de Mantenimiento"],
        "OBSERVACION": ["Registros de Observaciones"]
    }

    for area, opciones in areas_data.items():
        # Verificamos permiso ignorando espacios
        if area in st.session_state.permisos:
            with st.expander(f"📁 {area}"):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. PANEL CENTRAL
if st.session_state.sub_modulo:
    st.markdown(f"<h1 style='color: #feca57 !important;'>📍 {st.session_state.sub_modulo}</h1>", unsafe_allow_html=True)
    st.divider()
    
    # Contenido dinámico
    st.write(f"Gestionando información de: {st.session_state.sub_modulo}")
    
    if st.button("⬅ VOLVER"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1>BIENVENIDO</h1><p>Seleccione una opción a la izquierda.</p></div>", unsafe_allow_html=True)
