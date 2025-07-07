# MAIN
#
# Handles user input are calls upon sub files depending on what the user wants to do 

# File handling libraries
import os 
from pathlib import Path
import subprocess as sub
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# GUI library
import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog as fd 

# Python libraries
import re


def main(): 

  global configs

  configs = {}

  # initialize main GUI page
  gui = tk.Tk()
  gui.title('OpenProp')

  gui.rowconfigure(0, weight=1)
  gui.columnconfigure(0, weight=1)
  gui.columnconfigure(1, weight=1)

  # Functions
  functionsFrame = ttk.Frame(gui)
  functionsFrame.grid(row=0, column=0,sticky="nsew")

  functionsFrame.rowconfigure([1, 2, 3, 4], weight=1)  # Allow buttons to expand vertically
  functionsFrame.columnconfigure(0, weight=1)         # Allow buttons to fill horizontally

  functionsLabel = tk.Label(functionsFrame, text="Functions")
  functionsLabel.grid(row=0, column=0, sticky="nsew")

  nozzleBtn = ttk.Button(functionsFrame, text="Nozzle Iterator",
                         command=runNozzleIterator)
  nozzleBtn.grid(row=1, column=0, sticky="nsew")

  impulseBtn = ttk.Button(functionsFrame, text="Impulse Calculator",
                          command=runImpulseCalc)
  impulseBtn.grid(row=2, column=0, sticky="nsew")

  curativeBtn = ttk.Button(functionsFrame, text="Curative Calculator",
                          command=runCurativeCalculator)
  curativeBtn.grid(row=3, column=0, sticky="nsew")

  seriesBtn = ttk.Button(functionsFrame, text="Nozzle Iterator & Impulse Calculator",
                         command=runSeries)
  seriesBtn.grid(row=4,column=0, sticky="nsew")

  # Configurations 
  configsFrame = tk.Frame(gui)
  configsFrame.grid(row=0,column=1,sticky="nsew")

  configsFrame.rowconfigure([1, 2, 3, 4,5], weight=1)
  configsFrame.columnconfigure(0, weight=1)

  configsLabel = tk.Label(configsFrame, text="Settings")
  configsLabel.grid(row=0, column=0, sticky = "nsew")

  propConfigBtn = ttk.Button(configsFrame, text="Upload or Create Configs",
                               command=lambda: handleConfig(gui))
  propConfigBtn.grid(row= 1, column=0, sticky="nsew")

  gui.mainloop()

def runNozzleIterator():
  config = fd.askopenfilename()
  if config is not None:  
    sub.run([sys.executable, "NozzleIterator/NozzleIterator.py", config], check=True)

def handleConfig(gui):
  popup = tk.Toplevel(gui)
  
  popup.transient(gui) # Keep it on top of main window
  popup.grab_set()   

  popup.columnconfigure(0, weight=2)
  popup.columnconfigure(2, weight=7)
  popup.geometry("900x600") # width px by height px

  optionsFrame = tk.Frame(popup,borderwidth=1,relief="solid")
  optionsFrame.grid(row=0, column=0, rowspan=10, sticky='nsew')

  fakeLabelFrame =tk.Frame(popup)
  fakeLabelFrame.grid(row=0, column=2, sticky='nsew', padx=2)
  fakeFrame = tk.Frame(popup)
  fakeFrame.grid(row=1,column=2, sticky='nsew', padx=2)

  configLabel = tk.Button(optionsFrame, text="Create Propellant",command=lambda: createPropellant(popup))
  configLabel.grid(row=0,column=0,sticky='nsew')

  configLabel = tk.Button(optionsFrame, text="Create Grain Geometry",command=lambda: createGrainGeometry(popup))
  configLabel.grid(row=1,column=0,sticky='nsew')



def createPropellant(popup):

  propFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  propFrame.grid(row=1, column=2, sticky= 'nsew')

  propLabelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  propLabelFrame.grid(row=0,column=2, sticky='nsew')

  propLabelFrame.columnconfigure(0, weight=1)

  propFrame.rowconfigure([0,1,2,3], weight=1)
  propFrame.columnconfigure([0,1,2,3], weight=1)

  fields = [
            "Propellant Name", "Density - Kg/m^3", "Max Pressure - Pa", "Min Pressure - Pa",
            "Burn Rate Coefficient" , "Burn Rate Exponent", "Specific Heat Ratio",
            "Combustion Temperature - K", "Exhaust Molar Mass - g/mol"
            ]
  
  propLabel = tk.Label(propLabelFrame, text="Propellant Config", anchor="center", justify="center")
  propLabel.grid(row=0, column=0, sticky = 'nsew')

  entries = createLabledEntryBoxes(propFrame, fields)

  saveButton = tk.Button(propFrame, text="Save Config", command=lambda: saveEntries(entries,"Propellant"),
                        borderwidth=1, relief="solid")
  
  saveButton.grid(row=8,column=5, padx=4, pady=4,sticky = 'se')


def createLabledEntryBoxes(parent, fields):

  entries = {}
  j = 1
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

  return entries
  
def saveEntries(entries, configName):
    
    entryVals = {}
    for field in entries.keys():
      entryVals[field] = entries[field].get()
    
    if configName == "Propellant":
      configurePropellantDict(entryVals)

    print(configs)

def configurePropellantDict(entryVals):
  configs["Propellant"] = {}
  configs["Propellant"]["tabs"] = {}
  configs["Propellant"]["name"] = entryVals["Propellant Name"]
  configs["Propellant"]["density"] = entryVals["Density - Kg/m^3"]
  configs["Propellant"]["tabs"]["maxPressure"] = entryVals["Max Pressure - Pa"]
  configs["Propellant"]["tabs"]["minPressure"] = entryVals["Min Pressure - Pa"]
  configs["Propellant"]["tabs"]["a"] = entryVals["Burn Rate Coefficient"]
  configs["Propellant"]["tabs"]["n"] = entryVals["Burn Rate Exponent"]
  configs["Propellant"]["tabs"]["k"] = entryVals["Specific Heat Ratio"]
  configs["Propellant"]["tabs"]["t"] = entryVals["Combustion Temperature - K"]
  configs["Propellant"]["tabs"]["m"] = entryVals["Exhaust Molar Mass - g/mol"]

def grainConfig(gui):
  pass

def OMConfig(gui):
  pass

def NIConfig(gui):
  pass

def preSavedConfig(gui):
  pass
  
def runImpulseCalc():
  pass

def runSeries():
  pass

def runCurativeCalculator():
  pass


if __name__ == '__main__':
  main()