import serial, threading
import tkinter as tk

# MUDAR CASO NAO SEJA OQ TA SENDO USADO
PORT = "COM3"
BAUD = 9600

UPDATEDELAY = 10

#pega o valor do arduino, detalhe no BAUD, precisa ser igual ao do arduino /\
try:
	ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception:
	ser = None

#placeholder pra nao dar problema
last = "--.-"

def reader():
	global last
	if not ser:
		return
	while True:
		s = ser.readline().decode(errors="ignore").strip()
		if s:
			try:
				last = f" {float(s):.2f} °C " #enfase no ' °C ', com espaço
			except:
				pass

if ser:
	threading.Thread(target=reader, daemon=True).start()



root = tk.Tk()
root.title("Temperatura do bloco") #titulo janela

#mostra o valor nessa fonte
lbl = tk.Label(root, text=last, font=("Times New Roman", 240))
lbl.pack(expand=True, fill="both")


#da update no numero, 10ms de delay (aumentar isso caso o serial print tenha maior delay pra puxar menos processamento)
def update():
	lbl.config(text=last)
	root.after(UPDATEDELAY, update)




#fecha o programa caso feche a janela
def on_close():
	try:
		if ser:
			ser.close()
	except:
		pass
	root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.after(100, update)
root.mainloop()
