import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    st.markdown("### 🛠️ ADMINISTRACIÓN DE PERSONAL Y PERMISOS")
    st.write("Desde aquí puedes activar módulos y cambiar rangos de acceso.")

    try:
        # 1. Obtener datos actualizados de Supabase
        res = supabase.table("USUARIO").select("*").execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            # Buscador/Selector de usuario
            st.markdown("---")
            sel_user = st.selectbox("🔍 Buscar Usuario por ID:", df['ID'].tolist(), help="Selecciona el ID del trabajador")
            
            # Filtrar datos del usuario seleccionado
            datos = df[df['ID'] == sel_user].iloc[0]

            with st.form("ventana_gestion_usuarios"):
                st.subheader(f"👤 Perfil: {datos.get('Nombres')} {datos.get('Apellidos')}")
                
                # Layout de columnas para datos generales
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**DNI:** {datos.get('DNI')}")
                with c2:
                    tipo_actual = datos.get('Usuario_Tipo', 'OPERARIO')
                    nuevo_tipo = st.selectbox("Rango:", ["OPERARIO", "SUPERVISOR", "ADMIN"], 
                                             index=["OPERARIO", "SUPERVISOR", "ADMIN"].index(tipo_actual) if tipo_actual in ["OPERARIO", "SUPERVISOR", "ADMIN"] else 0)
                with c3:
                    st.write(f"**Registro:** {datos.get('Fecha_Registro', 'N/A')}")

                st.markdown("#### 🔑 PANEL DE ACCESOS")
                
                # Dividimos los permisos en 3 categorías lógicas
                col_prod, col_alm, col_sis = st.columns(3)
                
                actualizados = {}

                with col_prod:
                    st.markdown("**📦 PRODUCCIÓN**")
                    for p in ["Copela", "Crisol", "Mezcla", "Zaranda", "Molino"]:
                        val = 1 if datos.get(p) in [1, "1", "SI"] else 0
                        op = st.checkbox(p, value=(val == 1))
                        actualizados[p] = 1 if op else 0

                with col_alm:
                    st.markdown("**🏗️ LOGÍSTICA**")
                    for p in ["Almacen", "Embalaje", "Limpieza"]:
                        val = 1 if datos.get(p) in [1, "1", "SI"] else 0
                        op = st.checkbox(p, value=(val == 1))
                        actualizados[p] = 1 if op else 0

                with col_sis:
                    st.markdown("**🖥️ SISTEMA**")
                    for p in ["Usuario", "Historial", "Observacion", "Mantenimiento"]:
                        val = 1 if datos.get(p) in [1, "1", "SI"] else 0
                        op = st.checkbox(p, value=(val == 1))
                        actualizados[p] = 1 if op else 0

                # Campo de observación
                obs_act = datos.get('Observacion', '')
                actualizados['Observacion'] = st.text_area("Notas/Observaciones del personal", value=obs_act if obs_act else "")
                
                # Asignar el tipo de usuario seleccionado arriba
                actualizados['Usuario_Tipo'] = nuevo_tipo

                st.markdown("---")
                if st.form_submit_button("💾 GUARDAR CAMBIOS EN NUBE"):
                    # Guardar en Supabase
                    supabase.table("USUARIO").update(actualizados).eq("ID", sel_user).execute()
                    st.success(f"✅ ¡Éxito! Permisos actualizados para {sel_user}.")
                    st.balloons()
                    st.rerun()
        else:
            st.warning("No hay usuarios registrados en la base de datos.")
            
    except Exception as e:
        st.error(f"Error de conexión con Supabase: {e}")

    if st.button("⬅️ SALIR A PANEL PRINCIPAL"):
        st.session_state.sub_modulo = None
        st.rerun()
