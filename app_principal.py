import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. ESTILOS CSS PARA DISEÑO PROFESIONAL
st.markdown("""
    <style>
    .titulo-sistema {
        font-size: 65px !important;
        font-weight: 900;
        color: #1E272E;
        text-align: center;
        margin-bottom: 0px;
        line-height: 1;
    }
    .usuario-label {
        font-size: 28px;
        color: #0083B0;
        text-align: center;
        font-weight: bold;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    .marco-areas {
        background-color: #fcfcfc;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 25px;
        margin-top: 20px;
    }
    .area-titulo {
        font-size: 22px;
        color: #2c3e50;
        font-weight: bold;
        margin-bottom: 10px;
        cursor: pointer;
    }
    /* Estilo para los sub-enlaces de texto */
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #555 !important;
        text-align: left !important;
        padding: 2px 0px !important;
        font-size: 17px !important;
        transition: 0.2s;
        text-decoration: none !important;
    }
    .stButton > button:hover {
        color: #0083B0 !important;
        text-decoration: underline !important;
        background: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIONES DE DATOS
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
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "area_seleccionada": None})

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-sistema">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_industrial"):
            u_id = st.text_input("ID de Usuario")
            u_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INGRESAR"):
                df_u = leer_hoja_directo("USUARIO")
                if not df_u.empty:
                    valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        # Cargamos permisos donde el valor sea 1
                        st.session_state.permisos = [col for col in valido.iloc[0].index if str(valido.iloc[0][col]) == '1']
                        st.rerun()
                    else: st.error("Acceso denegado")
    st.stop()

# 6. CABECERA PRINCIPAL (FIJA ARRIBA)
st.markdown('<p class="titulo-sistema">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
st.markdown(f'<p class="usuario-label">USUARIO: {st.session_state.usuario}</p>', unsafe_allow_html=True)

# 7. ESTRUCTURA DE DATOS
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

# Botón cerrar sesión en sidebar
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.clear()
    st.rerun()

# 8. MARCO DE ÁREAS
st.markdown('<div class="marco-areas">', unsafe_allow_html=True)
st.subheader("🛠 ÁREAS")

# Grid de 3 columnas para las áreas
cols = st.columns(3)
idx = 0

for area, opciones in areas_data.items():
    # FILTRO POR PERMISO (Valor 1 en tabla Usuario)
    if area in st.session_state.permisos:
        with cols[idx % 3]:
            # El nombre del área actúa como un disparador
            if st.button(f"📁 {area}", key=f"btn_{area}"):
                st.session_state.area_seleccionada = area
            
            # Si se selecciona esta área, mostramos sus sub-opciones abajo
            if st.session_state.area_seleccionada == area:
                st.markdown(f"<div style='margin-left: 20px; border-left: 2px solid #0083B0; padding-left: 10px;'>", unsafe_allow_html=True)
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"opt_{opt}"):
                        st.toast(f"Abriendo {opt}...")
                        # Aquí puedes agregar st.switch_page o llamar a otra función
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("") # Espacio
            idx += 1

st.markdown('</div>', unsafe_allow_html=True)

# 9. ÁREA DE TRABAJO (Aquí se abrirán los archivos/formularios)
if st.session_state.area_seleccionada:
    st.divider()
    st.write(f"Usted está en el área: **{st.session_state.area_seleccionada}**")
