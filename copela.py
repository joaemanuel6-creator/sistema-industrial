import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests  # Si da error, ejecuta: pip install requests
import json

# --- CONFIGURACIÓN DE TU API DE GOOGLE (PROBADA EN REQBIN) ---
URL_API_GOOGLE = "https://script.google.com/macros/s/AKfycbx2-CDyiFjZ711oY7B5jCBdP_tJ5Vy2VruHYKhocCrUd0bFSdrWNJcEp-M6CgAwz8D8/exec"

class RegistroCopelas:
    def __init__(self, root_parent, nombre_operario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("SISTEMA INDUSTRIAL - CONTROL DE PRODUCCIÓN")
        self.nombre_operario = nombre_operario
        
        # Base de datos local
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#2c3e50")

        self.inicializar_db()
        self.crear_interfaz()
        self.cargar_datos_tabla()

    def inicializar_db(self):
        """Crea la tabla en tu PC si no existe"""
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
            print(f"Error al iniciar base de datos local: {e}")

    def enviar_a_google_drive(self, datos_dict):
        """Envía los datos al Excel de Google Sheets"""
        try:
            # Enviamos usando el formato que aceptó ReqBin
            response = requests.post(
                URL_API_GOOGLE, 
                json=datos_dict, 
                timeout=15
            )
            # Imprime en la consola negra lo que responde Google
            print(f"Respuesta de Google: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error de conexión con la nube: {e}")
            return False

    def registrar_datos(self):
        """Guarda en la PC y luego en la Nube"""
        # 1. Validar que no haya campos vacíos
        if not self.ent_mat.get() or not self.ent_uni.get() or not self.cb_prod.get():
            messagebox.showwarning("Atención", "Por favor, completa todos los campos.")
            return

        fecha_actual = self.ent_fec_reg.get().strip()
        if not fecha_actual:
            fecha_actual = datetime.now().strftime("%d/%m/%Y")

        # 2. Preparar el diccionario de datos
        datos_finales = {
            "codigo": self.cb_prod.get(),
            "fecha": fecha_actual,
            "operador": self.nombre_operario,
            "n_parrilla": self.cb_parr.get(),
            "cantidad": int(self.ent_uni.get()),
            "material": self.ent_mat.get().upper(),
            "prensa": self.cb_prensa.get()
        }

        try:
            # 3. GUARDAR EN SQLITE (PC LOCAL)
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                    VALUES (?,?,?,?,?,?,?,?)""", (
                        datos_finales["codigo"], datos_finales["fecha"], datos_finales["operador"], 
                        datos_finales["n_parrilla"], datos_finales["cantidad"], 
                        datos_finales["material"], datos_finales["prensa"], "SINCRONIZADO"
                    ))
                conn.commit()

            # 4. ENVIAR A GOOGLE DRIVE
            if self.enviar_a_google_drive(datos_finales):
                messagebox.showinfo("Éxito", f"✅ Registro exitoso para {self.nombre_operario}.\nDatos guardados en Google Sheets.")
            else:
                messagebox.showwarning("Aviso", "⚠️ Guardado en PC, pero no se pudo sincronizar con Google Sheets.\nRevisa tu conexión a internet.")

            self.limpiar_campos()
            self.cargar_datos_tabla()

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al registrar: {e}")

    def crear_interfaz(self):
        estilo_caja = {"width": 25, "font": ("Arial", 12)}
        
        # --- ENCABEZADO ---
        tk.Label(self.ventana, text="📝 REGISTRO DE PRODUCCIÓN: COPELAS", fg="#00d2ff", bg="#2c3e50", font=("Arial", 22, "bold")).pack(pady=20)

        # --- FORMULARIO ---
        f_form = tk.LabelFrame(self.ventana, text=" Datos de Entrada ", fg="white", bg="#2c3e50", font=("Arial", 11, "bold"), padx=20, pady=20)
        f_form.pack(pady=10, padx=30, fill="x")

        # Fila 1
        tk.Label(f_form, text="Código Producto:", fg="white", bg="#2c3e50").grid(row=0, column=0, sticky="w")
        self.cb_prod = ttk.Combobox(f_form, values=["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"], state="readonly", **estilo_caja)
        self.cb_prod.grid(row=1, column=0, padx=10, pady=5)

        tk.Label(f_form, text="Material:", fg="white", bg="#2c3e50").grid(row=0, column=1, sticky="w")
        self.ent_mat = tk.Entry(f_form, **estilo_caja)
        self.ent_mat.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(f_form, text="N° Parrilla:", fg="white", bg="#2c3e50").grid(row=0, column=2, sticky="w")
        self.cb_parr = ttk.Combobox(f_form, values=[f"P-{i:02d}" for i in range(1, 21)], state="readonly", **estilo_caja)
        self.cb_parr.grid(row=1, column=2, padx=10, pady=5)

        # Fila 2
        tk.Label(f_form, text="Cantidad:", fg="white", bg="#2c3e50").grid(row=2, column=0, sticky="w", pady=(10,0))
        self.ent_uni = tk.Entry(f_form, **estilo_caja)
        self.ent_uni.grid(row=3, column=0, padx=10, pady=5)

        tk.Label(f_form, text="Prensa:", fg="white", bg="#2c3e50").grid(row=2, column=1, sticky="w", pady=(10,0))
        self.cb_prensa = ttk.Combobox(f_form, values=["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"], state="readonly", **estilo_caja)
        self.cb_prensa.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(f_form, text="Fecha (DD/MM/YYYY):", fg="white", bg="#2c3e50").grid(row=2, column=2, sticky="w", pady=(10,0))
        self.ent_fec_reg = tk.Entry(f_form, **estilo_caja)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=3, column=2, padx=10, pady=5)

        # --- BOTÓN ---
        self.btn_guardar = tk.Button(self.ventana, text="💾 REGISTRAR Y GUARDAR EN NUBE", bg="#27ae60", fg="white", font=("Arial", 14, "bold"), 
                                     padx=20, pady=10, command=self.registrar_datos, cursor="hand2")
        self.btn_guardar.pack(pady=20)

        # --- TABLA ---
        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cod", "Fecha", "Op", "Parrilla", "Cant", "Mat", "Prensa", "Estado"), show="headings")
        cabeceras = [("ID", 40), ("Cod", 80), ("Fecha", 100), ("Op", 120), ("Parrilla", 80), ("Cant", 60), ("Mat", 120), ("Prensa", 100), ("Estado", 100)]
        for col, ancho in cabeceras:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=30, pady=10)

    def cargar_datos_tabla(self):
        """Muestra los últimos 10 registros locales"""
        for i in self.tabla.get_children(): self.tabla.delete(i)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC LIMIT 10")
                for fila in cur.fetchall():
                    self.tabla.insert("", "end", values=fila)
        except: pass

    def limpiar_campos(self):
        self.ent_mat.delete(0, tk.END)
        self.ent_uni.delete(0, tk.END)
        self.cb_prod.set('')
        self.cb_parr.set('')

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    app = RegistroCopelas(root, "MANUEL") # Cambia el nombre según el operario
    root.mainloop()
