import streamlit as st
from supabase import create_client, Client
import os
import sys

# --- FORZAR RUTA PARA ENCONTRAR EL ARCHIVO CON "S" ---
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

# Intentamos importar desde 'usuarios' (nombre exacto en tu GitHub)
try:
    from usuarios import modulo_permisos_maestro
except ImportError:
    st.error("⚠️ No se encontró 'usuarios.py'. Verifica el nombre en tu repositorio.")
    st.stop()

# 1. CONEXIÓN A SUPABASE
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

# Configuración de página
st.set_page_config(page_title="SISTEMA INDUSTRIAL v10", layout="centered")

# Inicializar estados
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False, "sub_modulo": None})

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .stButton>button { width: 100%; border: 1px solid #00d2ff; color: #00d2ff; background: transparent; }
    .stButton>button:hover { background: #00d2ff; color: black; }
    h1, h2, h3, label { color: #00d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE ACCESO
if not st.session_state.autenticado:
    if st.session_state.registrando:
        st.title("📝 Registro de Personal")
        with st.form("reg_form"):
            r_id = st.text_input("ID (Login)").upper().strip()
            r_pass = st.text_input("Clave Nueva", type="password")
            r_nom = st.text_input("Nombres y Apellidos").upper()
            if st.form_submit_button("REGISTRARME"):
                if r_id and r_pass:
                    try:
                        supabase.table("USUARIO").insert({"ID": r_id, "CONTRASEÑA": r_pass, "NOMBRES": r_nom}).execute()
                        st.success("✅ Registrado. Pide al admin que active tus permisos.")
                        st.session_state.registrando = False
                        st.rerun()
                    except: st.error("Error: El ID ya existe.")
        if st.button("⬅ Volver"):
            st.session_state.registrando = False
            st.rerun()
    else:
        st.title("🏭 ACCESO INDUSTRIAL")
        with st.form("login"):
            u = st.text_input("Usuario (ID)")
            p = st.text_input("Clave", type="password")
            if st.form_submit_button("INGRESAR"):
                res = supabase.table("USUARIO").select("*").eq("ID", u).eq("CONTRASEÑA", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['NOMBRES']
                    st.session_state.permisos = res.data[0]
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
        if st.button("➕ NO TENGO CUENTA - REGISTRARME"):
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# 3. PANEL DE CONTROL
with st.sidebar:
    st.header(f"👤 {st.session_state.usuario}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
    st.divider()

    # Verificar permiso de USUARIO para ver el botón de gestión
    if st.session_state.permisos.get("USUARIO") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.sub_modulo = "PERMISOS"

# 4. CARGA DE MÓDULOS
if st.session_state.sub_modulo == "PERMISOS":
    modulo_permisos_maestro(supabase) # Llama a la función en usuarios.py
else:
    st.title("🚀 Bienvenido")
    st.write("Selecciona una opción en el menú lateral.")
