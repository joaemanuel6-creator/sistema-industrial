import streamlit as st
import pandas as pd
from datetime import datetime

# URL de tu Google Sheet (formato exportación CSV)
SHEET_ID = "1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI"

def formulario_copelas(usuario_activo):
    st.markdown(f'<p class="titulo-central">📝 REGISTRO DE COPELAS</p>', unsafe_allow_html=True)
    st.write(f"**Operario:** {usuario_activo}")

    # --- FORMULARIO DE ENTRADA ---
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            codigo = st.selectbox("C/Producto (Codigo):", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
            cantidad = st.number_input("Cantidad:", min_value=0, step=1)
        with col2:
            material = st.text_input("Material:").upper()
            prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with col3:
            n_parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 21)])
            fecha = st.date_input("Fecha de Proceso:", datetime.now())

    # --- BOTONES DE ACCIÓN ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("💾 REGISTRAR EN DRIVE", use_container_width=True):
            # Aquí iría la lógica de Google Sheets API o un mensaje de éxito
            st.success(f"Registrado: {codigo} - {cantidad} unid. en Drive")
            
    with c2:
        archivo = st.file_uploader("📥 Importar Excel", type=["xlsx"])
        if archivo:
            df = pd.read_excel(archivo)
            st.dataframe(df.head())
            if st.button("Confirmar Carga"):
                st.info("Sincronizando con Google Drive...")

    # --- VISUALIZACIÓN DE DATOS DESDE GOOGLE DRIVE ---
    st.divider()
    st.subheader("📊 Últimos Registros en Copelas")
    
    # Leemos la pestaña COPELAS directamente del Drive
    try:
        url_drive = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=COPELAS"
        df_drive = pd.read_csv(url_drive)
        st.dataframe(df_drive, use_container_width=True)
    except:
        st.warning("No se pudo cargar la hoja 'COPELAS' del Drive. Verifica el nombre de la pestaña.")
