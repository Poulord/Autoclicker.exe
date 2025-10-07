import pyautogui
import keyboard
import time
import sys
#Simula clics del ratón en intervalos especificados durante un tiempo determinado.

minutos = 0 
horas = 0  

pyautogui.FAILSAFE = False #Si se mantiene este valor en True, mover el ratón a la esquina superior izquierda detendrá el programa.  

def Tiempo_de_Uso(horas, minutos): 
    while True:
        Respuesta = input("¡Hola! Bienvenido al auto-clicker. ¿Deseas usar el autoclicker deseas usar el auto-clicker? (Si/No) \n")
              
        if Respuesta.lower() == "si":
            break
        
        elif Respuesta.lower() == "no":
            print("¡Hasta luego!\n")
            sys.exit() 
        
        else:
            print("Por favor, responde con 'Si' o 'No'.\n")
            continue
        
    while True:    
        try:
            horas = int(input("\n¿Por cuántas horas deseas usar el auto-clicker?: "))
            
            print("\n¡Perfecto! Ahora dime por cuántos minutos deseas usar el auto-clicker.\n")
            
            minutos = int(input("Minutos: "))
            return horas * 3600, minutos * 60
        
        except ValueError:
            print("\nPor favor, introduce un número válido.")
            continue

# Actualiza las variables
horas, minutos = Tiempo_de_Uso(horas, minutos)


def formatear_tiempo(Tiempo_Restante):
    horas_final = Tiempo_Restante // 3600
    minutos_final = (Tiempo_Restante % 3600) // 60
    segundos_final = Tiempo_Restante % 60
    return horas_final, minutos_final, segundos_final


interval = 2.7 #Intervalo en segundos entre clicks 

duration = horas + minutos
    
def auto_clicker(interval, duration):

    end_time = time.time() + duration
    Letra_Tiempo_Restante = input("\n¿Que letra quieres usar para consultar las horas restantes del autoclicker?: \n")
    Letra_Stop = input("\n¿Que letra quieres usar para parar el autoclicker manualmente?: \n")
    print("Iniciando auto-clicker...")
    
    while time.time() < end_time:
        pyautogui.click()
        time.sleep(interval)

        if keyboard.is_pressed(Letra_Tiempo_Restante):
                    Tiempo_Restante = round(end_time - time.time()) 
                    horas, minutos, segundos = formatear_tiempo(Tiempo_Restante)
                    print(f"Has consultado las horas restantes del autocliker, Quedan:  {horas} horas, {minutos} minutos, {segundos} segundos.")
       
        if keyboard.is_pressed(Letra_Stop):
            Tiempo_Restante = round(end_time - time.time()) 
            horas, minutos, segundos = formatear_tiempo(Tiempo_Restante)
            print(f"Auto-clicker detenido por el usuario. Han sobrado:  {horas} horas, {minutos} minutos, {segundos} segundos.")
            break
        
        
    if time.time() >= end_time:
        print("Tiempo de uso del auto-clicker finalizado.")
            
auto_clicker(interval, duration)
