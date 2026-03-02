import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
# Importamos la función del otro archivo
from copela import ventana_registro_copelas 

st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide")

# 1. INICIALIZAR SESIÓN (Para que no de error de atributo)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.user_data = {}

# 2. FUNCIONES DE BASE DE DATOS
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre):
    try:
        conn = conectar_drive()
        # Intentamos leer la pestaña específica
        return conn.read(worksheet=nombre, ttl=0)
    except Exception as e:
        st.error(f"❌ Error de conexión con Google Sheets.")
        st.info("Revisa que el archivo sea Público y que el link en Secrets termine en /edit")
        # Esto imprimirá el error real en la pantalla para que lo veas
        st.write(f"Detalle técnico: {e}")
        return pd.DataFrame()

def guardar_datos(nombre, df_nuevo):
    conn = conectar_drive()
    df_actual = leer_tabla(nombre)
    df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
    conn.update(worksheet=nombre, data=df_final)
    return True

# 3. LÓGICA DE LOGIN (BLOQUEO)
if not st.session_state.autenticado:
    st.title("🔐 INICIO DE SESIÓN")
    with st.form("login"):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            df_user = leer_tabla("USUARIO")
            # Validación simple (ajusta según tus columnas)
            match = df_user[(df_user['ID'].astype(str) == u) & (df_user['Contraseña'].astype(str) == p)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.user_data = match.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop() # DETIENE EL CÓDIGO AQUÍ SI NO ESTÁ LOGUEADO

# 4. MENU LATERAL (SOLO SE VE SI PASÓ EL LOGIN)
st.sidebar.title("🏭 MENÚ")
st.sidebar.write(f"Operario: {st.session_state.user_data['Nombres']}")

if st.sidebar.button("📂 REGISTRO COPELAS", use_container_width=True):
    # Ahora sí, user_data ya existe y tiene datos
    ventana_registro_copelas(st.session_state.user_data['Nombres'], guardar_datos)

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

st.title("Panel Principal")
st.write("Bienvenido al sistema de control industrial.")



