import streamlit as st
from datetime import datetime
import pandas as pd

@st.dialog("REGISTRO DE COPELAS", width="large")
def ventana_registro_copelas(operario, funcion_guardar):
    st.write(f"Operario: {operario}")
    # ... (el resto de tu formulario de copelas)
    if st.button("GUARDAR"):
        # lógica de creación de dataframe 'nuevo_reg'
        if funcion_guardar("COPELA", nuevo_reg):
            st.success("Guardado!")
            st.rerun()
