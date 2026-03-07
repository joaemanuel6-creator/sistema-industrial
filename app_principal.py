import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="wide")

# 2. ESTADOS DE SESIÓN (LOGIN Y NAVEGACIÓN)
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}})

# 3. FUNCIONES DE BASE DE DATOS (CONEXIÓN A GOOGLE SHEETS)
def conectar_drive():
    try:
        # Busca la configuración en [connections.gsheets] de los secrets
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"❌ Error de configuración de conexión: {e}")
        return None

def leer_tabla(nombre_pestaña):
    try:
        conn = conectar_drive()
        if conn:
            # Forzamos la lectura de la pestaña específica
            # ttl=0 asegura que traiga los datos más recientes de la nube
            df = conn.read(worksheet=nombre_pestaña, ttl=0)
            
            if df is not None:
                # Limpieza de columnas (quitar espacios en blanco invisibles)
                df.columns = [str(c).strip() for c in df.columns]
                # Quitar filas que estén totalmente vacías
                df = df.dropna(how="all")
                return df
        return pd.DataFrame()
    except Exception as e:
        # Este mensaje te dirá exactamente qué falla si el Error 400 persiste
        st.error(f"⚠️ Error al acceder a la pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

def guardar_datos(nombre_pestaña, nuevo_df):
    try:
        conn = conectar_drive()
        df_actual = leer_tabla(nombre_pestaña)
        # Unimos los datos viejos con el nuevo registro
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        # Subimos la tabla completa actualizada
        conn.update(worksheet=nombre_pestaña, data=df_final)
        return True
    except Exception as e:
        st.error(f"❌ No se pudo guardar en la nube: {e}")
        return False

# 4. LÓGICA DE ACCESO (LOGIN)
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA INDUSTRIAL")
    
    with st.form("login_form"):
        u_input = st.text_input("Usuario (ID)").strip()
        p_input = st.text_input("Contraseña", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            # Intentamos leer la pestaña USUARIO
            df_u = leer_tabla("USUARIO")
            
            if not df_u.empty:
                # Normalizamos nombres de columnas para evitar errores de mayúsculas
                cols_map = {c.upper(): c for c in df_u.columns}
                
                if 'ID' in cols_map and 'CONTRASEÑA' in cols_map:
                    c_id = cols_map['ID']
                    c_pass = cols_map['CONTRASEÑA']
                    
                    # Buscamos coincidencia de credenciales
                    match = df_u[
                        (df_u[c_id].astype(str).str.strip() == u_input) & 
                        (df_u[c_pass].astype(str).str.strip() == p_input)
                    ]
                    
                    if not match.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")
                else:
                    st.warning(f"La tabla USUARIO no tiene las columnas 'ID' y 'CONTRASEÑA'. Columnas: {list(df_u.columns)}")
            else:
                st.info("No se pudo validar el acceso. Verifica la conexión con Google Sheets.")
    st.stop()

# 5. INTERFAZ PRINCIPAL (DESPUÉS DEL LOGIN)
st.sidebar.title("🏭 PANEL DE CONTROL")
user_name = st.session_state.user_data.get('NOMBRES', 'Operario')
st.sidebar.write(f"Conectado: **{user_name}**")
st.sidebar.divider()

# Navegación del menú lateral
menu = st.sidebar.radio("Ir a:", ["🏠 Inicio", "📦 Registro de Salida", "📋 Historial"])

if st.sidebar.button("🚪 Salir"):
    st.session_state.clear()
    st.rerun()

# --- VISTAS DEL SISTEMA ---
if menu == "🏠 Inicio":
    st.title(f"Bienvenido, {user_name}")
    st.write("Seleccione una opción en el menú lateral para comenzar.")
    
    # Mostrar resumen rápido del inventario
    st.subheader("📊 Stock Actual (Resumen)")
    df_alm = leer_tabla("ALMACEN")
    if not df_alm.empty:
        # Solo mostrar los que tienen stock
        df_ver = df_alm[df_alm['TOTAL'].astype(float) > 0]
        st.dataframe(df_ver, use_container_width=True, hide_index=True)

elif menu == "📦 Registro de Salida":
    st.title("📦 Registro de Salida de Material")
    
    # Formulario de registro
    with st.form("form_salida"):
        col1, col2 = st.columns(2)
        with col1:
            material = st.text_input("Nombre del Material").upper()
            lote = st.text_input("Número de Lote").upper()
        with col2:
            cantidad = st.number_input("Cantidad", min_value=1.0, step=1.0)
            destino = st.text_input("Destino / Área").upper()
        
        if st.form_submit_button("✅ Procesar Salida"):
            if material and lote and destino:
                nuevo_reg = pd.DataFrame([{
                    "FECHA": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    "MATERIAL": material,
                    "LOTE": lote,
                    "CANTIDAD": cantidad,
                    "DESTINO": destino,
                    "OPERADOR": user_name
                }])
                
                if guardar_datos("COPELA", nuevo_reg):
                    st.success("¡Registro guardado en Google Sheets correctamente!")
                else:
                    st.error("Error al guardar el registro.")
            else:
                st.warning("Complete todos los campos antes de guardar.")

elif menu == "📋 Historial":
    st.title("📋 Historial de Movimientos")
    df_hist = leer_tabla("COPELA")
    if not df_hist.empty:
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No hay movimientos registrados en la pestaña 'COPELA'.")
