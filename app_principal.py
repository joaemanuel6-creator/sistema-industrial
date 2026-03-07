import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SISTEMA INDUSTRIAL", page_icon="🏭", layout="centered")

# Inicializar el estado de autenticación
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario_nombre": ""})

# 2. FUNCIÓN PARA LEER HOJAS DE GOOGLE DRIVE
def conectar_y_leer(nombre_hoja):
    try:
        # Creamos la conexión usando los secretos configurados
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Leemos la pestaña específica (worksheet)
        # ttl=0 asegura que si cambias un usuario en el Excel, se actualice al instante
        df = conn.read(worksheet=nombre_hoja, ttl=0)
        
        if df is not None:
            # Limpiamos nombres de columnas (quitar espacios y poner en mayúsculas)
            df.columns = [str(c).strip().upper() for c in df.columns]
            # Quitamos filas vacías
            df = df.dropna(how="all")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al conectar con la hoja '{nombre_hoja}': {e}")
        return pd.DataFrame()

# 3. INTERFAZ DE LOGIN (PANTALLA DE INICIO)
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    st.write("Ingrese sus credenciales para conectar con la base de datos.")

    with st.form("login_form"):
        u_input = st.text_input("ID de Usuario").strip()
        p_input = st.text_input("Contraseña", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            # EL SISTEMA BUSCA EN LA HOJA 'USUARIO' DENTRO DEL DRIVE
            df_usuarios = conectar_y_leer("USUARIO")
            
            if not df_usuarios.empty:
                # Verificamos que existan las columnas ID y CONTRASEÑA
                if 'ID' in df_usuarios.columns and 'CONTRASEÑA' in df_usuarios.columns:
                    # Buscamos coincidencia
                    match = df_usuarios[
                        (df_usuarios['ID'].astype(str) == u_input) & 
                        (df_usuarios['CONTRASEÑA'].astype(str) == p_input)
                    ]
                    
                    if not match.empty:
                        st.session_state.autenticado = True
                        # Suponiendo que tienes una columna NOMBRES en tu Excel
                        nombre = match.iloc[0].get('NOMBRES', u_input)
                        st.session_state.usuario_nombre = nombre
                        st.success(f"✅ Bienvenida/o {nombre}")
                        st.rerun()
                    else:
                        st.error("❌ ID o Contraseña incorrectos.")
                else:
                    st.warning(f"⚠️ Estructura incorrecta en Excel. Columnas halladas: {list(df_usuarios.columns)}")
            else:
                st.info("No se pudo leer la tabla de usuarios. Revisa los permisos de 'Compartir' en Google Drive.")
    st.stop()

# 4. PANEL PRINCIPAL (SI EL LOGIN ES EXITOSO)
st.sidebar.title(f"👤 {st.session_state.usuario_nombre}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.clear()
    st.rerun()

st.title("🏭 PANEL DE CONTROL INDUSTRIAL")
st.write("Conexión exitosa con la hoja de cálculo.")

# Ejemplo de interacción con otra hoja (ALMACEN o COPELA)
if st.button("Ver Inventario"):
    df_inv = conectar_y_leer("ALMACEN")
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.warning("No hay datos en la pestaña ALMACEN.")
