import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    st.markdown("### 🛠 MODIFICACIÓN MAESTRA DE PERMISOS")
    
    # 1. Traer todos los usuarios de la nube
    res = supabase.table("USUARIO").select("*").execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        user_to_edit = st.selectbox("Seleccione Usuario para dar Permisos:", df['ID'].tolist())
        datos_user = df[df['ID'] == user_to_edit].iloc[0]
        
        with st.form("form_permisos"):
            st.write(f"Editando a: **{datos_user['NOMBRES']}**")
            col1, col2 = st.columns(2)
            
            # Lista de permisos que quieres controlar
            lista_p = ["COPELAS", "CRISOLES", "MEZCLA", "ALMACEN", "USUARIO", "MANTENIMIENTO", "HISTORIAL"]
            dict_nuevos = {}
            
            for i, p in enumerate(lista_p):
                # Si el valor en la base es 1, el radio marca "SI"
                valor_actual = 1 if datos_user.get(p) == 1 else 0
                with col1 if i % 2 == 0 else col2:
                    dict_nuevos[p] = st.radio(f"Permiso {p}:", ["NO", "SI"], index=valor_actual, horizontal=True)
            
            if st.form_submit_button("✅ ACTUALIZAR PERMISOS EN LA NUBE"):
                # Convertimos "SI" a 1 y "NO" a 0
                payload = {k: (1 if v == "SI" else 0) for k, v in dict_nuevos.items()}
                supabase.table("USUARIO").update(payload).eq("ID", user_to_edit).execute()
                st.success(f"Permisos actualizados para {user_to_edit}")
                st.rerun()
    
    if st.button("⬅ Cerrar Gestión"):
        st.session_state.modulo = None
        st.rerun()
