import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import json
import requests  # RECUERDA: pip install requests

# --- CONFIGURACIÓN DE TU API DE GOOGLE ---
URL_API_GOOGLE = "https://script.google.com/macros/s/AKfycbw-ub_uSE-6NX9DcWKwHOLABXdF4633-PBgV17cyr84Z5oXBeXl79S0Zb6oeBP0_9rO/exec"

class RegistroCopelas:
    def __init__(self, root_parent, nombre_operario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("SISTEMA INDUSTRIAL - REGISTRO DE COPELAS")
        self.nombre_operario = nombre_operario
        
        # Configuración de base de datos local
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#2f3640")

        self.inicializar_db()
        self.crear_interfaz()
        self.cargar_datos_tabla()

    def inicializar_db(self):
        """Crea la tabla local si no existe"""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS COPELA (
                N_Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Codigo TEXT, Fecha_Registro TEXT, Operador TEXT, 
                N_Parrilla TEXT, Cantidad INTEGER, Material TEXT, 
                Prensa TEXT, Estado TEXT)""")
            conn.commit()

    def enviar_a_google_drive(self, datos):
        """Envía el diccionario de datos al Apps Script de Google"""
        try:
            response = requests.post(
                URL_API_GOOGLE, 
                data=json.dumps(datos),
                headers={'Content-Type': 'application/json'},
                timeout=10 # Espera máximo 10 segundos
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error de conexión con Google: {e}")
            return False

    def registrar_datos(self):
        """Lógica principal de guardado local y nube"""
        # Validación básica
        if not self.ent_mat.get() or not self.ent_uni.get():
            messagebox.showwarning("Atención", "Por favor llene todos los campos.")
            return

        fecha_proceso = self.ent_fec_reg.get().strip()
        if not fecha_proceso:
            fecha_proceso = datetime.now().strftime("%d/%m/%Y")

        # Preparar paquete de datos
        datos_registro = {
            "codigo": self.cb_prod.get(),
            "fecha": fecha_proceso,
            "operador": self.nombre_operario,
            "n_parrilla": self.cb_parr.get(),
            "cantidad": int(self.ent_uni.get()),
            "material": self.ent_mat.get().upper(),
            "prensa": self.cb_prensa.get()
        }

        try:
            # 1. GUARDAR LOCAL (SQLite)
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                    VALUES (?,?,?,?,?,?,?,?)""", (
                        datos_registro["codigo"], datos_registro["fecha"], datos_registro["operador"], 
                        datos_registro["n_parrilla"], datos_registro["cantidad"], 
                        datos_registro["material"], datos_registro["prensa"], "PENDIENTE"
                    ))
                conn.commit()

            # 2. ENVIAR A GOOGLE DRIVE
            exito_nube = self.enviar_a_google_drive(datos_registro)

            if exito_nube:
                messagebox.showinfo("Éxito", "✅ Registro guardado en PC y sincronizado con Google Drive.")
            else:
                messagebox.showwarning("Sincronización", "⚠️ Guardado en PC, pero NO se pudo subir a la nube. Revise su internet.")

            self.limpiar_formulario()
            self.cargar_datos_tabla()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def crear_interfaz(self):
        estilo = {"width": 25, "font": ("Arial", 12)}
        
        # Encabezado
        header = tk.Frame(self.ventana, bg="#2f3640")
        header.pack(fill="x", pady=15)
        tk.Label(header, text="📝 REGISTRO DE PRODUCCIÓN: COPELAS", fg="#00d2d3", bg="#2f3640", font=("Arial", 22, "bold")).pack()
        tk.Label(header, text=f"Operario actual: {self.nombre_operario}", fg="white", bg="#2f3640", font=("Arial", 10)).pack()

        # Contenedor de Formulario
        f_main = tk.LabelFrame(self.ventana, text=" Datos de Entrada ", fg="white", bg="#2f3640", font=("Arial", 11, "bold"), padx=20, pady=20)
        f_main.pack(pady=10, padx=30, fill="x")

        # Fila 1
        tk.Label(f_main, text="Código Producto:", fg="white", bg="#2f3640").grid(row=0, column=0, sticky="w")
        self.cb_prod = ttk.Combobox(f_main, values=["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"], state="readonly", **estilo)
        self.cb_prod.current(0)
        self.cb_prod.grid(row=1, column=0, padx=10, pady=5)

        tk.Label(f_main, text="Material / Mezcla:", fg="white", bg="#2f3640").grid(row=0, column=1, sticky="w")
        self.ent_mat = tk.Entry(f_main, **estilo)
        self.ent_mat.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(f_main, text="N° Parrilla:", fg="white", bg="#2f3640").grid(row=0, column=2, sticky="w")
        self.cb_parr = ttk.Combobox(f_main, values=[f"P-{i:02d}" for i in range(1, 21)], state="readonly", **estilo)
        self.cb_parr.grid(row=1, column=2, padx=10, pady=5)

        # Fila 2
        tk.Label(f_main, text="Cantidad (Unidades):", fg="white", bg="#2f3640").grid(row=2, column=0, sticky="w", pady=(10,0))
        self.ent_uni = tk.Entry(f_main, **estilo)
        self.ent_uni.grid(row=3, column=0, padx=10, pady=5)

        tk.Label(f_main, text="Prensa Utilizada:", fg="white", bg="#2f3640").grid(row=2, column=1, sticky="w", pady=(10,0))
        self.cb_prensa = ttk.Combobox(f_main, values=["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"], state="readonly", **estilo)
        self.cb_prensa.current(0)
        self.cb_prensa.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(f_main, text="Fecha (DD/MM/YYYY):", fg="white", bg="#2f3640").grid(row=2, column=2, sticky="w", pady=(10,0))
        self.ent_fec_reg = tk.Entry(f_main, **estilo)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=3, column=2, padx=10, pady=5)

        # Botón de Acción
        self.btn_guardar = tk.Button(self.ventana, text="💾 REGISTRAR Y SUBIR A DRIVE", bg="#10ac84", fg="white", font=("Arial", 14, "bold"), 
                                     padx=20, pady=10, command=self.registrar_datos, cursor="hand2")
        self.btn_guardar.pack(pady=20)

        # Tabla de Visualización
        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cod", "Fecha", "Op", "Parrilla", "Cant", "Mat", "Prensa"), show="headings")
        cabeceras = [("ID", 50), ("Cod", 100), ("Fecha", 120), ("Op", 150), ("Parrilla", 100), ("Cant", 80), ("Mat", 120), ("Prensa", 120)]
        for col, ancho in cabeceras:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=30, pady=10)

    def cargar_datos_tabla(self):
        """Refresca la tabla con los datos de SQLite"""
        for i in self.tabla.get_children(): self.tabla.delete(i)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC LIMIT 15")
                for fila in cur.fetchall():
                    self.tabla.insert("", "end", values=fila)
        except: pass

    def limpiar_formulario(self):
        self.ent_mat.delete(0, tk.END)
        self.ent_uni.delete(0, tk.END)
        self.cb_prod.current(0)
        self.cb_parr.set('')

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Oculta la ventana principal de root
    app = RegistroCopelas(root, "JOA EMANUEL") # Nombre del operario de prueba
    root.mainloop()
