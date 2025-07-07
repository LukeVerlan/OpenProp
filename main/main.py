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
import json


def main(): 

  global configs

  configs = {}

  # Apply default OpenMotor Settings
  configs["Motor"] = {

        "SimulationParameters" : {
            "maxPressure" : 10000000,
            "maxMassFlux" : 1406,
            "maxMachNumber" : 0.8,
            "minPortThroat" : 2,
            "flowSeparationWarnPercent" : 0.15
        },

        "SimulationBehavior" : {
            "burnoutWebThres" : 0.000025,
            "burnoutThrustThres" : 0.001,
            "timestep" : 0.03,
            "ambPressure" : 101325,
            "mapDim" : 750,
            "sepPressureRatio" : 0.3
        }
    }

  # initialize main GUI page
  gui = tk.Tk()
  gui.title('OpenProp')

  gui.geometry("600x480")

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
  popup.geometry("1000x300") # width px by height px

  optionsFrame = tk.Frame(popup)
  optionsFrame.grid(row=0, column=0, rowspan=10, sticky='nsew')

  fakeLabelFrame =tk.Frame(popup)
  fakeLabelFrame.grid(row=0, column=2, sticky='nsew', padx=2)
  fakeFrame = tk.Frame(popup)
  fakeFrame.grid(row=1,column=2, sticky='nsew', padx=2)

  propConfigLabel = tk.Button(optionsFrame, text="Create Propellant",command=lambda: createPropellant(popup))
  propConfigLabel.grid(row=0,column=0,sticky='nsew', pady=2)

  grainConfigLabel = tk.Button(optionsFrame, text="Create Grain Geometry",command=lambda: createGrainGeometry(popup))
  grainConfigLabel.grid(row=1,column=0,sticky='nsew', pady=2)

  NIConfigLabel = tk.Button(optionsFrame, text="Create Nozzle Iterator Config",command=lambda: createNozzleIterator(popup))
  NIConfigLabel.grid(row=2,column=0,sticky='nsew', pady=2)

  OMConfigLabel = tk.Button(optionsFrame, text="Create OpenMotor settings config",command=lambda: createOMsettings(popup))
  OMConfigLabel.grid(row=3,column=0,sticky='nsew', pady=2)
  
  propUploadLabel = tk.Button(optionsFrame, text="Upload Propellant config",command=lambda: uploadPropellant(popup))
  propUploadLabel.grid(row=4,column=0,sticky='nsew', pady=2)

  grainUploadLabel = tk.Button(optionsFrame, text="Upload Grain config",command=lambda: uploadGrainGeometry(popup))
  grainUploadLabel.grid(row=5,column=0,sticky='nsew', pady=2)

  NIUploadLabel = tk.Button(optionsFrame, text="Upload Nozzle Iterator Config",command=lambda: uploadNozzleIterator(popup))
  NIUploadLabel.grid(row=6,column=0,sticky='nsew', pady=2)

  OMCUploadLabel = tk.Button(optionsFrame, text="Uplaod Open Motor config",command=lambda: uploadOMsettings(popup))
  OMCUploadLabel.grid(row=7,column=0,sticky='nsew', pady=2)
  
  preSavedConfigLabel = tk.Button(optionsFrame, text="Upload complete preset",command=lambda: uploadPreSavedsettings(popup))
  preSavedConfigLabel.grid(row=8,column=0,sticky='nsew', pady=2)

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

      label = tk.Label(parent, text=dropDown[0])
      label.grid(row=j,column=i+1,sticky='nsew', padx=14, pady=6)

      comboBox = ttk.Combobox(parent, values=dropDown[1])
      comboBox.grid(row=j+1,column=i+1,sticky='nsew', padx=14, pady=6)
      comboBox.set("Select Preference")

      entries[dropDown[0]] = comboBox

    currIndex += 1

  return entries
  
def saveEntries(entries, configName):
    
    entryVals = {}
    for field in entries.keys():
      entryVals[field] = entries[field].get()
    
    if configName == "Propellant":
      configurePropellantDict(entryVals)
    elif configName == "OMsetting":
      configureOMDict(entryVals)
    elif configName == "NozzleIterator":
      configureNIDict(entryVals)
    elif configName == "Grain":
      configureGrains(entryVals)

    print(configs)

def createPropellant(popup):

  saveRow = 8
  labelName = "Propellant Config"
  dropDown = None
  saveName = "Propellant"

  fields = [
            "Propellant Name", "Density - Kg/m^3", "Max Pressure - Pa", "Min Pressure - Pa",
            "Burn Rate Coefficient - m/(s*Pa^n)" , "Burn Rate Exponent", "Specific Heat Ratio",
            "Combustion Temperature - K", "Exhaust Molar Mass - g/mol"
            ]
    
  createSettingsPage(labelName, fields, saveRow, popup, dropDown, saveName)

def grainConfig(gui):
  pass

def createOMsettings(popup):
  labelName = "OpenMotor settings Config"
  saveRow = 8
  dropDown = None
  saveName = "OMsetting"

  fields = [
            "Max Pressure - Pa", "Max Mass Flux - kg/(m^2*s)", "Max Mach Number", "Min Port Throat Ratio",
            "Flow Separation Precent - 0.##","Burnout Web Threshold - m","Burnout Thrust Threshold","Time step - s",
            "Ambient Pressure - Pa", "Grain Map Dimension", "Separation Pressure Ratio" 
            ]
  
  createSettingsPage(labelName, fields, saveRow, popup, dropDown, saveName)

def createNozzleIterator(popup):
  labelName = "Nozzle Iterator"
  saveRow = 8
  dropDown = ["Search Preference", ["ISP", "ThrustCoef", "burnTime", "Impulse", "AvgThrust"]]
  saveName = "NozzleIterator"

  fields = [
            "Min Throat Diameter - m", "Max Throat Diameter - m", "Min Throat Length - m", "Max Throat Length - m",
            "Exit Half Angle - deg","Slag Coefficient - (m*Pa)/s","Erosion Coefficient - s/(m*Pa)","Efficiency - 0.##",
            "Nozzle Diameter - m", "Nozzle Length - m", "Min Half Convergence Angle - deg", "Max Half Convergence Angle - deg",
            "Iteraton Step Size - m"
            ]
  
  createSettingsPage(labelName, fields, saveRow, popup, dropDown, saveName)

def createSettingsPage(labelName, fields, saveRow, popup, dropDown, saveName):

  frame = tk.Frame(popup, borderwidth=1, relief="solid")
  frame.grid(row=1, column=2, sticky= 'nsew')

  labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  labelFrame.grid(row=0,column=2, sticky='nsew')

  labelFrame.columnconfigure(0, weight=1)

  frame.rowconfigure([0,1,2,3], weight=1)
  frame.columnconfigure([0,1,2,3], weight=1)
  
  propLabel = tk.Label(labelFrame, text=labelName, anchor="center", justify="center")
  propLabel.grid(row=0, column=0, sticky = 'nsew')

  entries = createLabledEntryBoxes(frame, fields, dropDown)

  saveButton = tk.Button(frame, text="Save Config", command=lambda: saveEntries(entries,saveName),
                        borderwidth=1, relief="solid")
  
  saveButton.grid(row=saveRow,column=5, padx=4, pady=4, sticky = 'se')


def preSavedConfig(gui):
  pass
  
def runImpulseCalc():
  pass

def runSeries():
  pass

def runCurativeCalculator():
  pass

def configurePropellantDict(entryVals):
  configs["Propellant"] = {}
  configs["Propellant"]["tabs"] = {}
  configs["Propellant"]["name"] = entryVals["Propellant Name"]
  configs["Propellant"]["density"] = entryVals["Density - Kg/m^3"]
  configs["Propellant"]["tabs"]["maxPressure"] = entryVals["Max Pressure - Pa"]
  configs["Propellant"]["tabs"]["minPressure"] = entryVals["Min Pressure - Pa"]
  configs["Propellant"]["tabs"]["a"] = entryVals["Burn Rate Coefficient - m/(s*Pa^n)"]
  configs["Propellant"]["tabs"]["n"] = entryVals["Burn Rate Exponent"]
  configs["Propellant"]["tabs"]["k"] = entryVals["Specific Heat Ratio"]
  configs["Propellant"]["tabs"]["t"] = entryVals["Combustion Temperature - K"]
  configs["Propellant"]["tabs"]["m"] = entryVals["Exhaust Molar Mass - g/mol"]

def configureOMDict(entryVals):
  configs["Motor"]["SimulationParameters"]["maxPressure"] = entryVals["Max Pressure - Pa"]
  configs["Motor"]["SimulationParameters"]["maxMassFlux"] = entryVals["Max Mass Flux - kg/(m^2*s)"]
  configs["Motor"]["SimulationParameters"]["maxMachNumber"] = entryVals["Max Mach Number"]
  configs["Motor"]["SimulationParameters"]["minPortThroat"] = entryVals["Min Port Throat Ratio"]
  configs["Motor"]["SimulationParameters"]["flowSeparationWarmPercent"] = entryVals["Flow Separation Precent - 0.##"]
  configs["Motor"]["SimulationBehavior"]["burnoutWebThres"] = entryVals["Burnout Web Threshold - m"]
  configs["Motor"]["SimulationBehavior"]["burnoutThrustThrus"] = entryVals["Burnout Thrust Threshold"]
  configs["Motor"]["SimulationBehavior"]["timestep"] = entryVals["Time step - s"]
  configs["Motor"]["SimulationBehavior"]["ambPressure"] = entryVals["Ambient Pressure - Pa"]
  configs["Motor"]["SimulationBehavior"]["mapDim"] = entryVals["Grain Map Dimension"]
  configs["Motor"]["SimulationBehavior"]["sepPressureRatio"] = entryVals["Separation Pressure Ratio"]

def configureNIDict(entryVals):
  configs["Nozzle"] = {}
  configs["Nozzle"]["minDia"] = entryVals["Min Throat Diameter - m"]
  configs["Nozzle"]["maxDia"] = entryVals["Max Throat Diameter - m"]
  configs["Nozzle"]["minLen"] = entryVals["Min Throat Length - m"]
  configs["Nozzle"]["maxLen"] = entryVals["Min Throat Length - m"]
  configs["Nozzle"]["exitHalf"] = entryVals["Exit Half Angle - deg"]
  configs["Nozzle"]["SlagCoef"] = entryVals["Slag Coefficient - (m*Pa)/s"]
  configs["Nozzle"]["ErosionCoef"] = entryVals["Erosion Coefficient - s/(m*Pa)"]
  configs["Nozzle"]["Efficiency"] = entryVals["Efficiency - 0.##"]
  configs["Nozzle"]["nozzleDia"] = entryVals["Nozzle Diameter - m"]
  configs["Nozzle"]["nozzleLength"] = entryVals["Nozzle Length - m"]
  configs["Nozzle"]["minHalfConv"] = entryVals["Min Half Convergence Angle - deg"]
  configs["Nozzle"]["maxHalfConv"] = entryVals["Max Half Convergence Angle - deg"]
  configs["Nozzle"]["nozzleDia"] = entryVals["Nozzle Diameter - m"]
  configs["Nozzle"]["iteration_step_size"] = entryVals["Iteraton Step Size - m"]
  configs["Nozzle"]["preference"] = entryVals["Search Preference"]

if __name__ == '__main__':
  main()