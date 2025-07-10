import tkinter as tk 
from tkinter import ttk
import configureDictionaries

def createSettingsPage(configs, labelName, fields, popup, dropDown):

  frame = createBaseFrame(popup)
  labelFrame = createLabelFrame(popup,labelName)

  entries = createLabledEntryBoxes(frame, fields, dropDown)

  saveButton = tk.Button(frame, text="Save Config", command=lambda: saveEntries(configs, entries,labelName, None),
                        borderwidth=1, relief="solid")
  
  saveButton.grid(row=8,column=5, padx=4, pady=4, sticky = 'se')

def createBaseFrame(popup):

  frame = tk.Frame(popup, borderwidth=1, relief="solid")
  frame.grid(row=1, column=1, sticky= 'nsew')

  frame.rowconfigure([0,1,2,3], weight=1)
  frame.columnconfigure([0,1,2,3], weight=1)

  return frame

def createLabelFrame(popup, labelName):

  labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  labelFrame.grid(row=0,column=1, sticky='nsew')

  frameLabel = tk.Label(labelFrame, text=labelName, anchor="center", justify="center")
  frameLabel.grid(row=0, column=0, sticky = 'nsew')

  labelFrame.columnconfigure(0, weight=1)

  return labelFrame

def createLabledEntryBoxes(parent, fields, dropDown):

  entries = {}
  j = 1
  currIndex = 0 
  for i, field in enumerate(fields):

    # Wrap every 4 columns
    if i > 3:
      i = i % 4
      if i % 4 == 0:
        j += 2 

    label = tk.Label(parent, text=field)
    label.grid(row=j,column=i,sticky='nsew', padx=14, pady=6)

    entry = tk.Entry(parent)
    entry.grid(row=j+1, column=i, sticky='nsew', padx=14, pady=4)
    
    entries[field] = entry
    if dropDown is not None and currIndex == len(fields) - 1:
      for key in dropDown:

        label = tk.Label(parent, text=key)
        label.grid(row=j,column=i+1,sticky='nsew', padx=14, pady=6)

        comboBox = ttk.Combobox(parent, values=dropDown[key])
        comboBox.grid(row=j+1,column=i+1,sticky='nsew', padx=14, pady=6)
        comboBox.set("Select Preference")

        i+=1 

        entries[key] = comboBox

    currIndex += 1

  return entries

def saveEntries(configs, entries, configName, type):
    
    entryVals = {}
    for field in entries.keys():
      entryVals[field] = entries[field].get()
    
    if configName == "Propellant Config":
      configureDictionaries.configurePropellantDict(configs, entryVals)
    elif configName.startswith("OpenMotor"):
      configureDictionaries.configureOMDict(configs, entryVals)
    elif configName == "Nozzle Iterator":
      configureDictionaries.configureNIDict(configs, entryVals)
    elif configName == "Grain":
      configureDictionaries.configureGrainDict(configs, entryVals, type)

    print(configs)
