import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO

from adc_reader import init_spi, read_adc
from valve_control import setup_valves, control_valve
from sensor_tolva import setup_sensor, is_product_available
from oscillator_control import Oscillator
from config_loader import load_config, save_config
from manual_control import toggle_output, set_output

VALVE_PINS = [17, 27, 22, 10]
OSC_PINS = [5, 6, 13, 19]
TOLVA_SENSOR_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

setup_valves(VALVE_PINS)
setup_sensor(TOLVA_SENSOR_PIN)

for pin in OSC_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

spi = init_spi()
config = load_config()

oscillators = []
for i in range(4):
    ton = float(config['oscillators'][i]['ton'])
    toff = float(config['oscillators'][i]['toff'])
    delay = float(config['oscillators'][i].get('delay', 0))
    osc = Oscillator(OSC_PINS[i], ton, toff, delay)
    oscillators.append(osc)
    osc.start()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pesaje Automatizado")
        self.emergency_stop = False

        self.tabs = ttk.Notebook(root)
        self.tab_main = ttk.Frame(self.tabs)
        self.tab_config = ttk.Frame(self.tabs)
        self.tab_manual = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_main, text='Visualización')
        self.tabs.add(self.tab_config, text='Configuración')
        self.tabs.add(self.tab_manual, text='Modo Manual')
        self.tabs.pack(expand=1, fill="both")

        self.weights = [tk.StringVar() for _ in range(4)]
        self.valve_states = [tk.StringVar() for _ in range(4)]
        self.tolva_state = tk.StringVar()

        self.build_main_tab()
        self.build_config_tab()
        self.build_manual_tab()

        self.update_loop()

    def build_main_tab(self):
        for i in range(4):
            ttk.Label(self.tab_main, text=f"Báscula {i+1}").grid(row=i, column=0, padx=10, pady=5)
            ttk.Label(self.tab_main, textvariable=self.weights[i]).grid(row=i, column=1)
            ttk.Label(self.tab_main, textvariable=self.valve_states[i]).grid(row=i, column=2)
        ttk.Label(self.tab_main, text="Tolva Principal").grid(row=4, column=0, pady=10)
        ttk.Label(self.tab_main, textvariable=self.tolva_state).grid(row=4, column=1)
        ttk.Button(self.tab_main, text="🚨 Parada de Emergencia", command=self.toggle_emergency_stop).grid(row=5, column=0, columnspan=2, pady=20)

    def build_config_tab(self):
        self.config_entries = []
        for i in range(4):
            ttk.Label(self.tab_config, text=f"Tiempo ON/OFF Báscula {i+1} (s)").grid(row=i, column=0)
            ton = tk.Entry(self.tab_config)
            toff = tk.Entry(self.tab_config)
            ton.grid(row=i, column=1)
            toff.grid(row=i, column=2)
            ton.insert(0, str(config['oscillators'][i]['ton']))
            toff.insert(0, str(config['oscillators'][i]['toff']))
            self.config_entries.append((ton, toff))
        ttk.Button(self.tab_config, text="Guardar Configuración", command=self.save_config).grid(row=5, column=1, pady=10)

    def build_manual_tab(self):
        for i in range(4):
            ttk.Label(self.tab_manual, text=f"EV {i+1}").grid(row=i, column=0)
            ttk.Button(self.tab_manual, text="Toggle", command=lambda i=i: toggle_output(VALVE_PINS[i])).grid(row=i, column=1)
        for i in range(4):
            ttk.Label(self.tab_manual, text=f"OSC {i+1}").grid(row=i, column=2)
            ttk.Button(self.tab_manual, text="Toggle", command=lambda i=i: toggle_output(OSC_PINS[i])).grid(row=i, column=3)

    def save_config(self):
        for i, (ton_entry, toff_entry) in enumerate(self.config_entries):
            ton = float(ton_entry.get())
            toff = float(toff_entry.get())
            config['oscillators'][i]['ton'] = ton
            config['oscillators'][i]['toff'] = toff
            oscillators[i].stop()
            oscillators[i] = Oscillator(OSC_PINS[i], ton, toff, 0)
            oscillators[i].start()
        save_config(config)

    def toggle_emergency_stop(self):
        self.emergency_stop = not self.emergency_stop
        if self.emergency_stop:
            for pin in VALVE_PINS + OSC_PINS:
                GPIO.output(pin, GPIO.LOW)
            for osc in oscillators:
                osc.stop()
        else:
            for i, osc in enumerate(oscillators):
                ton = config['oscillators'][i]['ton']
                toff = config['oscillators'][i]['toff']
                oscillators[i] = Oscillator(OSC_PINS[i], ton, toff, 0)
                oscillators[i].start()

    def update_loop(self):
        for i in range(4):
            adc_value = read_adc(i, spi)
            self.weights[i].set(f"{adc_value} unidades")
            self.valve_states[i].set("Abierta" if GPIO.input(VALVE_PINS[i]) else "Cerrada")
        self.tolva_state.set("Disponible" if is_product_available(TOLVA_SENSOR_PIN) else "Vacía")
        self.root.after(1000, self.update_loop)

root = tk.Tk()
app = App(root)
root.mainloop()
