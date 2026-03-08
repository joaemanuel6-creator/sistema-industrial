import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    """
    Esta función actúa como la 'ventana' de gestión de usuarios.
    Se activa cuando el admin presiona el botón en la app principal.
    """
    st.markdown("<h2 style='color: #00d2ff; text-align: center;'>🛠️ GESTIÓN DE PERMISOS Y USUARIOS</h2>", unsafe_allow_html=True)
    st.write("Seleccione un usuario para modificar su acceso a los módulos industriales.")

    try:
        # 1. Obtener datos actualizados de Supabase
        res = supabase.table("USUARIO").select("*").execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            # 2. Selector de Usuario
            user_list = df['ID'].tolist()
            usuario_sel = st.selectbox("🔍 Buscar Usuario por ID:", user_list)
            
            # Extraer datos del usuario seleccionado
            datos_u = df[df['ID'] == usuario_sel].iloc[0]

            # 3. Formulario de Edición (La Ventana)
            with st.form("ventana_permisos", clear_on_submit=False):
                st.markdown(f"### Perfil: {datos_u.get('Nombres')} {datos_u.get('Apellidos')}")
                
                col1, col2, col3 = st.columns(3)
                
                # Definimos las columnas de permisos exactas de tu DB
                permisos_lista = [
                    "Copela", "Crisol", "Limpieza", "Embalaje", "Mezcla", 
                    "Zaranda", "Molino", "Usuario", "Historial", 
                    "Observacion", "Almacen", "Mantenimiento"
                ]
                
                nuevos_permisos = {}

                # Generar interruptores (Radios) para cada permiso
                for i, permiso in enumerate(permisos_lista):
                    # Ubicación en columnas
                    target_col = [col1, col2, col3][i % 3]
                    
                    with target_col:
                        # Determinar estado actual (1 = SI, 0 = NO)
                        val_actual = 1 if datos_u.get(permiso) in [1, "1", "SI"] else 0
                        
                        sel = st.radio(
                            f"**{permiso}**", 
                            ["NO", "SI"], 
                            index=val_actual, 
                            horizontal=True,
                            key=f"perm_{permiso}"
                        )
                        nuevos_permisos[permiso] = 1 if sel == "SI" else 0

                st.divider()

                # Datos de Clasificación
                c_pie1, c_pie2 = st.columns(2)
                with c_pie1:
                    nuevos_permisos["Usuario_Tipo"] = st.selectbox(
                        "Categoría de Usuario", 
                        ["OPERARIO", "SUPERVISOR", "ADMIN"],
                        index=["OPERARIO", "SUPERVISOR", "ADMIN"].index(datos_u.get("Usuario_Tipo", "OPERARIO"))
                    )
                with c_pie2:
                    nuevos_permisos["Observacion"] = st.text_input("Nota / Observación", value=datos_u.get("Observacion", ""))

                # 4. Botón de Guardado
                if st.form_submit_button("💾 GUARDAR CAMBIOS EN LA NUBE"):
                    try:
                        supabase.table("USUARIO").update(nuevos_permisos).eq("ID", usuario_sel).execute()
                        st.success(f"✅ Permisos actualizados para {usuario_sel}")
                        # Pequeña pausa para mostrar el éxito antes de recargar
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

        else:
            st.warning("No hay usuarios registrados en la base de datos.")

    except Exception as e:
        st.error(f"Error de conexión con Supabase: {e}")

    # Botón para cerrar la 'ventana'
    if st.button("⬅️ VOLVER AL PANEL"):
        st.session_state.sub_modulo = None
        st.rerun()
