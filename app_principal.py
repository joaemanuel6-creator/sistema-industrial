import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Intentar importar el módulo de copelas
try:
    from copela import ventana_registro_copelas
except ImportError:
    st.error("⚠️ No se encontró 'copela.py' en la misma carpeta.")

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide")

# 2. ESTADOS DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 3. FUNCIONES DE BASE DE DATOS
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        df = conn.read(worksheet=nombre_pestaña, ttl=0)
        # Limpieza de nombres de columnas (quitar espacios y basura)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Error al leer pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

def guardar_datos(nombre_pestaña, nuevo_df):
    try:
        conn = conectar_drive()
        df_actual = leer_tabla(nombre_pestaña)
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        conn.update(worksheet=nombre_pestaña, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 4. LÓGICA DE LOGIN REFORZADA
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    with st.form("login_form"):
        u_input = st.text_input("Usuario (ID)").strip()
        p_input = st.text_input("Contraseña", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            df_u = leer_tabla("USUARIO")
            
            if not df_u.empty:
                # Buscamos las columnas sin importar mayúsculas/minúsculas
                cols_nombres = {c.upper(): c for c in df_u.columns}
                
                if 'ID' in cols_nombres and 'CONTRASEÑA' in cols_nombres:
                    c_id = cols_nombres['ID']
                    c_pass = cols_nombres['CONTRASEÑA']
                    
                    # Validación
                    match = df_u[
                        (df_u[c_id].astype(str).str.strip() == u_input) & 
                        (df_u[c_pass].astype(str).str.strip() == p_input)
                    ]
                    
                    if not match.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                else:
                    st.warning(f"⚠️ No se encontró la columna 'ID'. Columnas detectadas: {list(df_u.columns)}")
            else:
                st.error("La pestaña USUARIO está vacía o no existe.")
    st.stop()

# 5. MENÚ PRINCIPAL
st.sidebar.title("🏭 MENÚ")
st.sidebar.write(f"Operario: **{st.session_state.user_data.get('Nombres')}**")
st.sidebar.divider()

if st.sidebar.button("📂 REGISTRO COPELAS", use_container_width=True):
    ventana_registro_copelas(st.session_state.user_data.get('Nombres'), guardar_datos)

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

st.title("📊 PANEL DE CONTROL")
df_vista = leer_tabla("COPELA")
if not df_vista.empty:
    st.dataframe(df_vista.tail(10), use_container_width=True, hide_index=True)





