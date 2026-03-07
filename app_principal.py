import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL v9.0", layout="centered", page_icon="🏭")

# CREDENCIALES SUPABASE
SUPABASE_URL = "https://rrekwemzohknmaxzsefy.supabase.co"
SUPABASE_KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# 2. DISEÑO CSS (Tu estilo cian/oscuro)
st.markdown("""
    <style>
    .stApp { background: #0d1117; }
    .titulo-central { color: #00d2ff; font-size: 35px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .stButton > button { background-color: transparent; border: 1px solid #00d2ff; color: #00d2ff; width: 100%; border-radius: 10px; }
    .stButton > button:hover { background-color: #00d2ff; color: black; }
    .btn-nuevo { background-color: #161b22 !important; border: 1px dashed #ffda79 !important; color: #ffda79 !important; }
    h1, h2, h3, p, span, label { color: #e6edf3 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. MANEJO DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "registrando": False})

# --- PANTALLA DE ACCESO (LOGIN + BOTÓN NUEVO) ---
if not st.session_state.autenticado:
    
    # OPCIÓN A: FORMULARIO DE REGISTRO
    if st.session_state.registrando:
        st.markdown('<p class="titulo-central">📝 REGISTRO DE NUEVO PERSONAL</p>', unsafe_allow_html=True)
        with st.form("registro_nuevo_en_login"):
            col1, col2 = st.columns(2)
            with col1:
                n_id = st.text_input("🆔 ID Usuario (Ej: M123)").upper().strip()
                n_pass = st.text_input("🔑 Contraseña", type="password")
                n_nom = st.text_input("Nombres").upper()
            with col2:
                n_ape = st.text_input("Apellidos").upper()
                n_dni = st.text_input("DNI")
                n_tipo = st.selectbox("Tipo de Acceso", ["OPERARIO", "SUPERVISOR"])

            st.info("Nota: Al registrarse, un administrador deberá activar sus permisos de módulos.")
            
            if st.form_submit_button("💾 FINALIZAR REGISTRO"):
                if n_id and n_pass:
                    payload = {
                        "ID": n_id, "CONTRASEÑA": n_pass, "NOMBRES": n_nom, 
                        "APELLIDOS": n_ape, "DNI": n_dni, "TIPO_USUARIO": n_tipo,
                        "FECHA_REGISTRO": str(datetime.now())
                    }
                    try:
                        supabase.table("USUARIO").insert(payload).execute()
                        st.success("✅ ¡Registrado! Ahora intenta ingresar.")
                        st.session_state.registrando = False
                        st.rerun()
                    except:
                        st.error("Error: El ID ya existe o hay un problema de red.")
                else:
                    st.warning("Completa ID y Contraseña.")
        
        if st.button("⬅ VOLVER AL LOGIN"):
            st.session_state.registrando = False
            st.rerun()

    # OPCIÓN B: LOGIN TRADICIONAL
    else:
        st.markdown('<p class="titulo-central">🏗️ SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login"):
                u_id = st.text_input("🆔 USUARIO").strip()
                u_pass = st.text_input("🔑 CLAVE", type="password").strip()
                if st.form_submit_button("INGRESAR AL PANEL"):
                    res = supabase.table("USUARIO").select("*").eq("ID", u_id).eq("CONTRASEÑA", u_pass).execute()
                    if res.data:
                        st.session_state.autenticado = True
                        st.session_state.usuario = res.data[0]['NOMBRES']
                        st.rerun()
                    else:
                        st.error("❌ Credenciales inválidas")
            
            st.write("---")
            # BOTÓN PARA ABRIR EL FORMULARIO DE REGISTRO
            if st.button("➕ NO TENGO CUENTA (REGISTRARME)", key="btn_reg"):
                st.session_state.registrando = True
                st.rerun()
    st.stop()

# --- 4. PANEL PRINCIPAL (Solo se ve si está autenticado) ---
st.sidebar.title(f"👤 {st.session_state.usuario}")
if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

st.title("🚀 Panel de Control Industrial")
st.write("Bienvenido al sistema de gestión en la nube.")
# Aquí irían tus módulos (Copelas, Crisoles, etc.)
