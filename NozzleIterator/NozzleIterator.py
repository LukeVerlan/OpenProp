# NOZZLE ITERATOR
# This is a nozzle iteration tool to solve for an ideal nozzle for a desired grain geometry 
# A config is needed to use this tool, see config.json as an example config already setup with
# the defualt settings that openMotor uses. Currently compares the ISP between each nozzle.
# Looking to make the criteria more customizable 

# File handling libraries
import sys
import os
import argparse

# This basically says look at the file path above me, and pull my imports from there 
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Open Motor Classes
from motorlib.propellant import Propellant
from motorlib.grains.bates import BatesGrain
from motorlib.grains.finocyl import Finocyl
from motorlib.nozzle import Nozzle
from motorlib.motor import Motor

# Python libraries
import json
import math
import copy
import time

# Custom Classes
from NozzleIterator.ConfigWrapper import ConfigWrapper
from NozzleIterator.SimulationUI import SimulationUI

# Multicore processing tools
import concurrent.futures
from itertools import product


# Used for multicore processesing black magic
def frange(start, stop, step):
    vals = []
    while start <= stop + 1e-8:
        vals.append(round(start, 8))
        start += step
    return vals

# Brief - Parses the config given to the nozzle files and runs the simluation flow
def main():

  # Parses command line arguments, nessecary for integrating with main
  parser = argparse.ArgumentParser(description="Nozzle config parser") # create cmd parser 
  parser.add_argument("config_path", help="Path to the config JSON file") # grab configfilepath
  args = parser.parse_args() # Parse those arguments
  configFile = args.config_path # give me the file at the end of that directory

  with open(configFile, 'r') as file:
    propConfig = json.load(file)
  
  motor = setupProp(propConfig)

  # From config or CLI
  parallel_mode = propConfig.get("parallel_mode", True)
  max_threads = propConfig.get("iteration_threads", None)

  bestConfiguration = iteration(propConfig["Nozzle"], motor, max_threads, parallel_mode)

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
          
        if grain_type == "FINOCYL":
          grain = Finocyl()
          grain.props['numFins'].setValue(grain_cfg['numFins'])
          grain.props['finWidth'].setValue(grain_cfg['finWidth'])
          grain.props['finLength'].setValue(grain_cfg['finLength'])
          grain.props['coreDiameter'].setValue(grain_cfg['coreDiameter'])
          grain.props['invertedFins'].setValue(grain_cfg['invertedFins'])
          grain.props['inhibitedEnds'].setValue(grain_cfg['inhibitedEnds'])

        grain.props['diameter'].setValue(grain_cfg['diameter'])
        grain.props['length'].setValue(grain_cfg['length'])
        localGrains.append(grain)

    motor = Motor()
    
    # Combine simulation parameters and behavior dicts
    combined_config = propConfig['Motor']["SimulationParameters"] | propConfig['Motor']["SimulationBehavior"]
    
    # Wrap combined_config in ConfigWrapper
    motor.config = ConfigWrapper(combined_config)
    
    motor.propellant = prop
    motor.grains = localGrains

    return motor

# Breif - Performs the iterative solving of the nozzle
# param nozzleConfig - configuration dictionary of the nozzle
# return - tuple with the best nozzle and motor sim respectively 
def iteration(nozzleConfig, motor, max_threads=None, parallel_mode=True):
    stepSize = nozzleConfig["iteration_step_size"]

    # Create sweep grid
    throat_vals = frange(nozzleConfig["minDia"], nozzleConfig["maxDia"], stepSize)
    throatLength_vals = frange(nozzleConfig["minLen"], nozzleConfig["maxLen"], stepSize)
    combinations = list(product(throat_vals, throatLength_vals))

    print(f"\n🔁 Preparing {len(combinations)} simulations...")
    start_time = time.perf_counter()

    # Fallback container
    results = []

    # Decide whether to run parallel or not
    if parallel_mode:
        try:
            batch_size = 100
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_threads) as executor:
                for i in range(0, len(combinations), batch_size):
                    batch = combinations[i:i+batch_size]
                    futures = [
                        executor.submit(simulate_point, throat, throatLen, nozzleConfig, motor)
                        for throat, throatLen in batch
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result is not None:
                            results.append(result)
        except Exception as e:
            print(f"\n Parallel execution failed: {e}\nFalling back to sequential mode...\n")
            results = run_simulations_sequentially(combinations, nozzleConfig, motor)
    else:
        results = run_simulations_sequentially(combinations, nozzleConfig, motor)

    # Select best
    bestSim, bestNozzle = None, None
    for simRes, nozzle in results:
        if bestSim is None or isPriority(nozzleConfig["preference"], simRes, bestSim, nozzle, bestNozzle):
            bestSim = simRes
            bestNozzle = nozzle

    elapsed_time = time.perf_counter() - start_time
    print(f"\n✅ Completed {len(results)} successful simulations in {elapsed_time:.2f} seconds")
    return bestSim, bestNozzle

def run_simulations_sequentially(combinations, nozzleConfig, motor):
    print("🧱 Running sequentially (1 core)...")
    results = []
    for throat, throatLen in combinations:
        result = simulate_point(throat, throatLen, nozzleConfig, motor)
        if result is not None:
            results.append(result)
    return results

def simulate_point(throat, throatLength, nozzleConfig, motor_serialized):
    import copy
    from motorlib.nozzle import Nozzle

    motor = copy.deepcopy(motor_serialized)

    nozzle = {
        "throat": throat,
        "throatLength": throatLength,
        "divAngle": nozzleConfig["exitHalf"],
        "efficiency": nozzleConfig["Efficiency"],
        "slagCoeff": nozzleConfig["SlagCoef"],
        "erosionCoeff": nozzleConfig["ErosionCoef"],
        "exit": nozzleConfig['exitDia'],
    }

    convAngle = calcConvergenceHalfAngle(
        nozzleConfig["nozzleDia"],
        nozzleConfig["nozzleLength"],
        throat,
        throatLength,
        nozzle["divAngle"],
        nozzle["exit"]
    )

    if not (nozzleConfig["minHalfConv"] <= convAngle <= nozzleConfig["maxHalfConv"]):
        return None

    nozzle["convAngle"] = convAngle

    currNozz = Nozzle()
    for key, value in nozzle.items():
        if key in currNozz.props:
            currNozz.props[key].setValue(value)

    motor.nozzle = currNozz
    simRes = motor.runSimulation()

    if simRes.success:
        return simRes, nozzle
    return None

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
  ui.exportThrustCurve("TestCSV.csv")
  ui.plotThrustCurve()
  
  
# Brief - calculate the expansion ratio of the given nozzle
# param throatDia - diameter of the nozzle throat
# pararm exitDia - exit diameter of the nozzle
# return - the given nozzles expansion ratio
def getExpansionRatio(throatDia, exitDia):
  return (math.pow(exitDia,2))/(math.pow(throatDia,2))

# Brief - Determines if the simluation should be prefered to the current best
# param priority - criteria to base preference on
# param simRes - similuation to compare to 
# param bestSim - current best simulation
def isPriority(priority, simRes, bestSim, nozzle=None, bestNozzle=None):
    throat_penalty_factor = 0.1  # Adjust as needed
    min_safe_throat_length = 0.012
    score = getattr(simRes, f"get{priority}")()
    if nozzle and nozzle["throatLength"] < min_safe_throat_length:
        score *= (1 - throat_penalty_factor)
    best_score = getattr(bestSim, f"get{priority}")()
    return score > best_score

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
 