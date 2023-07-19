import tkinter as tk
import serial.tools.list_ports
import serial
import time

class MotorControlGUI:
    def __init__(self, root):
        self.root = root
        self.serial_port = None
        self.posicion_actual = 0
        
        # Variables de control
        self.mm_desplazamiento = tk.StringVar()
        self.velocidad_serial = tk.StringVar()
        self.puerto_serial = tk.StringVar()
        
        # Configuración de la ventana
        self.root.title("Control de Motor")
        
        # Text para mostrar mensajes
        self.text_mensajes = tk.Text(self.root, wrap=tk.WORD, width=50, height=10)
        self.text_mensajes.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        
        # Etiqueta y entrada para los milímetros de desplazamiento
        label_desplazamiento = tk.Label(self.root, text="Desplazamiento (mm):")
        label_desplazamiento.grid(row=1, column=0, padx=10, pady=5)
        
        entry_desplazamiento = tk.Entry(self.root, textvariable=self.mm_desplazamiento)
        entry_desplazamiento.grid(row=1, column=1, padx=10, pady=5)
        
        # Etiqueta para mostrar la posición actual
        self.label_posicion = tk.Label(self.root, text="Posición actual: 0 mm")
        self.label_posicion.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        
        # Etiqueta y lista desplegable para seleccionar la velocidad del puerto serial
        label_velocidad = tk.Label(self.root, text="Velocidad del Puerto Serial:")
        label_velocidad.grid(row=3, column=0, padx=10, pady=5)
        
        lista_velocidad = tk.OptionMenu(self.root, self.velocidad_serial, *serial.Serial.BAUDRATES)
        lista_velocidad.grid(row=3, column=1, padx=10, pady=5)
        
        # Etiqueta y pestaña para mostrar los puertos seriales disponibles
        label_puerto = tk.Label(self.root, text="Puerto Serial:")
        label_puerto.grid(row=4, column=0, padx=10, pady=5)
        
        self.lista_puertos = tk.Listbox(self.root)
        self.lista_puertos.grid(row=4, column=1, padx=10, pady=5)
        
        # Botón de Conexión y Desconexión
        self.boton_conexion = tk.Button(self.root, text="Conectar", command=self.conectar_desconectar)
        self.boton_conexion.grid(row=4, column=2, columnspan=2, padx=10, pady=5)
        
        # Botón para establecer el origen
        boton_origen = tk.Button(self.root, text="Establecer Origen", command=self.establecer_origen)
        boton_origen.grid(row=2, column=2, columnspan=2, padx=10, pady=5)
        
        # Botón para iniciar el desplazamiento
        boton_desplazar = tk.Button(self.root, text="Iniciar Desplazamiento", command=self.iniciar_desplazamiento)
        boton_desplazar.grid(row=1, column=2, columnspan=2, padx=10, pady=5)
        
        # Botón para actualizar los puertos seriales disponibles
        boton_actualizar_puertos = tk.Button(self.root, text="Actualizar Puertos", command=self.actualizar_puertos_disponibles)
        boton_actualizar_puertos.grid(row=8, column=2, columnspan=2, padx=10, pady=5)
        
        # Obtener los puertos seriales disponibles y mostrarlos en la lista
        self.actualizar_puertos_disponibles()
        
    def actualizar_puertos_disponibles(self):
        self.lista_puertos.delete(0, tk.END)
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        for puerto in puertos:
            self.lista_puertos.insert(tk.END, puerto)
        
    def establecer_origen(self):
        self.posicion_actual = 0
        self.actualizar_posicion()
        
    def iniciar_desplazamiento(self):
        mm = int(self.mm_desplazamiento.get())
        comando = 1 if mm > 0 else 2
        cantidad = abs(mm)
        
        if self.serial_port is None:
            self.text_mensajes.insert(tk.END, "No se ha establecido conexión con el puerto serial.\n")
            return
        
        try:
            for x in range(cantidad):
                self.serial_port.write(str(comando).encode())
                self.actualizar_posicion(comando)
                #self.root.update_idletasks()  # Actualizar la interfaz gráfica
                time.sleep(0.01)
                x = x+1

            self.root.update_idletasks()  # Actualizar la interfaz gráfica
        except serial.SerialException:
            self.text_mensajes.insert(tk.END, "Error al enviar el comando por el puerto serial.\n")
            return
        
        self.text_mensajes.insert(tk.END, "Desplazamiento completado.\n")
    
    def conectar_desconectar(self):
        if self.serial_port is None:
            try:
                puerto_seleccionado = self.lista_puertos.get(tk.ACTIVE)
                velocidad = int(self.velocidad_serial.get())
                self.serial_port = serial.Serial(puerto_seleccionado, velocidad)
                self.boton_conexion.config(text="Desconectar")
                self.text_mensajes.insert(tk.END, f"Conexión establecida en el puerto {puerto_seleccionado}.\n")
            except serial.SerialException:
                self.text_mensajes.insert(tk.END, "Error al abrir el puerto serial.\n")
        else:
            self.serial_port.close()
            self.serial_port = None
            self.boton_conexion.config(text="Conectar")
            self.text_mensajes.insert(tk.END, "Conexión cerrada.\n")
        
    def actualizar_posicion(self, comando=None):
        if comando == 1:
            self.posicion_actual += 1
        elif comando == 2:
            self.posicion_actual -= 1
        
        self.label_posicion.config(text=f"Posición actual: {self.posicion_actual} mm")

if __name__ == "__main__":
    root = tk.Tk()
    gui = MotorControlGUI(root)
    root.mainloop()

