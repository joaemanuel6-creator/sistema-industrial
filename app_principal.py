import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN Y ESTILO VISUAL (TU DISEÑO ORIGINAL) ---
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #064e3b !important; border-right: 4px solid #10b981; }
    .user-text { font-size: 24px !important; color: #ffffff !important; font-weight: 900 !important; margin-bottom: 10px; display: block; }
    div[data-testid="stWidgetLabel"] p { font-size: 19px !important; color: #f1c40f !important; font-weight: 800 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-weight: 700 !important; }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 55px;
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white !important; font-size: 18px !important; font-weight: 900; border: 2px solid #ffffff;
    }
    .resumen-salida {
        background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #f1c40f; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNCIONES DE CONEXIÓN A GOOGLE DRIVE ---
def conectar_drive():
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        # ttl=0 para que siempre lea datos frescos del Excel
        return conn.read(worksheet=nombre_pestaña, ttl=0)
    except Exception as e:
        st.error(f"Error al leer la pestaña {nombre_pestaña}: {e}")
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

# --- 3. GESTIÓN DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}, "modulo_activo": "COPELAS"})

if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    with st.form("login"):
        u = st.text_input("👤 ID DE USUARIO").strip()
        p = st.text_input("🔑 CONTRASEÑA", type="password")
        if st.form_submit_button("INGRESAR"):
            df_usuarios = leer_tabla("USUARIO")
            if not df_usuarios.empty:
                # Limpiar datos para evitar errores de comparación
                df_usuarios['ID'] = df_usuarios['ID'].astype(str).str.strip()
                df_usuarios['Contrasena'] = df_usuarios['Contrasena'].astype(str).str.strip()
                
                user = df_usuarios[(df_usuarios['ID'] == u) & (df_usuarios['Contrasena'] == p)]
                if not user.empty:
                    st.session_state.autenticado = True
                    st.session_state.user_data = user.iloc[0].to_dict()
                    st.rerun()
                else: 
                    st.error("❌ ID de Usuario o Contraseña incorrectos")
            else: 
                st.error("⚠️ No se encontró la tabla de usuarios en Drive.")
    st.stop()

# --- 4. BARRA LATERAL ---
st.sidebar.title("🏭 SISTEMA PRINCIPAL")
st.sidebar.markdown(f'<span class="user-text">👤 {st.session_state.user_data.get("Nombres")}</span>', unsafe_allow_html=True)
st.sidebar.divider()

modulos = ["COPELAS", "CRISOLES", "MEZCLA", "QUEMA", "LIMPIEZA", "ALMACEN"]
for op in modulos:
    if st.sidebar.button(f"📂 {op}"):
        st.session_state.modulo_activo = op

st.sidebar.divider()
if st.sidebar.button("🚪 SALIR", type="secondary"):
    st.session_state.clear()
    st.rerun()

# --- 5. MÓDULOS DE REGISTRO ---

def modulo_copelas():
    st.header("📝 REGISTRO DE COPELAS")
    with st.form("form_copelas", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            prod = st.selectbox("C/Producto:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
            mat = st.text_input("Material (Nombre):").upper()
            prensa = st.selectbox("Seleccione Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with c2:
            parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 31)])
            cant = st.number_input("Cantidad Unidades:", min_value=0, step=1)
            # FECHA CORREGIDA A DD/MM/YYYY
            fecha_f = st.text_input("FECHA (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y"))
        
        if st.form_submit_button("💾 GUARDAR EN DRIVE"):
            if mat and cant > 0:
                nuevo = pd.DataFrame([{
                    "Codigo": prod, "Fecha_Registro": fecha_f, "Operador": st.session_state.user_data['ID'],
                    "N_Parrilla": parrilla, "Cantidad": cant, "Material": mat, "Prensa": prensa, "Estado": "PENDIENTE"
                }])
                if guardar_datos("COPELA", nuevo):
                    st.success(f"✅ Registrado en Excel con fecha {fecha_f}")

def modulo_crisoles():
    st.header("🔥 REGISTRO DE CRISOLES")
    with st.form("form_crisoles", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            prod = st.selectbox("C/Producto:", ["Cod-15", "Cod-30", "Cod-40", "Cod-50"])
            mat = st.text_input("Material Utilizado:").upper()
            prensa = st.selectbox("Prensa asignada:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with c2:
            paleta = st.selectbox("N° Paleta:", [f"P-{i:02d}" for i in range(1, 31)])
            cant = st.number_input("Cantidad Registrada:", min_value=0, step=1)
            fecha_f = st.text_input("FECHA (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y"))
        
        if st.form_submit_button("💾 REGISTRAR EN DRIVE"):
            if mat and cant > 0:
                nuevo = pd.DataFrame([{
                    "Codigo": prod, "Fecha_Registro": fecha_f, "Operador": st.session_state.user_data['ID'],
                    "N_Parrilla": paleta, "Cantidad": cant, "Material": mat, "Prensa": prensa, "Estado": "PENDIENTE"
                }])
                if guardar_datos("CRISOL", nuevo):
                    st.success(f"✅ Registrado en Excel con fecha {fecha_f}")

def modulo_mezcla():
    st.header("🧪 CONTROL DE MEZCLAS")
    st.info("Módulo conectado a Google Sheets. Los cálculos se guardan en el historial.")
    # (Aquí puedes añadir tu lógica de multiplicación de baldes adaptada a leer_tabla)
    st.write("Selecciona una opción en el menú lateral para registrar productos.")

# --- 6. RENDERIZADO FINAL ---
mod = st.session_state.modulo_activo
if mod == "COPELAS": modulo_copelas()
elif mod == "CRISOLES": modulo_crisoles()
elif mod == "MEZCLA": modulo_mezcla()
else: st.title(f"📂 MÓDULO {mod} EN CONSTRUCCIÓN")
