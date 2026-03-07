import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONEXIÓN (Asumiendo que ya tienes init_connection) ---
URL = "https://rrekwemzohknmaxzsefy.supabase.co"
KEY = "sb_publishable_d3blWIICLZB58Drby3-Mbg_1yiZd-9J"
supabase = create_client(URL, KEY)

def modulo_gestion_usuarios(admin_actual):
    st.markdown('<p class="titulo-central">👥 GESTIÓN DE USUARIOS MAESTRA</p>', unsafe_allow_html=True)

    # 1. BUSCADOR / SELECCIÓN DE USUARIO EXISTENTE
    st.subheader("🔍 Buscar o Editar Usuario")
    try:
        res = supabase.table("USUARIO").select("*").execute()
        df_usuarios = pd.DataFrame(res.data)
        
        if not df_usuarios.empty:
            usuario_sel = st.selectbox("Seleccione un usuario para editar/eliminar:", 
                                     ["--- NUEVO USUARIO ---"] + df_usuarios['ID'].tolist())
        else:
            usuario_sel = "--- NUEVO USUARIO ---"
    except:
        usuario_sel = "--- NUEVO USUARIO ---"
        st.error("Error al conectar con la tabla USUARIO.")

    # Cargar datos si se selecciona uno
    datos_previa = {}
    if usuario_sel != "--- NUEVO USUARIO ---":
        datos_previa = df_usuarios[df_usuarios['ID'] == usuario_sel].iloc[0].to_dict()

    # 2. FORMULARIO DE DATOS
    with st.form("form_usuarios", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            u_id = st.text_input("🆔 ID Usuario (Login)", value=datos_previa.get('ID', "")).upper()
            u_pass = st.text_input("🔑 Contraseña", value=datos_previa.get('CONTRASEÑA', ""), type="password")
            u_nom = st.text_input("Nombres", value=datos_previa.get('NOMBRES', "")).upper()
            u_tipo = st.selectbox("Tipo de Usuario", ["OPERARIO", "SUPERVISOR", "ADMINISTRADOR"], 
                                 index=0 if not datos_previa else ["OPERARIO", "SUPERVISOR", "ADMINISTRADOR"].index(datos_previa.get('TIPO_USUARIO', "OPERARIO")))

        with col2:
            u_ape = st.text_input("Apellidos", value=datos_previa.get('APELLIDOS', "")).upper()
            u_dni = st.text_input("DNI", value=datos_previa.get('DNI', ""))
            st.info(f"Registrado por: {datos_previa.get('ADMIN_REGISTRO', admin_actual)}")

        st.divider()
        st.markdown("**🛡️ PERMISOS DE ACCESO (1 = SI, 0 = NO)**")
        
        # Grid de permisos (3 columnas)
        p_cols = st.columns(3)
        permisos_lista = [
            "COPELAS", "CRISOLES", "LIMPIEZA", "EMBALAJE", "MEZCLA", "ZARANDA", 
            "MOLINO", "USUARIO", "HISTORIAL", "OBSERVACION", "ALMACEN", "MANTENIMIENTO"
        ]
        
        nuevos_permisos = {}
        for i, perm in enumerate(permisos_lista):
            with p_cols[i % 3]:
                # En Supabase guardamos 1 o 0
                valor_actual = int(datos_previa.get(perm, 0))
                nuevos_permisos[perm] = st.radio(f"{perm}", [1, 0], index=0 if valor_actual == 1 else 1, horizontal=True)

        # Botones de Acción
        c_btn1, c_btn2, c_btn3 = st.columns(3)
        with c_btn1:
            btn_guardar = st.form_submit_button("💾 GUARDAR / ACTUALIZAR")
        with c_btn2:
            btn_eliminar = st.form_submit_button("🗑️ ELIMINAR USUARIO")

    # 3. LÓGICA DE BASE DE DATOS
    if btn_guardar:
        if u_id and u_pass:
            payload = {
                "ID": u_id,
                "CONTRASEÑA": u_pass,
                "NOMBRES": u_nom,
                "APELLIDOS": u_ape,
                "DNI": u_dni,
                "TIPO_USUARIO": u_tipo,
                "ADMIN_REGISTRO": admin_actual,
                "FECHA_REGISTRO": datetime.now().strftime("%Y-%m-%d %H:%M"),
                **nuevos_permisos
            }
            
            try:
                # Upsert: Si el ID existe lo actualiza, si no lo crea
                supabase.table("USUARIO").upsert(payload).execute()
                st.success(f"✅ Usuario {u_id} procesado correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al procesar: {e}")
        else:
            st.warning("ID y Contraseña son obligatorios.")

    if btn_eliminar:
        if usuario_sel != "--- NUEVO USUARIO ---":
            try:
                supabase.table("USUARIO").delete().eq("ID", usuario_sel).execute()
                st.success(f"🗑️ Usuario {usuario_sel} eliminado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")

    # 4. TABLA DE RESUMEN
    st.divider()
    st.subheader("📋 Lista de Personal")
    if not df_usuarios.empty:
        st.dataframe(df_usuarios[['ID', 'NOMBRES', 'APELLIDOS', 'TIPO_USUARIO', 'DNI']], use_container_width=True)
