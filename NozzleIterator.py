# NOZZLE ITERATOR
# This is a nozzle iteration tool to solve for an ideal nozzle for a desired grain geometry 

import motorlib as ml
from motorlib.propellant import Propellant
from motorlib.grains.bates import BatesGrain
from motorlib.nozzle import Nozzle 

import json
import math

def main():

  configFile = input('Upload propellant config: ')

  with open(configFile, 'r') as file:
    propConfig = json.load(file)
  
  setupProp(propConfig)
  iteration(propConfig["Nozzle"], propConfig["Initial"])


def setupProp(propConfig):
  global prop
  prop = Propellant(propConfig["Propellant"])

  global grains
  grains = []

  for grain_cfg in propConfig["Grains"]:
    grain_type = grain_cfg["type"]

    if grain_type == "BATES":
      grain = BatesGrain()
      grain.props['diameter'].setValue(grain_cfg['diameter'])
      grain.props['length'].setValue(grain_cfg['length'])
      grain.props['coreDiameter'].setValue(grain_cfg['coreDiameter'])
      grain.props['inhibitedEnds'].setValue(grain_cfg['inhibitedEnds'])
      grains.append(grain)

def iteration(nozzleConfig, simulationConfig):
  
  # Store config files in dict
  stepSize = simulationConfig["Step_size"]
  tempInitial = simulationConfig["temp_initial"]
  sealvlpress = simulationConfig["sealvl_press"]

  # Parse nozzle data
  bounds = setupNozzleDict(nozzleConfig)

  # Known dimensions
  dia = bounds["minDia"]
  len = bounds["minLen"]
  exitHalf = bounds["exitHalf"]

  nozzle = {}

  # Iterative dimensions
  nozzle["nozzleLengh"] = bounds["nozzleLength"]
  nozzle["nozzleDia"] = bounds["nozzleDia"] 

  nozzle["exitHalf"] = exitHalf

  while dia <= bounds["maxDia"]:

    nozzle["dia"] = dia

    while len <= bounds["maxLen"]:

      nozzle["len"] = len
      nozzle["convHalf"] = calcConvergenceHalfAngle(nozzle["nozzleDia"], nozzle["nozzleLength"],
                                                    dia, len, nozzle["exitHalf"])
      
      convHalf = nozzle["convHalf"]
      if convHalf <= bounds["maxHalfConv"] and convHalf >= bounds["minHalfConv"]:
        
        # Create nozzle 

        # simluate

        # compare to old best nozzle

        # rinse and repeat

      len += stepSize
    dia += stepSize

def calcConvergenceHalfAngle(dia, len, throatDia, throatLen, exitHalf):

  thickness = (dia + throatDia)/2.0
  lenDiverge = thickness/(math.tan(exitHalf))
  lenConverge = len - throatLen - lenDiverge
  return math.atan(thickness/lenConverge)

def setupNozzleDict(nozzleConfig):

  bounds = {}

  bounds["minDia"] = nozzleConfig["throat_dia_min"]
  bounds["maxDia"] = nozzleConfig["throat_dia_max"]
  bounds["minLen"] = nozzleConfig["throat_len_min"]
  bounds["maxLen"] = nozzleConfig["throat_len_max"]
  bounds["minHalfConv"] = nozzleConfig["minConverganceHalfAngle"]
  bounds["maxHalfConv"] = nozzleConfig["maxConverganceHalfAngle"]
  bounds["exitHalf"] = nozzleConfig["exitHalf"]
  bounds["nozzleLength"] = nozzleConfig["length"]
  bounds["nozzleDia"] = nozzleConfig["dia"]
  bounds["slagCoef"] = nozzleConfig["SlagCoef"]
  bounds["erosionCoef"] = nozzleConfig["ErosionCoef"]
  bounds["efficiency"] = nozzleConfig["Efficiency"]

  return bounds


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()


