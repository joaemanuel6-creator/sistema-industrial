import streamlit as st
from supabase import create_client, Client
import os
import sys
from datetime import datetime

# --- CONFIGURACIÓN DE RUTA PARA IMPORTAR usuarios.py ---
# Esto asegura que Streamlit encuentre el archivo en la nube
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

try:
    from usuarios import modulo_permisos_maestro
except ImportError:
    st.error("⚠️ Error: No se encontró el archivo 'usuarios.py' en el repositorio de GitHub.")
    st.stop()

# --- CONEXIÓN A SUPABASE ---
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

# Configuración visual de la página
st.set_page_config(page_title="SISTEMA INDUSTRIAL v10", layout="wide", page_icon="🏭")

# --- INICIALIZACIÓN DE ESTADOS DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.update({
        "autenticado": False, 
        "usuario_nombre": "", 
        "permisos": {}, 
        "registrando": False, 
        "sub_modulo": None
    })

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 2px solid #00d2ff; }
    .titulo-principal { color: #00d2ff; font-weight: bold; text-align: center; font-size: 30px; }
    .stButton>button { width: 100%; border-radius: 8px; border: 1px solid #00d2ff; color: #00d2ff; background: transparent; transition: 0.3s; }
    .stButton>button:hover { background: #00d2ff; color: black; box-shadow: 0px 0px 15px #00d2ff; }
    label { color: #00d2ff !important; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #0d1117; color: white; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ACCESO (LOGIN Y REGISTRO) ---
if not st.session_state.autenticado:
    
    # OPCIÓN A: FORMULARIO DE REGISTRO
    if st.session_state.registrando:
        st.markdown('<p class="titulo-principal">📝 REGISTRO DE NUEVO PERSONAL</p>', unsafe_allow_html=True)
        with st.form("registro_nuevo"):
            c1, c2 = st.columns(2)
            with c1:
                r_id = st.text_input("🆔 ID de Usuario (Login)").upper().strip()
                r_pass = st.text_input("🔑 Contrasena", type="password")
                r_nom = st.text_input("Nombres").upper()
            with c2:
                r_ape = st.text_input("Apellidos").upper()
                r_dni = st.text_input("DNI")
                r_tipo = st.selectbox("Tipo solicitado", ["OPERARIO", "SUPERVISOR"])

            if st.form_submit_button("FINALIZAR REGISTRO"):
                if r_id and r_pass and r_nom:
                    payload = {
                        "ID": r_id, 
                        "Contrasena": r_pass, 
                        "Nombres": r_nom, 
                        "Apellidos": r_ape, 
                        "DNI": r_dni, 
                        "Usuario_Tipo": r_tipo,
                        "Fecha_Registro": str(datetime.now().date())
                    }
                    try:
                        supabase.table("USUARIO").insert(payload).execute()
                        st.success("✅ ¡Registrado! Ahora pide al administrador que active tus permisos.")
                        st.session_state.registrando = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: El ID ya existe o falta conexión. {e}")
                else:
                    st.warning("ID, Contrasena y Nombres son obligatorios.")
        
        if st.button("⬅ VOLVER AL LOGIN"):
            st.session_state.registrando = False
            st.rerun()

    # OPCIÓN B: LOGIN TRADICIONAL
    else:
        st.markdown('<p class="titulo-principal">🏗️ SISTEMA DE GESTIÓN INDUSTRIAL</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                u_input = st.text_input("🆔 USUARIO (ID)")
                p_input = st.text_input("🔑 CONTRASENA", type="password")
                if st.form_submit_button("INGRESAR AL SISTEMA"):
                    # Consulta exacta a las columnas que pasaste
                    res = supabase.table("USUARIO").select("*").eq("ID", u_input).eq("Contrasena", p_input).execute()
                    if res.data:
                        fila = res.data[0]
                        st.session_state.autenticado = True
                        st.session_state.usuario_nombre = f"{fila['Nombres']} {fila['Apellidos']}"
                        st.session_state.permisos = fila  # Guardamos todos los campos (Copela, Crisol, Usuario, etc.)
                        st.rerun()
                    else:
                        st.error("❌ ID o Contrasena incorrectos.")
            
            st.write("---")
            if st.button("➕ NO TENGO CUENTA (REGISTRARME)"):
                st.session_state.registrando = True
                st.rerun()
    st.stop()

# --- PANEL DE CONTROL (USUARIO AUTENTICADO) ---
with st.sidebar:
    st.markdown(f'<p style="color:#ffda79; font-size:20px; text-align:center;">👤 {st.session_state.usuario_nombre}</p>', unsafe_allow_html=True)
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.markdown('<p style="color:#00d2ff; font-weight:bold;">MÓDULOS DISPONIBLES</p>', unsafe_allow_html=True)

    # Menú Dinámico basado en las columnas de tu base de datos
    # Solo mostramos el botón si el valor en la columna es 1
    
    if st.session_state.permisos.get("Usuario") == 1:
        if st.button("⚙️ GESTIÓN DE PERMISOS"):
            st.session_state.sub_modulo = "PERMISOS"

    if st.session_state.permisos.get("Copela") == 1:
        if st.button("📝 REGISTRO DE COPELAS"):
            st.session_state.sub_modulo = "COPELAS"

    if st.session_state.permisos.get("Almacen") == 1:
        if st.button("📦 ALMACÉN"):
            st.session_state.sub_modulo = "ALMACEN"

    if st.session_state.permisos.get("Historial") == 1:
        if st.button("📜 HISTORIAL"):
            st.session_state.sub_modulo = "HISTORIAL"

# --- CARGA DE CONTENIDO CENTRAL ---
if st.session_state.sub_modulo == "PERMISOS":
    modulo_permisos_maestro(supabase) # Llama a la función en usuarios.py

elif st.session_state.sub_modulo == "COPELAS":
    st.title("📝 Módulo de Copelas")
    st.write("Bienvenido al registro de producción de copelas.")
    # Aquí puedes llamar a una función de copela.py si lo deseas
    if st.button("⬅ Volver"):
        st.session_state.sub_modulo = None
        st.rerun()

else:
    # Pantalla de Bienvenida por defecto
    st.markdown(f"""
        <div style='text-align:center; margin-top:100px;'>
            <h1 style='color:#00d2ff;'>BIENVENIDO AL PANEL INDUSTRIAL</h1>
            <p style='font-size:18px;'>Hola <b>{st.session_state.usuario_nombre}</b>, selecciona un módulo en el menú lateral para operar.</p>
        </div>
    """, unsafe_allow_html=True)
