import streamlit as st
from supabase import create_client, Client
import os
import sys

# --- CONEXIÓN DE ARCHIVOS ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Importamos la función de registro desde usuarios.py
    from usuarios import formulario_crear_usuario
except ImportError:
    st.error("⚠️ No se encontró el archivo 'usuarios.py' en el repositorio.")
    st.stop()

# --- CONEXIÓN SUPABASE ---
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False})

# --- LÓGICA DE PANTALLA ---
if not st.session_state.autenticado:
    
    # SI EL BOTÓN FUE PRESIONADO, SE ABRE EL FORMULARIO DE usuarios.py
    if st.session_state.registrando:
        formulario_crear_usuario(supabase)
    
    # SI NO, MUESTRA EL LOGIN
    else:
        st.title("🏭 BIENVENIDO AL SISTEMA")
        with st.form("login_form"):
            user_input = st.text_input("Usuario")
            pass_input = st.text_input("Contrasena", type="password")
            if st.form_submit_button("INGRESAR"):
                res = supabase.table("USUARIO").select("*").eq("ID", user_input).eq("Contrasena", pass_input).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['Nombres']
                    st.session_state.permisos = res.data[0]
                    st.rerun()
                else:
                    st.error("Datos incorrectos")
        
        st.write("---")
        # BOTÓN QUE ABRE LA VENTANA DE usuarios.py
        if st.button("➕ ¿NO TIENES CUENTA? REGÍSTRATE AQUÍ"):
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# --- SISTEMA ADENTRO ---
st.success(f"Sesión iniciada como: {st.session_state.usuario}")
if st.sidebar.button("Salir"):
    st.session_state.clear()
    st.rerun()
