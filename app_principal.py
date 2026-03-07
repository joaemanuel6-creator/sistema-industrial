import streamlit as st
import os
import sys

# --- BLOQUE ANTICRÍTICO: FORZAR RUTA ---
# Obtiene la carpeta donde está este archivo
ruta_raiz = os.path.dirname(os.path.abspath(__file__))
# Si la carpeta no está en el sistema de búsqueda, la añadimos
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

try:
    from usuario import modulo_permisos_maestro
except ImportError as e:
    st.error(f"⚠️ ERROR CRÍTICO: No se encuentra 'usuario.py'")
    st.info(f"Buscando en: {ruta_raiz}")
    st.write("Archivos encontrados en el servidor:", os.listdir(ruta_raiz))
    st.stop()
