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

# Custom files
import configureDictionaries
import FileUpload
import guiFunction

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

  impulseBtn = ttk.Button(functionsFrame, text="Impulse Calculator")
  impulseBtn.grid(row=2, column=0, sticky="nsew")

  curativeBtn = ttk.Button(functionsFrame, text="Curative Calculator")
  curativeBtn.grid(row=3, column=0, sticky="nsew")

  seriesBtn = ttk.Button(functionsFrame, text="Nozzle Iterator & Impulse Calculator")
  seriesBtn.grid(row=4,column=0, sticky="nsew")

  # Configurations 
  configsFrame = tk.Frame(gui)
  configsFrame.grid(row=0,column=1,sticky="nsew")

  configsFrame.rowconfigure([1, 2, 3, 4,5], weight=1)
  configsFrame.columnconfigure(0, weight=1)

  configsLabel = tk.Label(configsFrame, text="Settings")
  configsLabel.grid(row=0, column=0, sticky = "nsew")

  createConfigBtn = ttk.Button(configsFrame, text="Upload or Create Configs",
                               command=lambda: handleCreateConfig(gui))
  createConfigBtn.grid(row= 1, column=0, sticky="nsew")

  gui.mainloop()

def runNozzleIterator():
  config = fd.askopenfilename()
  if config is not None:  
    sub.run([sys.executable, "NozzleIterator/NozzleIterator.py", config], check=True)

def handleCreateConfig(gui):
  popup = tk.Toplevel(gui)
  
  popup.transient(gui) # Keep it on top of main window
  popup.grab_set()   

  popup.columnconfigure(0, weight=1)
  popup.columnconfigure(1, weight=2)
  popup.columnconfigure(2, weight=1)
  popup.geometry("1200x500") # width px by height px

  optionsFrame = tk.Frame(popup)
  optionsFrame.grid(row=0, column=0, rowspan=10, sticky='nsew')

  fakeLabelFrame =tk.Frame(popup)
  fakeLabelFrame.grid(row=0, column=1, sticky='nsew', padx=2)

  fakeFrame = tk.Frame(popup)
  fakeFrame.grid(row=1,column=1, sticky='nsew', padx=2)

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
  
  preSavedConfigLabel = tk.Button(optionsFrame, text="Upload complete preset",command=lambda: FileUpload.uploadConfig(popup, 'All'))
  preSavedConfigLabel.grid(row=8,column=0,sticky='nsew', pady=2)

  savedConfigs = tk.Button(optionsFrame, text="Save Current Configs",command=lambda: saveCurrentConfigs(popup))
  savedConfigs.grid(row=9,column=0,sticky='nsew', pady=2)

def createPropellant(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "Propellant Config"
  dropDown = None

  fields = [
            "Propellant Name", "Density - Kg/m^3", "Max Pressure - Pa", "Min Pressure - Pa",
            "Burn Rate Coefficient - m/(s*Pa^n)" , "Burn Rate Exponent", "Specific Heat Ratio",
            "Combustion Temperature - K", "Exhaust Molar Mass - g/mol"
            ]
    
  guiFunction.createSettingsPage(configs,labelName, fields, popup, dropDown)

def createOMsettings(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "OpenMotor settings Config - this program features default OM settings unless changed here"
  dropDown = None

  fields = [
            "Max Pressure - Pa", "Max Mass Flux - kg/(m^2*s)", "Max Mach Number", "Min Port Throat Ratio",
            "Flow Separation Precent - 0.##","Burnout Web Threshold - m","Burnout Thrust Threshold","Time step - s",
            "Ambient Pressure - Pa", "Grain Map Dimension", "Separation Pressure Ratio" 
            ]
  
  guiFunction.createSettingsPage(configs,labelName, fields, popup, dropDown)

def createNozzleIterator(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "Nozzle Iterator"
  dropDown = { 
                "Search Preference" : ["ISP", "ThrustCoef", "burnTime", "Impulse", "AvgThrust"], 
                "Parallel Simulation (Harder on computer)" : ["True", "False"]
              }

  fields = [
            "Min Throat Diameter - m", "Max Throat Diameter - m", "Min Throat Length - m", "Max Throat Length - m",
            "Exit Half Angle - deg","Slag Coefficient - (m*Pa)/s","Erosion Coefficient - s/(m*Pa)","Efficiency - 0.##",
            "Nozzle Diameter - m", "Nozzle Length - m", "Min Conv Half Angle - deg", "Max Conv Half Angle - deg",
            "Iteraton Step Size - m", " # Threads to allocate for simulation"
            ]
  
  guiFunction.createSettingsPage(configs,labelName, fields, popup, dropDown)


def createGrainGeometry(popup):
  guiFunction.clearWidgetColumn(popup, 1)

  def refresh():
        createGrainGeometry(popup) 

  labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  labelFrame.grid(row=0,column=1, sticky='nsew',columnspan=1, padx=2)
  
  buttonFrame = tk.Frame(popup)
  buttonFrame.grid(row=1,column=1,sticky= 'nsew', padx=2,columnspan=1)

  frameLabel = tk.Label(labelFrame, text="Grain Geometry Configurator", anchor="center", justify="center")
  frameLabel.grid(row=0, column=0, sticky = 'nsew', padx=2,columnspan=1)

  labelFrame.columnconfigure(0, weight=1)
  buttonFrame.rowconfigure(0,weight=0)

  functionFrame = tk.Frame(popup)
  functionFrame.grid(row=2,column=1,sticky='nsew')

  functionFrame.rowconfigure([0,1,2,3], weight=1)
  functionFrame.columnconfigure([0,1,2,3], weight=1)
  
  addGrainButton = tk.Button(buttonFrame, text="Add Grain", command=lambda: addGrains(functionFrame, refresh))
  addGrainButton.grid(row=0, column=0, padx=10, pady=15)

  if "Grains" in configs and configs["Grains"] is not None:
    deleteGrainButton = tk.Button(buttonFrame, text="Delete Grains", command=lambda: deleteGrains(functionFrame))
    deleteGrainButton.grid(row=0,column=1,padx=10,pady=15)

    viewGrainsButton = tk.Button(buttonFrame, text="View Grains", command=lambda: viewGrains(functionFrame))
    viewGrainsButton.grid(row=0, column=2, padx=10,pady=15)

    copyGrainsButton = tk.Button(buttonFrame, text="Copy Grains", command=lambda: copyGrains(functionFrame))
    copyGrainsButton.grid(row=0, column=3, padx=10,pady=15)


    
def addGrains(frame, refreshCall):

  grainSelectFrame = tk.Frame(frame)
  grainSelectFrame.grid(row=0,column=0,sticky='nsew')

  grainAdditionFrame = tk.Frame(frame)
  grainAdditionFrame.grid(row=1,column=0,sticky = 'nsew')

  grainSelect = ttk.Combobox(grainSelectFrame, values=["BATES","FINOCYL"])
  grainSelect.grid(row=0,column=0,sticky='nsew', padx=14, pady=6)
  grainSelect.set("Select Grain")

  grainSelectaddButton = tk.Button(grainSelectFrame, text="Set", command=lambda: addGrainWindow(grainAdditionFrame,
                                                                                                 grainSelect.get(), 
                                                                                                 refreshCall))
  grainSelectaddButton.grid(row=0,column=1,sticky='nsew')

  grainAdditionFrame.rowconfigure(0,weight=1)

def addGrainWindow(frame, type, refreshCall):

  if type == "BATES":
    dropDown = { 
                  "Inhibited Ends" : ["Top", "Bottom", "Neither"], 
                }

    fields = [
              "Core Diameter - m", "Diameter - m", "Length - m" 
              ]
  elif type == "FINOCYL":

    dropDown = { 
                  "Inhibited Ends" : ["Top", "Bottom", "Neither"], 
                  "Inverted Fins" : ["True", "False"]
                }

    fields = [
              "Core Diameter - m", "Diameter - m", "Length - m", "Number of Fins", "Fin Length - m",
              "Fin Width - m"
              ]
    
  frame = guiFunction.clear(frame)

  entries = guiFunction.createLabledEntryBoxes(frame, fields, dropDown)

  saveButton = tk.Button(frame, text="Save Config", command=lambda: (guiFunction.saveEntries(configs,entries,"Grain", type), refreshCall()),
                        borderwidth=1, relief="solid")
  
  saveButton.grid(row=8,column=5, padx=4, pady=4, sticky = 'se')
  
def saveCurrentConfigs(popup):

  guiFunction.createLabelFrame(popup, "Save Settings")
  frame = guiFunction.createBaseFrame(popup)

  saveButton = tk.Button(frame, text='Save', command=lambda:FileUpload.cfgToJson(configs,frame))
  saveButton.grid(row=0,column=0)
  

if __name__ == '__main__':
  main()