import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v3.0", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO PROFESIONAL CON COLORES LLAMATIVOS (CSS)
st.markdown("""
    <style>
    /* Fondo Oscuro Profundo */
    .stApp {
        background: radial-gradient(circle, #1e272e 0%, #0f1418 100%);
    }
    
    /* Barra Lateral Estilo Cristal */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        border-right: 2px solid #00d2ff;
    }

    /* Títulos Neón */
    .titulo-sidebar {
        font-size: 26px !important;
        font-weight: 900;
        color: #00d2ff; /* Cian Brillante */
        text-shadow: 0px 0px 10px #00d2ff;
        text-align: center;
        margin-bottom: 0px;
    }

    .usuario-sidebar {
        font-size: 16px;
        color: #ffffff;
        text-align: center;
        border: 1px solid #00d2ff;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 25px;
        background: rgba(0, 210, 255, 0.1);
    }

    /* Estilo de Submenús (Letras Turquesa) */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #55efc4 !important; /* Turquesa Neón */
        text-align: left !important;
        width: 100%;
        font-size: 16px !important;
        font-weight: 500;
        transition: 0.3s;
        padding-left: 10px !important;
    }
    .stButton > button:hover {
        color: #ffffff !important;
        text-shadow: 0px 0px 8px #55efc4;
        transform: translateX(8px);
    }

    /* Expander Estilo Carpeta */
    .st-ae {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 5px !important;
        margin-bottom: 5px !important;
    }
    
    h1, h2, h3, span, label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS (LECTURA CSV DIRECTA)
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
    st.markdown("<h1 style='text-align: center; color: #00d2ff !important; font-size: 50px;'>SISTEMA INDUSTRIAL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_industrial"):
            u_id = st.text_input("ID DE USUARIO").strip()
            u_pass = st.text_input("CONTRASEÑA", type="password").strip()
            if st.form_submit_button("ACCEDER"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # CARGA DE PERMISOS (Detecta 1 en cualquier formato)
                        fila = valido.iloc[0]
                        st.session_state.permisos = [col for col in fila.index if str(fila[col]) == '1']
                        st.rerun()
                    else: st.error("Credenciales incorrectas")
    st.stop()

# 6. SIDEBAR (NAVEGACIÓN IZQUIERDA)
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown("<h3 style='color: #00d2ff;'>📁 ÁREAS DE PRODUCCIÓN</h3>", unsafe_allow_html=True)

    # Estructura de Datos Unificada
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

    # Generación dinámica del menú basado en permisos (1)
    for area, opciones in areas_data.items():
        if area in st.session_state.permisos:
            with st.expander(f"📦 {area}"):
                for opt in opciones:
                    # Al hacer clic, se guarda la opción para abrirla en el centro
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. PANEL CENTRAL (DERECHA)
if st.session_state.sub_modulo:
    st.markdown(f"<h1 style='color: #55efc4 !important; border-bottom: 2px solid #55efc4;'>📍 {st.session_state.sub_modulo}</h1>", unsafe_allow_html=True)
    st.write("")
    
    # Lógica para mostrar tablas automáticamente si el nombre coincide con una pestaña del Drive
    if "Kardex" in st.session_state.sub_modulo or "Inventario" in st.session_state.sub_modulo:
        df_mostrar = leer_hoja_directo("ALMACEN")
        st.dataframe(df_mostrar, use_container_width=True)
    
    if st.button("⬅ VOLVER AL MENÚ"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    # Pantalla de Bienvenida con Diseño
    st.markdown("""
        <div style='text-align: center; margin-top: 10%; background: rgba(255,255,255,0.03); padding: 50px; border-radius: 20px; border: 1px solid rgba(0,210,255,0.2);'>
            <h1 style='font-size: 60px; color: #00d2ff !important;'>BIENVENIDO AL PANEL</h1>
            <p style='font-size: 22px; color: #ffffff;'>Seleccione una operación en el menú lateral para gestionar la planta.</p>
        </div>
    """, unsafe_allow_html=True)
