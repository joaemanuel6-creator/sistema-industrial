import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. ESTO DEBE IR PRIMERO QUE TODO
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide")

# 2. INICIALIZAR LA SESIÓN (Para que no salga el error de la línea 2)
if "autenticado" not in st.session_state:
    st.session_state.update({
        "autenticado": False, 
        "user_data": {}, 
        "modulo_activo": "COPELAS"
    })

# 3. CONEXIÓN A GOOGLE (Asegúrate de que en Secrets esté el enlace)
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        # ttl=0 obliga a Streamlit a leer el Excel real y no una copia vieja
        return conn.read(worksheet=nombre_pestaña, ttl=0)
    except Exception as e:
        st.error(f"No se encontró la pestaña '{nombre_pestaña}'. Revisa el nombre en tu Excel.")
        return pd.DataFrame()

# 4. AHORA SÍ EL LOGIN (Ya no dará error en st.session_state)
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    with st.form("login"):
        u = st.text_input("👤 ID DE USUARIO").strip()
        p = st.text_input("🔑 CONTRASEÑA", type="password")
        if st.form_submit_button("INGRESAR"):
            df_usuarios = leer_tabla("USUARIO")
            if not df_usuarios.empty:
                # Ajustamos los nombres de columnas de tu Excel
                df_usuarios.columns = df_usuarios.columns.str.strip()
                u_col = 'ID'
                p_col = 'Contraseña' # Con la Ñ como en tu Excel
                
                if u_col in df_usuarios.columns and p_col in df_usuarios.columns:
                    df_usuarios[u_col] = df_usuarios[u_col].astype(str).str.strip()
                    df_usuarios[p_col] = df_usuarios[p_col].astype(str).str.strip()
                    
                    user = df_usuarios[(df_usuarios[u_col] == u) & (df_usuarios[p_col] == p)]
                    if not user.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = user.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o Contraseña incorrectos")
                else:
                    st.error(f"⚠️ Las columnas '{u_col}' o '{p_col}' no existen en la pestaña USUARIO.")
    st.stop()

# --- SI LLEGA AQUÍ, ES QUE YA SE LOGUEÓ ---
st.success(f"Bienvenido {st.session_state.user_data.get('Nombres')}")


