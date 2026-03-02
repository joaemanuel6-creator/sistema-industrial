import streamlit as st
import pandas as pd
from datetime import datetime

@st.dialog("REGISTRO DE COPELAS", width="large")
def ventana_registro_copelas(nombre_operario, funcion_guardar):
    st.markdown(f"### 📋 Formulario de Producción")
    st.write(f"**Operario Responsable:** {nombre_operario}")
    
    # --- CAMPOS DE ENTRADA ---
    col1, col2 = st.columns(2)
    
    with col1:
        prod = st.selectbox("C/Producto (Código):", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
        mat = st.text_input("Material Utilizado:").upper()
        parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 31)])
        
    with col2:
        cant = st.number_input("Cantidad de Unidades:", min_value=0, step=1)
        prensa = st.selectbox("Prensa Asignada:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        fecha_manual = st.text_input("Fecha (DD/MM/YYYY):", placeholder="Dejar vacío para usar hoy")

    st.divider()
    
    # --- BOTONES DE ACCIÓN ---
    c1, c2 = st.columns(2)
    
    if c1.button("💾 GUARDAR REGISTRO", use_container_width=True, type="primary"):
        if mat and cant > 0:
            # Definir fecha
            fecha_final = fecha_manual if fecha_manual.strip() != "" else datetime.now().strftime("%d/%m/%Y")
            
            # Crear el DataFrame con tu estructura de Excel
            nuevo_reg = pd.DataFrame([{
                "Codigo": prod,
                "Fecha_Registro": fecha_final,
                "Operador": nombre_operario,
                "N_Parrilla": parrilla,
                "Cantidad": cant,
                "Material": mat,
                "Prensa": prensa,
                "Estado": "PENDIENTE"
            }])
            
            # Llamar a la función de guardado que viene del archivo principal
            if funcion_guardar("COPELA", nuevo_reg):
                st.success(f"✅ ¡Registrado con éxito! ({fecha_final})")
                st.balloons()
                st.rerun() # Cierra el diálogo y refresca la tabla principal
        else:
            st.error("⚠️ Por favor completa el Material y la Cantidad.")

    if c2.button("❌ CANCELAR", use_container_width=True):
        st.rerun()
