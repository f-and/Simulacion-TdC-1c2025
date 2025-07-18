import math
import matplotlib.pyplot as plt
import tkinter as tk
import random
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Constantes globales
constante_gases = 8.314 # J/K*mol
temperatura_deseada = 523.15 # K
volumen_tanque = 10.0 # m^3
masa_molar_agua = 18.0 # g/mol
presion_minima = 0.2e6 # Pa
presion_maxima = 1.5e6 # Pa
carbon_minimo = 0.1 # kg/seg
carbon_maximo = 0.8 # kg/seg
poder_calorifico_promedio = 29e6 # J/kg
temperatura_agua = 20 # C
energia_requerida = 2900 # J/g

# Variables configurables
vapor_inicial = random.randint(8200, 62000) # g
valor_referencia = 1.2e6 # Pa
vapor_utilizado_predeterminado = 2500 # g/s
vapor_utilizado = 2500 # g/s
tiempo_maximo_espera = 25 # s

# Variables globales
error_integral = 0
vapor_almacenado = vapor_inicial # g
presion_medida = 0 # Pa
ultimas_senales_error = [0, 0, 0, 0, 0] # Pa
caudal_carbon = carbon_maximo
tiempo = 0
tiempo_cambio = 0
tiempo_anterior = 0
simulacion_pausada = False
popup_mostrado = False

tiempo_transcurrido = []
vapor_acumulado_data = []
caudal_carbon_data = []
error_data = []

vapor_almacenado_historico = []

def manometro_digital(entrada):
  constante_transferencia = ((constante_gases / masa_molar_agua) * temperatura_deseada) / volumen_tanque
  return entrada * constante_transferencia # Pa

def senal_error(presion_medida):
  return math.floor(valor_referencia - presion_medida) # Pa

def controlador(error):
    global caudal_carbon, error_integral

    Kp = 1e-6
    Ki = 1e-8 

    error_integral += error

    caudal_carbon = Kp * error + Ki * error_integral

    # Clampeo
    if caudal_carbon > carbon_maximo:
        caudal_carbon = carbon_maximo
        error_integral = 0  # Anti-windup
    elif caudal_carbon < carbon_minimo:
        caudal_carbon = carbon_minimo
        error_integral = 0

    franja_20 = valor_referencia - (presion_maxima * 0.2) # 900000
    franja_90 = valor_referencia - (presion_maxima * 0.9) # -150000

    if error > franja_20:
      caudal_carbon = carbon_maximo
    elif error < franja_90:
      caudal_carbon = carbon_minimo

def caldera(caudal):
  return poder_calorifico_promedio / energia_requerida * caudal # caudal * 10000

def salida_turbinas(vapor_generado): 
  return vapor_generado - vapor_utilizado

def actualizar_vapor_consumido(nuevo_valor):
  global vapor_utilizado
  vapor_utilizado = float(nuevo_valor)

def loop(entrada):
  presion_medida = manometro_digital(entrada)
  #print(presion_medida)
  global error_data
  s_error = senal_error(presion_medida)
  error_data.append(s_error/1e6)
  ultimas_senales_error.pop(0)
  ultimas_senales_error.append(s_error)
  controlador(s_error)
  caudal = caudal_carbon
  #print(caudal)
  vapor_generado = caldera(caudal)
  vapor_a_almacenar = salida_turbinas(vapor_generado)
  entrada += vapor_a_almacenar
  #print(entrada)
  global tiempo
  tiempo += 1
  return entrada

# Activar modo interactivo
#plt.ion()
fig, ax = plt.subplots(3, 1)
line1, = ax[0].plot([], [], color='blue')
line2, = ax[1].plot([], [], color='red')
line3, = ax[2].plot([], [], color='green')

# Configurar ejes
#ax.set_xlim(0, 50)
#ax.set_ylim(0, 10)
ax[0].set_xlabel("t [seg]")
ax[1].set_xlabel("t [seg]")
ax[2].set_xlabel("t [seg]")
ax[0].set_ylabel("vapor en tanque [kg]")
ax[1].set_ylabel("caudal [kg/s]")
ax[2].set_ylabel("error [MPa]")

def draw(t, entrada):
    tiempo_transcurrido.append(t)
    vapor_acumulado_data.append(entrada/1000)  # Punto aleatorio
    caudal_carbon_data.append(caudal_carbon)
    # Actualizar datos del gráfico
    #line.set_xdata(tiempo_transcurrido)
    #line.set_ydata(vapor_acumulado_data)
    line1.set_data(tiempo_transcurrido, vapor_acumulado_data)
    line2.set_data(tiempo_transcurrido, caudal_carbon_data)
    line3.set_data(tiempo_transcurrido, error_data)

    # Ajustar límites si hace falta
    ax[0].relim()
    ax[1].relim()
    ax[2].relim()
    ax[0].autoscale_view()
    ax[1].autoscale_view()
    ax[2].autoscale_view()

    # Redibujar
    
    canvas.draw()
    #plt.draw()
    #plt.pause(0.01)  # Pausa entre frames
  
ventana = tk.Tk()
ventana.title("Controlador de Planta a Carbón")
#ventana.geometry("300x200")

# Incrustar la figura dentro de la ventana de tkinter
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Controles
controles = tk.Frame(ventana)
controles.pack(side=tk.BOTTOM, fill=tk.X)

etiqueta = tk.Label(controles, text="Cantidad de Vapor Utilizado [kg/s]")
etiqueta.pack(side=tk.LEFT)
slider = ttk.Scale(controles, from_=vapor_utilizado_predeterminado, to=7500, value=vapor_utilizado_predeterminado, orient=tk.HORIZONTAL, command=actualizar_vapor_consumido)
slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)

def reiniciar():
  global vapor_almacenado, vapor_utilizado, tiempo, tiempo_cambio, caudal_carbon, presion_medida, tiempo_transcurrido, vapor_acumulado_data, caudal_carbon_data, ax
  global error_data, error_integral, simulacion_pausada
  vapor_inicial = random.randint(8200, 62000)
  vapor_almacenado = vapor_inicial
  vapor_utilizado = vapor_utilizado_predeterminado
  tiempo = 0
  tiempo_cambio = 0
  presion_medida = 0
  error_integral = 0
  caudal_carbon = carbon_maximo
  tiempo_transcurrido = []
  vapor_acumulado_data = []
  caudal_carbon_data = []
  error_data = []
  
  simulacion_pausada = False
  boton_pausa.config(text="Pausar simulación")
  
  line1.set_data(tiempo_transcurrido, vapor_acumulado_data)
  line2.set_data(tiempo_transcurrido, caudal_carbon_data)
  line3.set_data(tiempo_transcurrido, error_data)

def perturbacion_impulso(vapor_nuevo):
   vapor_utilizado_viejo = vapor_utilizado
   actualizar_vapor_consumido(vapor_nuevo)
   ventana.after(200, lambda: actualizar_vapor_consumido(vapor_utilizado_viejo))

def toggle_pausa():
    global simulacion_pausada
    simulacion_pausada = not simulacion_pausada
    if simulacion_pausada:
        boton_pausa.config(text="Reanudar simulación")
    else:
        boton_pausa.config(text="Pausar simulación")

boton_pausa = ttk.Button(controles, text="Pausar simulación", command=toggle_pausa)
boton_pausa.pack(side=tk.RIGHT, padx=10)

boton = ttk.Button(controles, text="Reiniciar simulación", command=reiniciar)
boton.pack(side=tk.RIGHT, padx=10)
boton = ttk.Button(controles, text="Perturbación (consumo de emergencia)", 
                   command=lambda: perturbacion_impulso(20000))
boton.pack(side=tk.RIGHT, padx=10)
boton = ttk.Button(controles, text="Perturbación (perdida de turbina)", 
                   command=lambda: perturbacion_impulso(0))
boton.pack(side=tk.RIGHT, padx=10)

def loop_total():
    global vapor_almacenado
    global popup_mostrado, simulacion_pausada
    if vapor_almacenado * 24.164 > presion_maxima and not (popup_mostrado or simulacion_pausada):
        messagebox.showerror("¡Falla!", "Presión demasiado alta, el tanque explotó.")
        popup_mostrado = True
        simulacion_pausada = True
        boton_pausa.config(text="Reanudar simulación")
    elif vapor_almacenado * 24.164 < presion_minima and not (popup_mostrado or simulacion_pausada):
        messagebox.showerror("¡Falla!", "Presión demasiado baja, el tanque se llenó de aire.")
        popup_mostrado = True
        simulacion_pausada = True
        boton_pausa.config(text="Reanudar simulación")
    else:
        popup_mostrado = False
    if not simulacion_pausada:
        vapor_almacenado = loop(vapor_almacenado)
        draw(tiempo, vapor_almacenado)
    ventana.after(50, loop_total)

ventana.after(50,loop_total)
ventana.mainloop()