import json #Importerer json
import subprocess #Importerer subprocess
import sys  #Importerer sys
import os   #Importerer os
from tkinter import * #Importerer tkinter klassisk bibloteket
from tkinter import filedialog #Importerer fildialog
from tkinter import messagebox #Importerer meldings boks
from tkinter import simpledialog #Importere simple dialog bokser
from datetime import datetime #Imporeterer timestamps

isSaved = True
currentFile = None
maxListItem = 20
undoStack = []
redoStack = []
fullItem = {}

def updateTitle():
    if currentFile:
        window.title(f"Munus* - {os.path.basename(currentFile)}")
    else:
        window.title("Munus*")

def updateStatus(newStatus): #Funksjon for å oppdatere status
    selectedIndex = listbox.curselection() #Henter indexen av elemente i liste 1

    if not selectedIndex:
        return
   
    top_index = statusList.nearest(0)

    for index in reversed(selectedIndex):
        listboxTask = listbox.get(index)
   
        if newStatus == "Done":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            newStatusTime = f"Done  | {timestamp}"
            statusList.delete(index)
            statusList.insert(index, newStatusTime)

        else:
            statusList.delete(index) #Fjerner existerende status
            statusList.insert(index, newStatus) #Leger til ny status på same index som elemnete i liste 1
    state = {"task": fullItem.copy(), "status": [statusList.get(i) for i in range(statusList.size())]}
    undoStack.append(state)
    redoStack.clear()
   
    statusList.yview_moveto(top_index / max(1, statusList.size()))

    global isSaved #Henter isSaved variablen
    isSaved = False #Gjør isSaved variablen False
    updateTitle()
    syncSelection(None)

def updateListboxDisplay():
    listbox.delete(0, END)  # fjern alt før vi legger inn på nytt
    maxChr = max(10, listbox.winfo_width() // 10)
   
    scroll_pos = listbox.yview()

    for i in range(len(fullItem)):
        fullText = fullItem.get(i, "")
        if len(fullText) > maxChr:
            displayText = fullText[:maxChr-3] + "..."
        else:
            displayText = fullText
       
        listbox.insert(END, displayText)

    listbox.yview_moveto(scroll_pos[0])

def syncSelection(event=None):
    try:
        selectedIndex = listbox.curselection()
        statusList.select_clear(0, END)
        for index in selectedIndex:
            statusList.select_set(index)

    except Exception as e:
        print("syncSelection failed:", e)

def syncScroll(*args): #Funksjon for å syncronisere scroll
    listbox.yview(*args)
    statusList.yview(*args)

def listboxYscroll(*args):
    listboxScroll.set(*args)

def deleteItem(event=None):
    selectedIndex = listbox.curselection() #Henter indexen av elemente i liste 1

    if not selectedIndex:
        return

    for index in reversed(selectedIndex):
        statusList.delete(index) #Fjerner existerende status
        listbox.delete(index)
        if index in fullItem:
            del fullItem[index]
       
        newFullItem = {i: listbox.get(i) for i in range(listbox.size())}
        fullItem.clear()
        fullItem.update(newFullItem)
   
    global isSaved #Henter isSaved variablen
    isSaved = False #Gjør isSaved variablen False
    updateTitle()

def addItem(args): #Funksjon for å legge til nye elementer
    newItem = itemInput.get()
    if not newItem:
        return

    state = {"task": fullItem.copy(), "status": [statusList.get(i) for i in range(statusList.size())]}
    undoStack.append(state)
    redoStack.clear()

    index = len(fullItem)
    fullItem[index] = newItem
    statusList.insert(END, status)
    itemInput.delete(0, END)

    listbox.insert(END, newItem)
    updateListboxDisplay()

    global isSaved #Henter isSaved variablen
    isSaved = False #Gjør isSaved variablen False
    updateTitle()

def editItem(event):
    selectedIndex = listbox.curselection()
   
    if not selectedIndex:
        return
   
    index = selectedIndex[0]

    state = {"task": fullItem.copy(), "status": [statusList.get(i) for i in range(statusList.size())]}
    undoStack.append(state)
    redoStack.clear()

    oldText = fullItem.get(index, "")
    newText = simpledialog.askstring("Edit Task", "Update task:", initialvalue=oldText)

    if newText:
        fullItem[index]= newText
        listbox.delete(index)
        listbox.insert(index, newText)

    global isSaved
    isSaved = False
    updateTitle()
    syncSelection(None)

def getAppFolder(): #Henter App mappen
    homeDir = os.path.expanduser("~") #Henter home mappe
    appDir = os.path.join(homeDir, "munus") #Finner app mappen i home

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

            global isSaved, currentFile #Henter isSaved variablen
            isSaved = True #Gjør isSaved variblen True
            currentFile = file
            window.title(f"Munus - {os.path.basename(file)}")

        except Exception as e: #Hånterer errror
            print("Error occurd while saving:", e)

def loadFile(): #Funksjon for å åpne gamle filer
    defultDir = getAppFolder() #Henter siten til app mappen
    file = filedialog.askopenfilename(initialdir=defultDir, title="Open saved list", filetypes=[("JSON files", "*.json")]) #Åpner filutforsker for å åpne filen
    if not isSaved:
        answer = messagebox.askyesno("", "Do you whant to save the previos file?")
        if answer:
            saveFile()
            if file:
                print("try Load file")
                try:
                    with open(file, "r") as f: #Leser datan i filen
                        data = json.load(f) #Åpner all infoen
                        listbox.delete(0, END) #Fjerner existerende data
                        statusList.delete(0, END) #Fjerner existerende data
                        for item in data:
                            listbox.insert(END, item["task"]) #laster opp fil informasjon
                            statusList.insert(END, item["status"]) #laster opp fil informasjon
                       
                        fullItem.clear()
                        for i, item in enumerate(data):
                            fullItem[i] = item["task"]

                    global currentFile
                    currentFile = file
                    window.title(f"Munus - {os.path.basename(file)}")

                except Exception as e: #Hånterer errror
                    print("Data failed to load:", e)
        elif not answer:
            if file:
                print("try Load file")
                try:
                    with open(file, "r") as f: #Leser datan i filen
                        data = json.load(f) #Åpner all infoen
                        listbox.delete(0, END) #Fjerner existerende data
                        statusList.delete(0, END) #Fjerner existerende data
                        for item in data:
                            listbox.insert(END, item["task"]) #laster opp fil informasjon
                            statusList.insert(END, item["status"]) #laster opp fil informasjon
                       
                        fullItem.clear()
                        for i, item in enumerate(data):
                            fullItem[i] = item["task"]

                    currentFile = file
                    window.title(f"Munus - {os.path.basename(file)}")

                except Exception as e: #Hånterer errror
                    print("Data failed to load:", e)
    else:
        if file:
            try:
                with open(file, "r") as f: #Leser datan i filen
                    data = json.load(f) #Åpner all infoen
                    listbox.delete(0, END) #Fjerner existerende data
                    statusList.delete(0, END) #Fjerner existerende data
                    for item in data:
                        listbox.insert(END, item["task"]) #laster opp fil informasjon
                        statusList.insert(END, item["status"]) #laster opp fil informasjon

                    fullItem.clear()
                    for i, item in enumerate(data):
                        fullItem[i] = item["task"]
                currentFile = file
                window.title(f"Munus - {os.path.basename(file)}")

            except Exception as e: #Hånterer errror
                print("Data failed to load:", e)

def newFile(): #Funksjon for å åpne ny fil
    subprocess.Popen([sys.executable, sys.argv[0]]) #Åpner nytt vindu uten å fjerne existerende vindu

def onClosing(event=None): #Sikkerhets funksjon
    if not isSaved: #Om filen ikke er lagret..
        answer = messagebox.askyesno("", "Do you want to save?") #Spør bruker om di vil lagre
        if answer: #Vis det er ja..
            saveFile() #Kall lagrings funksjon
           
    window.destroy() #Lukk vindu

def resourcePath(relativePath):
    if hasattr(sys, "_MEIPASS"):  # Hvis kjører exe fra PyInstaller
        basePath = sys._MEIPASS
    else:  # Hvis kjører skript
        basePath = os.path.dirname(os.path.abspath(__file__))  # mappen til skriptet
    return os.path.join(basePath, relativePath)

def restoreState(state):
    try:
        listbox.delete(0, END)
        statusList.delete(0, END)
        fullItem.clear()
        fullItem.update({i: task for i, task in enumerate(state["task"].values())})

        for i, task in enumerate(fullItem.values()):
            listbox.insert(END, task)
            statusList.insert(END, state["status"][i])

        updateListboxDisplay()
        syncSelection(None)
        window.update_idletasks()
    except Exception as e:
        print("restoreStatus failed:", e)

def undo():
    if not undoStack:
        return
   
    currentState = {"task": {i: fullItem[i] for i in range(len(fullItem))}, "status": [statusList.get(i) for i in range(statusList.size())]}
    redoStack.append(currentState)

    prevState = undoStack.pop()
    restoreState(prevState)

def redo():
    if not redoStack:
        return
   
    currentState = {"task": {i: fullItem[i] for i in range(len(fullItem))}, "status": [statusList.get(i) for i in range(statusList.size())]}
    undoStack.append(currentState)

    nextState = redoStack.pop()
    restoreState(nextState)

class toolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipWindow = None
        self.widget.bind("<Motion>", self.showTip)
        self.widget.bind("<Leave>", self.hideTip)

    def showTip(self, event):
        index = self.widget.nearest(event.y)

        if index < 0 or index >= self.widget.size():
            self.hideTip()
            return
       
        text = fullItem.get(index, "")

        if not text:
            self.hideTip()
            return
       
        if len(text) > self.widget["width"]:
            self._show(text, event.x_root, event.y_root)
        else:
            self.hideTip()
   
    def _show(self, text, x, y):
        self.hideTip()
        self.tipWindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x+20}+{y+20}")
        tipLable = Label(tw, text=text, justify="left", bg="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 10))
        tipLable.pack(padx=5, pady=2)
   
    def hideTip(self, event=None):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()

status = "Not Started" #Start status

window = Tk() #Vindue som holder alle GUI elementer
window.geometry("820x570") #Setter størelse på vindue
window.title("Munus") #Gir navn til appen
window.rowconfigure(1, weight=0)
window.rowconfigure(2, weight=0)
window.rowconfigure(3, weight=1)
window.rowconfigure(4, weight=0)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

window.bind_all("<Control-s>", lambda event: saveFile()) #Hurtigtast for å lagre en fil
window.bind_all("<Control-o>", lambda event: loadFile()) #Hurtigtast for å laste in en fil
window.bind_all("<Control-n>", lambda event: newFile()) #Hurtigtast for å opprete en ny fil
window.bind_all("<Control-z>", lambda event: undo())
window.bind_all("<Control-Shift-Z>", lambda event: redo())
window.bind("<Delete>", lambda event: deleteItem()) #Hurtigtast for å fjerne et element fra listen
window.bind("<Configure>", lambda event: updateListboxDisplay())

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

controlFrame = Frame(window) #Bruker venlig het
controlFrame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10) #Posisjonen til controlFrame

controlLableSave = Label(controlFrame, text="Save = ctrl + S,", font=("Arial", 10), fg="gray") #Tekst for å vise hurtitasten for lagring
controlLableSave.grid(row=0,column=0, sticky="ew") #Posisjon inni controlFrame
controlLableLoad = Label(controlFrame, text="Load = ctrl + O,", font=("Arial", 10), fg="gray") #Tekst for å vise hurtitasten for å åpne en fil
controlLableLoad.grid(row=0, column=1, sticky="ew") #Posisjon inni controlFrame
controlLableNew = Label(controlFrame, text="New = ctrl + N,", font=("Arial", 10), fg="gray") #Tekst for å vise hurtitasten for å åpne en ny fil
controlLableNew.grid(row=0, column=2, sticky="ew") #Posisjon inni controlFrame
controlLableRemove = Label(controlFrame, text="Remove = DEL,", font=("Arial", 10), fg="gray") #Tekst for å vise hurtitasten forå fjerne et element fra listen
controlLableRemove.grid(row=0, column=3, sticky="ew") #Posisjon inni controlFrame
controlLableSHIFTselect = Label(controlFrame, text="Multi select = shift + mouse click,", font=("Arial", 10), fg="gray")
controlLableSHIFTselect.grid(row=0, column=4, sticky="ew")
controlLableCtrlselect = Label(controlFrame, text="Toggle select = ctrl + mouse click,", font=("Arial", 10), fg="gray")
controlLableCtrlselect.grid(row=0, column=5, sticky="ew")
controlLableUndo = Label(controlFrame, text="Undo = ctrl + z,", font=("Arial", 10), fg="gray")
controlLableUndo.grid(row=1, column=0, sticky="ew")
controlLableRedo = Label(controlFrame, text="Redo = shift + ctrl + z.", font=("Arial", 10), fg="gray")
controlLableRedo.grid(row=1, column=1, sticky="ew")

inputBoxFrame = Frame(window) #Frame for å plasere input elementer
inputBoxFrame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10) #Posisjon til inputBoxFrame
inputBoxFrame.columnconfigure(1, weight=1)

inputLable = Label(inputBoxFrame, text="New Task:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="nsew") #Tekst som viser hva bruke skal skrive

itemInput = Entry(inputBoxFrame) #Henter input fra bruker
itemInput.config(font=("Arial", 12)) #Setter font til elemente
itemInput.config(width=30) #Setter breden til input boksen
itemInput.grid(row=0, column=1, sticky="nsew") #Setter hvor teksten skal lige
itemInput.bind("<Return>", addItem) #Gjør så du kan trykke enter for å legge til et nytt element

buttonFrame = Frame(window) #Lagger en konteiner for noen knaper inni window
buttonFrame.grid(row=1, column=1, sticky="ew", padx=10) #Leger konteineren in i rad 1 kolone 1

finishButton = Button(buttonFrame, width=2, background="green", command = lambda: updateStatus("Done")).grid(row=0, column=0, sticky="ew", padx=2) #lager en knap som setter status til 'Done'
startedButton = Button(buttonFrame, width=2, background="yellow", command = lambda: updateStatus("In Progress")).grid(row=0, column=1, sticky="ew", padx=2) #lager en knap som setter status til 'In Progress'
notstartedButton = Button(buttonFrame, width=2, background="red", command = lambda: updateStatus("Not Started")).grid(row=0, column=2, sticky="ew", padx=2) #lager en knap som setter status til 'Not Started'

listLable = Label(window, text="Task List: ", width=40, font=("Arial", 12)).grid(row=2, column=0) #Leger til info tekst
statusLable = Label(window, text="Task Status: ", width=40, font=("Arial", 12)).grid(row=2, column=1) #Leger til info tekst

listboxFrame = Frame(window)
listboxFrame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
listboxFrame.rowconfigure(0, weight=1)
listboxFrame.columnconfigure(0, weight=1)

listbox = Listbox(listboxFrame, width=40, height=20, font=("Arial", 12), selectmode=EXTENDED, exportselection=False) #Lager listen som skal holde alle elementene
listbox.grid(row=0, column=0, sticky="nsew") #Sier hvor lista skal så

listbox.bind("<Double-Button-1>", editItem) #Dobbel klikk for å endre et element i listen
listbox.bind("<<ListboxSelect>>", syncSelection)

toolTip(listbox)

listboxScroll = Scrollbar(listboxFrame, orient=VERTICAL, command=listbox.yview)
listboxScroll.grid(row=0, column=1, sticky="ns")
listboxScroll.config(command=syncScroll)
listbox.config(yscrollcommand=listboxYscroll)

statusListFrame = Frame(window)
statusListFrame.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
statusListFrame.rowconfigure(0, weight=1)
statusListFrame.columnconfigure(0, weight=1)

statusList = Listbox(statusListFrame, width=40, height=20, font=("Arial", 12), selectmode=EXTENDED, exportselection=False) #Lager listen som skal holde statusen til alle elementene
statusList.grid(row=0, column=0, sticky="nsew") #Sier hvor lista skal så
statusList.config(yscrollcommand=listboxYscroll)

window.protocol("WM_DELETE_WINDOW", onClosing) #Sikkerhet for lagring

window.mainloop() #Åpner vinuet