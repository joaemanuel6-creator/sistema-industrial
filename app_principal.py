# --- GESTIÓN DE SESIÓN (ADAPTADO A TU EXCEL) ---
if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA INDUSTRIAL")
    with st.form("login"):
        u = st.text_input("👤 ID DE USUARIO (Columna B)").strip()
        p = st.text_input("🔑 CONTRASEÑA (Columna C)", type="password")
        
        if st.form_submit_button("INGRESAR"):
            df_usuarios = leer_tabla("USUARIO")
            
            if not df_usuarios.empty:
                # 1. Aseguramos que los nombres coincidan con tu Excel (mayúsculas/minúsculas y Ñ)
                # Limpiamos espacios en blanco por si acaso
                df_usuarios.columns = df_usuarios.columns.str.strip()
                
                # 2. Verificamos que existan las columnas ID y Contraseña
                if 'ID' in df_usuarios.columns and 'Contraseña' in df_usuarios.columns:
                    # Convertimos a texto para comparar sin errores
                    df_usuarios['ID'] = df_usuarios['ID'].astype(str).str.strip()
                    df_usuarios['Contraseña'] = df_usuarios['Contraseña'].astype(str).str.strip()
                    
                    # 3. Buscamos al usuario
                    user = df_usuarios[(df_usuarios['ID'] == u) & (df_usuarios['Contraseña'] == p)]
                    
                    if not user.empty:
                        st.session_state.autenticado = True
                        st.session_state.user_data = user.iloc[0].to_dict()
                        st.success(f"✅ Bienvenido, {st.session_state.user_data.get('Nombres')}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o Contraseña incorrectos.")
                else:
                    st.error("⚠️ No se encontraron las columnas 'ID' o 'Contraseña' en el Excel.")
            else:
                st.error("⚠️ La pestaña 'USUARIO' está vacía o no se puede leer.")
    st.stop()
elif mod == "CRISOLES": modulo_crisoles()
elif mod == "MEZCLA": modulo_mezcla()
else: st.title(f"📂 MÓDULO {mod} EN CONSTRUCCIÓN")

