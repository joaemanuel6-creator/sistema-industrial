import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN INICIAL (DEBE IR PRIMERO)
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide")

# Estilos visuales (Tu diseño original)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #064e3b !important; border-right: 4px solid #10b981; }
    .user-text { font-size: 24px !important; color: #ffffff !important; font-weight: 900 !important; }
    h1, h2, h3, p, label { color: #ffffff !important; }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 50px;
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white !important; font-weight: bold; border: 1px solid white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAR SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}, "modulo_activo": "COPELAS"})

# 3. FUNCIONES DE CONEXIÓN ROBUSTAS
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        # Intentamos leer por nombre, si falla, traerá un error que capturamos abajo
        return conn.read(worksheet=nombre_pestaña, ttl=0)
    except Exception:
        try:
            # SI FALLA EL NOMBRE, INTENTA LEER LA PRIMERA HOJA (POSICIÓN 0)
            conn = conectar_drive()
            df = conn.read(ttl=0) 
            return df
        except Exception as e:
            st.error(f"Error crítico de conexión: {e}")
            return pd.DataFrame()

def guardar_datos(nombre_pestaña, nuevo_df):
    try:
        conn = conectar_drive()
        df_actual = leer_tabla(nombre_pestaña)
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        conn.update(worksheet=nombre_pestaña, data=df_final)
        st.success("✅ ¡Datos guardados en la nube!")
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 4. PANTALLA DE LOGIN
if not st.session_state.autenticado:
    st.title("🔐 CONTROL DE ACCESO")
    with st.form("login_form"):
        u_input = st.text_input("👤 ID DE USUARIO").strip()
        p_input = st.text_input("🔑 CONTRASEÑA", type="password").strip()
        
        if st.form_submit_button("INGRESAR AL SISTEMA"):
            df_usuarios = leer_tabla("USUARIO")
            
            if not df_usuarios.empty:
                # Normalizar nombres de columnas (quitar espacios y manejar Ñ)
                df_usuarios.columns = [str(c).strip() for c in df_usuarios.columns]
                
                # Buscamos las columnas correctas
                col_id = 'ID'
                col_pw = 'Contraseña' if 'Contraseña' in df_usuarios.columns else 'Contrasena'
                
                if col_id in df_usuarios.columns and col_pw in df_usuarios.columns:
                    # Convertir todo a string para comparar
                    df_usuarios[col_id] = df_usuarios[col_id].astype(str).str.strip()
                    df_usuarios[col_pw] = df_usuarios[col_pw].astype(str).str.strip()
                    
                    user_match = df_usuarios[(df_usuarios[col_id] == u_input) & (df_usuarios[col_pw] == p_input)]
                    
                    if not user_match.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = user_match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o Contraseña incorrectos")
                else:
                    st.error(f"⚠️ El Excel debe tener columnas llamadas 'ID' y 'Contraseña'. Encontrado: {list(df_usuarios.columns)}")
            else:
                st.error("⚠️ No se pudo leer la tabla de usuarios. Verifica los permisos de 'Editor' en el botón Compartir de Google Drive.")
    st.stop()

# 5. INTERFAZ PRINCIPAL (DESPUÉS DEL LOGIN)
st.sidebar.title("🏭 MENÚ INDUSTRIAL")
st.sidebar.markdown(f"**Operador:** {st.session_state.user_data.get('Nombres', 'Usuario')}")
st.sidebar.divider()

opciones = ["COPELAS", "CRISOLES", "MEZCLA", "LIMPIEZA", "ALMACEN"]
for op in opciones:
    if st.sidebar.button(f"📂 {op}"):
        st.session_state.modulo_activo = op

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

# 6. MÓDULO DE COPELAS (EJEMPLO DE REGISTRO)
if st.session_state.modulo_activo == "COPELAS":
    st.header("📝 REGISTRO DE COPELAS")
    with st.form("registro_copelas", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cod = st.selectbox("Código:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C"])
            mat = st.text_input("Material:").upper()
        with col2:
            cant = st.number_input("Cantidad:", min_value=1, step=1)
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        if st.form_submit_button("💾 GUARDAR REGISTRO"):
            nuevo_reg = pd.DataFrame([{
                "ID": st.session_state.user_data['ID'],
                "Fecha": fecha,
                "Producto": cod,
                "Cantidad": cant,
                "Material": mat,
                "Estado": "PROCESADO"
            }])
            guardar_datos("COPELA", nuevo_reg)

# OTROS MÓDULOS (ESTRUCTURA SIMILAR)
else:
    st.info(f"Módulo {st.session_state.modulo_activo} cargado. Listo para recibir datos.")

