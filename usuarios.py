import streamlit as st
from datetime import datetime

def formulario_crear_usuario(supabase):
    """Esta función crea la ventana de registro de usuario"""
    st.markdown("<h2 style='text-align: center; color: #00d2ff;'>📝 SOLICITUD DE REGISTRO</h2>", unsafe_allow_html=True)
    
    # Usamos un formulario de Streamlit para agrupar los datos
    with st.form("crear_usuario_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            id_user = st.text_input("🆔 ID de Usuario").upper().strip()
            contra = st.text_input("🔑 Contrasena", type="password")
            nombres = st.text_input("Nombres").upper()
            apellidos = st.text_input("Apellidos").upper()
            dni = st.text_input("DNI")
        
        with col2:
            tipo = st.selectbox("Tipo de Usuario", ["OPERARIO", "SUPERVISOR", "ADMIN"])
            obs = st.text_area("Observacion")
            st.info("⚠️ Los permisos (Copela, Crisol, etc.) se inician en NO (0) por defecto.")

        if st.form_submit_button("✅ ENVIAR REGISTRO"):
            if id_user and contra and nombres:
                # Diccionario con tus columnas exactas de Supabase
                datos_nuevos = {
                    "ID": id_user,
                    "Contrasena": contra,
                    "Nombres": nombres,
                    "Apellidos": apellidos,
                    "DNI": dni,
                    "Fecha_Registro": str(datetime.now().date()),
                    "Usuario_Tipo": tipo,
                    "Observacion": obs,
                    # Permisos en 0 por defecto
                    "Copela": 0, "Crisol": 0, "Limpieza": 0, "Embalaje": 0,
                    "Mezcla": 0, "Zaranda": 0, "Molino": 0, "Usuario": 0,
                    "Historial": 0, "Almacen": 0, "Mantenimiento": 0
                }
                
                try:
                    supabase.table("USUARIO").insert(datos_nuevos).execute()
                    st.success("✨ ¡Registro enviado con éxito! Espere la aprobación.")
                    st.session_state.registrando = False # Volver al login
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: El ID ya existe o falta conexión.")
            else:
                st.warning("⚠️ ID, Contrasena y Nombres son campos obligatorios.")

    # Botón fuera del formulario para cancelar
    if st.button("⬅️ CANCELAR Y VOLVER"):
        st.session_state.registrando = False
        st.rerun()

def modulo_permisos_maestro(supabase):
    """Esta es tu función para dar permisos (para el admin)"""
    st.write("### Panel de Control de Permisos")
    # ... (aquí va el código de actualización de permisos que ya teníamos)
