import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. ESTILOS CSS PARA PERSONALIZAR LA INTERFAZ
st.markdown("""
    <style>
    .titulo-grande {
        font-size: 50px !important;
        font-weight: bold;
        color: #1E272E;
        text-align: center;
        margin-bottom: 0px;
    }
    .usuario-texto {
        font-size: 24px;
        color: #0083B0;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0083B0;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LÓGICA DE SESIÓN Y NAVEGACIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "menu_actual": "INICIO"})

# Función de lectura directa (Método estable)
def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 4. INTERFAZ DE LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-grande">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    with st.container():
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
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
                            st.rerun()
                        else: st.error("Credenciales incorrectas")
    st.stop()

# 5. CABECERA PRINCIPAL
st.markdown('<p class="titulo-grande">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
st.markdown(f'<p class="usuario-texto">USUARIO: {st.session_state.usuario}</p>', unsafe_allow_html=True)

# Botón para volver al menú principal en la barra lateral
if st.sidebar.button("🏠 VOLVER AL MENÚ PRINCIPAL"):
    st.session_state.menu_actual = "INICIO"
    st.rerun()

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

# 6. DEFINICIÓN DE ÁREAS Y SUBMENÚS
areas = {
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

# 7. LOGICA DE NAVEGACIÓN DINÁMICA
if st.session_state.menu_actual == "INICIO":
    st.subheader("🛠 Áreas de Producción")
    
    # Creamos un marco visual usando st.expander o st.container
    with st.container(border=True):
        # Organizamos las áreas en columnas para que se vea ordenado
        cols = st.columns(3)
        for i, (area, submenus) in enumerate(areas.items()):
            with cols[i % 3]:
                st.markdown(f"**{area}**")
                for sub in submenus:
                    if st.button(sub, key=sub):
                        st.session_state.menu_actual = sub
                        st.rerun()
else:
    # VENTANA DE CADA MÓDULO
    st.header(f"📍 {st.session_state.menu_actual}")
    st.info(f"Aquí se cargará el formulario o reporte correspondiente a: {st.session_state.menu_actual}")
    
    # Ejemplo de tabla para el módulo de Inventario
    if "Inventario" in st.session_state.menu_actual:
        df_inv = leer_hoja_directo("ALMACEN")
        st.dataframe(df_inv, use_container_width=True)
    
    if st.button("⬅ Regresar"):
        st.session_state.menu_actual = "INICIO"
        st.rerun()
