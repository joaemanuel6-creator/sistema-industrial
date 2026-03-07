import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SISTEMA INDUSTRIAL", layout="centered")

# ID de tu documento de Google Sheets
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "usuario": ""})

# 2. FUNCIÓN DE LECTURA DIRECTA (Sin librerías de conexión)
def leer_hoja_directo(nombre_pestaña):
    try:
        # Construimos el link de exportación CSV para esa pestaña específica
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nombre_pestaña}"
        
        # Leemos con Pandas directamente desde la URL
        df = pd.read_csv(url)
        
        # Limpieza de columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"⚠️ Error al acceder a la pestaña '{nombre_pestaña}': {e}")
        return pd.DataFrame()

# 3. INTERFAZ DE LOGIN
if not st.session_state.autenticado:
    st.title("🏭 ACCESO AL SISTEMA")
    
    with st.form("login"):
        u_id = st.text_input("ID de Usuario").strip()
        u_pass = st.text_input("Contraseña", type="password").strip()
        
        if st.form_submit_button("INGRESAR"):
            # Intentamos leer la hoja 'USUARIO'
            df_u = leer_hoja_directo("USUARIO")
            
            if not df_u.empty:
                # Verificamos si las credenciales existen
                if 'ID' in df_u.columns and 'CONTRASEÑA' in df_u.columns:
                    valido = df_u[
                        (df_u['ID'].astype(str) == u_id) & 
                        (df_u['CONTRASEÑA'].astype(str) == u_pass)
                    ]
                    
                    if not valido.empty:
                        st.session_state.autenticado = True
                        st.session_state.usuario = valido.iloc[0].get('NOMBRES', u_id)
                        st.rerun()
                    else:
                        st.error("❌ Usuario o clave incorrectos.")
                else:
                    st.warning(f"La hoja no tiene columnas ID/CONTRASEÑA. Columnas: {list(df_u.columns)}")
            else:
                st.info("No se pudo conectar. Verifica que el archivo de Google Sheets sea PÚBLICO.")
    st.stop()

# 4. SISTEMA PRINCIPAL
st.sidebar.write(f"Operario: **{st.session_state.usuario}**")
if st.sidebar.button("Salir"):
    st.session_state.clear()
    st.rerun()

st.title("✅ SISTEMA CONECTADO")
st.write(f"Bienvenido al panel de control de producción.")

# Ejemplo para ver el stock de otra pestaña llamada 'ALMACEN'
if st.checkbox("Ver Stock Actual"):
    df_stock = leer_hoja_directo("ALMACEN")
    if not df_stock.empty:
        st.table(df_stock)
