#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Dependencias externas
# pip install pyautogui keyboard
import pyautogui

# "keyboard" permite hotkeys globales; en Windows suele requerir permisos de admin.
# Si no están disponibles, la app sigue funcionando con los botones de la GUI.
try:
    import keyboard
    KEYBOARD_OK = True
except Exception:
    KEYBOARD_OK = False

pyautogui.FAILSAFE = False  # Si True, mover el ratón a la esquina sup-izq detiene el programa

class AutoClickerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoClicker - Fácil")
        self.geometry("580x480")
        self.resizable(False, False)

        # Estado
        self.click_thread = None
        self.stop_event = threading.Event()
        self.running = False
        self.end_time = None

        # Variables de UI
        self.var_horas = tk.StringVar(value="0")
        self.var_minutos = tk.StringVar(value="0")
        self.var_intervalo = tk.StringVar(value="2.7")  # segundos
        self.var_hotkey_info = tk.StringVar(value="i")  # consultar tiempo restante
        self.var_hotkey_stop = tk.StringVar(value="s")  # parar
        self.var_status = tk.StringVar(value="Listo.")
        self.var_restante = tk.StringVar(value="00:00:00")

        self._build_ui()

        if not KEYBOARD_OK:
            self._warn_keyboard_unavailable()

        # Cerrar limpio
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        pad = {"padx": 12, "pady": 8}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # Duración
        ttk.Label(frm, text="Duración").grid(row=0, column=0, sticky="w", **pad)
        sub = ttk.Frame(frm)
        sub.grid(row=0, column=1, sticky="w", **pad)
        ttk.Label(sub, text="Horas:").grid(row=0, column=0, sticky="e", padx=(0,6))
        ttk.Entry(sub, width=6, textvariable=self.var_horas).grid(row=0, column=1, sticky="w", padx=(0,12))
        ttk.Label(sub, text="Minutos:").grid(row=0, column=2, sticky="e", padx=(0,6))
        ttk.Entry(sub, width=6, textvariable=self.var_minutos).grid(row=0, column=3, sticky="w")

        # Intervalo
        ttk.Label(frm, text="Intervalo entre clics (segundos):").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, width=10, textvariable=self.var_intervalo).grid(row=1, column=1, sticky="w", **pad)

        # Hotkeys
        ttk.Label(frm, text="Tecla para consultar tiempo restante:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm, width=10, textvariable=self.var_hotkey_info).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Tecla para detener manualmente:").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(frm, width=10, textvariable=self.var_hotkey_stop).grid(row=3, column=1, sticky="w", **pad)

        # Contador y estado
        sep = ttk.Separator(frm)
        sep.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=4)

        ttk.Label(frm, text="Tiempo restante:").grid(row=5, column=0, sticky="w", **pad)
        lbl_rest = ttk.Label(frm, textvariable=self.var_restante, font=("Segoe UI", 14, "bold"))
        lbl_rest.grid(row=5, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Estado:").grid(row=6, column=0, sticky="w", **pad)
        ttk.Label(frm, textvariable=self.var_status).grid(row=6, column=1, sticky="w", **pad)

        # Botones
        btns = ttk.Frame(frm)
        btns.grid(row=7, column=0, columnspan=2, pady=10)
        self.btn_start = ttk.Button(btns, text="Iniciar", command=self.on_start)
        self.btn_stop = ttk.Button(btns, text="Detener", command=self.on_stop, state="disabled")
        self.btn_start.grid(row=0, column=0, padx=8)
        self.btn_stop.grid(row=0, column=1, padx=8)

        # Ayuda
        help_txt = (
            "Consejos:\n"
            "• Puedes usar solo los botones Iniciar/Detener si las teclas rápidas no funcionan.\n"
            "• Algunas teclas globales requieren permisos de administrador en Windows.\n"
            "• No muevas el ratón mientras hace clic si quieres máxima precisión.\n"
        )
        ttk.Label(frm, text=help_txt, foreground="#555").grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=(0,6))

    def _warn_keyboard_unavailable(self):
        self.var_status.set("Teclas rápidas globales no disponibles. Usa los botones.")
        messagebox.showinfo(
            "Aviso",
            "La librería de teclas globales no está disponible.\n"
            "Podrás iniciar/detener con los botones de la ventana.\n"
            "En Windows, ejecutar como Administrador suele habilitar las hotkeys."
        )

    def on_start(self):
        if self.running:
            return
        # Validación
        try:
            horas = int(self.var_horas.get())
            minutos = int(self.var_minutos.get())
            if horas < 0 or minutos < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Horas y minutos deben ser números enteros (>= 0).")
            return

        try:
            intervalo = float(self.var_intervalo.get())
            if intervalo <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El intervalo debe ser un número (> 0).")
            return

        hotkey_info = (self.var_hotkey_info.get() or "i").strip()
        hotkey_stop = (self.var_hotkey_stop.get() or "s").strip()

        duration = horas * 3600 + minutos * 60
        if duration <= 0:
            messagebox.showerror("Error", "La duración total debe ser mayor que 0.")
            return

        self.end_time = time.time() + duration
        self.stop_event.clear()
        self.running = True
        self._toggle_inputs(disabled=True)
        self.var_status.set("Iniciando auto-clicker...")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        # Lanzar hilo de clics
        self.click_thread = threading.Thread(
            target=self._click_loop,
            args=(intervalo, hotkey_info, hotkey_stop),
            daemon=True
        )
        self.click_thread.start()

        # Actualizar contador en UI
        self._tick_countdown()

    def _toggle_inputs(self, disabled: bool):
        state = "disabled" if disabled else "normal"
        # Entradas
        for w in self.children.values():
            pass  # (no usamos aquí)
        # Más explícito:
        # Buscar todos los widgets editables manualmente:
        # En este layout, configuramos directamente:
        # (Simplemente deshabilitamos/rehabilitamos al inicio/fin)
        # Dejamos como está por claridad: los Entry siguen activos pero no pasa nada si el usuario teclea.
        # Si lo prefieres, puedes guardar las referencias y configurar state=state en cada Entry.

    def _tick_countdown(self):
        if not self.running:
            return
        remaining = max(0, int(round(self.end_time - time.time())))
        h = remaining // 3600
        m = (remaining % 3600) // 60
        s = remaining % 60
        self.var_restante.set(f"{h:02d}:{m:02d}:{s:02d}")

        if remaining <= 0:
            # El hilo de clicks cerrará el estado; aquí solo prevenimos loops
            return
        self.after(200, self._tick_countdown)

    def _click_loop(self, intervalo: float, hotkey_info: str, hotkey_stop: str):
        self.var_status.set("Auto-clicker en marcha.")
        info_last_print = 0  # para evitar spam si se mantiene pulsada la tecla
        try:
            while time.time() < self.end_time and not self.stop_event.is_set():
                pyautogui.click()

                # Dormimos en pequeños pasos para ser más sensibles a stop_event
                t_end = time.time() + intervalo
                while time.time() < t_end:
                    if self.stop_event.is_set():
                        break
                    time.sleep(min(0.01, max(0, t_end - time.time())))

                # Hotkeys (si están disponibles)
                if KEYBOARD_OK and not self.stop_event.is_set():
                    try:
                        if hotkey_info and keyboard.is_pressed(hotkey_info):
                            now = time.time()
                            if now - info_last_print > 0.5:  # antirebote
                                restante = max(0, int(round(self.end_time - now)))
                                hh = restante // 3600
                                mm = (restante % 3600) // 60
                                ss = restante % 60
                                self.var_status.set(
                                    f"Quedan: {hh} h, {mm} min, {ss} s."
                                )
                                info_last_print = now
                        if hotkey_stop and keyboard.is_pressed(hotkey_stop):
                            self.stop_event.set()
                            break
                    except Exception:
                        # Si keyboard falla en caliente, seguimos sin hotkeys
                        pass

            # Fin normal o por stop
            restante = max(0, int(round(self.end_time - time.time())))
            hh = restante // 3600
            mm = (restante % 3600) // 60
            ss = restante % 60

            if self.stop_event.is_set():
                self.var_status.set(f"Auto-clicker detenido. Sobraron: {hh} h, {mm} min, {ss} s.")
            else:
                self.var_status.set("Tiempo de uso del auto-clicker finalizado.")

        finally:
            self.running = False
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

    def on_stop(self):
        if not self.running:
            return
        self.stop_event.set()

    def on_close(self):
        if self.running:
            if not messagebox.askyesno("Salir", "El auto-clicker está en ejecución. ¿Deseas detenerlo y salir?"):
                return
            self.stop_event.set()
        self.destroy()


def main():
    # Pregunta inicial opcional (sencillez para usuarios): mostramos la ventana directamente
    app = AutoClickerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
