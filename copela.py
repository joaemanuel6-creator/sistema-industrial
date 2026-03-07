import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests
import json

# --- CONFIGURACIÓN ---
URL_API_GOOGLE = "https://script.google.com/macros/s/AKfycbyMjLXjtHgApvfRYaybrbyoOox6wFhh-EtY4ny3lLmUHHiGUpPpwoY0WooHDHKN6Yyo/exec"

class RegistroCopelas:
    def __init__(self, root_parent, nombre_usuario):
        self.ventana = tk.Toplevel(root_parent)
        self.ventana.title("SISTEMA INDUSTRIAL - REGISTRO DE COPELAS")
        self.nombre_usuario = nombre_usuario
        
        self.directorio = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(self.directorio, "mi_base_de_datos.db")
        
        self.ventana.state('zoomed') 
        self.ventana.configure(bg="#1e272e")

        # --- ESTILOS ---
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        self.estilo.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=25)
        self.estilo.heading("Treeview", background="#34495e", foreground="white", font=("Arial", 10, "bold"))
        self.estilo.map("Treeview", background=[('selected', '#10ac84')])

        self.inicializar_db()
        self.crear_interfaz()
        self.verificar_permisos()
        self.cargar_datos_tabla()

    def inicializar_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS COPELA (
                N_Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Codigo TEXT, Fecha_Registro TEXT, Operador TEXT, 
                N_Parrilla TEXT, Cantidad INTEGER, Material TEXT, 
                Prensa TEXT, Estado TEXT)""")
            conn.commit()

    def verificar_permisos(self):
        """ Verifica en la tabla USUARIO si el rango es 1 """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT rango FROM USUARIO WHERE usuario = ?", (self.nombre_usuario,))
                res = cur.fetchone()
                if res and (str(res[0]) == "1"):
                    self.btn_modificar.config(state="normal")
                    self.btn_eliminar.config(state="normal")
        except:
            pass

    def enviar_a_nube(self, payload):
        try:
            # Forzamos el envío como JSON para Google Apps Script
            response = requests.post(URL_API_GOOGLE, json=payload, timeout=10)
            print(f"Respuesta Google: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error Nube: {e}")
            return False

    def registrar_datos(self):
        if not self.ent_mat.get() or self.ent_uni.get() == "":
            messagebox.showwarning("Atención", "Complete todos los campos")
            return
        
        try:
            datos = {
                "accion": "crear",
                "codigo": self.cb_prod.get(),
                "fecha": self.ent_fec_reg.get(),
                "operador": self.nombre_usuario,
                "n_parrilla": "P-01",
                "cantidad": int(self.ent_uni.get()),
                "material": self.ent_mat.get().upper(),
                "prensa": "PRENSA-1"
            }

            # 1. Guardar Local
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                            VALUES (?,?,?,?,?,?,?,?)""",
                            (datos["codigo"], datos["fecha"], datos["operador"], datos["n_parrilla"], 
                             datos["cantidad"], datos["material"], datos["prensa"], "SINCRONIZADO"))
                conn.commit()
            
            # 2. Guardar Nube
            self.enviar_a_nube(datos)
            
            # 3. Actualizar interfaz
            self.cargar_datos_tabla()
            self.ent_mat.delete(0, tk.END)
            self.ent_uni.delete(0, tk.END)
            messagebox.showinfo("Éxito", "Registro completado")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {e}")

    def crear_interfaz(self):
        # Configuramos la cuadrícula de la ventana principal
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(1, weight=1) # La tabla (fila 1) se expandirá

        # --- SECCIÓN 1: ENTRADA (ARRIBA) ---
        f_superior = tk.Frame(self.ventana, bg="#1e272e", pady=20)
        f_superior.grid(row=0, column=0, sticky="ew")

        tk.Label(f_superior, text="CÓDIGO:", fg="white", bg="#1e272e").grid(row=0, column=0, padx=5)
        self.cb_prod = ttk.Combobox(f_superior, values=["Cod-7C", "Cod-8C", "Cod-9C"], state="readonly", width=10)
        self.cb_prod.set("Cod-7C")
        self.cb_prod.grid(row=0, column=1, padx=5)

        tk.Label(f_superior, text="MATERIAL:", fg="white", bg="#1e272e").grid(row=0, column=2, padx=5)
        self.ent_mat = tk.Entry(f_superior, bg="#2c3e50", fg="white", width=15)
        self.ent_mat.grid(row=0, column=3, padx=5)

        tk.Label(f_superior, text="CANT:", fg="white", bg="#1e272e").grid(row=0, column=4, padx=5)
        self.ent_uni = tk.Entry(f_superior, bg="#2c3e50", fg="white", width=8)
        self.ent_uni.grid(row=0, column=5, padx=5)

        tk.Label(f_superior, text="FECHA:", fg="white", bg="#1e272e").grid(row=0, column=6, padx=5)
        self.ent_fec_reg = tk.Entry(f_superior, bg="#2c3e50", fg="white", width=12)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=0, column=7, padx=5)

        tk.Button(f_superior, text="GUARDAR", bg="#10ac84", fg="white", width=12, command=self.registrar_datos).grid(row=0, column=8, padx=15)

        # --- SECCIÓN 2: TABLA (CENTRO) ---
        f_tabla = tk.Frame(self.ventana, bg="#1e272e")
        f_tabla.grid(row=1, column=0, sticky="nsew", padx=20)
        
        f_tabla.columnconfigure(0, weight=1)
        f_tabla.rowconfigure(0, weight=1)

        columnas = ("ID", "COD", "FECHA", "OPERADOR", "PARR", "CANT", "MAT", "PRENSA", "ESTADO")
        self.tabla = ttk.Treeview(f_tabla, columns=columnas, show="headings")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- SECCIÓN 3: BOTONES ADMIN (ABAJO) ---
        f_inferior = tk.Frame(self.ventana, bg="#1e272e", pady=20)
        f_inferior.grid(row=2, column=0, sticky="ew")

        self.btn_modificar = tk.Button(f_inferior, text="🔧 MODIFICAR", bg="#f39c12", fg="white", width=20, state="disabled")
        self.btn_modificar.grid(row=0, column=0, padx=20)

        self.btn_eliminar = tk.Button(f_inferior, text="🗑️ ELIMINAR", bg="#e74c3c", fg="white", width=20, state="disabled")
        self.btn_eliminar.grid(row=0, column=1, padx=20)

    def cargar_datos_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM COPELA ORDER BY N_Codigo DESC")
                for fila in cur.fetchall():
                    self.tabla.insert("", "end", values=fila)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    # Cambia "MANUEL" por el usuario del login
    app = RegistroCopelas(root, "MANUEL") 
    root.mainloop()
