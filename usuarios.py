import streamlit as st
from datetime import datetime

def formulario_registro(supabase):
    """Muestra el formulario para nuevos usuarios"""
    st.markdown("<h2 style='color: #00d2ff; text-align: center;'>📝 REGISTRO DE NUEVO USUARIO</h2>", unsafe_allow_html=True)
    
    with st.form("registro_usuarios_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            id_user = st.text_input("🆔 ID de Usuario (Login)").upper().strip()
            contra = st.text_input("🔑 Contraseña", type="password")
            nombres = st.text_input("Nombres").upper()
            apellidos = st.text_input("Apellidos").upper()
        
        with col2:
            dni = st.text_input("DNI")
            tipo = st.selectbox("Tipo de Usuario", ["OPERARIO", "SUPERVISOR"])
            obs = st.text_area("Observación")
        
        st.info("Nota: Al registrarse, sus permisos estarán desactivados hasta que un administrador los habilite.")

        if st.form_submit_button("💾 FINALIZAR REGISTRO"):
            if id_user and contra and nombres:
                # Preparamos los datos con tus columnas exactas
                datos = {
                    "ID": id_user,
                    "Contrasena": contra,
                    "Nombres": nombres,
                    "Apellidos": apellidos,
                    "DNI": dni,
                    "Fecha_Registro": str(datetime.now().date()),
                    "Usuario_Tipo": tipo,
                    "Observacion": obs,
                    # Inicializamos permisos en 0 (NO)
                    "Copela": 0, "Crisol": 0, "Limpieza": 0, "Embalaje": 0,
                    "Mezcla": 0, "Zaranda": 0, "Molino": 0, "Usuario": 0,
                    "Historial": 0, "Almacen": 0, "Mantenimiento": 0
                }
                
                try:
                    supabase.table("USUARIO").insert(datos).execute()
                    st.success("✅ ¡Registro exitoso! Ahora puedes intentar ingresar.")
                    st.session_state.registrando = False # Volver al login
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: El ID ya existe o hay un problema con la base de datos.")
            else:
                st.warning("Por favor, complete los campos obligatorios (ID, Contraseña y Nombres).")

    if st.button("⬅️ VOLVER AL ACCESO"):
        st.session_state.registrando = False
        st.rerun()
