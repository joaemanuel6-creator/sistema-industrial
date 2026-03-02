import streamlit as st
import pandas as pd
from datetime import datetime

@st.dialog("NUEVO REGISTRO DE COPELAS", width="large")
def ventana_registro_copelas(nombre_operario, funcion_guardar):
    st.write(f"📝 Registrando como: **{nombre_operario}**")
    
    col1, col2 = st.columns(2)
    with col1:
        prod = st.selectbox("Código Producto:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
        mat = st.text_input("Material:").upper()
        parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 31)])
        
    with col2:
        cant = st.number_input("Cantidad:", min_value=1, step=1)
        prensa = st.selectbox("Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        fecha_manual = st.text_input("Fecha (DD/MM/YYYY):", placeholder="Vacio = Hoy")

    st.divider()
    
    c1, c2 = st.columns(2)
    if c1.button("💾 GUARDAR", use_container_width=True, type="primary"):
        if mat.strip():
            f_final = fecha_manual if fecha_manual.strip() else datetime.now().strftime("%d/%m/%Y")
            
            nueva_fila = pd.DataFrame([{
                "Codigo": prod,
                "Fecha_Registro": f_final,
                "Operador": nombre_operario,
                "N_Parrilla": parrilla,
                "Cantidad": cant,
                "Material": mat,
                "Prensa": prensa,
                "Estado": "PENDIENTE"
            }])
            
            if funcion_guardar("COPELA", nueva_fila):
                st.success("✅ Guardado correctamente")
                st.rerun()
        else:
            st.error("⚠️ El campo Material es obligatorio.")

    if c2.button("❌ CANCELAR", use_container_width=True):
        st.rerun()
