import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    st.markdown("### 🛠️ CONTROL MAESTRO DE PERMISOS")
    
    try:
        # Traemos la lista de usuarios
        res = supabase.table("USUARIO").select("*").execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            sel_user = st.selectbox("👤 Seleccionar usuario para modificar:", df['ID'].tolist())
            datos = df[df['ID'] == sel_user].iloc[0]

            with st.form("form_permisos_detallado"):
                st.info(f"Editando a: **{datos.get('Nombres')} {datos.get('Apellidos')}**")
                
                # LISTA EXACTA DE TUS COLUMNAS DE PERMISOS
                columnas_permisos = [
                    "Copela", "Crisol", "Limpieza", "Embalaje", "Mezcla", 
                    "Zaranda", "Molino", "Usuario", "Historial", 
                    "Observacion", "Almacen", "Mantenimiento"
                ]
                
                nuevos_datos = {}
                col1, col2, col3 = st.columns(3)

                for i, p in enumerate(columnas_permisos):
                    # Identificar si el permiso actual es 1 o SI
                    valor_db = datos.get(p)
                    estado_act = 1 if valor_db in [1, "1", "SI"] else 0
                    
                    # Distribuir en 3 columnas para que se vea ordenado
                    with [col1, col2, col3][i % 3]:
                        op = st.radio(f"¿{p}?", ["NO", "SI"], index=estado_act, horizontal=True)
                        nuevos_datos[p] = 1 if op == "SI" else 0

                st.divider()
                # Campo para el tipo de usuario
                tipo_act = datos.get('Usuario_Tipo', 'OPERARIO')
                nuevos_datos['Usuario_Tipo'] = st.selectbox("Tipo de Usuario:", ["OPERARIO", "SUPERVISOR", "ADMIN"], 
                                                           index=["OPERARIO", "SUPERVISOR", "ADMIN"].index(tipo_act) if tipo_act in ["OPERARIO", "SUPERVISOR", "ADMIN"] else 0)

                if st.form_submit_button("💾 ACTUALIZAR PERMISOS"):
                    supabase.table("USUARIO").update(nuevos_datos).eq("ID", sel_user).execute()
                    st.success(f"✅ Permisos de {sel_user} actualizados correctamente.")
                    st.rerun()
        else:
            st.warning("No hay usuarios registrados.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

    if st.button("⬅️ REGRESAR"):
        st.session_state.sub_modulo = None
        st.rerun()
