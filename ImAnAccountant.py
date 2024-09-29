import customtkinter as ctk
import pandas as pd
from collections import Counter
from tkinter import filedialog, messagebox

class ContadorCodigoBarras:
    def __init__(self):
        self.conteo = Counter()
        self.productos_conocidos = {}
        self.productos_nuevos = {}
        self.codebar_to_id = {}
        
        self.root = ctk.CTk()
        self.root.title("Contador de Códigos de Barras")
        self.root.geometry("500x500")
        
        self.boton_cargar_db = ctk.CTkButton(self.root, text="Cargar Base de Datos", command=self.cargar_base_datos)
        self.boton_cargar_db.pack(pady=10)
        
        self.entrada = ctk.CTkEntry(self.root, width=200)
        self.entrada.pack(pady=20)
        self.entrada.bind("<Return>", self.procesar_codigo)
        
        self.boton_agregar = ctk.CTkButton(self.root, text="Agregar", command=self.procesar_codigo)
        self.boton_agregar.pack(pady=10)
        
        self.boton_descargar = ctk.CTkButton(self.root, text="Descargar Excel", command=self.descargar_excel)
        self.boton_descargar.pack(pady=10)
        
        self.boton_reiniciar = ctk.CTkButton(self.root, text="Reiniciar Conteo", command=self.reiniciar_conteo)
        self.boton_reiniciar.pack(pady=10)
        
        self.etiqueta = ctk.CTkLabel(self.root, text="")
        self.etiqueta.pack(pady=20)
        
        self.debug_info = ctk.CTkLabel(self.root, text="")
        self.debug_info.pack(pady=10)
    
    def cargar_base_datos(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if filename:
            try:
                df = pd.read_excel(filename)
                df['Codebar'] = df['Codebar'].astype(str)
                df['IDProducto'] = df['IDProducto'].astype(str)
                
                # Usar IDProducto como índice
                self.productos_conocidos = df.set_index('IDProducto').to_dict('index')
                
                # Crear un diccionario para mapear Codebar a IDProducto
                self.codebar_to_id = dict(zip(df['Codebar'], df['IDProducto']))
                
                messagebox.showinfo("Base de Datos Cargada", f"Se cargaron {len(self.productos_conocidos)} productos.")
                self.mostrar_debug_info(f"Productos cargados: {len(self.productos_conocidos)}")
            except Exception as e:
                messagebox.showerror("Error al cargar", f"Ocurrió un error al cargar la base de datos: {str(e)}")
                self.mostrar_debug_info(f"Error al cargar: {str(e)}")
    
    def procesar_codigo(self, event=None):
        codigo = self.entrada.get().strip()
        if codigo:
            codigo = str(codigo)
            self.conteo[codigo] += 1
            if codigo not in self.codebar_to_id and codigo not in self.productos_nuevos:
                self.solicitar_descripcion(codigo)
            self.entrada.delete(0, 'end')
            self.actualizar_etiqueta()
            self.mostrar_debug_info(f"Código procesado: {codigo}")
    
    def solicitar_descripcion(self, codigo):
        descripcion = ctk.CTkInputDialog(text=f"Ingrese descripción para el nuevo producto (Codebar: {codigo}):", title="Nuevo Producto").get_input()
        if descripcion:
            self.productos_nuevos[codigo] = {'Producto': descripcion}
        else:
            self.productos_nuevos[codigo] = {'Producto': "Sin descripción"}
    
    def actualizar_etiqueta(self):
        texto = "\n".join([f"{codigo}: {cantidad}" for codigo, cantidad in self.conteo.items()])
        self.etiqueta.configure(text=texto)
    
    def descargar_excel(self):
        if not self.conteo:
            messagebox.showwarning("Sin datos", "No hay datos para descargar. Realice un conteo primero.")
            return
        
        df_conteo = pd.DataFrame(list(self.conteo.items()), columns=['Codebar', 'Cantidad Contada'])
        df_conteo['Codebar'] = df_conteo['Codebar'].astype(str)
        
        # Crear un DataFrame con todos los productos (conocidos y nuevos)
        df_productos = pd.DataFrame.from_dict(self.productos_conocidos, orient='index')
        df_productos.reset_index(inplace=True)
        df_productos.rename(columns={'index': 'IDProducto'}, inplace=True)
        
        df_nuevos = pd.DataFrame.from_dict(self.productos_nuevos, orient='index')
        df_nuevos.reset_index(inplace=True)
        df_nuevos.rename(columns={'index': 'Codebar'}, inplace=True)
        df_nuevos['IDProducto'] = 'NUEVO_' + df_nuevos['Codebar']
        
        # Combinar los DataFrames
        df_final = pd.merge(df_conteo, df_productos, left_on='Codebar', right_on='Codebar', how='left')
        df_final = pd.merge(df_final, df_nuevos, on='Codebar', how='left', suffixes=('', '_nuevo'))
        
        df_final['Producto'] = df_final['Producto'].fillna(df_final['Producto_nuevo'])
        df_final['es_nuevo'] = df_final['IDProducto'].isnull()
        df_final['IDProducto'] = df_final['IDProducto'].fillna(df_final['IDProducto_nuevo'])
        
        columnas_requeridas = ['IDProducto', 'Codebar', 'Cantidad Contada', 'Producto', 'Cajas Stock Suc28', 'Costo', 'Troquel', 'es_nuevo']
        df_final = df_final.reindex(columns=columnas_requeridas)
        
        with pd.ExcelWriter("reporte_stock.xlsx") as writer:
            df_final.to_excel(writer, sheet_name='Reporte de Stock', index=False)
            df_final[df_final['es_nuevo']].to_excel(writer, sheet_name='Productos Nuevos', index=False)
        
        messagebox.showinfo("Excel Generado", "Se ha generado el archivo 'reporte_stock.xlsx' con el reporte completo.")
        self.mostrar_debug_info(f"Excel generado. Filas: {len(df_final)}")
    
    def reiniciar_conteo(self):
        if messagebox.askyesno("Confirmar Reinicio", "¿Estás seguro de que quieres reiniciar el conteo? Esto borrará todos los datos actuales."):
            self.conteo.clear()
            self.productos_nuevos.clear()
            self.actualizar_etiqueta()
            messagebox.showinfo("Conteo Reiniciado", "El conteo ha sido reiniciado. Puedes comenzar un nuevo conteo.")
            self.mostrar_debug_info("Conteo reiniciado")
    
    def mostrar_debug_info(self, info):
        self.debug_info.configure(text=info)
    
    def iniciar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ContadorCodigoBarras()
    app.iniciar()