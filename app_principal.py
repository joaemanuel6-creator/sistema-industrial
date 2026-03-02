import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# IMPORTANTE: Importamos la función desde tu otro archivo
try:
    from copela import ventana_registro_copelas
except ImportError:
    st.error("⚠️ No se encontró el archivo 'copela.py'. Asegúrate de que esté en la misma carpeta en GitHub.")

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide", page_icon="🏭")

# Estilos para que se vea profesional (Dark Mode)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #064e3b !important; border-right: 2px solid #10b981; }
    h1, h2, h3, p, label { color: #ffffff !important; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAR ESTADOS DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 3. FUNCIONES DE CONEXIÓN ROBUSTAS
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        df = conn.read(worksheet=nombre_pestaña, ttl=0)
        # LIMPIEZA AUTOMÁTICA DE COLUMNAS: Quita espacios y normaliza
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Error al leer la pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

def guardar_datos(nombre_pestaña, nuevo_df):
    try:
        conn = conectar_drive()
        df_actual = leer_tabla(nombre_pestaña)
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        conn.update(worksheet=nombre_pestaña, data=df_final)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar en Google Sheets: {e}")
        return False

# 4. LÓGICA DE ACCESO (LOGIN)
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    with st.form("login_form"):
        u_input = st.text_input("👤 ID DE USUARIO").strip()
        p_input = st.text_input("🔑 CONTRASEÑA", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            df_usuarios = leer_tabla("USUARIO")
            
            if not df_usuarios.empty:
                # Buscamos las columnas correctas sin importar mayúsculas/minúsculas
                # Comparamos quitando espacios para evitar el KeyError
                try:
                    user_match = df_usuarios[
                        (df_usuarios['ID'].astype(str).str.strip() == u_input) & 
                        (df_usuarios['Contraseña'].astype(str).str.strip() == p_input)
                    ]
                    
                    if not user_match.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = user_match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ ID o Contraseña incorrectos.")
                except KeyError:
                    st.error("⚠️ El Excel no tiene las columnas 'ID' o 'Contraseña'.")
                    st.info(f"Columnas encontradas: {list(df_usuarios.columns)}")
            else:
                st.error("⚠️ No se pudo cargar la tabla de usuarios.")
    st.stop() # DETIENE LA APP AQUÍ SI NO SE HA LOGUEADO

# 5. MENÚ LATERAL (SOLO SE EJECUTA SI ESTÁ LOGUEADO)
st.sidebar.title("🏭 MENÚ PRINCIPAL")
st.sidebar.write(f"Operario: **{st.session_state.user_data.get('Nombres')}**")
st.sidebar.divider()

if st.sidebar.button("📂 REGISTRO DE COPELAS", use_container_width=True):
    # LLAMADA AL OTRO ARCHIVO
    ventana_registro_copelas(st.session_state.user_data.get('Nombres'), guardar_datos)

if st.sidebar.button("🚪 CERRAR SESIÓN", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# 6. PANEL DE VISTA GENERAL
st.title("📊 MONITOREO DE PRODUCCIÓN")
df_vista = leer_tabla("COPELA")
if not df_vista.empty:
    st.dataframe(df_vista.tail(10), use_container_width=True, hide_index=True)
else:
    st.info("No hay registros previos en la tabla COPELA.")




