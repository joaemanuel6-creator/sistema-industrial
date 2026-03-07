import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import json
import requests  # RECUERDA: pip install requests

# --- CONFIGURACIÓN DE TU NUEVA API DE GOOGLE ---
URL_API_GOOGLE = "https://script.google.com/macros/s/AKfycbx2-CDyiFjZ711oY7B5jCBdP_tJ5Vy2VruHYKhocCrUd0bFSdrWNJcEp-M6CgAwz8D8/exec"

class RegistroCopelas:
    def __init__(self, root_parent, nombre_operario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("SISTEMA INDUSTRIAL - REGISTRO DE COPELAS")
        self.nombre_operario = nombre_operario
        
        # Ruta de base de datos local
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#2c3e50")

        self.inicializar_db()
        self.crear_interfaz()
        self.cargar_datos_tabla()

    def inicializar_db(self):
        """Crea la tabla local si no existe"""
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
            print(f"Error DB Local: {e}")

    def enviar_a_google_drive(self, datos):
        """Envía el diccionario de datos al Apps Script de Google"""
        try:
            # Enviamos los datos como JSON
            response = requests.post(
                URL_API_GOOGLE, 
                data=json.dumps(datos),
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            # Imprimimos en consola para depuración
            print(f"Respuesta de Google: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error de conexión con Google: {e}")
            return False

    def registrar_datos(self):
        """Lógica de guardado local y sincronización con Drive"""
        # Validación de campos
        if not self.ent_mat.get() or not self.ent_uni.get() or not self.cb_prod.get():
            messagebox.showwarning("Atención", "Por favor llene todos los campos.")
            return

        fecha_proceso = self.ent_fec_reg.get().strip()
        if not fecha_proceso:
            fecha_proceso = datetime.now().strftime("%d/%m/%Y")

        # Preparar paquete para la API (9 columnas en total con N_Codigo y Estado)
        datos_para_api = {
            "codigo": self.cb_prod.get(),
            "fecha": fecha_proceso,
            "operador": self.nombre_operario,
            "n_parrilla": self.cb_parr.get(),
            "cantidad": self.ent_uni.get(),
            "material": self.ent_mat.get().upper(),
            "prensa": self.cb_prensa.get()
        }

        try:
            # 1. GUARDAR LOCAL (SQLite)
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                    VALUES (?,?,?,?,?,?,?,?)""", (
                        datos_para_api["codigo"], datos_para_api["fecha"], datos_para_api["operador"], 
                        datos_para_api["n_parrilla"], datos_para_api["cantidad"], 
                        datos_para_api["material"], datos_para_api["prensa"], "SINCRONIZADO"
                    ))
                conn.commit()

            # 2. ENVIAR A GOOGLE DRIVE
            exito_nube = self.enviar_a_google_drive(datos_para_api)

            if exito_nube:
                messagebox.showinfo("Éxito", f"✅ Registro exitoso para {self.nombre_operario}.\nSincronizado con Google Drive.")
            else:
                messagebox.showwarning("Sincronización", "⚠️ Guardado en PC, pero NO se reflejó en Google Drive.\nVerifique su internet o la configuración del Script.")

            self.limpiar_formulario()
            self.cargar_datos_tabla()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def crear_interfaz(self):
        estilo = {"width": 22, "font": ("Arial", 12)}
        
        # Título Principal
        header = tk.Frame(self.ventana, bg="#2c3e50")
        header.pack(fill="x", pady=20)
        tk.Label(header, text="📝 REGISTRO DE PRODUCCIÓN: COPELAS", fg="#00d2ff", bg="#2c3e50", font=("Arial", 22, "bold")).pack()

        # Contenedor de Formulario
        f_main = tk.LabelFrame(self.ventana, text=" Panel de Entrada ", fg="white", bg="#2c3e50", font=("Arial", 11, "bold"), padx=20, pady=20)
        f_main.pack(pady=10, padx=30, fill="x")

        # Fila 1
        tk.Label(f_main, text="Código Producto:", fg="white", bg="#2c3e50").grid(row=0, column=0, sticky="w")
        self.cb_prod = ttk.Combobox(f_main, values=["Cod-7C", "Cod-8C", "Cod-9C", "Cod-11C", "Cod-9R"], state="readonly", **estilo)
        self.cb_prod.grid(row=1, column=0, padx=10, pady=5)

        tk.Label(f_main, text="Material / Mezcla:", fg="white", bg="#2c3e50").grid(row=0, column=1, sticky="w")
        self.ent_mat = tk.Entry(f_main, **estilo)
        self.ent_mat.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(f_main, text="N° Parrilla:", fg="white", bg="#2c3e50").grid(row=0, column=2, sticky="w")
        self.cb_parr = ttk.Combobox(f_main, values=[f"P-{i:02d}" for i in range(1, 21)], state="readonly", **estilo)
        self.cb_parr.grid(row=1, column=2, padx=10, pady=5)

        # Fila 2
        tk.Label(f_main, text="Cantidad:", fg="white", bg="#2c3e50").grid(row=2, column=0, sticky="w", pady=(10,0))
        self.ent_uni = tk.Entry(f_main, **estilo)
        self.ent_uni.grid(row=3, column=0, padx=10, pady=5)

        tk.Label(f_main, text="Prensa:", fg="white", bg="#2c3e50").grid(row=2, column=1, sticky="w", pady=(10,0))
        self.cb_prensa = ttk.Combobox(f_main, values=["Prensa 01", "Prensa 02", "Prensa 03", "Prensa 04", "Prensa 05"], state="readonly", **estilo)
        self.cb_prensa.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(f_main, text="Fecha (DD/MM/YYYY):", fg="white", bg="#2c3e50").grid(row=2, column=2, sticky="w", pady=(10,0))
        self.ent_fec_reg = tk.Entry(f_main, **estilo)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=3, column=2, padx=10, pady=5)

        # Botón Guardar
        self.btn_guardar = tk.Button(self.ventana, text="💾 REGISTRAR Y GUARDAR EN DRIVE", bg="#27ae60", fg="white", font=("Arial", 14, "bold"), 
                                     padx=20, pady=10, command=self.registrar_datos, cursor="hand2")
        self.btn_guardar.pack(pady=20)

        # Tabla de Visualización (Muestra los últimos registros locales)
        self.tabla = ttk.Treeview(self.ventana, columns=("ID", "Cod", "Fecha", "Op", "Parrilla", "Cant", "Mat", "Prensa", "Est"), show="headings")
        cabeceras = [("ID", 40), ("Cod", 80), ("Fecha", 100), ("Op", 120), ("Parrilla", 80), ("Cant", 60), ("Mat", 100), ("Prensa", 100), ("Est", 100)]
        for col, ancho in cabeceras:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=30, pady=10)

    def cargar_datos_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC LIMIT 10")
                for fila in cur.fetchall():
                    self.tabla.insert("", "end", values=fila)
        except: pass

    def limpiar_formulario(self):
        self.ent_mat.delete(0, tk.END)
        self.ent_uni.delete(0, tk.END)
        self.cb_prod.set('')
        self.cb_parr.set('')

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    app = RegistroCopelas(root, "MANUEL") # Nombre del operario
    root.mainloop()
