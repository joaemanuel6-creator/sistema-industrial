import streamlit as st
from supabase import create_client, Client
import os
import sys

# --- CONFIGURACIÓN DE RUTA ---
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

try:
    from usuarios import modulo_permisos_maestro
except ImportError:
    st.error("⚠️ No se encontró 'usuarios.py' en GitHub.")
    st.stop()

# --- CONEXIÓN SUPABASE ---
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="SISTEMA INDUSTRIAL v10", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False, "sub_modulo": None})

# 2. LOGIN Y REGISTRO
if not st.session_state.autenticado:
    if st.session_state.registrando:
        st.title("➕ Registro de Personal")
        with st.form("reg_form"):
            r_id = st.text_input("ID (Login)").upper().strip()
            r_pass = st.text_input("Contrasena", type="password")
            r_nom = st.text_input("Nombres").upper()
            r_ape = st.text_input("Apellidos").upper()
            r_dni = st.text_input("DNI")
            if st.form_submit_button("ENVIAR DATOS"):
                payload = {
                    "ID": r_id, "Contrasena": r_pass, "Nombres": r_nom, 
                    "Apellidos": r_ape, "DNI": r_dni, "Usuario_Tipo": "OPERARIO"
                }
                try:
                    supabase.table("USUARIO").insert(payload).execute()
                    st.success("✅ Registrado. Solicita activación al admin.")
                    st.session_state.registrando = False
                    st.rerun()
                except: st.error("El ID ya existe.")
        if st.button("⬅ Volver"):
            st.session_state.registrando = False
            st.rerun()
    else:
        st.title("🏭 ACCESO INDUSTRIAL")
        with st.form("login"):
            u = st.text_input("ID Usuario")
            p = st.text_input("Contrasena", type="password")
            if st.form_submit_button("INGRESAR"):
                # Buscamos usando los nombres de columna exactos
                res = supabase.table("USUARIO").select("*").eq("ID", u).eq("Contrasena", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['Nombres']
                    st.session_state.permisos = res.data[0]
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
        if st.button("➕ REGISTRARME"):
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# 3. SIDEBAR
with st.sidebar:
    st.header(f"👤 {st.session_state.usuario}")
    if st.button("🚪 Salir"):
        st.session_state.clear()
        st.rerun()
    st.divider()

    # Si tiene permiso en la columna 'Usuario' (con U mayúscula como pediste)
    if st.session_state.permisos.get("Usuario") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.sub_modulo = "PERMISOS"

# 4. CARGA DE MÓDULO
if st.session_state.sub_modulo == "PERMISOS":
    modulo_permisos_maestro(supabase)
else:
    st.title("🚀 Panel Principal")
    st.write("Selecciona una opción a la izquierda.")
