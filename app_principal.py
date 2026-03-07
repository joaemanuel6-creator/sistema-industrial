import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v6.0", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO DE ALTO IMPACTO (CSS)
st.markdown("""
    <style>
    /* Fondo General Oscuro */
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
        margin-bottom: 5px;
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

    /* BOTÓN LOGIN PERSONALIZADO */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #00d2ff, #005f73) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        border: none !important;
    }

    /* LETRAS DE LOS MENÚS (COLOR INICIAL CIAN) */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #00d2ff !important;
        text-align: left !important;
        width: 100%;
        font-size: 17px !important;
        transition: 0.3s ease;
    }

    /* COLOR ROJO AL HACER CLICK (PARA TODOS) */
    .stButton > button:focus, .stButton > button:active, .stButton > button:hover {
        color: #ff4d4d !important; 
        text-shadow: 0px 0px 15px #ff4d4d;
        background: transparent !important;
        transform: scale(1.05);
        font-weight: bold !important;
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

# 3. FUNCIÓN DE DATOS (LECTURA Y LIMPIEZA)
def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        # Limpieza absoluta de nombres de columnas
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
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_industrial"):
            u_id = st.text_input("🆔 ID USUARIO").strip()
            u_pass = st.text_input("🔑 CONTRASEÑA", type="password").strip()
            if st.form_submit_button("INGRESAR AL SISTEMA"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # CARGA DE PERMISOS (Fuerza limpieza de nombres)
                        fila = valido.iloc[0]
                        st.session_state.permisos = [str(col).strip().upper() for col in fila.index if str(fila[col]) == '1']
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
    st.markdown("<h4 style='color: #00d2ff;'>📂 CATEGORÍAS</h4>", unsafe_allow_html=True)

    # Definición de Áreas
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
        "USUARIO": ["Registro de Usuarios"],
        "MANTENIMIENTO": ["Control Mantenimiento"],
        "OBSERVACION": ["Registros Observaciones"]
    }

    # Dibujado con filtro de permisos (1)
    for area, opciones in areas_data.items():
        if area in st.session_state.permisos:
            with st.expander(f"📦 {area}"):
                for opt in opciones:
                    # Al hacer clic aquí, el color cambiará a Rojo por el CSS superior
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. PANEL CENTRAL
if st.session_state.sub_modulo:
    st.markdown(f'<p class="titulo-central">📍 {st.session_state.sub_modulo}</p>', unsafe_allow_html=True)
    st.divider()
    st.write(f"Módulo activo: **{st.session_state.sub_modulo}**")
    
    if st.button("⬅ VOLVER"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h1 style='color:#00d2ff;'>SISTEMA INDUSTRIAL CONECTADO</h1><p>Seleccione un módulo en la izquierda.</p></div>", unsafe_allow_html=True)
