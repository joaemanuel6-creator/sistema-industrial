import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide", page_icon="🏭")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. ESTILOS CSS (Sin botones, estilo de enlaces limpios)
st.markdown("""
    <style>
    .titulo-principal {
        font-size: 60px !important;
        font-weight: 800;
        color: #1E272E;
        text-align: center;
        margin-bottom: 5px;
    }
    .usuario-banner {
        font-size: 28px;
        color: #0083B0;
        text-align: center;
        font-weight: bold;
        margin-bottom: 40px;
    }
    .area-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0083B0;
        height: 100%;
        margin-bottom: 20px;
    }
    .enlace-menu {
        font-size: 18px;
        color: #4b4b4b;
        text-decoration: none;
        display: block;
        padding: 5px 0;
        transition: 0.2s;
        cursor: pointer;
    }
    .enlace-menu:hover {
        color: #0083B0;
        font-weight: bold;
        padding-left: 5px;
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
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "menu_actual": "INICIO"})

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-principal">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
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
                        # Guardamos los permisos (columnas que digan 'SI')
                        user_row = valido.iloc[0]
                        st.session_state.permisos = [col for col in user_row.index if str(user_row[col]).upper() == 'SI']
                        st.rerun()
                    else: st.error("Acceso denegado")
    st.stop()

# 6. CABECERA DESPUÉS DE LOGUEAR
st.markdown('<p class="titulo-principal">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
st.markdown(f'<p class="usuario-banner">USUARIO: {st.session_state.usuario}</p>', unsafe_allow_html=True)

# Menú lateral para navegación rápida
if st.sidebar.button("🏠 Inicio"):
    st.session_state.menu_actual = "INICIO"
    st.rerun()
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.clear()
    st.rerun()

# 7. ESTRUCTURA DE MENÚS (Igual a la solicitada)
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

# 8. MOSTRAR ÁREAS DE PRODUCCIÓN SEGÚN PERMISOS
if st.session_state.menu_actual == "INICIO":
    st.subheader("🛠 Áreas de Producción")
    
    # Grid de 3 columnas
    cols = st.columns(3)
    idx = 0
    
    for area, submenus in areas.items():
        # SOLO SE MUESTRA SI EL NOMBRE DE LA CATEGORÍA ESTÁ EN LOS PERMISOS DEL USUARIO (VALOR 'SI' EN EXCEL)
        if area in st.session_state.permisos:
            with cols[idx % 3]:
                st.markdown(f"""<div class="area-box">
                    <h3 style='margin-top:0; color:#1E272E;'>{area}</h3>
                """, unsafe_allow_html=True)
                
                for sub in submenus:
                    # Usamos botones que parecen texto (link style)
                    if st.button(f"➤ {sub}", key=sub, help=f"Entrar a {sub}"):
                        st.session_state.menu_actual = sub
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                idx += 1
    
    if idx == 0:
        st.warning("Usted no tiene permisos asignados para ver ninguna área. Contacte al administrador.")

else:
    # VISTA DE CADA MÓDULO
    st.header(f"📍 {st.session_state.menu_actual}")
    st.button("⬅ Volver al Menú", on_click=lambda: st.session_state.update({"menu_actual": "INICIO"}))
    st.divider()
    st.info(f"Contenido para {st.session_state.menu_actual} en desarrollo...")
