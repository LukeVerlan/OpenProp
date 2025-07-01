# NOZZLE ITERATOR
# This is a nozzle iteration tool to solve for an ideal nozzle for a desired grain geometry 

import motorlib as ml
import json

def main():

  configFile = input('Upload propellant config: ')

  with(configFile, 'r') as file:
    propConfig = json.load(file)
  
  setupProp(propConfig)


def setupProp(propConfig):
  global prop
  prop = ml.Propellant(**propConfig["Propellant"])

  global grains
  grains = []

  for grain_cfg in propConfig["Grains"]:
    grain_type = grain_cfg["type"]

    if grain_type == "BATES":
      grain = ml.grains.bates()
      grain.props['diameter'].setValue(grain_cfg['diameter'])
      grain.props['length'].setValue(grain_cfg['length'])
      grain.props['coreDiameter'].setValue(grain_cfg['coreDiameter'])
      grain.props['inhibitedEnds'].setValue(grain_cfg['inhibited_ends'])
      grains.append(grain)




  

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()


