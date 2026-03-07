import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import os
import sys

# --- FORZAR LA RUTA PARA ENCONTRAR USUARIO.PY ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

try:
    from usuario import modulo_permisos_maestro
except ImportError:
    st.error("⚠️ Error: No se encontró el archivo 'usuario.py' en el repositorio.")
    st.stop()

# 1. CONFIGURACIÓN Y CONEXIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL v10", layout="centered")

URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

# Inicializar estados de sesión
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False, "sub_modulo": None})

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; border: 1px solid #00d2ff; color: #00d2ff; background: transparent; }
    .stButton>button:hover { background: #00d2ff; color: black; }
    h1, h2, h3, label { color: #00d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. PANTALLA DE ACCESO (LOGIN / REGISTRO)
if not st.session_state.autenticado:
    if st.session_state.registrando:
        st.title("📝 Registro de Personal")
        with st.form("form_reg"):
            r_id = st.text_input("ID de Usuario (Login)").upper().strip()
            r_pass = st.text_input("Contraseña Nueva", type="password")
            r_nom = st.text_input("Nombres y Apellidos").upper()
            if st.form_submit_button("ENVIAR SOLICITUD DE REGISTRO"):
                if r_id and r_pass:
                    try:
                        supabase.table("USUARIO").insert({"ID": r_id, "CONTRASEÑA": r_pass, "NOMBRES": r_nom}).execute()
                        st.success("✅ Registrado con éxito. Solicita a un administrador que active tus permisos.")
                        st.session_state.registrando = False
                        st.rerun()
                    except: st.error("Error: El ID ya existe en la base de datos.")
                else: st.warning("Por favor completa ID y Contraseña.")
        if st.button("⬅ Volver al Inicio de Sesión"):
            st.session_state.registrando = False
            st.rerun()
    else:
        st.title("🏭 ACCESO AL SISTEMA")
        with st.form("login"):
            u = st.text_input("Usuario (ID)")
            p = st.text_input("Clave", type="password")
            if st.form_submit_button("INGRESAR AL PANEL"):
                res = supabase.table("USUARIO").select("*").eq("ID", u).eq("CONTRASEÑA", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['NOMBRES']
                    st.session_state.permisos = res.data[0] # Guardamos todos los permisos del usuario
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
        st.write("---")
        if st.button("➕ NO TENGO CUENTA - REGISTRARME"):
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# 3. PANEL DE CONTROL (ADENTRO)
with st.sidebar:
    st.header(f"👤 {st.session_state.usuario}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
    st.divider()

    # --- MENÚ DINÁMICO SEGÚN PERMISOS ---
    # Solo muestra el botón si en la DB tiene un 1 en la columna USUARIO
    if st.session_state.permisos.get("USUARIO") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.sub_modulo = "PERMISOS"

    if st.session_state.permisos.get("COPELAS") == 1:
        if st.button("📝 REGISTRO DE COPELAS"):
            st.session_state.sub_modulo = "COPELAS"

# 4. CARGA DE MÓDULOS EN PANTALLA CENTRAL
if st.session_state.sub_modulo == "PERMISOS":
    modulo_permisos_maestro(supabase) # Llama a la función del archivo usuario.py

elif st.session_state.sub_modulo == "COPELAS":
    st.title("📝 Registro de Copelas")
    st.info("Módulo de producción de copelas habilitado.")
    # Aquí puedes añadir tu formulario de copelas
    if st.button("⬅ Volver"):
        st.session_state.sub_modulo = None
        st.rerun()

else:
    st.title("🚀 Bienvenido al Panel Principal")
    st.write("Selecciona una opción en el menú de la izquierda para comenzar.")
