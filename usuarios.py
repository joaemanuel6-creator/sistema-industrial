import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    st.markdown("### 🛠️ PANEL DE CONTROL DE PERMISOS")
    st.write("Selecciona un usuario para activar o desactivar sus módulos de acceso.")

    try:
        # Traer todos los usuarios de la base de datos
        res = supabase.table("USUARIO").select("*").execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            # Selector de usuario
            user_to_edit = st.selectbox("👤 Seleccionar Personal para Editar:", df['ID'].tolist())
            datos_user = df[df['ID'] == user_to_edit].iloc[0]

            with st.form("form_permisos_nube"):
                st.info(f"Modificando a: **{datos_user.get('NOMBRES', 'Sin Nombre')}**")
                
                # Lista de columnas de permisos en tu tabla de Supabase
                permisos = ["COPELAS", "CRISOLES", "MEZCLA", "ALMACEN", "USUARIO", "MANTENIMIENTO", "HISTORIAL", "LIMPIEZA"]
                nuevos_valores = {}

                # Diseño en 2 columnas para mejor visualización
                col1, col2 = st.columns(2)
                
                for i, p in enumerate(permisos):
                    # Valor actual en la DB (1 o 0)
                    estado_actual = 1 if datos_user.get(p) == 1 else 0
                    
                    with col1 if i % 2 == 0 else col2:
                        # Radio button para elegir SI o NO
                        opcion = st.radio(f"Acceso a {p}:", ["NO", "SI"], index=estado_actual, horizontal=True)
                        nuevos_valores[p] = 1 if opcion == "SI" else 0

                if st.form_submit_button("💾 APLICAR CAMBIOS EN LA NUBE"):
                    supabase.table("USUARIO").update(nuevos_valores).eq("ID", user_to_edit).execute()
                    st.success(f"✅ Permisos actualizados para {user_to_edit}")
                    st.rerun()
        else:
            st.warning("No se encontraron usuarios registrados.")
            
    except Exception as e:
        st.error(f"Error al conectar con la tabla USUARIO: {e}")

    if st.button("⬅️ VOLVER AL PANEL PRINCIPAL"):
        st.session_state.sub_modulo = None
        st.rerun()
