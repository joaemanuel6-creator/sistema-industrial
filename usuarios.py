import streamlit as st
import pandas as pd
from datetime import datetime

def formulario_registro(supabase):
    """Función para que nuevos usuarios se registren"""
    st.markdown("### ➕ REGISTRO DE NUEVO PERSONAL")
    with st.form("reg_publico"):
        c1, c2 = st.columns(2)
        with c1:
            r_id = st.text_input("🆔 ID (Login)").upper().strip()
            r_pass = st.text_input("🔑 Contrasena", type="password")
            r_nom = st.text_input("Nombres").upper()
        with c2:
            r_ape = st.text_input("Apellidos").upper()
            r_dni = st.text_input("DNI")
            r_tipo = st.selectbox("Tipo", ["OPERARIO", "SUPERVISOR"])

        if st.form_submit_button("ENVIAR SOLICITUD"):
            if r_id and r_pass:
                payload = {
                    "ID": r_id, "Contrasena": r_pass, "Nombres": r_nom, 
                    "Apellidos": r_ape, "DNI": r_dni, "Usuario_Tipo": r_tipo,
                    "Fecha_Registro": str(datetime.now().date())
                }
                try:
                    supabase.table("USUARIO").insert(payload).execute()
                    st.success("✅ Registrado. El administrador activará tus permisos pronto.")
                    st.session_state.registrando = False
                    st.rerun()
                except: st.error("Error: El ID ya existe.")
            else: st.warning("ID y Contraseña son obligatorios.")

    if st.button("⬅ Volver al Login"):
        st.session_state.registrando = False
        st.rerun()

def modulo_permisos_maestro(supabase):
    """Función para que el administrador asigne permisos"""
    st.markdown("### 🛠️ GESTIÓN DE PERMISOS")
    res = supabase.table("USUARIO").select("*").execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        user = st.selectbox("Seleccionar Usuario:", df['ID'].tolist())
        datos = df[df['ID'] == user].iloc[0]
        
        with st.form("form_p"):
            st.write(f"Editando a: **{datos.get('Nombres')}**")
            # Lista de permisos según tu tabla
            campos = ["Copela", "Crisol", "Limpieza", "Embalaje", "Mezcla", "Zaranda", "Molino", "Usuario", "Historial", "Almacen", "Mantenimiento"]
            actualizados = {}
            
            c1, c2 = st.columns(2)
            for i, p in enumerate(campos):
                estado_actual = 1 if datos.get(p) == 1 else 0
                with c1 if i % 2 == 0 else c2:
                    op = st.radio(f"{p}:", ["NO", "SI"], index=estado_actual, horizontal=True)
                    actualizados[p] = 1 if op == "SI" else 0
            
            if st.form_submit_button("💾 GUARDAR CAMBIOS"):
                supabase.table("USUARIO").update(actualizados).eq("ID", user).execute()
                st.success("✅ Permisos actualizados.")
                st.rerun()

    if st.button("⬅️ Cerrar"):
        st.session_state.sub_modulo = None
        st.rerun()
