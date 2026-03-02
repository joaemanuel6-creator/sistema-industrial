import streamlit as st
import pandas as pd
from datetime import datetime

@st.dialog("REGISTRO DE COPELAS", width="large")
def ventana_registro_copelas():
    st.markdown(f"**Operario:** {st.session_state.user_data.get('Nombres')}")
    
    # --- INTERFAZ IGUAL A TU TKINTER ---
    col1, col2 = st.columns(2)
    
    with col1:
        prod = st.selectbox("C/Producto (Codigo):", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
        mat = st.text_input("Material:").upper()
        parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 21)])
        
    with col2:
        cant = st.number_input("Cantidad:", min_value=0, step=1)
        prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        fecha_manual = st.text_input("Fecha (Opcional DD/MM/YYYY):", placeholder="Vacío = Hoy")

    st.divider()
    
    # Botones de acción al final de la ventana
    c_btn1, c_btn2 = st.columns(2)
    
    if c_btn1.button("💾 REGISTRAR", use_container_width=True):
        if mat and cant > 0:
            fecha_final = fecha_manual if fecha_manual.strip() != "" else datetime.now().strftime("%d/%m/%Y")
            
            nuevo_reg = pd.DataFrame([{
                "Codigo": prod,
                "Fecha_Registro": fecha_final,
                "Operador": st.session_state.user_data.get('Nombres'),
                "N_Parrilla": parrilla,
                "Cantidad": cant,
                "Material": mat,
                "Prensa": prensa,
                "Estado": "PENDIENTE"
            }])
            
            if guardar_datos("COPELA", nuevo_reg):
                st.success(f"Registrado con éxito: {fecha_final}")
                st.rerun() # Cierra la ventana y refresca
        else:
            st.error("Completa Material y Cantidad")

    if c_btn2.button("❌ CERRAR", use_container_width=True):
        st.rerun()
