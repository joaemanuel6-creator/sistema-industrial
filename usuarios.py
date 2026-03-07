import streamlit as st
import pandas as pd

def modulo_permisos_maestro(supabase):
    st.markdown("### 🛠️ PANEL DE PERMISOS (Nube)")
    
    try:
        res = supabase.table("USUARIO").select("*").execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            sel_user = st.selectbox("Elegir usuario para dar permisos:", df['ID'].tolist())
            datos = df[df['ID'] == sel_user].iloc[0]

            with st.form("form_p"):
                st.info(f"Usuario: {datos.get('NOMBRES')}")
                # Columnas de tu tabla en Supabase
                permisos = ["COPELAS", "CRISOLES", "MEZCLA", "ALMACEN", "USUARIO", "MANTENIMIENTO", "LIMPIEZA"]
                actualizados = {}

                c1, c2 = st.columns(2)
                for i, p in enumerate(permisos):
                    estado = 1 if datos.get(p) == 1 else 0
                    with c1 if i % 2 == 0 else c2:
                        op = st.radio(f"{p}:", ["NO", "SI"], index=estado, horizontal=True)
                        actualizados[p] = 1 if op == "SI" else 0

                if st.form_submit_button("💾 ACTUALIZAR EN SUPABASE"):
                    supabase.table("USUARIO").update(actualizados).eq("ID", sel_user).execute()
                    st.success("✅ Permisos sincronizados.")
                    st.rerun()
        else:
            st.warning("No hay usuarios.")
    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("⬅️ VOLVER"):
        st.session_state.sub_modulo = None
        st.rerun()
