import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from copela import ventana_registro_copelas 

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide")

# 2. SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 3. CONEXIÓN (CON REINTENTO AUTOMÁTICO)
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        df = conn.read(worksheet=nombre_pestaña, ttl=0)
        df.columns = [str(c).strip() for c in df.columns] # Limpiar nombres de columnas
        return df
    except Exception as e:
        st.error(f"❌ Error al leer '{nombre_pestaña}'. Verifica que la pestaña exista en el Excel.")
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

# 4. LOGIN
if not st.session_state.autenticado:
    st.title("🔐 ACCESO")
    with st.form("login"):
        u = st.text_input("Usuario (ID)").strip()
        p = st.text_input("Contraseña", type="password").strip()
        if st.form_submit_button("Ingresar"):
            df_u = leer_tabla("USUARIO")
            if not df_u.empty and 'ID' in df_u.columns:
                user = df_u[(df_u['ID'].astype(str) == u) & (df_u['Contraseña'].astype(str) == p)]
                if not user.empty:
                    st.session_state.autenticado = True
                    st.session_state.user_data = user.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Datos incorrectos")
            else:
                st.warning("No se encontró la columna 'ID' en la pestaña USUARIO")
    st.stop()

# 5. MENÚ
st.sidebar.title("MENÚ")
st.sidebar.write(f"Operario: {st.session_state.user_data.get('Nombres')}")

if st.sidebar.button("📂 REGISTRO COPELAS", use_container_width=True):
    ventana_registro_copelas(st.session_state.user_data.get('Nombres'), guardar_datos)

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

st.title("🏭 PANEL DE CONTROL")
st.write("Bienvenido. Registre sus datos en el menú lateral.")





