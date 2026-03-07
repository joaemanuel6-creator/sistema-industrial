import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os
import pandas as pd
import requests  # Importante: pip install requests
import json

# --- CONFIGURACIÓN DE CONEXIÓN ---
# Pega aquí la URL que obtuviste al "Implementar" tu Apps Script
URL_API_GOOGLE = https://docs.google.com/spreadsheets/d/1dKqjZESRQ8pDmILv58u8ARm5Vowix185NudbaeUNfLI/edit?gid=0#gid=0

class RegistroCopelas:
    def __init__(self, root_parent, nombre_operario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("SISTEMA DE CONTROL - REGISTRO DE COPELAS")
        self.nombre_operario = nombre_operario
        
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.id_seleccionado = tk.StringVar(value="")
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#2f3640")

        self.inicializar_db()
        self.crear_interfaz()
        self.cargar_datos()

    # --- NUEVA FUNCIÓN: ENVÍO A GOOGLE DRIVE ---
    def enviar_a_google_sheets(self, datos_dict):
        try:
            # Enviamos el JSON a tu script de Google
            response = requests.post(URL_API_GOOGLE, data=json.dumps(datos_dict))
            if response.status_code == 200:
                print("Sincronizado con Google Drive correctamente.")
                return True
            else:
                print(f"Error en Drive: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error de red: {e}")
            return False

    def inicializar_db(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS COPELA (
                    N_Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    Codigo TEXT, Fecha_Registro TEXT, Operador TEXT, 
                    N_Parrilla TEXT, Cantidad INTEGER, Material TEXT, 
                    Prensa TEXT, Estado TEXT)""")
                conn.commit()
        except Exception as e:
            print(f"Error al inicializar DB: {e}")

    def obtener_fecha_proceso(self):
        fecha_manual = self.ent_fec_reg.get().strip()
        if not fecha_manual:
            return datetime.now().strftime("%d/%m/%Y")
        return fecha_manual

    def registrar(self):
        fecha_proceso = self.obtener_fecha_proceso()
        
        # 1. Preparamos el diccionario para Google Sheets
        datos_api = {
            "codigo": self.cb_prod.get(),
            "fecha": fecha_proceso,
            "operador": self.nombre_operario,
            "n_parrilla": self.cb_parr.get(),
            "cantidad": int(self.ent_uni.get()),
            "material": self.ent_mat.get().upper(),
            "prensa": self.cb_prensa.get()
        }
        
        try:
            # 2. Guardar en Base de Datos Local (SQLite)
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                    VALUES (?,?,?,?,?,?,?,?)""", (datos_api["codigo"], datos_api["fecha"], datos_api["operador"], 
                    datos_api["n_parrilla"], datos_api["cantidad"], datos_api["material"], datos_api["prensa"], "PENDIENTE"))
                conn.commit()

            # 3. ENVIAR A GOOGLE DRIVE (Sincronización)
            exito_nube = self.enviar_a_google_sheets(datos_api)

            if exito_nube:
                messagebox.showinfo("Éxito", f"Registrado localmente y en Google Drive.\nFecha: {fecha_proceso}")
            else:
                messagebox.showwarning("Aviso", "Guardado localmente, pero falló la subida a Google Drive (Revisa internet).")

            self.cargar_datos()
            self.limpiar_campos()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crear_interfaz(self):
        # ... (Tu código de interfaz se mantiene igual) ...
        # Asegúrate de que el botón REGISTRAR llame a self.registrar
        MEDIDAS = {"width": 20, "font": ("Arial", 12)}
        
        header = tk.Frame(self.ventana, bg="#2f3640")
        header.pack(fill="x", pady=10)
        tk.Label(header, text="REGISTRO DE COPELAS", fg="white", bg="#2f3640", font=("Arial", 25, "bold")).pack()
        
        f_in = tk.LabelFrame(self.ventana, text=" Datos de Producción ", fg="#00d2d3", bg="#2f3640", font=("Arial", 12, "bold"), padx=15, pady=15)
        f_in.pack(pady=10, padx=20, fill="x")
        
        # FILA 1
        tk.Label(f_in, text="C/Producto:", fg="white", bg="#2f3640").grid(row=0, column=0)
        self.cb_prod = ttk.Combobox(f_in, values=["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"], state="readonly", **MEDIDAS)
        self.cb_prod.grid(row=1, column=0, padx=5, pady=10)

        tk.Label(f_in, text="Material:", fg="white", bg="#2f3640").grid(row=0, column=1)
        self.ent_mat = tk.Entry(f_in, **MEDIDAS)
        self.ent_mat.grid(row=1, column=1, padx=5, pady=10)

        tk.Label(f_in, text="N° Parrilla:", fg="white", bg="#2f3640").grid(row=0, column=2)
        self.cb_parr = ttk.Combobox(f_in, values=[f"P-{i:02d}" for i in range(1, 21)], state="readonly", **MEDIDAS)
        self.cb_parr.grid(row=1, column=2, padx=5, pady=10)

        # FILA 2
        tk.Label(f_in, text="Cantidad:", fg="white", bg="#2f3640").grid(row=2, column=0)
        self.ent_uni = tk.Entry(f_in, **MEDIDAS)
        self.ent_uni.grid(row=3, column=0, padx=5, pady=10)

        tk.Label(f_in, text="Prensa:", fg="white", bg="#2f3640").grid(row=2, column=1)
        self.cb_prensa = ttk.Combobox(f_in, values=["Prensa 01", "Prensa 02", "Prensa 03"], state="readonly", **MEDIDAS)
        self.cb_prensa.grid(row=3, column=1, padx=5, pady=10)

        tk.Label(f_in, text="Fecha (DD/MM/YYYY):", fg="white", bg="#2f3640").grid(row=2, column=2)
        self.ent_fec_reg = tk.Entry(f_in, **MEDIDAS)
        self.ent_fec_reg.grid(row=3, column=2, padx=5, pady=10)

        # TABLA
        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cod", "Fec", "Op", "Par", "Cant", "Mat", "Pre"), show="headings")
        for c in self.tabla["columns"]: self.tabla.heading(c, text=c); self.tabla.column(c, width=100)
        self.tabla.pack(expand=True, fill="both", padx=20)

        # BOTÓN REGISTRAR
        self.btn_reg = tk.Button(self.ventana, text="REGISTRAR Y SINCRONIZAR", bg="#008080", fg="white", font=("Arial", 12, "bold"), command=self.registrar)
        self.btn_reg.pack(pady=20)

    def cargar_datos(self, filtro=""):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC")
            for r in cur.fetchall(): self.tabla.insert("", "end", values=r)

    def limpiar_campos(self):
        self.cb_prod.set(''); self.ent_mat.delete(0, tk.END); self.cb_parr.set('')
        self.ent_uni.delete(0, tk.END); self.cb_prensa.set(''); self.ent_fec_reg.delete(0, tk.END)

# --- INICIO ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = RegistroCopelas(root, "OPERARIO_PRUEBA")
    root.mainloop()
