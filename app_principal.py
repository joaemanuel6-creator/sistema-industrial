import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import os
import sys

# Forzar a Python a buscar en la carpeta actual para encontrar usuario.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from usuario import modulo_permisos_maestro
except ImportError:
    st.error("⚠️ Error: No se encontró el archivo 'usuario.py'. Verifica que esté en la misma carpeta de GitHub.")

# 1. CONFIGURACIÓN Y CONEXIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL v10", layout="wide")

URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": {}, "registrando": False, "sub_modulo": None})

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; border: 1px solid #00d2ff; color: #00d2ff; background: transparent; }
    .stButton>button:hover { background: #00d2ff; color: black; }
    h1, h2, h3, label { color: #00d2ff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN Y REGISTRO
if not st.session_state.autenticado:
    if st.session_state.registrando:
        st.title("📝 Registro de Nuevo Personal")
        with st.form("reg_form"):
            r_id = st.text_input("ID de Usuario").upper().strip()
            r_pass = st.text_input("Contraseña", type="password")
            r_nom = st.text_input("Nombres Completos").upper()
            if st.form_submit_button("REGISTRARSE"):
                if r_id and r_pass:
                    try:
                        supabase.table("USUARIO").insert({"ID": r_id, "CONTRASEÑA": r_pass, "NOMBRES": r_nom}).execute()
                        st.success("✅ Registrado. El administrador debe activarte.")
                        st.session_state.registrando = False
                        st.rerun()
                    except: st.error("Ese ID ya existe.")
        if st.button("⬅ Volver"):
            st.session_state.registrando = False
            st.rerun()
    else:
        st.title("🏭 ACCESO AL SISTEMA")
        with st.form("login"):
            u = st.text_input("ID Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ENTRAR"):
                res = supabase.table("USUARIO").select("*").eq("ID", u).eq("CONTRASEÑA", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['NOMBRES']
                    st.session_state.permisos = res.data[0]
                    st.rerun()
                else: st.error("❌ Datos incorrectos")
        if st.button("➕ CREAR CUENTA NUEVA"):
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# 3. SIDEBAR Y MENÚ
with st.sidebar:
    st.header(f"👤 {st.session_state.usuario}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
    st.divider()

    # Si tiene permiso de USUARIO, ve el botón de gestión
    if st.session_state.permisos.get("USUARIO") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.sub_modulo = "PERMISOS"

# 4. CARGA DE MÓDULO EXTERNO
if st.session_state.sub_modulo == "PERMISOS":
    modulo_permisos_maestro(supabase)
else:
    st.title("🚀 Panel Principal")
    st.write("Bienvenido. Selecciona una opción del menú lateral.")
