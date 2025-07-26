
# @breif Configures the propellant dictionary with the given entry values.
# @param configs The dictionary containing the current configurations.
# @param entryVals The dictionary containing the entry values for the propellant configuration.
def configurePropellantDict(configs, entryVals):
    configs["Propellant"] = {}
    configs["Propellant"]["name"] = str(entryVals["Propellant Name"])
    configs["Propellant"]["density"] = float(entryVals["Density - Kg/m^3"])
    configs["Propellant"]["tabs"] = [{
        "maxPressure": float(entryVals["Max Pressure - Pa"]),
        "minPressure": float(entryVals["Min Pressure - Pa"]),
        "a": float(entryVals["Burn Rate Coefficient - m/(s*Pa^n)"]),
        "n": float(entryVals["Burn Rate Exponent"]),
        "k": float(entryVals["Specific Heat Ratio"]),
        "t": float(entryVals["Combustion Temperature - K"]),
        "m": float(entryVals["Exhaust Molar Mass - g/mol"])
    }]

# @brief Configures the motor dictionary with the given entry values.
# @param configs The dictionary containing the current configurations.
# @param entryVals The dictionary containing the entry values for the motor configuration.
def configureOMDict(configs,entryVals):
    configs["Motor"]["SimulationParameters"]["maxPressure"] = float(entryVals["Max Pressure - Pa"])
    configs["Motor"]["SimulationParameters"]["maxMassFlux"] = float(entryVals["Max Mass Flux - kg/(m^2*s)"])
    configs["Motor"]["SimulationParameters"]["maxMachNumber"] = float(entryVals["Max Mach Number"])
    configs["Motor"]["SimulationParameters"]["minPortThroat"] = float(entryVals["Min Port Throat Ratio"])
    configs["Motor"]["SimulationParameters"]["flowSeparationWarnPercent"] = float(entryVals["Flow Separation Precent - 0.##"])
    configs["Motor"]["SimulationBehavior"]["burnoutWebThres"] = float(entryVals["Burnout Web Threshold - m"])
    configs["Motor"]["SimulationBehavior"]["burnoutThrustThres"] = float(entryVals["Burnout Thrust Threshold"])
    configs["Motor"]["SimulationBehavior"]["timestep"] = float(entryVals["Time step - s"])
    configs["Motor"]["SimulationBehavior"]["ambPressure"] = float(entryVals["Ambient Pressure - Pa"])
    configs["Motor"]["SimulationBehavior"]["mapDim"] = float(entryVals["Grain Map Dimension"])
    configs["Motor"]["SimulationBehavior"]["sepPressureRatio"] = float(entryVals["Separation Pressure Ratio"])

# @brief Configures the nozzle iterator dictionary with the given entry values.
# @param configs The dictionary containing the current configurations.
# @param entryVals The dictionary containing the entry values for the nozzle iterator configuration.
# @note This function sets various parameters related to the nozzle design and simulation.
def configureNIDict(configs,entryVals):
  
  configs["Nozzle"] = {}
  configs["Nozzle"]["minDia"] = float(entryVals["Min Throat Diameter - m"])
  configs["Nozzle"]["maxDia"] = float(entryVals["Max Throat Diameter - m"])
  configs["Nozzle"]["minLen"] = float(entryVals["Min Throat Length - m"])
  configs["Nozzle"]["maxLen"] = float(entryVals["Max Throat Length - m"])
  configs["Nozzle"]["exitHalf"] = float(entryVals["Exit Half Angle - deg"])
  configs["Nozzle"]["SlagCoef"] = float(entryVals["Slag Coefficient - (m*Pa)/s"])
  configs["Nozzle"]["ErosionCoef"] = float(entryVals["Erosion Coefficient - s/(m*Pa)"])
  configs["Nozzle"]["Efficiency"] = float(entryVals["Efficiency - 0.##"])
  configs["Nozzle"]["nozzleDia"] = float(entryVals["Nozzle Diameter - m"])
  configs["Nozzle"]["nozzleLength"] = float(entryVals["Nozzle Length - m"])
  configs["Nozzle"]["minHalfConv"] = float(entryVals["Min Conv Half Angle - deg"])
  configs["Nozzle"]["maxHalfConv"] = float(entryVals["Max Conv Half Angle - deg"])
  configs["Nozzle"]["nozzleDia"] = float(entryVals["Nozzle Diameter - m"])
  configs["Nozzle"]["iteration_step_size"] = float(entryVals["Iteraton Step Size - m"])
  configs["Nozzle"]["preference"] = str(entryVals["Search Preference"])
  configs["Nozzle"]["parallel_mode"] = bool(entryVals["Parallel Simulation (Harder on computer)"])
  configs["Nozzle"]["iteration_threads"] = int(entryVals["# Threads to allocate for simulation"])
  configs["Nozzle"]["exitDia"] = float(entryVals["Exit Diameter - m"])

# @brief Configures the grain dictionary with the given entry values.
# @param configs The dictionary containing the current configurations.
# @param entryVals The dictionary containing the entry values for the grain configuration.
# @param type The type of grain being configured (e.g., 'FINOCYL', 'BATES')
def configureGrainDict(configs, entryVals, type):

  if "Grains" not in configs:
    configs["Grains"] = []

  configs["Grains"].append({})
  configs["Grains"][-1]['type'] = str(type)
  configs["Grains"][-1]['length'] = float(entryVals["Length - m"])
  configs["Grains"][-1]['diameter'] = float(entryVals["Diameter - m"])
  configs["Grains"][-1]['coreDiameter'] = float(entryVals["Core Diameter - m"])
  configs["Grains"][-1]['inhibitedEnds'] = bool(entryVals["Inhibited Ends"])


  if type == "FINOCYL":
   configs["Grains"][-1]['invertedFins'] = bool(entryVals["Inverted Fins"])
   configs["Grains"][-1]['numFins'] = float(entryVals["Number of Fins"])
   configs["Grains"][-1]['finLength'] = float(entryVals["Fin Length - m"])
   configs["Grains"][-1]['finWidth'] = float(entryVals["Fin Width - m"])

# @brief Verifies that all entry boxes are of the correct values
# @param entryvals - entry boxes
# @return true if valid false if invald 
def verifyEntryBoxes(entryvals):
  # Set of keys that should be treated as strings (words), not numbers
  string_keys = {
    "Propellant Name",
    "Search Preference",
    'type',
  }

  def is_number(s):
    try:
      float(s)
      return True
    except ValueError:
      return False

  for key, val in entryvals.items():
    if key in string_keys:
      continue

    if not is_number(val):
      return False

  return True


   

