import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL v9.0", layout="wide", page_icon="🏭")

SUPABASE_URL = "https://rrekwemzohknmaxzsefy.supabase.co"
SUPABASE_KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# 2. ESTILOS CSS (Tu diseño original mantenido)
st.markdown("""
    <style>
    .stApp { background: #0d1117; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 3px solid #00d2ff; }
    .titulo-sidebar { font-size: 26px; font-weight: 900; color: #00d2ff; text-align: center; }
    .usuario-sidebar { font-size: 20px; color: #ffda79; text-align: center; font-weight: bold; }
    .titulo-central { color: #00d2ff; font-size: 40px; font-weight: bold; }
    .stButton > button { border: none; background: none; color: #00d2ff; width: 100%; text-align: left; font-size: 17px; }
    .stButton > button:hover { color: #ff4d4d !important; text-shadow: 0px 0px 10px #ff4d4d; }
    h1, h2, h3, p, span { color: #e6edf3 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def modulo_usuarios(admin_actual):
    st.markdown('<p class="titulo-central">👥 GESTIÓN DE USUARIOS</p>', unsafe_allow_html=True)
    
    # Selector de usuario para edición
    res = supabase.table("USUARIO").select("*").execute()
    df_u = pd.DataFrame(res.data)
    
    opciones = ["--- NUEVO USUARIO ---"] + (df_u['ID'].tolist() if not df_u.empty else [])
    seleccion = st.selectbox("Seleccionar usuario para editar:", opciones)
    
    datos_u = {} if seleccion == "--- NUEVO USUARIO ---" else df_u[df_u['ID'] == seleccion].iloc[0].to_dict()

    with st.form("form_gestion_u", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            u_id = st.text_input("ID Login", value=datos_u.get('ID', "")).upper()
            u_pass = st.text_input("Contraseña", value=datos_u.get('CONTRASEÑA', ""), type="password")
            u_nom = st.text_input("Nombres", value=datos_u.get('NOMBRES', "")).upper()
        with c2:
            u_ape = st.text_input("Apellidos", value=datos_u.get('APELLIDOS', "")).upper()
            u_dni = st.text_input("DNI", value=datos_u.get('DNI', ""))
            u_tipo = st.selectbox("Tipo", ["OPERARIO", "SUPERVISOR", "ADMIN"], index=0)

        st.write("**PERMISOS (1=SI, 0=NO)**")
        p_cols = st.columns(4)
        permisos_lista = ["COPELAS", "CRISOLES", "MEZCLA", "ALMACEN", "USUARIO", "HISTORIAL", "MANTENIMIENTO", "LIMPIEZA"]
        nuevos_p = {}
        for i, p in enumerate(permisos_lista):
            with p_cols[i % 4]:
                val_act = int(datos_u.get(p, 0))
                nuevos_p[p] = st.radio(p, [1, 0], index=0 if val_act == 1 else 1, horizontal=True)

        if st.form_submit_button("💾 GUARDAR CAMBIOS"):
            payload = {"ID": u_id, "CONTRASEÑA": u_pass, "NOMBRES": u_nom, "APELLIDOS": u_ape, 
                       "DNI": u_dni, "TIPO_USUARIO": u_tipo, "ADMIN_REGISTRO": admin_actual, **nuevos_p}
            supabase.table("USUARIO").upsert(payload).execute()
            st.success("✅ Usuario guardado correctamente")
            st.rerun()

# --- MÓDULO COPELAS ---
def formulario_copelas(usuario):
    st.markdown('<p class="titulo-central">📝 REGISTRO DE COPELAS</p>', unsafe_allow_html=True)
    with st.form("copelas_f"):
        c1, c2, c3 = st.columns(3)
        with c1: codigo = st.selectbox("Producto", ["Cod-7C", "Cod-8C", "Cod-9C"])
        with c2: material = st.text_input("Material").upper()
        with c3: cantidad = st.number_input("Cantidad", min_value=0)
        
        if st.form_submit_button("💾 GUARDAR"):
            datos = {"codigo": codigo, "material": material, "cantidad": cantidad, "operador": usuario, "fecha": str(datetime.now().date())}
            supabase.table("COPELAS").insert(datos).execute()
            st.success("Guardado en Supabase")

# 4. MANEJO DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": "", "permisos": [], "sub_modulo": None})

# 5. LOGIN
if not st.session_state.autenticado:
    st.markdown('<p class="titulo-central" style="text-align:center;">SISTEMA INDUSTRIAL</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u_id = st.text_input("🆔 ID USUARIO").strip()
            u_pass = st.text_input("🔑 CONTRASEÑA", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                res = supabase.table("USUARIO").select("*").eq("ID", u_id).eq("CONTRASEÑA", u_pass).execute()
                if res.data:
                    fila = res.data[0]
                    st.session_state.autenticado = True
                    st.session_state.usuario = fila['NOMBRES']
                    st.session_state.permisos = [k.upper() for k, v in fila.items() if str(v) == '1']
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
    st.stop()

# 6. SIDEBAR
with st.sidebar:
    st.markdown('<p class="titulo-sidebar">SISTEMA PRINCIPAL</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="usuario-sidebar">👤 {st.session_state.usuario}</p>', unsafe_allow_html=True)
    
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # BOTÓN RÁPIDO PARA NUEVO USUARIO (Si tiene permiso)
    if "USUARIO" in st.session_state.permisos:
        if st.button("➕ REGISTRAR NUEVO USUARIO", use_container_width=True):
            st.session_state.sub_modulo = "Gestion de Usuarios"
    
    st.divider()
    
    # Menú de Módulos
    areas = ["COPELAS", "CRISOLES", "ALMACEN", "HISTORIAL", "USUARIO", "MANTENIMIENTO"]
    for area in areas:
        if area in st.session_state.permisos:
            if st.button(f"📦 {area}"):
                st.session_state.sub_modulo = area

# 7. PANEL CENTRAL
if st.session_state.sub_modulo:
    if st.session_state.sub_modulo in ["USUARIO", "Gestion de Usuarios"]:
        modulo_usuarios(st.session_state.usuario)
    elif st.session_state.sub_modulo == "COPELAS":
        formulario_copelas(st.session_state.usuario)
    else:
        st.write(f"Modulo {st.session_state.sub_modulo} en desarrollo...")
    
    if st.button("⬅ VOLVER"):
        st.session_state.sub_modulo = None
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h1 style='color:#00d2ff;'>BIENVENIDO</h1><p>Seleccione un módulo para comenzar</p></div>", unsafe_allow_html=True)
