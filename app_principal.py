import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide")

# Estilos visuales personalizados
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #064e3b !important; }
    h1, h2, h3, p, label { color: #ffffff !important; }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAR SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 3. FUNCIONES DE CONEXIÓN A GOOGLE SHEETS
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        return conn.read(worksheet=nombre_pestaña, ttl=0)
    except Exception as e:
        st.error(f"Error al leer la pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

def guardar_datos(nombre_pestaña, nuevo_df):
    try:
        conn = conectar_drive()
        df_actual = leer_tabla(nombre_pestaña)
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        conn.update(worksheet=nombre_pestaña, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 4. VENTANAS FLOTANTES (MODALES)
@st.dialog("REGISTRO DE COPELAS", width="large")
def ventana_registro_copelas():
    st.markdown(f"**Operario:** {st.session_state.user_data.get('Nombres')}")
    
    col1, col2 = st.columns(2)
    with col1:
        prod = st.selectbox("C/Producto (Codigo):", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
        mat = st.text_input("Material:").upper()
        parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 21)])
        
    with col2:
        cant = st.number_input("Cantidad:", min_value=0, step=1)
        prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        fecha_manual = st.text_input("Fecha (Opcional DD/MM/YYYY):", placeholder="Vacio = Hoy")

    st.divider()
    c_btn1, c_btn2 = st.columns(2)
    
    if c_btn1.button("💾 REGISTRAR", use_container_width=True):
        if mat and cant > 0:
            fecha_final = fecha_manual if fecha_manual.strip() != "" else datetime.now().strftime("%d/%m/%Y")
            
            nuevo_reg = pd.DataFrame([{
                "Codigo": prod,
                "Fecha_Registro": fecha_final,
                "Operador": st.session_state.user_data.get('Nombres'),
                "N_Parrilla": parrilla,
                "Cantidad": cant,
                "Material": mat,
                "Prensa": prensa,
                "Estado": "PENDIENTE"
            }])
            
            if guardar_datos("COPELA", nuevo_reg):
                st.success(f"Registrado con éxito: {fecha_final}")
                st.rerun()
        else:
            st.error("Completa Material y Cantidad")

    if c_btn2.button("❌ CERRAR", use_container_width=True):
        st.rerun()

# 5. LÓGICA DE ACCESO (LOGIN)
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    with st.form("login"):
        u = st.text_input("👤 ID DE USUARIO").strip()
        p = st.text_input("🔑 CONTRASEÑA", type="password").strip()
        if st.form_submit_button("INGRESAR"):
            df_usuarios = leer_tabla("USUARIO")
            if not df_usuarios.empty:
                # Normalizar nombres de columnas (Quitar espacios y manejar Ñ)
                df_usuarios.columns = [str(c).strip() for c in df_usuarios.columns]
                
                # Buscamos coincidencias (Asegúrate que en Excel diga "Contraseña")
                user = df_usuarios[(df_usuarios['ID'].astype(str) == u) & 
                                   (df_usuarios['Contraseña'].astype(str) == p)]
                
                if not user.empty:
                    st.session_state.autenticado = True
                    st.session_state.user_data = user.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("❌ Usuario o Contraseña incorrectos")
            else:
                st.error("⚠️ No se pudo conectar con la tabla USUARIO.")
    st.stop()

# 6. INTERFAZ PRINCIPAL (SIDEBAR Y CONTENIDO)
st.sidebar.title("🏭 MENÚ")
st.sidebar.write(f"Bienvenido: **{st.session_state.user_data.get('Nombres')}**")
st.sidebar.divider()

if st.sidebar.button("📂 REGISTRO COPELAS", use_container_width=True):
    ventana_registro_copelas()

if st.sidebar.button("📂 REGISTRO CRISOLES", use_container_width=True):
    st.sidebar.info("Módulo Crisoles en desarrollo...")

st.sidebar.divider()
if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

# Pantalla de bienvenida al entrar
st.title("BIENVENIDO AL SISTEMA INDUSTRIAL")
st.write("Seleccione una opción en el menú de la izquierda para comenzar.")

# Opcional: Mostrar una tabla rápida de los últimos registros
st.subheader("📊 Últimos Registros de Copelas")
df_vista = leer_tabla("COPELA")
if not df_vista.empty:
    st.dataframe(df_vista.tail(10), use_container_width=True)

