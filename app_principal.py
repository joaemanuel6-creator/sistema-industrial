import streamlit as st
from supabase import create_client, Client
from usuario import modulo_permisos_maestro # IMPORTANTE

# CONFIGURACIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL v10", layout="wide")

URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "registrando": False, "modulo": None})

# --- PANTALLA INICIAL (LOGIN / REGISTRO) ---
if not st.session_state.autenticado:
    if st.session_state.registrando:
        st.subheader("📝 Crear Nueva Cuenta (Solicitud)")
        with st.form("reg_form"):
            n_id = st.text_input("ID").upper()
            n_pass = st.text_input("Clave", type="password")
            n_nom = st.text_input("Nombres").upper()
            if st.form_submit_button("ENVIAR REGISTRO"):
                supabase.table("USUARIO").insert({"ID": n_id, "CONTRASEÑA": n_pass, "NOMBRES": n_nom}).execute()
                st.success("Registrado. Pide al administrador que te dé permisos.")
                st.session_state.registrando = False
                st.rerun()
        if st.button("⬅ Volver"): 
            st.session_state.registrando = False
            st.rerun()
    else:
        st.title("🏭 SISTEMA INDUSTRIAL")
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.form_submit_button("ENTRAR"):
                res = supabase.table("USUARIO").select("*").eq("ID", u).eq("CONTRASEÑA", p).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]['NOMBRES']
                    # Guardamos los permisos en la sesión
                    st.session_state.permisos_datos = res.data[0]
                    st.rerun()
        if st.button("➕ REGISTRARSE"): 
            st.session_state.registrando = True
            st.rerun()
    st.stop()

# --- PANEL DE CONTROL (ADENTRO) ---
with st.sidebar:
    st.write(f"👤 {st.session_state.usuario}")
    if st.button("🚪 Salir"): st.session_state.clear(); st.rerun()
    st.divider()
    
    # Botón para ir al formato de dar permisos (Solo si el admin tiene permiso de USUARIO)
    if st.session_state.permisos_datos.get("USUARIO") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.modulo = "PERMISOS"

# Cargar el módulo desde usuario.py
if st.session_state.modulo == "PERMISOS":
    modulo_permisos_maestro(supabase)
