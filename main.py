import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from threading import Thread
import os, pyaudio, wave, pyttsx3, time, keyboard, psutil, random, json, win32api, subprocess, webbrowser
from win32com.shell import shell, shellcon
import pyautogui as gui
from sound import Sound
from currency import currency
import speech_recognition as sr
# Переменные
pcUser = os.getlogin() # Имя юзера
mainPath = os.getcwd()

p = pyaudio.PyAudio()
stream = p.open(
	format=pyaudio.paInt16,
	channels=1,
	rate=16000,
	input=True,
	frames_per_buffer=8000
)
stream.start_stream()

# Вот штучка для импорта словаря с командами
with open(f'{mainPath}\\cmd.json', 'r', encoding='utf-8') as f:
	options = json.loads(f.read())

# Функции

def disks(): # Инфа о дисках
	global logs
	drives = win32api.GetLogicalDriveStrings()
	drives = drives.split('\000')[:-1]
	for x in drives:
		free = psutil.disk_usage(x)
		logs.insert(tk.END, f'Диск: {x}\nВсего: {free.total / (1024 * 1024 * 1024):.4} Gb\nИспользовано: {free.used / (1024 * 1024 * 1024):.4} Gb\nСвободно: {free.free / (1024 * 1024 * 1024):.4} Gb\nЗанято в процентах: {free.percent}%\n')


def play(audio): # Вопроизвести аудио файл
	wf = wave.open(f'{mainPath}\\audio\\{audio}')
	p = pyaudio.PyAudio()
	chunk = 1024
	stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
					channels = wf.getnchannels(),
					rate = wf.getframerate(),
					output = True)
	data = wf.readframes(chunk)
	while data != b'':
		stream.write(data)
		data = wf.readframes(chunk)

def done(): # Сказать что все сделано
	play(random.choice(
		["yes_sir.wav", "There_is.wav", "Loading_sir.wav",
		 "Request_completed_sir.wav"]))
	print(f"[Jarvis]: {random.choice(['Да, сэр', 'Готово', 'Загружаю', 'Запрос выполнен'])}")

def show(text): # Всплывающие окно
	messagebox.showinfo("Хэй!", text)

def log(text):
	print(text)

def print(text): # Запринтить в логах
	global logs
	logs.insert(tk.END, f'{text}\n')

# Всякая интерфейсная штука
window = tk.Tk()
window.geometry('280x420')
window.title('Джарвис')
window.resizable(False, False)
bg = '#18191d'
window.config(bg=bg)
mic = PhotoImage(file=f"{mainPath}\\img\\mic.png")
quit = False
settings = PhotoImage(file=f"{mainPath}\\img\\settings.png")

logs = tk.Text(bg=bg, height=20, bd=0, fg='white', insertbackground='white', font='Heretic 11')
butns = tk.Frame(relief=tk.RAISED, bg='#282e33')
micro = tk.Button(master=butns, bg='#282e33', width=90, height=90, image=mic, bd=0, command=lambda: show('Пока эта кнопка не работает'))
sets = tk.Button(master=butns, bg='#282e33', width=90, height=90, image=settings, bd=0, relief=tk.FLAT, activebackground='Gray30', command=lambda: show('Пока эта кнопка не работает'))

logs.pack(side="top")
butns.pack(side='bottom', fill='x')
sets.pack(side='right', anchor='se')
micro.pack(side='right', anchor='se')

def main():
	print('[Jarvis]: Начал работу...')
	while True:
		rec = sr.Recognizer()
		with sr.Microphone() as source:
			rec.pause_threshold = 0.5
			rec.adjust_for_ambient_noise(source=source, duration=0.5)
			audio = rec.listen(source)
		try:
			text = rec.recognize_google(audio, language="RU" ).lower()
			for i in options:
				if any(word in text for word in options[i]):
					print(f'[You]: {text.capitalize()}')
					break
				else:
					continue
		except sr.UnknownValueError:
			continue
	
		if any(word in text for word in options['weather']): #1
			webbrowser.open('https://yandex.ru/pogoda/')
			done()
		
		elif any(word in text for word in options['write']): #2
			for i in range(len(['write'])):
				i = options['write'][i]
				if text.startswith(f' {i}'):
					text = text.replace(f' {i} ', '')
					keyboard.write(text)
					done()
					break
				else: continue
	
		elif any(word in text for word in options['disks']):
			print(disks())
			done()
	
		elif any(word in text for word in options['currency']):
			print('[Jarvis]: Доллар - {}\nЕвро - {}\nBitcoin - {}\nEthereum - {}'.format(currency(), currency('euro'), currency('bitcoin'), currency('ethereum')))
			done()
	
		# Hotkeys
		
		elif any(word in text for word in options['lang']): #3
			keyboard.send('shift+alt')
			done()
		
		elif any(word in text for word in options['press']) and any(word in text for word in options['del']): #4
			keyboard.send('del')
			done()
		
		elif any(word in text for word in options['enter']): #5
			keyboard.send('enter')
			done()
		
		elif any(word in text for word in options['esc']): #6
			keyboard.send('esc')
			done()
		
		elif any(word in text for word in options['copy']): #7
			keyboard.send('ctrl+c')
			done()
		
		elif any(word in text for word in options['paste']): #8
			keyboard.send('ctrl+v')
			done()
		
		elif any(word in text for word in options['hide']): #9
			keyboard.send('win+d')
			done()  
		
		# End of hotkeys
	
		elif any(word in text for word in options['y_find']):
			for i in options['y_find']:
				if i in text:
					text = text.replace(f' {i} ', '')
			webbrowser.open(f'https://www.youtube.com/results?search_query={text}')
			done()
	
		elif any(word in text for word in options['ram']): #11
			ram = psutil.virtual_memory().percent
			print(f'Использовано оперативной\nпамяти - {ram}%')
			done()
		
		elif any(word in text for word in options['cpu']): #12
			cpu = psutil.cpu_percent()
			print(f'Нагрузка на ЦП {cpu}%')
			done()
		
		elif any(word in text for word in options['screenshot']): #13
			if os.path.exists(f'{mainPath}\\screenshots') is True:
				pass
			else:
				os.mkdir(f'{mainPath}\\screenshots')
			gui.screenshot(f'{mainPath}\\screenshots\\screen.jpg')
			done()
		
		elif any(word in text for word in options['pcOff']): #15
			play("power_off.wav")
			time.sleep(3)
			os.system('shutdown -s')
		
		elif any(word in text for word in options['pcRestart']): #16
			play("As_you_wish.wav")
			time.sleep(3)
			os.system('shutdown -r -t 0')
		
		elif any(word in text for word in options['goodMorning']): #17
			play("good_morning.wav")
			done()
		
		elif any(word in text for word in options['atHome']): #18
			play("Jarvis greetings.wav")
			done()
		
		elif any(word in text for word in options['call']): #20
			play(random.choice(
				["yes_sir.wav", "Always_at_your_service_sir.wav"]))

Thread(target=main).start()

window.mainloop()