import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL v9.0", layout="wide")

# ID de tu documento
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

# 2. DISEÑO CSS (Manteniendo tus colores)
st.markdown("""
    <style>
    .stApp { background: #0d1117; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 3px solid #00d2ff; }
    .titulo-sidebar { color: #00d2ff; text-shadow: 0px 0px 15px #00d2ff; text-align: center; font-weight: 900; font-size: 26px; }
    .usuario-sidebar { color: #ffda79 !important; text-align: center; font-weight: bold; font-size: 20px; }
    .stButton > button { color: #00d2ff !important; background: none !important; border: none !important; width: 100%; text-align: left; font-size: 17px; }
    .stButton > button:focus, .stButton > button:active, .stButton > button:hover {
        color: #ff4d4d !important; text-shadow: 0px 0px 15px #ff4d4d !important; font-weight: bold !important;
    }
    .titulo-central { color: #00d2ff !important; font-size: 40px; font-weight: bold; }
    h1, h2, h3, p, span, label { color: #e6edf3 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_hoja_directo(nombre_pestaña):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        df = pd.read_csv(url)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- MODULO DE COPELAS CON GUARDADO REAL ---
def formulario_copelas(usuario):
    st.markdown('<p class="titulo-central">📝 REGISTRO DE COPELAS</p>', unsafe_allow_html=True)
    
    with st.form("form_copelas", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            codigo = st.selectbox("C/Producto:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
            cantidad = st.number_input("Cantidad:", min_value=0, step=1)
        with col2:
            material = st.text_input("Material:").upper()
            prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with col3:
            parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 21)])
            fecha = st.date_input("Fecha:", datetime.now())
        
        btn_guardar = st.form_submit_button("💾 GUARDAR EN GOOGLE DRIVE")

    if btn_guardar:
        if material == "" or cantidad == 0:
            st.error("⚠️ Por favor, completa el Material y la Cantidad.")
        else:
            try:
                # 1. Leer datos actuales de la pestaña COPELAS
                df_actual = conn.read(worksheet="COPELAS")
                
                # 2. Crear nueva fila
                nueva_fila = pd.DataFrame([{
                    "CODIGO": codigo,
                    "FECHA": fecha.strftime("%d/%m/%Y"),
                    "OPERADOR": usuario,
                    "N_PARRILLA": parrilla,
                    "CANTIDAD": cantidad,
                    "MATERIAL": material,
                    "PRENSA": prensa,
                    "ESTADO": "PENDIENTE"
                }])
                
                # 3. Concatenar y actualizar
                df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                conn.update(worksheet="COPELAS", data=df_final)
                
                st.success("✅ ¡Datos sincronizados con Google Drive exitosamente!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error al conectar con Drive: {e}")

# 4. LÓGICA DE SESIÓN Y LOGIN (Simplificada para el ejemplo)
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

if not st.session_state.autenticado:
    st.markdown('<p class="titulo-central" style="text-align:center;">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    with st.container():
        u_id = st.text_input("🆔 ID USUARIO")
        u_pass = st.text_input("🔑 CONTRASEÑA", type="password")
        if st.button("INGRESAR"):
            df_u = leer_hoja_directo("USUARIO")
            valido = df_u[(df_u['ID'].astype(str) == u_id) & (df_u['CONTRASEÑA'].astype(str) == u_pass)]
            if not valido.empty:
                st.session_state.update({"autenticado": True, "usuario": valido.iloc[0]['NOMBRES']})
                fila = valido.iloc[0]
                st.session_state.permisos = [str(col).strip().upper() for col in fila.index if str(fila[col]).strip() == '1']
                st.rerun()
    st.stop()

# 5. SIDEBAR Y PANEL CENTRAL
with st.sidebar:
    st.markdown(f'<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # Menú dinámico basado en permisos
    modulos = ["COPELAS", "CRISOLES", "MANTENIMIENTO", "OBSERVACION", "ALMACEN"]
    for mod in modulos:
        if mod in st.session_state.permisos:
            if st.button(f"📂 {mod}", key=f"btn_{mod}"):
                st.session_state.sub_modulo = mod

# PANEL CENTRAL
if st.session_state.sub_modulo == "COPELAS":
    formulario_copelas(st.session_state.usuario)
elif st.session_state.sub_modulo:
    st.markdown(f'<p class="titulo-central">📍 {st.session_state.sub_modulo}</p>', unsafe_allow_html=True)
    if st.button("⬅ VOLVER"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<h2 style='text-align:center; margin-top:100px;'>Bienvenido al Panel de Control</h2>", unsafe_allow_html=True)
