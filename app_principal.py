import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. ESTILOS CSS PERSONALIZADOS
st.markdown("""
    <style>
    .titulo-principal {
        font-size: 55px !important;
        font-weight: 800;
        color: #1E272E;
        text-align: center;
        margin-bottom: 0px;
    }
    .usuario-banner {
        font-size: 24px;
        color: #0083B0;
        text-align: center;
        font-weight: bold;
        margin-top: 0px;
        margin-bottom: 40px;
    }
    .area-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        border-top: 4px solid #0083B0;
        margin-bottom: 20px;
        min-height: 250px;
    }
    /* Estilo para que el botón parezca un enlace de texto */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #4b4b4b !important;
        text-align: left !important;
        padding: 0px !important;
        font-size: 16px !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        color: #0083B0 !important;
        font-weight: bold !important;
        text-decoration: underline !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE DATOS (MÉTODO DIRECTO)
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
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "menu_actual": "INICIO"})

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-principal">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login"):
            u_id = st.text_input("ID de Usuario")
            u_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ENTRAR"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    # Validar credenciales
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        
                        # LOGICA DE PERMISOS: Solo columnas con el número 1
                        user_row = valido.iloc[0]
                        # Filtramos las columnas donde el valor sea exactamente 1
                        st.session_state.permisos = [col for col in user_row.index if str(user_row[col]) == '1']
                        st.rerun()
                    else: st.error("ID o Contraseña incorrectos")
    st.stop()

# 6. CABECERA
st.markdown('<p class="titulo-principal">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
st.markdown(f'<p class="usuario-banner">USUARIO: {st.session_state.usuario}</p>', unsafe_allow_html=True)

# 7. MENÚS Y SUBMENÚS
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

# Navegación Sidebar
if st.sidebar.button("🏠 INICIO"):
    st.session_state.menu_actual = "INICIO"
    st.rerun()
if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

# 8. PANEL DE ÁREAS (SEGÚN PERMISOS 1/0)
if st.session_state.menu_actual == "INICIO":
    st.subheader("📦 Áreas de Producción")
    
    cols = st.columns(3)
    visible_count = 0
    
    for area, submenus in areas.items():
        # Verificamos si la columna del área tiene un 1 para este usuario
        if area in st.session_state.permisos:
            with cols[visible_count % 3]:
                st.markdown(f'<div class="area-box"><h3>{area}</h3>', unsafe_allow_html=True)
                for sub in submenus:
                    # El botón ahora se comporta como un enlace de texto
                    if st.button(f"• {sub}", key=sub):
                        st.session_state.menu_actual = sub
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                visible_count += 1

    if visible_count == 0:
        st.warning("No tienes áreas permitidas (asigna '1' en la tabla de usuarios).")

else:
    # VISTA DE MÓDULO SELECCIONADO
    st.header(f"📍 {st.session_state.menu_actual}")
    if st.button("⬅ Volver"):
        st.session_state.menu_actual = "INICIO"
        st.rerun()
    st.divider()
    st.write(f"Contenido del módulo {st.session_state.menu_actual} enlazado a Google Sheets.")
