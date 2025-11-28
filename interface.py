import serial, threading
import tkinter as tk

#max e min das barras
MIN_VAL = 25
MAX_VAL = 55

# number of slots in the bar (8 by default)
N_SLOTS = 8



# serial config
PORT = "COM3"
BAUD = 9600

UPDATEDELAY = 50 #update delay, deixar pouco ou perto de pouco

#pega o valor do arduino, detalhe no BAUD, precisa ser igual ao do arduino /\
try:
	ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception:
	ser = None



#placeholder pra nao dar problema
last = "--.-"
last_val = None
running = True



def reader():
	global last, last_val
	if not ser:
		return
	while running:
		try:
			s = ser.readline().decode(errors="ignore").strip()
		except (serial.SerialException, OSError):
			break   # exit thread if port becomes invalid
		if s:
			try:
				v = float(s)
				last_val = v
				last = f" {v:.2f} °C " #enfase no ' °C ', com espaço
			except:
				pass

if ser:
	threading.Thread(target=reader, daemon=True).start()


#UI
root = tk.Tk()
root.title("Temperatura - bottom-up bar")







#######################################################
#######################################################
#######################################################
#######################################################
#######################################################

#arco írises

#parede da esquerda
bar_w = 150
bar_h = 800
bar = tk.Canvas(root, width=bar_w, height=bar_h, highlightthickness=0, bg="white")
bar.pack(side="left", fill="y")

#cor crescente de graus
colors = [
	"#ff0000",  #55
	"#ff7f00",
	"#ffff00",
	"#99ff00",
	"#66ccff",
	"#0099ff",
	"#0077ff",
	"#4b0082"   #25
]

# create rects (coords set on resize)
rect_ids = []
for _ in range(N_SLOTS):
	rid = bar.create_rectangle(0, 0, 0, 0, fill=bar['bg'], outline="black", width=3)
	rect_ids.append(rid)

def resize_bar(event=None):
	w = bar.winfo_width() or bar_w
	h = bar.winfo_height() or bar_h
	slot_h = h / len(rect_ids)
	for i, rid in enumerate(rect_ids):
		y1 = i * slot_h + 4
		y2 = (i + 1) * slot_h - 4
		bar.coords(rid, 4, y1, w - 4, y2)

bar.bind("<Configure>", lambda e: resize_bar())
root.update_idletasks()
resize_bar()

def value_to_filled_count(val, vmin=MIN_VAL, vmax=MAX_VAL, slots=N_SLOTS):
	"""
	Map val in [vmin, vmax] to how many slots should be FILLED (1..slots).
	At vmin -> 1 (only bottom)
	At vmax -> slots (all)
	Intermediate -> round proportion of (slots-1) + 1
	"""
	if val is None:
		return 0
	# clamp
	if val <= vmin:
		prop = 0.0
	elif val >= vmax:
		prop = 1.0
	else:
		prop = (val - vmin) / (vmax - vmin)
	# compute filled_count: scale to [0 .. slots-1], round, then +1 so min maps to 1
	filled = int(round(prop * (slots - 1))) + 1
	if filled < 1:
		filled = 1
	if filled > slots:
		filled = slots
	return filled

def update_bar_bottom_up(val):
	"""
	Fill from bottom up according to value.
	rect_ids are top->bottom, so to fill bottom-up we color indices >= start_idx.
	"""
	bg = bar['bg']
	# number of filled slots (0 means clear all)
	filled = value_to_filled_count(val)
	# clear all first
	for i, rid in enumerate(rect_ids):
		bar.itemconfig(rid, fill=bg, outline="black", width=3)
	if filled == 0:
		return
	# compute start index (top-based)
	# filled_count = filled -> number of bottom slots to color
	start_idx = len(rect_ids) - filled
	# color slots from start_idx .. end (bottom)
	for i in range(start_idx, len(rect_ids)):
		bar.itemconfig(rect_ids[i], fill=colors[i], outline="black", width=4)

#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
#######################################################







#mostra o valor nessa fonte
lbl = tk.Label(root, text=last, font=("Times New Roman", 240))
lbl.pack(expand=True, fill="both")


#da update no numero, delay configurado la em cima
def update():
	lbl.config(text=last)
	update_bar_bottom_up(last_val)
	root.after(UPDATEDELAY, update)




#fecha o programa caso feche a janela, ta dando um erro estranho atualmente
def on_close():
	global running
	running = False
	try:
		if ser:
			ser.close()
	except:
		pass
	root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.after(100, update)
root.mainloop()
