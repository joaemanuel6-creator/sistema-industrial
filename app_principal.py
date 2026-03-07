import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide")

# 2. ESTADOS DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 3. FUNCIONES DE BASE DE DATOS MEJORADAS
def conectar_drive():
    # Esta línea busca automáticamente en la sección [connections.gsheets] de tus secrets
    return st.connection("gsheets", type=GSheetsConnection)

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        # Leemos la pestaña específica. ttl=0 evita errores de caché.
        df = conn.read(worksheet=nombre_pestaña, ttl=0)
        
        if df is not None:
            # Limpiamos nombres de columnas (quitar espacios en blanco)
            df.columns = [str(c).strip() for c in df.columns]
            # Limpiamos datos (quitar filas vacías que ensucian el DataFrame)
            df = df.dropna(how="all")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al conectar con la pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

def guardar_datos(nombre_pestaña, nuevo_df):
    try:
        conn = conectar_drive()
        df_actual = leer_tabla(nombre_pestaña)
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        # Actualizar la hoja en la nube
        conn.update(worksheet=nombre_pestaña, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 4. LÓGICA DE LOGIN
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    
    with st.form("login_form"):
        u_input = st.text_input("Usuario (ID)").strip()
        p_input = st.text_input("Contraseña", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            # Intentamos leer la pestaña USUARIO
            df_u = leer_tabla("USUARIO")
            
            if not df_u.empty:
                # Buscamos columnas ID y CONTRASEÑA sin importar mayúsculas
                cols_normalizadas = {c.upper(): c for c in df_u.columns}
                
                if 'ID' in cols_normalizadas and 'CONTRASEÑA' in cols_normalizadas:
                    c_id = cols_normalizadas['ID']
                    c_pass = cols_normalizadas['CONTRASEÑA']
                    
                    # Verificación de credenciales
                    match = df_u[
                        (df_u[c_id].astype(str).str.strip() == u_input) & 
                        (df_u[c_pass].astype(str).str.strip() == p_input)
                    ]
                    
                    if not match.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                else:
                    st.warning(f"⚠️ Estructura incorrecta. Columnas detectadas: {list(df_u.columns)}")
            else:
                st.error("No se pudo leer la tabla 'USUARIO'. Revisa el nombre de la pestaña en Google Drive.")
    st.stop()

# 5. MENÚ PRINCIPAL (Interfaz después del Login)
st.sidebar.title("🏭 MENÚ PRINCIPAL")
nombre_usuario = st.session_state.user_data.get('NOMBRES', 'Usuario')
st.sidebar.write(f"Operario: **{nombre_usuario}**")
st.sidebar.divider()

# Botones de navegación
opcion = st.sidebar.radio("Seleccione una opción:", ["📊 Panel de Control", "📂 Registro de Copelas"])

if st.sidebar.button("🚪 CERRAR SESIÓN"):
    st.session_state.clear()
    st.rerun()

# --- VISTAS DEL SISTEMA ---
if opcion == "📊 Panel de Control":
    st.title("📊 ESTADO ACTUAL DE PRODUCCIÓN")
    df_vista = leer_tabla("COPELA")
    if not df_vista.empty:
        st.dataframe(df_vista.tail(15), use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros recientes en la pestaña COPELA.")

elif opcion == "📂 Registro de Copelas":
    st.title("📂 REGISTRO DE COPELAS")
    # Aquí puedes llamar a la función de copela.py o escribirla directamente
    st.info("Interfaz de registro lista para procesar.")
    # Ejemplo rápido de formulario
    with st.form("salida_copelas"):
        mat = st.selectbox("Material", ["COPELA TIPO A", "COPELA TIPO B"])
        cant = st.number_input("Cantidad", min_value=1)
        if st.form_submit_button("Guardar Salida"):
            st.success(f"Registrado: {cant} de {mat}")

