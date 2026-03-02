import streamlit as st
import pandas as pd
from datetime import datetime

@st.dialog("REGISTRO DE COPELAS", width="large")
def ventana_registro_copelas(operario, fn_guardar):
    st.write(f"Operario: {operario}")
    
    c1, c2 = st.columns(2)
    with c1:
        prod = st.selectbox("Código:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C"])
        mat = st.text_input("Material:").upper()
    with c2:
        cant = st.number_input("Cantidad:", min_value=1)
        prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03"])

    if st.button("💾 GUARDAR"):
        if mat:
            nueva_fila = pd.DataFrame([{
                "Codigo": prod,
                "Fecha_Registro": datetime.now().strftime("%d/%m/%Y"),
                "Operador": operario,
                "N_Parrilla": "P-01",
                "Cantidad": cant,
                "Material": mat,
                "Prensa": prensa,
                "Estado": "PENDIENTE"
            }])
            if fn_guardar("COPELA", nueva_fila):
                st.success("¡Guardado!")
                st.rerun()
        else:
            st.error("Falta el material")
