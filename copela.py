import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import requests

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

        self.inicializar_db()
        self.crear_interfaz()
        self.verificar_permisos()
        self.cargar_datos_tabla()

    def inicializar_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            # Tabla principal de producción
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
                # Ajustado a tabla USUARIO y columnas usuario/rango
                cur.execute("SELECT rango FROM USUARIO WHERE usuario = ?", (self.nombre_usuario,))
                res = cur.fetchone()
                if res and (str(res[0]) == "1"):
                    self.btn_modificar.config(state="normal")
                    self.btn_eliminar.config(state="normal")
        except Exception as e:
            print(f"Error permisos: {e}")

    def enviar_a_nube(self, payload):
        try:
            # Se usa un hilo o timeout corto para no congelar la interfaz
            requests.post(URL_API_GOOGLE, json=payload, timeout=10)
        except Exception as e:
            print(f"Error nube: {e}")

    def registrar_datos(self):
        if not self.ent_mat.get() or not self.ent_uni.get():
            messagebox.showwarning("Atención", "Complete Material y Unidades")
            return
        
        try:
            datos = {
                "accion": "crear",
                "codigo": self.cb_prod.get(),
                "fecha": self.ent_fec_reg.get(),
                "operador": self.nombre_usuario,
                "n_parrilla": self.cb_parr.get(),
                "cantidad": int(self.ent_uni.get()),
                "material": self.ent_mat.get().upper(),
                "prensa": self.cb_prensa.get()
            }

            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("""INSERT INTO COPELA 
                    (Codigo, Fecha_Registro, Operador, N_Parrilla, Cantidad, Material, Prensa, Estado) 
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (datos["codigo"], datos["fecha"], datos["operador"], datos["n_parrilla"], 
                     datos["cantidad"], datos["material"], datos["prensa"], "SINCRONIZADO"))
                conn.commit()
            
            self.enviar_a_nube(datos)
            self.cargar_datos_tabla()
            
            # Limpiar campos
            self.ent_mat.delete(0, tk.END)
            self.ent_uni.delete(0, tk.END)
            messagebox.showinfo("Éxito", "Registro guardado correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número")

    def abrir_ventana_modificar(self):
        selected = self.tabla.selection()
        if not selected: return
        val = self.tabla.item(selected)['values']
        
        edit_win = tk.Toplevel(self.ventana)
        edit_win.title("Modificar")
        edit_win.geometry("300x350")
        edit_win.configure(bg="#2c3e50")
        edit_win.grab_set()

        tk.Label(edit_win, text="EDITAR REGISTRO", fg="cyan", bg="#2c3e50", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(edit_win, text="Cantidad:", fg="white", bg="#2c3e50").pack()
        ent_c = tk.Entry(edit_win); ent_c.insert(0, val[5]); ent_c.pack(pady=5)
        
        tk.Label(edit_win, text="Material:", fg="white", bg="#2c3e50").pack()
        ent_m = tk.Entry(edit_win); ent_m.insert(0, val[6]); ent_m.pack(pady=5)

        def confirmar():
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("UPDATE COPELA SET Cantidad=?, Material=? WHERE N_Codigo=?", 
                            (ent_c.get(), ent_m.get().upper(), val[0]))
                conn.commit()
            
            self.enviar_a_nube({"accion": "modificar", "id_remoto": val[0], "cantidad": ent_c.get(), "material": ent_m.get().upper()})
            self.cargar_datos_tabla()
            edit_win.destroy()

        tk.Button(edit_win, text="ACTUALIZAR", bg="#27ae60", fg="white", command=confirmar).pack(pady=20)

    def eliminar_registro(self):
        selected = self.tabla.selection()
        if not selected: return
        
        if messagebox.askyesno("Eliminar", "¿Desea eliminar este registro?"):
            id_db = self.tabla.item(selected)['values'][0]
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM COPELA WHERE N_Codigo=?", (id_db,))
                conn.commit()
            
            self.enviar_a_nube({"accion": "eliminar", "id_remoto": id_db})
            self.cargar_datos_tabla()

    def crear_interfaz(self):
        # --- PANEL DE ENTRADA ---
        f_input = tk.LabelFrame(self.ventana, text=" DATOS DE PRODUCCIÓN ", fg="cyan", bg="#1e272e", font=("Arial", 10, "bold"))
        f_input.pack(pady=15, padx=20, fill="x")

        # Configuración de columnas para centrar
        for i in range(5): f_input.columnconfigure(i, weight=1)

        self.cb_prod = ttk.Combobox(f_input, values=["Cod-7C", "Cod-8C", "Cod-9C"], state="readonly", width=12)
        self.cb_prod.set("Cod-7C")
        self.cb_prod.grid(row=0, column=0, pady=10)

        self.ent_mat = tk.Entry(f_input, width=15); self.ent_mat.grid(row=0, column=1)
        self.ent_mat.insert(0, "MATERIAL") # Placeholder

        self.ent_uni = tk.Entry(f_input, width=10); self.ent_uni.grid(row=0, column=2)
        self.ent_uni.insert(0, "CANT") # Placeholder

        self.ent_fec_reg = tk.Entry(f_input, width=12)
        self.ent_fec_reg.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ent_fec_reg.grid(row=0, column=3)

        tk.Button(f_input, text=" GUARDAR ", bg="#10ac84", fg="white", width=15, command=self.registrar_datos).grid(row=0, column=4, padx=10)

        # Labels informativos para los Entry
        tk.Label(f_input, text="Código", bg="#1e272e", fg="gray").grid(row=1, column=0)
        tk.Label(f_input, text="Material", bg="#1e272e", fg="gray").grid(row=1, column=1)
        tk.Label(f_input, text="Cantidad", bg="#1e272e", fg="gray").grid(row=1, column=2)
        tk.Label(f_input, text="Fecha", bg="#1e272e", fg="gray").grid(row=1, column=3)

        # --- CONTENEDOR DE TABLA (LISTBOX PRO) ---
        f_tabla = tk.Frame(self.ventana, bg="#1e272e")
        f_tabla.pack(expand=True, fill="both", padx=20, pady=5)

        columnas = ("ID", "PRODUCTO", "FECHA", "OPERADOR", "PARRILLA", "CANT", "MAT", "PRENSA", "ESTADO")
        self.tabla = ttk.Treeview(f_tabla, columns=columnas, show="headings", selectmode="browse")
        
        # Scrollbar
        scrolly = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tabla.yview)
        scrollx = ttk.Scrollbar(f_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        self.tabla.pack(side="left", expand=True, fill="both")
        scrolly.pack(side="right", fill="y")
        scrollx.pack(side="bottom", fill="x")

        # --- BOTONES DE ACCIÓN (ADMIN) ---
        f_btns = tk.Frame(self.ventana, bg="#1e272e")
        f_btns.pack(pady=15)

        self.btn_modificar = tk.Button(f_btns, text="🔧 MODIFICAR", bg="#f39c12", fg="white", width=20, state="disabled", command=self.abrir_ventana_modificar)
        self.btn_modificar.grid(row=0, column=0, padx=10)

        self.btn_eliminar = tk.Button(f_btns, text="🗑️ ELIMINAR", bg="#e74c3c", fg="white", width=20, state="disabled", command=self.eliminar_registro)
        self.btn_eliminar.grid(row=0, column=1, padx=10)

        # Extras ocultos pero necesarios
        self.cb_parr = ttk.Combobox(values=["P-01"]); self.cb_parr.set("P-01")
        self.cb_prensa = ttk.Combobox(values=["PRENSA-1"]); self.cb_prensa.set("PRENSA-1")

    def cargar_datos_tabla(self):
        """ Limpia y recarga todos los registros de la DB local """
        for i in self.tabla.get_children():
            self.tabla.delete(i)
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
    # Cambia "MANUEL" por el usuario del login para probar el rango
    app = RegistroCopelas(root, "MANUEL") 
    root.mainloop()
