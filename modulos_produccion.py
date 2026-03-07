from modulos_produccion import modulo_registro_copelas

# ... en el panel central ...
if st.session_state.sub_modulo == "Registro de Copelas":
    modulo_registro_copelas()
