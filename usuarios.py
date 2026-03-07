import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    st.markdown("### 🛠️ PANEL DE CONTROL DE PERMISOS")
    st.write("Selecciona un usuario para activar o desactivar sus módulos.")

    try:
        # Traer todos los usuarios de Supabase
        res = supabase.table("USUARIO").select("*").execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            # Buscador de usuario
            user_to_edit = st.selectbox("👤 Seleccionar Personal:", df['ID'].tolist())
            datos_user = df[df['ID'] == user_to_edit].iloc[0]

            with st.form("form_permisos_nube"):
                st.info(f"Editando permisos para: **{datos_user.get('NOMBRES', 'Sin Nombre')}**")
                
                # Lista de columnas de permisos en tu tabla de Supabase
                permisos = ["COPELAS", "CRISOLES", "MEZCLA", "ALMACEN", "USUARIO", "MANTENIMIENTO", "HISTORIAL", "LIMPIEZA"]
                nuevos_valores = {}

                # Crear 2 columnas para que quepa bien en celular
                col1, col2 = st.columns(2)
                
                for i, p in enumerate(permisos):
                    # Verificamos si ya tiene permiso (1) o no (0)
                    estado_actual = 1 if datos_user.get(p) == 1 else 0
                    
                    with col1 if i % 2 == 0 else col2:
                        # Radio button: SI (1) / NO (0)
                        opcion = st.radio(f"Acceso a {p}:", ["NO", "SI"], index=estado_actual, horizontal=True)
                        nuevos_valores[p] = 1 if opcion == "SI" else 0

                if st.form_submit_button("💾 APLICAR CAMBIOS EN LA NUBE"):
                    supabase.table("USUARIO").update(nuevos_valores).eq("ID", user_to_edit).execute()
                    st.success(f"✅ Permisos actualizados para {user_to_edit}")
                    st.rerun()
        else:
            st.warning("No hay usuarios registrados en la base de datos.")
            
    except Exception as e:
        st.error(f"Error al conectar con la tabla USUARIO: {e}")

    if st.button("⬅️ VOLVER AL PANEL PRINCIPAL"):
        st.session_state.sub_modulo = None
        st.rerun()
