import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(
    page_title="SISTEMA INDUSTRIAL", 
    page_icon="🏭", 
    layout="wide"
)

# Estilo personalizado para el título
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color: #0083B0; }
    </style>
    """, unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 2. FUNCIÓN DE LECTURA DE GOOGLE SHEETS
def leer_datos(nombre_pestaña):
    try:
        # La conexión busca automáticamente el link en st.secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # ttl=0 obliga a refrescar los datos de Google Drive siempre
        df = conn.read(worksheet=nombre_pestaña, ttl=0)
        
        if df is not None:
            # Normalizamos nombres de columnas para evitar errores de escritura
            df.columns = [str(c).strip().upper() for c in df.columns]
            df = df.dropna(how="all")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al conectar con la pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

# 3. INTERFAZ DE LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="main-title">🔐 ACCESO AL SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_input = st.text_input("Usuario (ID)").strip()
        pass_input = st.text_input("Contraseña", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            # Buscamos en la hoja USUARIO del Excel
            df_usuarios = leer_datos("USUARIO")
            
            if not df_usuarios.empty:
                # Verificamos columnas clave
                if 'ID' in df_usuarios.columns and 'CONTRASEÑA' in df_usuarios.columns:
                    match = df_usuarios[
                        (df_usuarios['ID'].astype(str) == user_input) & 
                        (df_usuarios['CONTRASEÑA'].astype(str) == pass_input)
                    ]
                    
                    if not match.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
                else:
                    st.warning("⚠️ Error estructural: La hoja 'USUARIO' debe tener columnas 'ID' y 'CONTRASEÑA'.")
            else:
                st.info("No se pudo conectar con la base de datos de usuarios.")
    st.stop()

# 4. PANEL PRINCIPAL (Post-Login)
st.sidebar.markdown(f"### 👤 {st.session_state.user_data.get('NOMBRES', 'Operador')}")
st.sidebar.divider()

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.markdown('<p class="main-title">📊 PANEL DE CONTROL INDUSTRIAL</p>', unsafe_allow_html=True)
st.write(f"Conexión establecida con el archivo de Google Drive.")

# --- MÓDULOS DEL SISTEMA ---
tab1, tab2 = st.tabs(["📦 Inventario", "📝 Registros Recientes"])

with tab1:
    if st.button("🔄 Actualizar Stock"):
        df_alm = leer_datos("ALMACEN")
        if not df_alm.empty:
            st.dataframe(df_alm, use_container_width=True, hide_index=True)
        else:
            st.warning("No se encontraron datos en la pestaña 'ALMACEN'.")

with tab2:
    st.subheader("Últimas Salidas (Copelas)")
    df_cop = leer_datos("COPELA")
    if not df_cop.empty:
        st.dataframe(df_cop.tail(10), use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros de salidas en la pestaña 'COPELA'.")
