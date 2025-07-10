

def configurePropellantDict(configs, entryVals):
    configs["Propellant"] = {}
    configs["Propellant"]["name"] = entryVals["Propellant Name"]
    configs["Propellant"]["density"] = entryVals["Density - Kg/m^3"]
    configs["Propellant"]["tabs"] = [{
        "maxPressure": entryVals["Max Pressure - Pa"],
        "minPressure": entryVals["Min Pressure - Pa"],
        "a": entryVals["Burn Rate Coefficient - m/(s*Pa^n)"],
        "n": entryVals["Burn Rate Exponent"],
        "k": entryVals["Specific Heat Ratio"],
        "t": entryVals["Combustion Temperature - K"],
        "m": entryVals["Exhaust Molar Mass - g/mol"]
    }]


def configureOMDict(configs,entryVals):
    configs["Motor"]["SimulationParameters"]["maxPressure"] = entryVals["Max Pressure - Pa"]
    configs["Motor"]["SimulationParameters"]["maxMassFlux"] = entryVals["Max Mass Flux - kg/(m^2*s)"]
    configs["Motor"]["SimulationParameters"]["maxMachNumber"] = entryVals["Max Mach Number"]
    configs["Motor"]["SimulationParameters"]["minPortThroat"] = entryVals["Min Port Throat Ratio"]
    configs["Motor"]["SimulationParameters"]["flowSeparationWarnPercent"] = entryVals["Flow Separation Precent - 0.##"]
    configs["Motor"]["SimulationBehavior"]["burnoutWebThres"] = entryVals["Burnout Web Threshold - m"]
    configs["Motor"]["SimulationBehavior"]["burnoutThrustThres"] = entryVals["Burnout Thrust Threshold"]
    configs["Motor"]["SimulationBehavior"]["timestep"] = entryVals["Time step - s"]
    configs["Motor"]["SimulationBehavior"]["ambPressure"] = entryVals["Ambient Pressure - Pa"]
    configs["Motor"]["SimulationBehavior"]["mapDim"] = entryVals["Grain Map Dimension"]
    configs["Motor"]["SimulationBehavior"]["sepPressureRatio"] = entryVals["Separation Pressure Ratio"]


def configureNIDict(configs,entryVals):
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
  configs["Nozzle"]["minHalfConv"] = entryVals["Min Conv Half Angle - deg"]
  configs["Nozzle"]["maxHalfConv"] = entryVals["Max Conv Half Angle - deg"]
  configs["Nozzle"]["nozzleDia"] = entryVals["Nozzle Diameter - m"]
  configs["Nozzle"]["iteration_step_size"] = entryVals["Iteraton Step Size - m"]
  configs["Nozzle"]["preference"] = entryVals["Search Preference"]
  configs["Nozzle"]["parallel_mode"] = entryVals["Parallel Simulation (Harder on computer)"]
  configs["Nozzle"]["iteration_threads"] = entryVals[" # Threads to allocate for simulation"]

def configureGrainDict(configs, entryVals, type):

  if "Grains" in configs and configs["Grains"] is not None:
    configs["Grains"] = []

  configs["Grains"].append({})
  configs["Grains"][-1]['type'] = type
  configs["Grains"][-1]['length'] = entryVals["Length - m"]
  configs["Grains"][-1]['diameter'] = entryVals["Diameter - m"]
  configs["Grains"][-1]['coreDiameter'] = entryVals["Core Diameter - m"]
  configs["Grains"][-1]['inhibitedEnds'] = entryVals["Inhibited Ends"]


  if type == "FINOCYL":
   configs["Grains"][-1]['invertedFins'] = entryVals["Inverted Fins"]
   configs["Grains"][-1]['numFins'] = entryVals["Number of Fins"]
   configs["Grains"][-1]['finLength'] = entryVals["Fin Length - m"]
   configs["Grains"][-1]['finWidth'] = entryVals["Fin Width - m"]
