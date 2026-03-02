import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- IMPORTACIÓN DEL OTRO ARCHIVO ---
from copela import abrir_ventana_copelas

st.set_page_config(page_title="SISTEMA PRINCIPAL", layout="wide")

# (Aquí van tus funciones de conectar_drive, leer_tabla y guardar_datos que ya tenemos)
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    conn = conectar_drive()
    return conn.read(worksheet=nombre_pestaña, ttl=0)

def guardar_datos(nombre_pestaña, nuevo_df):
    conn = conectar_drive()
    df_actual = leer_tabla(nombre_pestaña)
    df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
    conn.update(worksheet=nombre_pestaña, data=df_final)
    return True

# --- LÓGICA DE LOGIN (Simplificada para el ejemplo) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # ... (Tu código de login aquí) ...
    if st.button("Simular Ingreso (Prueba)"): # Borra esto cuando pongas tu login real
        st.session_state.autenticado = True
        st.session_state.user_data = {"Nombres": "Manuel"}
        st.rerun()
    st.stop()

# --- SIDEBAR CON EL BOTÓN ---
st.sidebar.title("🏭 MENÚ")

if st.sidebar.button("📂 REGISTRO COPELAS", use_container_width=True):
    # LLAMAMOS A LA FUNCIÓN DEL OTRO ARCHIVO
    abrir_ventana_copelas(st.session_state.user_data['Nombres'], guardar_datos)

st.title("Bienvenido al Sistema")

