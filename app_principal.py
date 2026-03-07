import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO DE FONDO Y ESTILOS PROFESIONALES (CSS)
st.markdown("""
    <style>
    /* Fondo degradado industrial */
    .stApp {
        background: linear-gradient(135deg, #1e272e 0%, #2c3e50 100%);
        color: white;
    }
    
    /* Estilo de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    .titulo-sidebar {
        font-size: 24px !important;
        font-weight: 900;
        color: #00d2ff;
        text-align: center;
        margin-bottom: 0px;
        text-transform: uppercase;
    }

    .usuario-sidebar {
        font-size: 16px;
        color: #ffffff;
        text-align: center;
        background: rgba(0, 210, 255, 0.2);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 20px;
    }

    /* Botones tipo enlace en Sidebar */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #d1d8e0 !important;
        text-align: left !important;
        width: 100%;
        font-size: 14px !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        color: #00d2ff !important;
        transform: translateX(5px);
    }

    /* Títulos de secciones en blanco */
    h1, h2, h3, p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS REFORZADA
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

# 5. LOGIN PROFESIONAL
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #00d2ff !important;'>SISTEMA INDUSTRIAL</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_industrial"):
            u_id = st.text_input("ID DE USUARIO")
            u_pass = st.text_input("CONTRASEÑA", type="password")
            if st.form_submit_button("ACCEDER AL PANEL"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # Lógica flexible para permisos (detecta 1 como número o como texto)
                        fila = valido.iloc[0]
                        st.session_state.permisos = [col for col in fila.index if str(fila[col]) == '1']
                        st.rerun()
                    else: st.error("Credenciales incorrectas")
    st.stop()

# 6. PANEL LATERAL (SIDEBAR)
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 🧭 NAVEGACIÓN")

    # Estructura Completa
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

    # Dibujar Menú de Áreas
    for area, opciones in areas_data.items():
        # Verificación de seguridad: Se muestra si está en la lista de permisos
        if area in st.session_state.permisos:
            with st.expander(f"📁 {area}", expanded=False):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# 7. ÁREA CENTRAL DE TRABAJO
if st.session_state.sub_modulo:
    st.markdown(f"<h2 style='color: #00d2ff !important;'>📍 {st.session_state.sub_modulo}</h2>", unsafe_allow_html=True)
    st.divider()
    
    # Aquí puedes agregar la lógica de cada pestaña
    if "COPELAS" in st.session_state.sub_modulo or "CRISOLES" in st.session_state.sub_modulo:
        st.info("Cargando base de datos de producción...")
        # Ejemplo: Mostrar historial de esa área
        df_prod = leer_hoja_directo(st.session_state.sub_modulo.split()[-1].upper())
        if not df_prod.empty:
            st.dataframe(df_prod, use_container_width=True)
    
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    # Pantalla de bienvenida
    st.markdown("""
        <div style='text-align: center; margin-top: 100px;'>
            <h1 style='font-size: 50px;'>BIENVENIDO</h1>
            <p style='font-size: 20px; color: #d1d8e0 !important;'>Seleccione un área en el menú de la izquierda para comenzar.</p>
        </div>
    """, unsafe_allow_html=True)
