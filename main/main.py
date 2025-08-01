# MAIN
#
# Handles user input are calls upon sub files depending on what the user wants to do 

# File handling libraries
import os 
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# GUI library
import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog as fd 
from PIL import Image, ImageTk

# Python libraries
import re
import json
import copy
import matplotlib.pyplot as plt

# Custom files
import FileUpload
import guiFunction

# Tool Files
from NozzleIterator import NozzleIterator
from impulseCalc import ImpulseCalculator
from CurativeCalculator import CurativeCalculator

# @Breif Main function of OpenProp, initializes the GUI and sets up the main page
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
  
  # ----------------------------------------------------
  # FOR UPLOAD DEV WORK COMMENT OUT FOR USER EXPERIENCE
  # ----------------------------------------------------

  with open('./NozzleIterator/config.json', 'r') as file:
    configs = json.load(file)
    

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
                         command=lambda: NozzleIteratorGUI(gui))
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

  configsFrame.rowconfigure([1, 2, 3, 4, 5], weight=1)
  configsFrame.columnconfigure(0, weight=1)

  configsLabel = tk.Label(configsFrame, text="Settings")
  configsLabel.grid(row=0, column=0, sticky = "nsew")

  createConfigBtn = ttk.Button(configsFrame, text="Config Settings",
                               command=lambda: handleCreateConfig(gui))
  createConfigBtn.grid(row= 1, column=0, sticky="nsew")

  gui.mainloop()

def NozzleIteratorGUI(gui):

  OPimDir = "main/OpenPropLogo.png"
  OPim = Image.open(OPimDir)
  resizedOPim = OPim.resize((200,625))
  tk_OPim = ImageTk.PhotoImage(resizedOPim)

  popup=tk.Toplevel()

  popup.transient(gui) # Keep it on top of main window
  popup.grab_set()   

  popup.geometry("1061x720")
  popup.resizable(False, False) #bastard man

  labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  labelFrame.grid(row=0, column=0, sticky='nsew')

  labelFrame.columnconfigure(0, weight=1)
  labelFrame.rowconfigure([0,1], weight=1)

  logoFrame= tk.Frame(popup, borderwidth=1, relief='solid')
  logoFrame.grid(row=1, column=0,sticky='nsw')

  logoLabel = tk.Label(logoFrame,image=tk_OPim)
  logoLabel.grid(row=0,column=0, sticky='nsew')

  logoLabel.image = tk_OPim

  graphsFrame = tk.Frame(popup)
  graphsFrame.grid(row=0, column=1, sticky='nsew',rowspan=2)
  graphsFrame.rowconfigure([0,1,2,3], weight=1)

  functionsFrame = tk.Frame(popup, borderwidth=1, relief='solid')
  functionsFrame.grid(row=0, column=2, sticky='nsew', rowspan=2)

  functionsFrame.columnconfigure(0,weight=1)

  # Create a label for the Nozzle Iterator
  label = tk.Label(labelFrame, text="Nozzle Iterator Configuration")
  label.grid(row=0, column=0, pady=1, sticky='nsew')
  
  exitButton = tk.Button(labelFrame, text="exit", command=lambda: (plt.close('all'), popup.destroy()), borderwidth=1, relief='solid')
  exitButton.grid(row=3,column=0, pady=1, sticky='nsew')
  

  if FileUpload.hasConfigs(configs, 'All'):
    isValidLabel = tk.Label(labelFrame, text="Valid Config Found")
    isValidLabel.grid(row=1, column=0, pady=2, padx=2, sticky='nsew')

    runButton = tk.Button(labelFrame, text="Run Nozzle Iterator",
                           command= lambda:runNozzleIterator(), borderwidth=1, relief='solid')
    runButton.grid(row=2,column=0,sticky='nsew')

    def runNozzleIterator():
      runningLabel = tk.Label(graphsFrame, text="Running...")
      runningLabel.grid(row=0,column=0,sticky='ew', columnspan=2)
      popup.update()

      NIconfig = copy.deepcopy(configs)

      result = NozzleIterator.main(NIconfig)

      if result is not None:
        
        simImage = result.plotSim()
        resized = simImage.resize((700, 440))
        tk_simImage = ImageTk.PhotoImage(resized)

        simSuccesslabel = tk.Label(graphsFrame, text="Simulation Results")
        simSuccesslabel.grid(row=0,column=0,sticky='ew', columnspan=2)

        simGraph = tk.Label(graphsFrame, image=tk_simImage, borderwidth=1, relief='solid')
        simGraph.grid(row=1,column=0, sticky='nsew', pady=2, columnspan=2)
        simGraph.image = tk_simImage

        simResultsPeak = tk.Label(graphsFrame, text=result.peakValues())
        simResultsPeak.grid(row=2,column=0, sticky= 'nsew', pady=2)

        simResultsGeneral = tk.Label(graphsFrame, text= result.generalValues())
        simResultsGeneral.grid(row=2, column=1, sticky='nsew', pady=2)

        nozzleResults = tk.Label(graphsFrame, text=result.nozzleStatistics(), borderwidth=1, relief='solid')
        nozzleResults.grid(row=3,column=0, sticky='nsew', pady=2, columnspan=2)

        printAsCSVbutton = tk.Button(functionsFrame, text='Save Thrust Curve as CSV', 
                                     command=lambda: result.exportThrustCurve(fd.asksaveasfilename()),
                                     borderwidth=1, relief='solid')
        printAsCSVbutton.grid(row=0, column=0, sticky='nsew')

        saveButton = tk.Button(functionsFrame, text='Save Nozzle Statistics as txt', 
                              command=lambda: result.exportNozzleStats(fd.asksaveasfilename()),
                              borderwidth=1, relief='solid')
        saveButton.grid(row=1, column=0, sticky='nsew', pady = 2 )
      else:
        # Handle failed criteria like a boss
        simFailLabel = tk.Label(graphsFrame, text="No valid nozzle found, please change your settings")
        simFailLabel.grid(row=0,column=0,sticky='ew', columnspan=2)

  else:
    isValidLabel = tk.Label(labelFrame, text="No valid config found, please upload or create a config")
    isValidLabel.grid(row=0, column=0, sticky='nsew')

  # Create a button to run the Nozzle Iterator
  

def ImpulseCalculatorGUI(gui):

  OPimDir = "main/OpenPropLogo.png"
  OPim = Image.open(OPimDir)
  resizedOPim = OPim.resize((200,625))
  tk_OPim = ImageTk.PhotoImage(resizedOPim)

  popup=tk.Toplevel()

  popup.transient(gui) # Keep it on top of main window
  popup.grab_set()   

  popup.geometry("950x720")
  popup.resizable(False, False) #bastard man

  labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  labelFrame.grid(row=0, column=0, sticky='nsew')

  logoFrame= tk.Frame(popup, borderwidth=1, relief='solid')
  logoFrame.grid(row=1, column=0,sticky='nsw')

  logoLabel = tk.Label(logoFrame,image=tk_OPim)
  logoLabel.grid(row=0,column=0, sticky='nsew')

  logoLabel.image = tk_OPim

  graphsFrame = tk.Frame(popup)
  graphsFrame.grid(row=0, column=1, sticky='nsew',rowspan=2)
  graphsFrame.rowconfigure([0,1,2,3], weight=1)

  # Create a label for the Nozzle Iterator
  label = tk.Label(labelFrame, text="Impulse Calculator Configuration")
  label.grid(row=0, column=0, pady=1, sticky='ew')
  
  exitButton = tk.Button(labelFrame, text="exit", command=lambda: (plt.close('all'), popup.destroy()), borderwidth=1, relief='solid')
  exitButton.grid(row=3,column=0, pady=1, sticky='nsew')
  
  if FileUpload.hasConfigs(configs, 'All'):
    isValidLabel = tk.Label(labelFrame, text="Valid Config Found")
    isValidLabel.grid(row=1, column=0, pady=2, padx=2, sticky='ew')

    runButton = tk.Button(labelFrame, text="Run Nozzle Iterator",
                           command= lambda:runImpulseCalcualtor(), borderwidth=1, relief='solid')
    runButton.grid(row=2,column=0,sticky='nsew')


  def runImpulseCalcualtor():
      runningLabel = tk.Label(graphsFrame, text="Running...")
      runningLabel.grid(row=0,column=0,sticky='ew', columnspan=2)
      popup.update()

      NIconfig = copy.deepcopy(configs)
      jsonNI = json.dumps(NIconfig, indent=4)

      result = ImpulseCalculator.main(jsonNI)
    

# @Brief Handles the creation of the configuration GUI, allows user to create or upload configs
# @param gui - The main GUI window
def handleCreateConfig(gui):
  popup = tk.Toplevel(gui)
  
  popup.transient(gui) # Keep it on top of main window
  popup.grab_set()   

  popup.columnconfigure(0, weight=1)
  popup.columnconfigure(1, weight=2)
  popup.columnconfigure(2, weight=1)
  popup.geometry("1200x600") # width px by height px
  popup.resizable(False, False)

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
  
  ICConfigLabel = tk.Button(optionsFrame, text="Create Impulse Calculator config",command=lambda: createImpulseCalculator(popup))
  ICConfigLabel.grid(row=4,column=0,sticky='nsew', pady=2)

  ICUploadLabel = tk.Button(optionsFrame, text="Upload Impulse Calculator config",command=lambda: FileUpload.uploadConfig(popup, configs, 'ImpulseCalculator'))
  ICUploadLabel.grid(row=5,column=0,sticky='nsew', pady=2)

  propUploadLabel = tk.Button(optionsFrame, text="Upload Propellant config",command=lambda:FileUpload.uploadConfig(popup, configs, 'Propellant'))
  propUploadLabel.grid(row=6,column=0,sticky='nsew', pady=2)

  grainUploadLabel = tk.Button(optionsFrame, text="Upload Grain config",command=lambda: FileUpload.uploadConfig(popup, configs,'Grains'))
  grainUploadLabel.grid(row=7,column=0,sticky='nsew', pady=2)

  NIUploadLabel = tk.Button(optionsFrame, text="Upload Nozzle Iterator Config",command=lambda: FileUpload.uploadConfig(popup, configs, 'Nozzle'))
  NIUploadLabel.grid(row=8,column=0,sticky='nsew', pady=2)

  OMCUploadLabel = tk.Button(optionsFrame, text="Uplaod Open Motor config",command=lambda:FileUpload.uploadConfig(popup, configs, 'Motor'))
  OMCUploadLabel.grid(row=9,column=0,sticky='nsew', pady=2)
  
  preSavedConfigLabel = tk.Button(optionsFrame, text="Upload complete preset",command=lambda: FileUpload.uploadConfig(popup, configs, 'All'))
  preSavedConfigLabel.grid(row=10,column=0,sticky='nsew', pady=2)

  propSaveLabel = tk.Button(optionsFrame, text="Save Propellant config",command=lambda: saveCurrentConfigs(popup, 'Propellant'))
  propSaveLabel.grid(row=11,column=0,sticky='nsew', pady=2)

  grainSaveLabel = tk.Button(optionsFrame, text="Save Grain config",command=lambda: saveCurrentConfigs(popup, 'Grains'))
  grainSaveLabel.grid(row=12,column=0,sticky='nsew', pady=2)

  NIUSaveLabel = tk.Button(optionsFrame, text="Save Nozzle Iterator Config",command=lambda: saveCurrentConfigs(popup, 'Nozzle'))
  NIUSaveLabel.grid(row=13,column=0,sticky='nsew', pady=2)

  OMSaveLabel = tk.Button(optionsFrame, text="Save Open Motor config",command=lambda: saveCurrentConfigs(popup, 'Motor'))
  OMSaveLabel.grid(row=14,column=0,sticky='nsew', pady=2)

  saveConfigs = tk.Button(optionsFrame, text="Save All Current Configs",command=lambda: saveCurrentConfigs(popup, 'All'))
  saveConfigs.grid(row=15,column=0,sticky='nsew', pady=2)

  ICSaveLabel = tk.Button(optionsFrame, text="Save Impulse Calculator config",command=lambda: saveCurrentConfigs(popup, 'ImpulseCalculator'))
  ICSaveLabel.grid(row=16,column=0,sticky='nsew', pady=2)

# @Brief Creates the propellant configuration GUI
# @param popup - The popup window where the propellant configuration will be created
def createPropellant(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "Propellant Config"

  fields = [
            "Propellant Name", "Density - Kg/m^3", "Max Pressure - Pa", "Min Pressure - Pa",
            "Burn Rate Coefficient - m/(s*Pa^n)" , "Burn Rate Exponent", "Specific Heat Ratio",
            "Combustion Temperature - K", "Exhaust Molar Mass - g/mol"
            ]
  
  if "Propellant" in configs and configs["Propellant"] is not None:
    defaults = {
        "Propellant Name": configs["Propellant"].get("name", ""),
        "Density - Kg/m^3": configs["Propellant"].get("density", ""),
        "Max Pressure - Pa": configs["Propellant"]["tabs"][0].get("maxPressure", ""),
        "Min Pressure - Pa": configs["Propellant"]["tabs"][0].get("minPressure", ""),
        "Burn Rate Coefficient - m/(s*Pa^n)": configs["Propellant"]["tabs"][0].get("a", ""),
        "Burn Rate Exponent": configs["Propellant"]["tabs"][0].get("n", ""),
        "Specific Heat Ratio": configs["Propellant"]["tabs"][0].get("k", ""),
        "Combustion Temperature - K": configs["Propellant"]["tabs"][0].get("t", ""),
        "Exhaust Molar Mass - g/mol": configs["Propellant"]["tabs"][0].get("m", "")
    }
  else:
    defaults = None
    
  guiFunction.createSettingsPage(configs, labelName, fields, popup, defaults=defaults)

# @Brief Creates the OpenMotor settings configuration GUI
# @param popup - The popup window where the OpenMotor settings configuration will be created
def createOMsettings(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "OpenMotor settings Config - this program features default OM settings unless changed here"

  fields = [
            "Max Pressure - Pa", "Max Mass Flux - kg/(m^2*s)", "Max Mach Number", "Min Port Throat Ratio",
            "Flow Separation Precent - 0.##","Burnout Web Threshold - m","Burnout Thrust Threshold","Time step - s",
            "Ambient Pressure - Pa", "Grain Map Dimension", "Separation Pressure Ratio" 
            ]
  
  if "Motor" in configs and configs["Motor"] is not None:
    defaults = {
        "Max Pressure - Pa": configs["Motor"]["SimulationParameters"].get("maxPressure", ""),
        "Max Mass Flux - kg/(m^2*s)": configs["Motor"]["SimulationParameters"].get("maxMassFlux", ""),
        "Max Mach Number": configs["Motor"]["SimulationParameters"].get("maxMachNumber", ""),
        "Min Port Throat Ratio": configs["Motor"]["SimulationParameters"].get("minPortThroat", ""),
        "Flow Separation Precent - 0.##": configs["Motor"]["SimulationParameters"].get("flowSeparationWarnPercent", ""),
        "Burnout Web Threshold - m": configs["Motor"]["SimulationBehavior"].get("burnoutWebThres", ""),
        "Burnout Thrust Threshold": configs["Motor"]["SimulationBehavior"].get("burnoutThrustThres", ""),
        "Time step - s": configs["Motor"]["SimulationBehavior"].get("timestep", ""),
        "Ambient Pressure - Pa": configs["Motor"]["SimulationBehavior"].get("ambPressure", ""),
        "Grain Map Dimension": configs["Motor"]["SimulationBehavior"].get("mapDim", ""),
        "Separation Pressure Ratio": configs["Motor"]["SimulationBehavior"].get("sepPressureRatio", "")
    }
  else:
    defaults = None
  
  guiFunction.createSettingsPage(configs,labelName, fields, popup, defaults=defaults)

# @Brief Creates the Nozzle Iterator configuration GUI
# @param popup - The popup window where the Nozzle Iterator configuration will be created
def createNozzleIterator(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "Nozzle Iterator"
  dropDown = { 
                "Search Preference" : ["ISP", "ThrustCoef", "BurnTime", "Impulse", "AvgThrust"], 
                "Parallel Simulation (Harder on computer)" : ["True", "False"]
              }

  fields = [
            "Min Throat Diameter - m", "Max Throat Diameter - m", "Min Throat Length - m", "Max Throat Length - m", "Exit Diameter - m",
            "Exit Half Angle - deg","Slag Coefficient - (m*Pa)/s","Erosion Coefficient - s/(m*Pa)","Efficiency - 0.##",
            "Nozzle Diameter - m", "Nozzle Length - m", "Min Conv Half Angle - deg", "Max Conv Half Angle - deg",
            "Iteraton Step Size - m", "# Threads to allocate for simulation"
            ]
  
  if "Nozzle" in configs and configs["Nozzle"] is not None:
    defaults = {
        "Min Throat Diameter - m": configs["Nozzle"].get("minDia", ""),
        "Max Throat Diameter - m": configs["Nozzle"].get("maxDia", ""),
        "Min Throat Length - m": configs["Nozzle"].get("minLen", ""),
        "Max Throat Length - m": configs["Nozzle"].get("maxLen", ""),
        "Exit Half Angle - deg": configs["Nozzle"].get("exitHalf", ""),
        "Slag Coefficient - (m*Pa)/s": configs["Nozzle"].get("SlagCoef", ""),
        "Erosion Coefficient - s/(m*Pa)": configs["Nozzle"].get("ErosionCoef", ""),
        "Efficiency - 0.##": configs["Nozzle"].get("Efficiency", ""),
        "Nozzle Diameter - m": configs["Nozzle"].get("nozzleDia", ""),
        "Nozzle Length - m": configs["Nozzle"].get("nozzleLength", ""),
        "Min Conv Half Angle - deg": configs["Nozzle"].get("minHalfConv", ""),
        "Max Conv Half Angle - deg": configs["Nozzle"].get("maxHalfConv", ""),
        "Iteraton Step Size - m": configs["Nozzle"].get("iteration_step_size", ""),
        "# Threads to allocate for simulation": configs["Nozzle"].get("iteration_threads", ""),
        "Search Preference": configs["Nozzle"].get("preference", ""),
        "Parallel Simulation (Harder on computer)": configs["Nozzle"].get("parallel_mode", ""),
        "Exit Diameter - m": configs["Nozzle"].get("exitDia", "")
    }
  else:
    defaults = None
  
  guiFunction.createSettingsPage(configs, labelName, fields, popup, dropDown=dropDown, defaults=defaults)

# @Brief Saves the current configurations to a JSON file
# @param popup - The popup window where the configurations are saved

def createImpulseCalculator(popup):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "Impulse Calculator Config"

  fields = [
            "surfacePressure", "surfaceTemperature", "windVelocity", "railAngle", "launchSiteElevation",
            "dragArea", "dragCoefficient", "noMotorMass", "specificImpulse", "desiredApogee", "apogeeThreshold", 
            "burnTimeRange", "burnTimeStep", "minAvgTtW", "bisectionBoundPercDiff", "deltaT"
  ]  

  if "ImpulseCalculator" in configs and configs["ImpulseCalculator"] is not None:
    defaults = {
        "Min Throat Diameter - m": configs["Nozzle"].get("minDia", ""),
        "Max Throat Diameter - m": configs["Nozzle"].get("maxDia", ""),
        "Min Throat Length - m": configs["Nozzle"].get("minLen", ""),
        "Max Throat Length - m": configs["Nozzle"].get("maxLen", ""),
        "Exit Half Angle - deg": configs["Nozzle"].get("exitHalf", ""),
        "Slag Coefficient - (m*Pa)/s": configs["Nozzle"].get("SlagCoef", ""),
        "Erosion Coefficient - s/(m*Pa)": configs["Nozzle"].get("ErosionCoef", ""),
        "Efficiency - 0.##": configs["Nozzle"].get("Efficiency", ""),
        "Nozzle Diameter - m": configs["Nozzle"].get("nozzleDia", ""),
        "Nozzle Length - m": configs["Nozzle"].get("nozzleLength", ""),
        "Min Conv Half Angle - deg": configs["Nozzle"].get("minHalfConv", ""),
        "Max Conv Half Angle - deg": configs["Nozzle"].get("maxHalfConv", ""),
        "Iteraton Step Size - m": configs["Nozzle"].get("iteration_step_size", ""),
        "# Threads to allocate for simulation": configs["Nozzle"].get("iteration_threads", ""),
        "Search Preference": configs["Nozzle"].get("preference", ""),
        "Parallel Simulation (Harder on computer)": configs["Nozzle"].get("parallel_mode", ""),
        "Exit Diameter - m": configs["Nozzle"].get("exitDia", "")
    }

# @brief creates a save page including a save button
# @param popup - window that conatins the current 
# @param type - the type of config that you are saving
def saveCurrentConfigs(popup, type):

  guiFunction.clearWidgetColumn(popup, 1)

  guiFunction.createLabelFrame(popup, "Save " + type + " Settings")
  frame = guiFunction.createBaseFrame(popup)
  
  frame.rowconfigure(0,weight=1)

  if FileUpload.hasConfigs(configs, type):
    if type == 'All':
      cfg = configs
    elif type == 'Grains': 
      cfg = configs['Grains']
    elif type == 'Propellant':
      cfg = configs['Propellant']

    elif type == 'Motor':
      cfg = configs['Motor']
    elif type == 'Nozzle':
      cfg = configs['Nozzle']

    saveButton = tk.Button(frame, text='Save', command=lambda:FileUpload.cfgToJson(cfg, frame))
    saveButton.grid(row=0,column=0, sticky="ew")
  else:
    invalidLabel = tk.Label(frame,text= type + " Config Not Found")
    invalidLabel.grid(row=0, column=0, sticky='ew')

# @Brief Creates the grain geometry configuration GUI
# @param popup - The popup window where the grain geometry configuration will be created
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


# @Brief Adds a grain to the grain geometry configuration GUI
# @param frame - The frame where the grain will be added
def addGrains(frame, refreshCall):

  frame = guiFunction.clear(frame)

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

# @Brief Adds a grain window to the grain geometry configuration GUI
# @param frame - The frame where the grain window will be added
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

  saveButton = tk.Button(frame, text="Save Config", command=lambda: (guiFunction.saveEntries(configs, entries, "Grain", type, frame), refreshCall()),
                        borderwidth=1, relief="solid")
  
  saveButton.grid(row=9,column=5, padx=4, pady=4, sticky = 'se')

# @Brief Displays the grains in the grain geometry configuration GUI
# @param functionFrame - The frame where the grains will be displayed
def viewGrains(functionFrame):

  functionFrame = guiFunction.clear(functionFrame)

  num_grains = len(configs['Grains'])
  for i in range(num_grains):
    functionFrame.columnconfigure(i, weight=1)

  guidanceLabel = tk.Label(
        functionFrame,
        text="Grains closest to the nozzle are listed first, grains furthest from the nozzle are listed last"
    )
  guidanceLabel.grid(row=0, column=0, columnspan=num_grains, sticky='ew')

  row = 1
  column = 0
  grainCounter = 1

  for grain in configs['Grains']:
    if column == 4:
      column = 0
      row += 1  
    
    grainString = 'Grain ' + str(grainCounter) + ': \n'
    grainCounter += 1
    for key, value in grain.items():
      grainString += f"{key}: {value}, \n"
    
    grainLabel = tk.Label(functionFrame, text=grainString[:-2])  # Remove the last comma and space
    grainLabel.grid(row=row, column=column, sticky='nsew')

    column += 1

# @Brief Deletes a grain from the grain geometry configuration GUI
# @param functionFrame - The frame where the grain will be deleted
def deleteGrains(functionFrame):
  functionFrame = guiFunction.clear(functionFrame)

  
  grainList = configs['Grains']
  grainNames = [f"Grain {i + 1}" for i in range(len(grainList))]
  grainSelect = ttk.Combobox(functionFrame, values=grainNames)
  grainSelect.grid(row=0, column=0, sticky='nsew', padx=14, pady=6)
  grainSelect.set("Select Grain to Delete")

  deleteButton = tk.Button(functionFrame, text="Delete", command=lambda: deleteSelectedGrain(grainSelect.get()))
  deleteButton.grid(row=0, column=1, sticky='nsew')

# @Brief Deletes the selected grain from the grain geometry configuration GUI
# @param grainName - The name of the grain to be deleted
def deleteSelectedGrain(grainName):
  grainIndex = int(re.search(r'\d+', grainName).group())
  if 0 <= grainIndex < len(configs['Grains']):
    del configs['Grains'][grainIndex]
    print(f"Deleted {grainName}")
  else:
    print(f"Invalid grain index: {grainIndex}")

# @Brief Copies a grain in the grain geometry configuration GUI
# @param functionFrame - The frame where the grain will be copied
def copyGrains(functionFrame):
  functionFrame = guiFunction.clear(functionFrame)

  grainlist = configs['Grains']
  grainNames = [f"Grain {i + 1}" for i in range(len(grainlist))]
  grainSelect = ttk.Combobox(functionFrame, values=grainNames)
  grainSelect.grid(row=0, column=0, sticky='nsew', padx=14, pady=6)
  grainSelect.set("Select Grain to Copy")
  copyButton = tk.Button(functionFrame, text="Copy", command=lambda: copySelectedGrain(grainSelect.get()))
  copyButton.grid(row=0, column=1, sticky='nsew')

# @Brief Copies the selected grain in the grain geometry configuration GUI
# @param grainName - The name of the grain to be copied
def copySelectedGrain(grainName):
  grainIndex = int(re.search(r'\d+', grainName).group()) - 1 # Convert to zero-based index
  if 0 <= grainIndex < len(configs['Grains']):
    grainToCopy = configs['Grains'][grainIndex]
    newGrain = grainToCopy.copy()  # Create a copy of the selected grain
    configs['Grains'].append(newGrain)  # Add the copied grain to the list
    print(f"Copied {grainName}")
  else:
    print(f"Invalid grain index: {grainIndex}")
  
# Standard Boiler plate to run the main function 
if __name__ == '__main__':
  main()

