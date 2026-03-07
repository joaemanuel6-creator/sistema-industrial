import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SISTEMA INDUSTRIAL v8.0", layout="wide", page_icon="🏭")

# --- 2. CREDENCIALES SUPABASE (REEMPLAZA CON LAS TUYAS) ---
SUPABASE_URL = "https://rrekwemzohknmaxzsefy.supabase.co"
SUPABASE_KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- 3. DISEÑO PROFESIONAL (CSS INYECTADO - TU DISEÑO ORIGINAL) ---
st.markdown("""
    <style>
    .stApp { background: #0d1117; }
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 3px solid #00d2ff;
    }
    .titulo-sidebar {
        font-size: 26px !important;
        font-weight: 900;
        color: #00d2ff;
        text-shadow: 0px 0px 15px #00d2ff;
        text-align: center;
    }
    .usuario-sidebar {
        font-size: 20px;
        color: #ffda79 !important; 
        text-align: center;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 0px 0px 5px #ffda79;
    }
    .stButton > button {
        border: none !important;
        background: none !important;
        color: #00d2ff !important;
        text-align: left !important;
        width: 100%;
        font-size: 17px !important;
        transition: 0.1s;
    }
    .stButton > button:focus, .stButton > button:active, .stButton > button:hover {
        color: #ff4d4d !important; 
        text-shadow: 0px 0px 15px #ff4d4d !important;
        background-color: transparent !important;
        font-weight: bold !important;
    }
    .titulo-central {
        color: #00d2ff !important;
        font-size: 40px !important;
        font-weight: bold;
    }
    h1, h2, h3, p, span { color: #e6edf3 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MODULO DE COPELAS (AHORA GUARDA EN SUPABASE) ---
def formulario_copelas(usuario):
    st.markdown('<p class="titulo-central">📝 REGISTRO DE COPELAS</p>', unsafe_allow_html=True)
    with st.container():
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
    
    if st.button("💾 GUARDAR EN NUBE"):
        if material:
            nuevo_registro = {
                "codigo": codigo,
                "cantidad": int(cantidad),
                "material": material,
                "prensa": prensa,
                "parrilla": parrilla,
                "fecha": str(fecha),
                "operador": usuario
            }
            try:
                # INSERTAMOS EN LA TABLA 'COPELAS' DE SUPABASE
                supabase.table("COPELAS").insert(nuevo_registro).execute()
                st.success(f"✅ ¡Sincronizado! Registro exitoso para {usuario}")
            except Exception as e:
                st.error(f"❌ Error al guardar en Supabase: {e}")
        else:
            st.warning("⚠️ El material es obligatorio.")

# --- 5. MANEJO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

# --- 6. INTERFAZ DE LOGIN (AHORA VALIDA CON SUPABASE) ---
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-central" style="text-align:center;">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u_id = st.text_input("🆔 ID USUARIO").strip()
            u_pass = st.text_input("🔑 CONTRASEÑA", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                try:
                    # CONSULTAMOS LA TABLA 'USUARIO' EN SUPABASE
                    res = supabase.table("USUARIO").select("*").eq("ID", u_id).eq("CONTRASEÑA", u_pass).execute()
                    
                    if res.data:
                        fila = res.data[0]
                        st.session_state.autenticado = True
                        st.session_state.usuario = fila.get('NOMBRES', u_id)
                        # Filtramos las columnas que tienen '1' para dar permisos
                        st.session_state.permisos = [str(k).upper() for k, v in fila.items() if str(v).strip() == '1']
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                except Exception as e:
                    st.error(f"Error de conexión con la Nube: {e}")
    st.stop()

# --- 7. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    areas_data = {
        "COPELAS": ["Registro de Copelas"],
        "CRISOLES": ["Registro de Crisoles"],
        "QUEMA": ["Proceso de Quema"],
        "EMBALAJE": ["Embalaje General"],
        "LIMPIEZA": ["Limpieza de Equipos"],
        "MEZCLA": ["Control de Mezclas"],
        "ZARANDA": ["Zaranda y Martillo"],
        "MOLINO": ["Operación de Molino"],
        "ALMACEN": ["Kardex e Inventario"],
        "HISTORIAL": ["Registros Pasados"],
        "USUARIO": ["Gestión de Usuarios"],
        "MANTENIMIENTO": ["Plan de Mantenimiento"],
        "OBSERVACION": ["Registro de Observaciones"]
    }

    for area, opciones in areas_data.items():
        if area in st.session_state.permisos:
            with st.expander(f"📦 {area}"):
                for opt in opciones:
                    if st.button(f"➤ {opt}", key=f"btn_{opt}"):
                        st.session_state.sub_modulo = opt

# --- 8. PANEL CENTRAL ---
if st.session_state.sub_modulo:
    if "Copelas" in st.session_state.sub_modulo:
        formulario_copelas(st.session_state.usuario)
    
    elif "Mantenimiento" in st.session_state.sub_modulo:
        st.markdown('<p class="titulo-central">🛠 MANTENIMIENTO PREVENTIVO</p>', unsafe_allow_html=True)
        st.info("Cargando cronograma desde Supabase...")

    # ... Resto de sub-módulos ...

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h1 style='color:#00d2ff;'>SISTEMA INDUSTRIAL</h1><p>Panel de Control Activo en la Nube</p></div>", unsafe_allow_html=True)
