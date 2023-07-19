import tkinter as tk
from tkinter import ttk
import serial
import time
from serial.tools import list_ports
from tkinter import messagebox
import threading

# Funciones para la comunicación con Arduino
def conectar_arduino():
    global ser
    port = combo_ports.get()
    baud_rate = int(combo_baud.get())

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        boton_conectar.config(state=tk.DISABLED)
        boton_desconectar.config(state=tk.NORMAL)
        combo_ports.config(state=tk.DISABLED)
        combo_baud.config(state=tk.DISABLED)
        entrada_voltaje.config(state=tk.NORMAL)
        boton_set_voltaje.config(state=tk.NORMAL)
        boton_reset_voltaje.config(state=tk.NORMAL)
        mostrar_mensaje("Conectado a Arduino en el puerto {} con {} baudios.".format(port, baud_rate))
        recibir_thread = threading.Thread(target=recibir_datos)
        recibir_thread.start()
    except serial.SerialException:
        messagebox.showerror("Error", "No se pudo conectar a Arduino. Verifica la conexión y los puertos disponibles.")

def desconectar_arduino():
    global ser
    if ser.is_open:
        ser.close()
    boton_conectar.config(state=tk.NORMAL)
    boton_desconectar.config(state=tk.DISABLED)
    combo_ports.config(state=tk.NORMAL)
    combo_baud.config(state=tk.NORMAL)
    entrada_voltaje.config(state=tk.DISABLED)
    boton_set_voltaje.config(state=tk.DISABLED)
    boton_reset_voltaje.config(state=tk.DISABLED)
    mostrar_mensaje("Desconectado de Arduino.")

def setear_voltaje():
    global adu_anterior
    try:
        voltaje = float(entrada_voltaje.get())
        if voltaje < 0 or voltaje > 3:
            messagebox.showerror("Error", "El voltaje debe estar entre 0 y 3 V.")
            return

        adu_actual = round((voltaje + 0.0007) / 0.01235)

        if adu_actual > adu_anterior:
            diferencia = adu_actual - adu_anterior
            for _ in range(diferencia):
                ser.write(b'1')
                time.sleep(0.2)
        elif adu_actual < adu_anterior:
            diferencia = adu_anterior - adu_actual
            for _ in range(diferencia):
                ser.write(b'2')
                time.sleep(0.2)

        adu_anterior = adu_actual
        mostrar_mensaje("Voltaje seteado correctamente.")
    except ValueError:
        messagebox.showerror("Error", "Ingresa un valor numérico válido para el voltaje.")

def resetar_voltaje():
    ser.write(b'3')
    global adu_anterior
    adu_anterior = 0
    mostrar_mensaje("Voltaje reseteado a cero.")

def mostrar_mensaje(mensaje):
    texto_mensajes.config(state=tk.NORMAL)
   # texto_mensajes.delete("1.0", tk.END)  # Borramos el contenido anterior
    texto_mensajes.insert(tk.END, mensaje + "\n")  # Agregamos el último mensaje
    texto_mensajes.config(state=tk.DISABLED)
    texto_mensajes.see(tk.END) 

# Función para obtener la lista de puertos conectados
def obtener_puertos_conectados():
    puertos = [str(p.device) for p in list_ports.comports()]
    return puertos

# Función para actualizar la lista de puertos disponibles en el Combobox
def actualizar_lista_puertos():
    combo_ports["values"] = obtener_puertos_conectados()
    if combo_ports["values"]:
        combo_ports.set("Selecciona un puerto")
    else:
        combo_ports.set("")

# Función para recibir datos en tiempo real
def recibir_datos():
    global ser
    global adu_anterior
    while ser and ser.is_open:
        if ser.in_waiting > 0:
            data = ser.readline().decode("utf-8")
            texto_datos_recibidos.delete("1.0", tk.END)  # Borramos el contenido anterior
            texto_datos_recibidos.insert(tk.END, data.strip())  # Agregamos el último valor recibido
            texto_datos_recibidos.see(tk.END)  # Autoscroll para visualizar el último dato
            ventana.update_idletasks()
            if data == 'Se ha reseteado el sistema\r\n':
                adu_anterior = 0

#def verificar_conexion():
#    global ser
#    if ser and not ser.is_open:
#        mostrar_mensaje("¡Se perdió la conexión con el puerto!")
#        boton_desconectar.invoke()  # Simulamos una desconexión
#    ventana.after(1000, verificar_conexion)  # Verificar cada 1 segundo


# Configuración de la interfaz gráfica
ventana = tk.Tk()
ventana.title("CONTROL FUENTE MONOCROMADOR")
ventana.geometry("1000x600")  # Tamaño fijo de la interfaz (ancho x alto)


frame_conexion = tk.Frame(ventana)
frame_conexion.pack(padx=10, pady=10)

label_ports = tk.Label(frame_conexion, text="Puerto:")
label_ports.pack(side=tk.LEFT)
combo_ports = ttk.Combobox(frame_conexion)
combo_ports.pack(side=tk.LEFT)
combo_ports.set("Selecciona un puerto")

boton_actualizar_puertos = tk.Button(frame_conexion, text="Actualizar puertos", command=actualizar_lista_puertos)
boton_actualizar_puertos.pack(side=tk.LEFT)

label_baud = tk.Label(frame_conexion, text="Baud Rate:")
label_baud.pack(side=tk.LEFT)
bauds_disponibles = ["9600", "115200", "57600"]  # Puedes añadir más velocidades si lo deseas
combo_baud = ttk.Combobox(frame_conexion, values=bauds_disponibles)
combo_baud.pack(side=tk.LEFT)
combo_baud.set("Selecciona la velocidad")

boton_conectar = tk.Button(frame_conexion, text="Conectar", command=conectar_arduino)
boton_conectar.pack(side=tk.LEFT)
boton_desconectar = tk.Button(frame_conexion, text="Desconectar", command=desconectar_arduino, state=tk.DISABLED)
boton_desconectar.pack(side=tk.LEFT)

frame_voltaje = tk.Frame(ventana)
frame_voltaje.pack(padx=10, pady=10)

label_voltaje = tk.Label(frame_voltaje, text="Voltaje (0-3V):")
label_voltaje.pack(side=tk.LEFT)
entrada_voltaje = tk.Entry(frame_voltaje, width=10, state=tk.DISABLED)
entrada_voltaje.pack(side=tk.LEFT)
boton_set_voltaje = tk.Button(frame_voltaje, text="Setear Voltaje", command=setear_voltaje, state=tk.DISABLED)
boton_set_voltaje.pack(side=tk.LEFT)
boton_reset_voltaje = tk.Button(frame_voltaje, text="Resetear Voltaje", command=resetar_voltaje, state=tk.DISABLED)
boton_reset_voltaje.pack(side=tk.LEFT)

frame_mensajes = tk.Frame(ventana)
frame_mensajes.pack(padx=10, pady=10)

texto_mensajes = tk.Text(frame_mensajes, width=50, height=10, state=tk.DISABLED)
texto_mensajes.pack()

frame_datos = tk.Frame(ventana)
frame_datos.pack(padx=10, pady=10)

texto_datos_recibidos = tk.Text(frame_datos, width=50, height=10)
texto_datos_recibidos.pack()

# Variables globales
ser = None
adu_anterior = 0

# Actualizar la lista de puertos disponibles al abrir la ventana
actualizar_lista_puertos()


ventana.mainloop()
