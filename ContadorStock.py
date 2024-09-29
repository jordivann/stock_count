import customtkinter as ctk
import pandas as pd
from collections import Counter

class ContadorCodigoBarras:
    def __init__(self):
        self.conteo = Counter()
        
        self.root = ctk.CTk()
        self.root.title("Contador de Códigos de Barras")
        self.root.geometry("400x300")
        
        self.entrada = ctk.CTkEntry(self.root, width=200)
        self.entrada.pack(pady=20)
        self.entrada.bind("<Return>", self.agregar_codigo)  # Vincula la tecla Enter
        
        self.boton_agregar = ctk.CTkButton(self.root, text="Agregar", command=self.agregar_codigo)
        self.boton_agregar.pack(pady=10)
        
        self.boton_descargar = ctk.CTkButton(self.root, text="Descargar Excel", command=self.descargar_excel)
        self.boton_descargar.pack(pady=10)
        
        self.etiqueta = ctk.CTkLabel(self.root, text="")
        self.etiqueta.pack(pady=20)
        
    def agregar_codigo(self, event=None):
        codigo = self.entrada.get()
        if codigo:
            self.conteo[codigo] += 1
            self.entrada.delete(0, 'end')
            self.actualizar_etiqueta()
    
    def actualizar_etiqueta(self):
        texto = "\n".join([f"{codigo}: {cantidad}" for codigo, cantidad in self.conteo.items()])
        self.etiqueta.configure(text=texto)
    
    def descargar_excel(self):
        df = pd.DataFrame(list(self.conteo.items()), columns=['ean', 'stock real'])
        df.to_excel("conteo_codigos.xlsx", index=False)
        print("Excel descargado como 'conteo_codigos.xlsx'")
    
    def iniciar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ContadorCodigoBarras()
    app.iniciar()