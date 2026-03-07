import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v5.0", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO DE ALTO IMPACTO (CSS)
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background: #0b0e11; }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #11151c !important;
        border-right: 2px solid #00d2ff;
    }

    /* Título y Usuario en Sidebar */
    .titulo-sidebar {
        font-size: 26px !important;
        font-weight: 900;
        color: #00d2ff;
        text-shadow: 0px 0px 12px #00d2ff;
        text-align: center;
        margin-bottom: 5px;
    }
    .usuario-sidebar {
        font-size: 17px;
        color: #ff9f43 !important; /* Color Naranja para el nombre del usuario */
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* BOTÓN LOGIN (ACCEDER) */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00d2ff, #3a1c71) !important;
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        height: 3em !important;
    }

    /* LETRAS DE LOS MENÚS (Interactivos) */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #55efc4 !important; /* Turquesa inicial */
        text-align: left !important;
        width: 100%;
        font-size: 16px !important;
        transition: 0.4s ease;
    }

    /* COLOR CUANDO HACES CLICK O SELECCIONAS (No más blanco) */
    .stButton > button:focus, .stButton > button:active, .stButton > button:hover {
        color: #ff3f34 !important; /* Rojo Neón al seleccionar */
        text-shadow: 0px 0px 15px #ff3f34;
        background: transparent !important;
        transform: scale(1.05);
        border: none !important;
    }

    /* Títulos en Pantalla Central (No blancos) */
    .titulo-central {
        color: #00d2ff !important;
        font-size: 45px !important;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
    }

    h1, h2, h3, p, span { color: #d1d8e0 !important; }
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

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-central" style="text-align:center;">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            u_id = st.text_input("🆔 ID DE USUARIO").strip()
            u_pass = st.text_input("🔑 CONTRASEÑA", type="password").strip()
            if st.form_submit_button("ACCEDER AL PANEL"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # Cargamos permisos asegurando que no haya espacios
                        fila = valido.iloc[0]
                        st.session_state.permisos = [str(col).strip().upper() for col in fila.index if str(fila[col]) == '1']
                        st.rerun()
                    else: st.error("❌ Credenciales incorrectas")
    st.stop()

# 6. SIDEBAR (NAVEGACIÓN)
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 SALIR DEL SISTEMA"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown("<h4 style='color: #00d2ff;'>📁 ÁREAS DISPONIBLES</h4>", unsafe_allow_html=True)

    # Menú de Datos
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

    # Dibujado dinámico
    for area, opciones in areas_data.items():
        if area in st.session_state.permisos:
            with st.expander(f"📦 {area}"):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. PANEL CENTRAL
if st.session_state.sub_modulo:
    st.markdown(f'<p class="titulo-central">📍 {st.session_state.sub_modulo}</p>', unsafe_allow_html=True)
    st.divider()
    
    # Simulación de carga de datos
    st.write(f"Visualizando registros para: **{st.session_state.sub_modulo}**")
    
    if st.button("⬅ VOLVER AL MENÚ"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h1 style='color:#00d2ff;'>SISTEMA ACTIVO</h1><p>Seleccione una operación en la barra lateral.</p></div>", unsafe_allow_html=True)
