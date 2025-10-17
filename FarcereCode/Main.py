import json #Importerer json
import subprocess #Importerer subprocess
import sys  #Importerer sys
import os   #Importerer os
from tkinter import * #Importerer alt inni tkinter bibloteket
from tkinter import filedialog #Importerer fildialog
from tkinter import messagebox #Importerer meldings boks

isSaved = True

def updateStatus(newStatus): #Funksjon for å oppdatere status
    selectedIndex = listbox.curselection() #Henter indexen av elemente i liste 1
    if selectedIndex:
        index = selectedIndex[0] #Setter index til elemente i liste 1 sin index
        statusList.delete(index) #Fjerner existerende status
        statusList.insert(index, newStatus) #Leger til ny status på same index som elemnete i liste 1
   
    global isSaved #Henter isSaved variablen
    isSaved = False #Gjør isSaved variablen False

def addItem(args): #Funksjon for å legge til nye elementer
    listbox.insert(listbox.size(), itemInput.get()) #Legger input til nederst i listen
    statusList.insert(statusList.size(), status) #Legger status til nederst i listen
    itemInput.delete(0, END) #Fjerner tekst i input boksen

    if listbox.size() > 20: #Vis listen er støre en 20..
        listbox.config(height=listbox.size()) #Gjør listen lenger
   
    global isSaved #Henter isSaved variablen
    isSaved = False #Gjør isSaved variablen False

def getAppFolder(): #Henter App mappen
    homeDir = os.path.expanduser("~") #Henter home mappe
    appDir = os.path.join(homeDir, "facere") #Finner app mappen i home

    if not os.path.exists(appDir): #Om app mappen ikke er i home..
        os.makedirs(appDir) #Opprett en mappe
        print("AppFolder Made")
    else:
        print("Appfolder found")
   
    return appDir #Ellers gi app mappen

def saveFile(): #Funksjon for å lagre listen
    defultDir = getAppFolder() #Henter siten til app mappen
   
    file = filedialog.asksaveasfilename(initialdir=defultDir, defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save List") #hvor listen skal lagre og type
   
    if file:
        data = [] #Liste som skal holde all dataen
        for i in range(listbox.size()): #Løkke for å lagre alt
            task = listbox.get(i) #Variabel som skal holde alt far element listen
            statusSave = statusList.get(i) #Variabel for å holde alle statusene
            data.append({"task" : task, "status" : statusSave}) #Leger alt in i listen i dette formate
        try:
            with open(file, "w") as f: #Skriver in all informasjone til filen
                json.dump(data, f) #Skriver data in i filen
            global isSaved #Henter isSaved variablen
            isSaved = True #Gjør isSaved variblen True
        except Exception as e: #Hånterer errror
            print("Error occurd while saving:", e)

def loadFile(): #Funksjon for å åpne gamle filer
    defultDir = getAppFolder() #Henter siten til app mappen
    file = filedialog.askopenfilename(initialdir=defultDir, title="Open saved list", filetypes=[("JSON files", "*.json")]) #Åpner filutforsker for å åpne filen
   
    if file:
        try:
            with open(file, "r") as f: #Leser datan i filen
                data = json.load(f) #Åpner all infoen
                listbox.delete(0, END) #Fjerner existerende data
                statusList.delete(0, END) #Fjerner existerende data
                for item in data:
                    listbox.insert(END, item["task"]) #laster opp fil informasjon
                    statusList.insert(END, item["status"]) #laster opp fil informasjon
        except Exception as e: #Hånterer errror
            print("Data failed to load:", e)

def newFile(): #Funksjon for å åpne ny fil
    subprocess.Popen([sys.executable, sys.argv[0]]) #Åpner nytt vindu uten å fjerne existerende vindu

def onClosing(): #Sikkerhets funksjon
    if not isSaved: #Om filen ikke er lagret..
        answer = messagebox.askyesno("", "Do you want to save?") #Spør bruker om di vil lagre
        if answer: #Vis det er ja..
            saveFile() #Kall lagrings funksjon
            window.destroy() #Lukk vindu

   
    window.destroy() #Lukk vindu

def resourcePath(relativePath):
    if hasattr(sys, "_MEIPASS"):  # Hvis kjører exe fra PyInstaller
        basePath = sys._MEIPASS
    else:  # Hvis kjører skript
        basePath = os.path.dirname(os.path.abspath(__file__))  # mappen til skriptet
    return os.path.join(basePath, relativePath)

status = "Not Started" #Start status

window = Tk() #Vindue som holder alle GUI elementer
window.geometry("750x520") #Setter størelse på vindue
window.title("Facere") #Gir navn til appen

iconPath = resourcePath("app.png")
icon = PhotoImage(file=iconPath)
window.iconphoto(True, icon)

label = Label(window, text="To-do", font=("Arial", 40, "bold", "underline")) #Lager en tekst i vindue som det står To-do som har arial famliy font, 40 i størelse og er feit
label.grid(row=0, column=0) #Setter hvor teksten skal ligger

fileButtonFrame = Frame(window) #Lager en konteiner for noen knaper inni window
fileButtonFrame.grid(row=0, column=1, padx=10) #Leger konteineren in i rad 1 kolone 1

saveButton = Button(fileButtonFrame, text="Save", font=("Arial", 15), command=saveFile) #Lagrings knapp
saveButton.grid(row=0, column=0) #Setter hvor teksten skal ligger
loadButton = Button(fileButtonFrame, text="Load", font=("Arial", 15), command=loadFile) #Åpne fil knapp
loadButton.grid(row=0, column=1) #Setter hvor teksten skal ligger

newFilButton = Button(fileButtonFrame, text="New", font=("Arial", 15), command=newFile) #Åpner en ny fil knapp
newFilButton.grid(row=0, column=2) #Setter hvor teksten skal ligger

itemInput = Entry() #Henter input fra bruker
itemInput.config(font=("Arial", 12)) #Setter font til elemente
itemInput.config(width=40) #Setter breden til input boksen
itemInput.grid(row=1, column=0) #Setter hvor teksten skal lige
itemInput.bind("<Return>", addItem) #Gjør så du kan trykke enter for å legge til et nytt element


buttonFrame = Frame(window) #Lagger en konteiner for noen knaper inni window
buttonFrame.grid(row=1, column=1, padx=10) #Leger konteineren in i rad 1 kolone 1

finishButton = Button(buttonFrame, width=2, background="green", command = lambda: updateStatus("Done")).grid(row=0, column=0, padx=2) #lager en knap som setter status til 'Done'
startedButton = Button(buttonFrame, width=2, background="yellow", command = lambda: updateStatus("In Progress")).grid(row=0, column=1, padx=2) #lager en knap som setter status til 'In Progress'
notstartedButton = Button(buttonFrame, width=2, background="red", command = lambda: updateStatus("Not Started")).grid(row=0, column=2, padx=2) #lager en knap som setter status til 'Not Started'

listLable = Label(window, text="Task List: ", width=40, font=("Arial", 12)).grid(row=2, column=0) #Leger til info tekst
statusLable = Label(window, text="Task Status: ", width=40, font=("Arial", 12)).grid(row=2, column=1) #Leger til info tekst

listbox = Listbox(window, width=40, height=20, font=("Arial", 12)) #Lager listen som skal holde alle elementene
listbox.grid(row=3, column=0) #Sier hvor lista skal så

statusList = Listbox(window, width=40, height=20, font=("Arial", 12)) #Lager listen som skal holde statusen til alle elementene
statusList.grid(row=3, column=1) #Sier hvor lista skal så

window.protocol("WM_DELETE_WINDOW", onClosing) #Sikkerhet for lagring

window.mainloop() #Åpner vinuet