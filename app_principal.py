import streamlit as st
from supabase import create_client, Client
import os
import sys

# --- BLOQUE DE CONEXIÓN DE ARCHIVOS ---
# Esto obliga a Streamlit Cloud a buscar en la carpeta actual
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

# Intentamos importar las funciones desde usuarios.py
try:
    from usuarios import formulario_registro, modulo_permisos_maestro
except ImportError as e:
    st.error(f"⚠️ Error Crítico: No se pudo cargar 'usuarios.py'. Detalle: {e}")
    st.stop()

# --- CONEXIÓN SUPABASE ---
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="SISTEMA INDUSTRIAL v11", layout="centered")

# Inicializar estados de sesión
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False, "sub_modulo": None})

# --- INTERFAZ DE ACCESO ---
if not st.session_state.autenticado:
    if st.session_state.registrando:
        # AQUÍ LLAMAMOS AL FORMULARIO DE usuarios.py
        formulario_registro(supabase)
    else:
        st.markdown("<h2 style='text-align: center; color: #00d2ff;'>🏭 ACCESO AL SISTEMA</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("🆔 ID Usuario").upper().strip()
            p = st.text_input("🔑 Contrasena", type="password")
            if st.form_submit_button("INGRESAR"):
                res = supabase.table("USUARIO").select("*").eq("ID", u).eq("Contrasena", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['Nombres']
                    st.session_state.permisos = res.data[0]
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
        
        st.write("---")
        if st.button("➕ REGISTRARME (SOLICITAR ACCESO)"):
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# --- PANEL DE CONTROL (SI YA ESTÁ LOGUEADO) ---
with st.sidebar:
    st.header(f"👤 {st.session_state.usuario}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
    st.divider()

    # Botón de permisos (Solo si en DB 'Usuario' es 1)
    if st.session_state.permisos.get("Usuario") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.sub_modulo = "PERMISOS"

# Carga de módulos
if st.session_state.sub_modulo == "PERMISOS":
    modulo_permisos_maestro(supabase)
else:
    st.title("🚀 Bienvenido")
    st.write("Seleccione un módulo en el menú lateral para empezar.")
