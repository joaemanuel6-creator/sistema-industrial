import streamlit as st
from supabase import create_client, Client
import os
import sys

# --- CONFIGURACIÓN DE RUTAS ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos la función desde usuarios.py (asegúrate que el archivo se llame usuarios.py)
try:
    from usuarios import formulario_registro
except ImportError:
    st.error("⚠️ No se encontró el archivo 'usuarios.py'")
    st.stop()

# --- CONEXIÓN SUPABASE ---
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

# Inicializar estados
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False})

# --- PANTALLA DE ENTRADA ---
if not st.session_state.autenticado:
    
    # Si el usuario presionó el botón de registrar, llamamos a la función de usuarios.py
    if st.session_state.registrando:
        formulario_registro(supabase)
    
    # Si no, mostramos el Login normal
    else:
        st.markdown("<h1 style='text-align: center; color: #00d2ff;'>🏭 ACCESO AL SISTEMA</h1>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                u_id = st.text_input("🆔 ID USUARIO")
                u_pass = st.text_input("🔑 CONTRASEÑA", type="password")
                
                if st.form_submit_button("INGRESAR"):
                    res = supabase.table("USUARIO").select("*").eq("ID", u_id).eq("Contrasena", u_pass).execute()
                    if res.data:
                        st.session_state.autenticado = True
                        st.session_state.usuario = res.data[0]['Nombres']
                        st.session_state.permisos = res.data[0]
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
            
            st.write("---")
            # EL BOTÓN QUE ACTIVA LA FUNCIÓN DE USUARIOS.PY
            if st.button("➕ ¿NO TIENES CUENTA? REGÍSTRATE AQUÍ"):
                st.session_state.registrando = True
                st.rerun()
    st.stop()

# --- PANEL PRINCIPAL (SI YA ENTRÓ) ---
st.title(f"🚀 Bienvenido, {st.session_state.usuario}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.clear()
    st.rerun()
