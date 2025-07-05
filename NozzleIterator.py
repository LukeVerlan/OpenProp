# NOZZLE ITERATOR
# This is a nozzle iteration tool to solve for an ideal nozzle for a desired grain geometry 
# A config is needed to use this tool, see config.json as an example config already setup with
# the defualt settings that openMotor uses. 

# Open Motor Classes
from motorlib.propellant import Propellant
from motorlib.grains.bates import BatesGrain
from motorlib.nozzle import Nozzle
from motorlib.motor import Motor

# Python libraries
import json
import math
import copy
import time

# Custom Classes
from ConfigWrapper import ConfigWrapper
from SimulationUI import SimulationUI

def main():

  configFile = input('Upload propellant config: ')

  with open(configFile, 'r') as file:
    propConfig = json.load(file)
  
  setupProp(propConfig)
  bestConfiguration = iteration(propConfig["Nozzle"], propConfig["Motor"])
  (simRes, nozzle) = bestConfiguration
  iterationResult(simRes, nozzle)

# Brief - Parse the configuration files
# Parameters - config file 
def setupProp(propConfig):
    prop = Propellant(propConfig["Propellant"])
    localGrains = []

    for grain_cfg in propConfig["Grains"]:
        grain_type = grain_cfg["type"]
        if grain_type == "BATES":
            grain = BatesGrain()
            grain.props['coreDiameter'].setValue(grain_cfg['coreDiameter'])
            grain.props['inhibitedEnds'].setValue(grain_cfg['inhibitedEnds'])

        grain.props['diameter'].setValue(grain_cfg['diameter'])
        grain.props['length'].setValue(grain_cfg['length'])
        localGrains.append(grain)

    global motor
    motor = Motor()
    
    # Combine simulation parameters and behavior dicts
    combined_config = propConfig['Motor']["SimulationParameters"] | propConfig['Motor']["SimulationBehavior"]
    
    # Wrap combined_config in ConfigWrapper
    motor.config = ConfigWrapper(combined_config)
    
    motor.propellant = prop
    motor.grains = localGrains

# Breif - Performs the iterative solving of the nozzle
# param nozzleConfig - configuration dictionary of the nozzle
# param simluationConfig - configuration dictionary of the simluation
# return - tuple with the best nozzle and motor sim respectively 
def iteration(nozzleConfig, simulationConfig):

  # Store config files in dict
  stepSize = simulationConfig["Initial"]["iteration_step_size"]

  # Iterative class Dimenions
  throat = nozzleConfig["minDia"]
  throatLength = nozzleConfig["minLen"]
  exitHalf = nozzleConfig["exitHalf"]

  nozzle = {}

  # Known class Dimensions
  nozzle['divAngle'] = nozzleConfig["exitHalf"]
  nozzle['efficiency'] = nozzleConfig["Efficiency"]
  nozzle['slagCoeff'] = nozzleConfig["SlagCoef"]
  nozzle['erosionCoeff'] = nozzleConfig["ErosionCoef"]
  nozzle['exit'] = nozzleConfig['exitDia']

  # Set comparison 
  currBest = None
  bestNozzle = None

  start_time = time.perf_counter()
  while throat <= nozzleConfig["maxDia"]:
    if currBest is None:
      print('iterating')

    nozzle["throat"] = throat

    while throatLength <= nozzleConfig["maxLen"]:

      nozzle["throatLength"] = throatLength
      nozzle["convAngle"] = calcConvergenceHalfAngle(nozzleConfig["nozzleDia"], nozzleConfig["nozzleLength"],
                                                    throat, throatLength, nozzle["divAngle"], nozzle["exit"])
      
      convHalf = nozzle["convAngle"]
      if convHalf <= nozzleConfig["maxHalfConv"] and convHalf >= nozzleConfig["minHalfConv"]:

        # count += 1
        # if count == 2:
        #   printNozzleStatistics(nozzle)
        #   count = 0

        # Simulation setup 
        currNozz = Nozzle()
        for key, value in nozzle.items():
          if key in currNozz.props:
            currNozz.props[key].setValue(value)
        motor.nozzle = currNozz

        # simluate
        simRes = motor.runSimulation()
       
        # compare to old best nozzle
        if simRes.success and (currBest is None or simRes.getISP() > currBest.getISP()):
          currBest = simRes
          bestNozzle = copy.deepcopy(nozzle)

      throatLength += stepSize
    throatLength = nozzleConfig['minLen']
    throat += stepSize * 5

  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  print(f"Code executed in: {elapsed_time:.4f} seconds")
  return (currBest, bestNozzle)

# Brief - Calculates the convergence half angle of a nozzle given other dimensions
# param dia - overall diameter of the nozzle
# param len - overall length of the nozzle
# param throatDia - diameter of the throat
# param throatLen - length of the throat
# param exitHalf - exit half angle
# param exitDia - exit diameter
# return - the convergence half angle
def calcConvergenceHalfAngle(dia, len, throatDia, throatLen, exitHalf, exitDia):

  # Establish Radii 
  r_throat = throatDia/2
  r_exit = exitDia/2
  r_total = dia/2

  # Solve lengths
  lenDiv = (1/math.tan(math.radians(exitHalf))) * (r_exit - r_throat)
  lenConv = len - throatLen - lenDiv

  # Handle invalid geometry 
  if lenConv <= 0:
    return 999

  # Solve Convergence half angle
  return math.degrees(math.atan((r_total-r_throat)/lenConv))

# Brief - print out the statistics of the given nozzle
# param nozzle - nozzle dictionary 
def printNozzleStatistics(nozzle):
  print(f"\nNozzle Dimensions\n"
        f"  Angles\n"
        f"    Exit Half Angle: {format(nozzle['divAngle'],".2f")} deg\n"
        f"    Convergence Half Angle : {format(nozzle['convAngle'],".4f")} deg\n"
        f"\n"
        f"  Throat\n"
        f"    Diameter: {format(nozzle['throat'] * 100,".4f")} cm\n"
        f"    Length: {format((nozzle['throatLength'] * 100),".4f")} cm\n"
        f" \n"
        f" Expansion ratio: {format(getExpansionRatio(nozzle['throat'],nozzle['exit']),".2f")}\n")

# Brief - print out and format the results of the motor test
# param simRes - simulation result
# param nozzle - winning nozzle 
def iterationResult(simRes, nozzle):

  # Print out the nozzle statistics
  printNozzleStatistics(nozzle)
  
  # Create nice simulation tool
  ui = SimulationUI(simRes)

  # Print simluation peak values and plot thrust curve
  print(ui.peakValues())
  ui.exportThrustCurve()
  ui.plotThrustCurve()
  
  
# Brief - calculate the expansion ratio of the given nozzle
# param throatDia - diameter of the nozzle throat
# pararm exitDia - exit diameter of the nozzle
# return - the given nozzles expansion ratio
def getExpansionRatio(throatDia, exitDia):
  return (math.pow(exitDia,2))/(math.pow(throatDia,2))

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
