import guiFunction
import tkinter as tk
from   tkinter import ttk
import re

# @Brief Creates the propellant configuration GUI
# @param popup - The popup window where the propellant configuration will be created
def createPropellant(popup, configs):
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
def createOMsettings(popup, configs):
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
def createNozzleIterator(popup, configs):
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
def createImpulseCalculator(popup, configs):
  guiFunction.clearWidgetColumn(popup, 1)
  labelName = "Impulse Calculator Config"

  fields = [
            "Surface Pressure - Pa", "Surface Temperature - K", "Wind Velocity (- for into wind) - m/s", "Rail Angle (+ into wind) - radians", "Launch Site Elevation - m",
            "Cross-Section Area - m^2", "Drag Coefficient", "NO Motor Mass - kg", "Specific Impulse - (N * s)/kg", "Desired Apogee - m", "Apogee Range (0.01 = within 1%)", 
            "Burn Time Range %diff shown", "Burn Time Step - s", "Min Avg Thrust to Weight", "Bisection bound %diff", "Flight Sim min time step - s"
  ]  

  if "ImpulseCalculator" in configs and configs["ImpulseCalculator"] is not None:
    defaults = {
        "Surface Pressure - Pa": configs["ImpulseCalculator"].get("surfacePressure", ""),
        "Surface Temperature - K": configs["ImpulseCalculator"].get("surfaceTemperature", ""),
        "Wind Velocity (- for into wind) - m/s": configs["ImpulseCalculator"].get("windVelocity", ""),
        "Rail Angle (+ into wind) - radians": configs["ImpulseCalculator"].get("railAngle", ""),
        "Launch Site Elevation - m": configs["ImpulseCalculator"].get("launchSiteElevation", ""),
        "Cross-Section Area - m^2": configs["ImpulseCalculator"].get("dragArea", ""),
        "Drag Coefficient": configs["ImpulseCalculator"].get("dragCoefficient", ""),
        "NO Motor Mass - kg": configs["ImpulseCalculator"].get("noMotorMass", ""),
        "Specific Impulse - (N * s)/kg": configs["ImpulseCalculator"].get("specificImpulse", ""),
        "Desired Apogee - m": configs["ImpulseCalculator"].get("desiredApogee", ""),
        "Apogee Range (0.01 = within 1%)": configs["ImpulseCalculator"].get("apogeeThreshold", ""),
        "Burn Time Range %diff shown": configs["ImpulseCalculator"].get("burnTimeRange", ""),
        "Burn Time Step - s": configs["ImpulseCalculator"].get("burnTimeStep", ""),
        "Min Avg Thrust to Weight": configs["ImpulseCalculator"].get("minAvgTtW", ""),
        "Bisection bound %diff": configs["ImpulseCalculator"].get("bisectionBoundPercDiff", ""),
        "Flight Sim min time step - s": configs["ImpulseCalculator"].get("deltaT", ""),
    }
  else:
    defaults = None
  guiFunction.createSettingsPage(configs, labelName, fields, popup, None, defaults)

  # @Brief Creates the grain geometry configuration GUI
# @param popup - The popup window where the grain geometry configuration will be created
def createGrainGeometry(popup, configs):
  guiFunction.clearWidgetColumn(popup, 1)

  def refresh():
        createGrainGeometry(popup, configs) 

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
  
  addGrainButton = tk.Button(buttonFrame, text="Add Grain", command=lambda: addGrains(functionFrame, refresh, configs))
  addGrainButton.grid(row=0, column=0, padx=10, pady=15)

  if "Grains" in configs and configs["Grains"] is not None:
    deleteGrainButton = tk.Button(buttonFrame, text="Delete Grains", command=lambda: deleteGrains(functionFrame, configs))
    deleteGrainButton.grid(row=0,column=1,padx=10,pady=15)

    viewGrainsButton = tk.Button(buttonFrame, text="View Grains", command=lambda: viewGrains(functionFrame, configs))
    viewGrainsButton.grid(row=0, column=2, padx=10,pady=15)

    copyGrainsButton = tk.Button(buttonFrame, text="Copy Grains", command=lambda: copyGrains(functionFrame, configs))
    copyGrainsButton.grid(row=0, column=3, padx=10,pady=15)


# @Brief Adds a grain to the grain geometry configuration GUI
# @param frame - The frame where the grain will be added
def addGrains(frame, refreshCall, configs):

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
                                                                                                 refreshCall, configs))
  grainSelectaddButton.grid(row=0,column=1,sticky='nsew')

  grainAdditionFrame.rowconfigure(0,weight=1)

# @Brief Adds a grain window to the grain geometry configuration GUI
# @param frame - The frame where the grain window will be added
def addGrainWindow(frame, type, refreshCall, configs):

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
def viewGrains(functionFrame, configs):

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
def deleteGrains(functionFrame, configs):
  functionFrame = guiFunction.clear(functionFrame)

  
  grainList = configs['Grains']
  grainNames = [f"Grain {i + 1}" for i in range(len(grainList))]
  grainSelect = ttk.Combobox(functionFrame, values=grainNames)
  grainSelect.grid(row=0, column=0, sticky='nsew', padx=14, pady=6)
  grainSelect.set("Select Grain to Delete")

  deleteButton = tk.Button(functionFrame, text="Delete", command=lambda: deleteSelectedGrain(grainSelect.get(), configs))
  deleteButton.grid(row=0, column=1, sticky='nsew')

# @Brief Deletes the selected grain from the grain geometry configuration GUI
# @param grainName - The name of the grain to be deleted
def deleteSelectedGrain(grainName, configs):
  grainIndex = int(re.search(r'\d+', grainName).group())
  if 0 <= grainIndex < len(configs['Grains']):
    del configs['Grains'][grainIndex]
    print(f"Deleted {grainName}")
  else:
    print(f"Invalid grain index: {grainIndex}")

# @Brief Copies a grain in the grain geometry configuration GUI
# @param functionFrame - The frame where the grain will be copied
def copyGrains(functionFrame, configs):
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
def copySelectedGrain(grainName, configs):
  grainIndex = int(re.search(r'\d+', grainName).group()) - 1 # Convert to zero-based index
  if 0 <= grainIndex < len(configs['Grains']):
    grainToCopy = configs['Grains'][grainIndex]
    newGrain = grainToCopy.copy()  # Create a copy of the selected grain
    configs['Grains'].append(newGrain)  # Add the copied grain to the list
    print(f"Copied {grainName}")
  else:
    print(f"Invalid grain index: {grainIndex}")