import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import json
import requests

# --- CONFIGURACIÓN DE TU API (VERIFICADA) ---
URL_API_GOOGLE = "https://script.google.com/macros/s/AKfycbzggZNtHQJJv43ZoiO3zmQLLtcBL5O-K4S4E9_EUuV3JwfgRr7m_ww5MfSXDQjeMMSM/exec"

class RegistroCopelas:
    def __init__(self, root_parent, nombre_operario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("CONTROL INDUSTRIAL - COPELAS")
        self.nombre_operario = nombre_operario
        
        # Ruta de base de datos
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#1e272e") # Color oscuro profesional

        self.inicializar_db()
        self.crear_interfaz()
        self.cargar_datos_tabla()

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
            messagebox.showerror("Error Crítico DB", f"No se pudo crear la base de datos: {e}")

    def enviar_a_google_drive(self, datos):
        """Intenta enviar datos a Google Sheets"""
        try:
            # Importante: Usamos json.dumps para asegurar el formato
            response = requests.post(
                URL_API_GOOGLE, 
                data=json.dumps(datos),
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            # Imprime la respuesta en consola para depurar
            print(f"Respuesta Google: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error de Conexión: {e}")
            return False

    def registrar_datos(self):
        # 1. Validar campos vacíos
        if not self.cb_prod.get() or not self.ent_mat.get() or not self.ent_uni.get():
            messagebox.showwarning("Campos Vacíos", "Por favor completa todos los datos antes de registrar.")
            return

        # 2. Preparar el paquete de datos
        try:
            cant_num = int(self.ent_uni.get())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        datos_para_nube = {
            "codigo": self.cb_prod.get(),
            "fecha": self.ent_fec_reg.get().strip(),
            "operador": self.nombre_operario,
            "n_parrilla": self.cb_parr.get(),
            "cantidad": cant_num,
            "material": self.ent_mat.get().upper(),
            "prensa": self.cb_prensa.get()
        }

        # 3. GUARDADO LOCAL (SQLite)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                    VALUES (?,?,?,?,?,?,?,?)""", (
                        datos_para_nube["codigo"], datos_para_nube["fecha"], datos_para_nube["operador"], 
                        datos_para_nube["n_parrilla"], datos_para_nube["cantidad"], 
                        datos_para_nube["material"], datos_para_nube["prensa"], "SINCRONIZADO"
                    ))
                conn.commit()
            print("✅ Guardado en SQLite correctamente.")
        except Exception as e:
            messagebox.showerror("Error Local", f"Fallo al guardar en PC: {e}")
            return

        # 4. ENVÍO A LA NUBE
        messagebox.showinfo("Sincronizando", "Enviando datos a Google Drive... espera un momento.")
        if self.enviar_a_google_drive(datos_para_nube):
            messagebox.showinfo("Éxito Total", "✅ Datos guardados en PC y en el Excel de Google Sheets.")
        else:
            messagebox.showwarning("Sincronización Fallida", "⚠️ Se guardó en la PC, pero el Excel de Google NO recibió los datos. Revisa tu internet o la URL de la API.")

        self.limpiar_formulario()
        self.cargar_datos_tabla()

    def crear_interfaz(self):
        # Estilo de inputs
        estilo_in = {"width": 25, "font": ("Arial", 12)}
        
        # Título
        tk.Label(self.ventana, text="📝 REGISTRO DE COPELAS", fg="#00d2d3", bg="#1e272e", font=("Arial", 24, "bold")).pack(pady=20)

        # Contenedor
        f = tk.Frame(self.ventana, bg="#1e272e")
        f.pack(pady=10, padx=20)

        # Campos
        tk.Label(f, text="Código:", fg="white", bg="#1e272e").grid(row=0, column=0)
        self.cb_prod = ttk.Combobox(f, values=["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"], state="readonly", **estilo_in)
        self.cb_prod.grid(row=1, column=0, padx=10, pady=5)

        tk.Label(f, text="Material:", fg="white", bg="#1e272e").grid(row=0, column=1)
        self.ent_mat = tk.Entry(f, **estilo_in)
        self.ent_mat.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(f, text="N° Parrilla:", fg="white", bg="#1e272e").grid(row=0, column=2)
        self.cb_parr = ttk.Combobox(f, values=[f"P-{i:02d}" for i in range(1, 21)], state="readonly", **estilo_in)
        self.cb_parr.grid(row=1, column=2, padx=10, pady=5)

        tk.Label(f, text="Cantidad:", fg="white", bg="#1e272e").grid(row=2, column=0, pady=(15,0))
        self.ent_uni = tk.Entry(f, **estilo_in)
        self.ent_uni.grid(row=3, column=0, padx=10, pady=5)

        tk.Label(f, text="Prensa:", fg="white", bg="#1e272e").grid(row=2, column=1, pady=(15,0))
        self.cb_prensa = ttk.Combobox(f, values=["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"], state="readonly", **estilo_in)
        self.cb_prensa.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(f, text="Fecha (DD/MM/YYYY):", fg="white", bg="#1e272e").grid(row=2, column=2, pady=(15,0))
        self.ent_fec_reg = tk.Entry(f, **estilo_in)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=3, column=2, padx=10, pady=5)

        # Botón
        tk.Button(self.ventana, text="💾 REGISTRAR Y SINCRONIZAR", bg="#10ac84", fg="white", font=("Arial", 14, "bold"), 
                  command=self.registrar_datos, cursor="hand2", padx=20, pady=10).pack(pady=30)

        # Tabla
        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cod", "Fec", "Op", "Parrilla", "Cant", "Mat", "Pre"), show="headings")
        for c in self.tabla["columns"]: self.tabla.heading(c, text=c); self.tabla.column(c, width=100, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=40, pady=10)

    def cargar_datos_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC LIMIT 10")
            for r in cur.fetchall(): self.tabla.insert("", "end", values=r)

    def limpiar_formulario(self):
        self.ent_mat.delete(0, tk.END)
        self.ent_uni.delete(0, tk.END)
        self.cb_prod.set('')
        self.cb_parr.set('')

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = RegistroCopelas(root, "JOA EMANUEL")
    root.mainloop()
