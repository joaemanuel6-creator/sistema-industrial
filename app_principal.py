import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
# Importamos la función del otro archivo
from copela import ventana_registro_copelas 

# Configuración de conexión
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre):
    conn = conectar_drive()
    return conn.read(worksheet=nombre, ttl=0)

def guardar_datos(nombre, df_nuevo):
    conn = conectar_drive()
    df_actual = leer_tabla(nombre)
    df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
    conn.update(worksheet=nombre, data=df_final)
    return True

# --- SIDEBAR ---
st.sidebar.title("MENÚ")
if st.sidebar.button("📂 REGISTRO COPELAS"):
    # Llamamos a la función pasándole lo necesario
    ventana_registro_copelas(st.session_state.user_data['Nombres'], guardar_datos)


