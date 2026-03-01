import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN Y ESTILO VISUAL (SIN CAMBIOS) ---
st.set_page_config(page_title="SISTEMA INDUSTRIAL PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #064e3b !important; border-right: 4px solid #10b981; }
    .user-text { font-size: 24px !important; color: #ffffff !important; font-weight: 900 !important; margin-bottom: 10px; display: block; }
    div[data-testid="stWidgetLabel"] p { font-size: 19px !important; color: #f1c40f !important; font-weight: 800 !important; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-weight: 700 !important; }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 55px;
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white !important; font-size: 18px !important; font-weight: 900; border: 2px solid #ffffff;
    }
    .resumen-salida {
        background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #f1c40f; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_PATH = "mi_base_de_datos.db"

def conectar_db():
    return sqlite3.connect(DB_PATH)

# --- 2. GESTIÓN DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.update({"autenticado": False, "user_data": {}, "modulo_activo": "COPELAS"})

if not st.session_state.autenticado:
    st.title("🔐 ACCESO AL SISTEMA")
    with st.form("login"):
        u = st.text_input("👤 ID DE USUARIO").strip()
        p = st.text_input("🔑 CONTRASEÑA", type="password")
        if st.form_submit_button("INGRESAR"):
            with conectar_db() as conn:
                df = pd.read_sql_query("SELECT * FROM USUARIO WHERE ID=? AND Contrasena=?", conn, params=(u, p))
                if not df.empty:
                    st.session_state.autenticado = True
                    st.session_state.user_data = df.iloc[0].to_dict()
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
    st.stop()

# --- 3. BARRA LATERAL ---
st.sidebar.title("🏭 SISTEMA PRINCIPAL")
st.sidebar.markdown(f'<span class="user-text">👤 {st.session_state.user_data.get("Nombres")}</span>', unsafe_allow_html=True)
st.sidebar.divider()

for op in ["COPELAS", "CRISOLES", "MEZCLA", "QUEMA", "LIMPIEZA", "ALMACEN"]:
    if st.sidebar.button(f"📂 {op}", key=f"side_{op}"):
        st.session_state.modulo_activo = op

st.sidebar.divider()
if st.sidebar.button("🚪 SALIR", type="secondary"):
    st.session_state.clear()
    st.rerun()

# --- 4. MODULOS REGISTRO (FECHA CORREGIDA A TEXTO DD/MM/YYYY) ---

def modulo_copelas():
    st.header("📝 REGISTRO DE COPELAS")
    with st.form("form_copelas", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            prod = st.selectbox("C/Producto:", ["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"])
            mat = st.text_input("Material (Nombre):").upper()
            prensa = st.selectbox("Seleccione Prensa:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with c2:
            parrilla = st.selectbox("N° Parrilla:", [f"P-{i:02d}" for i in range(1, 31)])
            cant = st.number_input("Cantidad Unidades:", min_value=0, step=1)
            # CORRECCIÓN: Fecha como texto precargado DD/MM/YYYY
            fecha_f = st.text_input("FECHA (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y"))
        
        if st.form_submit_button("💾 GUARDAR COPELAS"):
            if mat and cant > 0:
                with conectar_db() as conn:
                    conn.execute("INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) VALUES (?,?,?,?,?,?,?,?)",
                                 (prod, fecha_f, st.session_state.user_data['ID'], parrilla, cant, mat, prensa, "PENDIENTE"))
                st.success(f"✅ Guardado correctamente con fecha: {fecha_f}")

def modulo_crisoles():
    st.header("🔥 REGISTRO DE CRISOLES")
    with st.form("form_crisoles", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            prod = st.selectbox("C/Producto:", ["Cod-15", "Cod-30", "Cod-40", "Cod-50"])
            mat = st.text_input("Material Utilizado:").upper()
            prensa = st.selectbox("Prensa asignada:", ["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"])
        with c2:
            paleta = st.selectbox("N° Paleta:", [f"P-{i:02d}" for i in range(1, 31)])
            cant = st.number_input("Cantidad Registrada:", min_value=0, step=1)
            # CORRECCIÓN: Fecha como texto precargado DD/MM/YYYY
            fecha_f = st.text_input("FECHA (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y"))
        
        if st.form_submit_button("💾 REGISTRAR CRISOLES"):
            if mat and cant > 0:
                with conectar_db() as conn:
                    conn.execute("INSERT INTO CRISOL (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) VALUES (?,?,?,?,?,?,?, 'PENDIENTE')",
                                 (prod, fecha_f, st.session_state.user_data['ID'], paleta, cant, mat, prensa))
                st.success(f"✅ Registrado correctamente con fecha: {fecha_f}")

# --- 5. LÓGICA DE MEZCLAS (MULTI-BALDES) ---

def modulo_mezcla():
    st.header("🧪 CONTROL DUAL DE MEZCLAS")
    tipo = st.radio("SELECCIONE TIPO DE MEZCLA:", ["MEZCLA COPELAS", "MEZCLA CRISOLES"], horizontal=True)
    st.divider()

    if tipo == "MEZCLA COPELAS":
        with conectar_db() as conn:
            df = pd.read_sql_query("SELECT N_Codigo, Codigo, Material, Cantidad_Ingresado FROM MZ_COPELA WHERE Cantidad_Ingresado > 0", conn)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            mex = df[df['Material'].str.contains("MEXICANA", na=False)]
            sel_mex = st.selectbox("MAT. MEXICANA:", [None] + mex['N_Codigo'].tolist(), format_func=lambda x: f"ID {x}" if x else "Seleccione")
            kg_mex = st.number_input("KG/BALDE (Mex):", min_value=0.0)
        with c2:
            reb = df[df['Material'].str.contains("REBECA", na=False)]
            sel_reb = st.selectbox("MAT. REBECA:", [None] + reb['N_Codigo'].tolist(), format_func=lambda x: f"ID {x}" if x else "Seleccione")
            kg_reb = st.number_input("KG/BALDE (Reb):", min_value=0.0)
        with c3:
            otr = df[~df['Material'].str.contains("MEXICANA|REBECA", na=False)]
            sel_otr = st.selectbox("MAT. OTROS:", [None] + otr['N_Codigo'].tolist(), format_func=lambda x: f"ID {x}" if x else "Seleccione")
            kg_otr = st.number_input("KG/BALDE (Otr):", min_value=0.0)

        col_f1, col_f2, col_f3 = st.columns(3)
        baldes = col_f1.number_input("CANT. BALDES:", min_value=1, value=1)
        nom_mat = col_f2.text_input("NOMBRE DEL MATERIAL:").upper()
        cod_mz = col_f3.text_input("COD. MEZCLA:").upper()
        fecha_custom = st.text_input("FECHA (DD/MM/YYYY):", datetime.now().strftime("%d/%m/%Y"))

        suma_materiales = kg_mex + kg_reb + kg_otr
        total_salida = suma_materiales * baldes

        st.markdown(f"""
            <div class="resumen-salida">
                <h4>📊 RESUMEN DE SALIDA</h4>
                <p>Suma Materiales: {suma_materiales:,.2f} KG x {baldes} Baldes</p>
                <p style="font-size: 22px; color: #f1c40f;">TOTAL A DESCONTAR: {total_salida:,.2f} KG</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🚀 EJECUTAR MEZCLA COPELA"):
            if total_salida > 0 and nom_mat and cod_mz:
                with conectar_db() as conn:
                    cur = conn.cursor()
                    for sid, skg in [(sel_mex, kg_mex), (sel_reb, kg_reb), (sel_otr, kg_otr)]:
                        if sid and skg > 0:
                            descuento_parcial = skg * baldes
                            cur.execute("UPDATE MZ_COPELA SET Cantidad_Ingresado = Cantidad_Ingresado - ?, Cantidad_Salida = Cantidad_Salida + ? WHERE N_Codigo=?", 
                                        (descuento_parcial, descuento_parcial, sid))
                    cur.execute("INSERT INTO HISOMZ (Codigo, Fecha_Registro, Operador, Material, Cantidad_Ingresado, Total) VALUES (?,?,?,?,?,?)",
                                (cod_mz, fecha_custom, st.session_state.user_data['ID'], nom_mat, total_salida, total_salida))
                st.success("✅ Mezcla Copela procesada.")
                st.rerun()

    else: # MEZCLA CRISOLES
        with conectar_db() as conn:
            df_vales = pd.read_sql_query("SELECT N_Codigo, Codigo, Material, Total FROM VALESCRISOL", conn)
            df_mz_c = pd.read_sql_query("SELECT N_Codigo, Codigo, Material, Total FROM MZ_CRISOL", conn)

        st.write("### 1. SELECCIONE LOS BALDES (VALESCRISOL)")
        st.dataframe(df_vales, use_container_width=True)
        id_vale = st.selectbox("ID VALE:", [None] + df_vales['N_Codigo'].tolist())
        
        st.write("### 2. SELECCIONE EL LOTE DE MEZCLA (MZ_CRISOL)")
        st.dataframe(df_mz_c, use_container_width=True)
        id_mz = st.selectbox("ID LOTE:", [None] + df_mz_c['N_Codigo'].tolist())

        c_v1, c_v2 = st.columns(2)
        baldes_usar = c_v1.number_input("BALDES A USAR:", min_value=0.0, step=0.5)
        kg_arcilla = c_v2.number_input("KG ARCILLA X BALDE:", min_value=0.0)

        desc_kg = kg_arcilla * 2 * baldes_usar
        st.markdown(f"""<div class="resumen-salida"><h4>📊 SALIDA: {baldes_usar} Baldes / {desc_kg:,.2f} KG</h4></div>""", unsafe_allow_html=True)

        if st.button("⚙️ EJECUTAR MEZCLA CRISOL"):
            if id_vale and id_mz and baldes_usar > 0:
                with conectar_db() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE VALESCRISOL SET Total = Total - ?, Cant_Valdes_Salida = Cant_Valdes_Salida + ? WHERE N_Codigo=?", (baldes_usar, baldes_usar, id_vale))
                    cur.execute("UPDATE MZ_CRISOL SET Total = Total - ?, Cantidad_Salida = Cantidad_Salida + ? WHERE N_Codigo=?", (desc_kg, desc_kg, id_mz))
                    cur.execute("INSERT INTO HISOMZ (Codigo, Fecha_Registro, Operador, Material, Cantidad_Saca, Cantidad_Salida) VALUES (?,?,?,?,?,?)",
                                ("MZ-CRISOL", datetime.now().strftime("%d/%m/%Y"), st.session_state.user_data['ID'], "MEZCLA CRISOLES", baldes_usar, desc_kg))
                st.success("✅ Mezcla Crisol procesada.")
                st.rerun()

# --- 6. RENDERIZADO ---
mod = st.session_state.modulo_activo
if mod == "COPELAS": modulo_copelas()
elif mod == "CRISOLES": modulo_crisoles()
elif mod == "MEZCLA": modulo_mezcla()
else: st.title(f"📂 MÓDULO {mod}")