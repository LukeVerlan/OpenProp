# SIMULATION UI
#
# This class is used to save simulation results and present the Data clealy. 
import csv 

# math handling modules
import math

# Image handling objects
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image
import io

class SimulationUI:

  # Breif - Constructor
  # param simResult - an openMotor simulation result
  # param nozzle - a nozzle dicitonary 
  def __init__(self, simResult, nozzle, NIconfig):
    self.simResult = simResult
    self.nozzle = nozzle
    self.NIconfig = NIconfig

  def plotSim(self):
    time = self.simResult.channels['time'].getData()
    thrust = self.simResult.channels['force'].getData()
    pressure = self.simResult.channels['pressure'].getData()
    kn = self.simResult.channels['kn'].getData()

    fig, ax1 = plt.subplots()

    units = {
        'pressure': 'Pa',
        'force': 'N',
        'time': 's',
        'kn': 'unitless'
    }

    # Pressure on left Y-axis
    ax1.plot(time, pressure, 'b-', label='Pressure (' + units['pressure'] + ')')
    ax1.set_xlabel('Time (' + units['time'] + ')')
    ax1.set_ylabel('Pressure (' + units['pressure'] + ')', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Thrust and Kn on right Y-axis
    ax2 = ax1.twinx()
    ax2.plot(time, thrust, 'r--', label='Thrust (' + units['force'] + ')')
    ax2.plot(time, kn, 'g-.', label='Kn (' + units['kn'] + ')')  # Share Y-axis
    ax2.set_ylabel('Thrust / Kn', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title('Motor Simulation Results with Optimal Nozzle')

    return self._plotToImage(fig)

  # @brief converts an a plot into an image
  # @param figure of the graph from mathpltlib
  def _plotToImage(self, fig):
         
    canvas = FigureCanvas(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    buf.seek(0)

    image = Image.open(buf)
    return image

  # Brief - Saves the simulation to a CSV
  # param fileName - name of the file to save to
  def saveCSV(self, fileName):
    with open(fileName, "w") as f: 
      f.write(self.simResult.getCSV())

  # Brief - Returns a string of all useful values of a motor simulation
  # return - formatted string of peak and general values
  def peakValues(self):
    return (f"Peak values\n"
            f"  Kn: {self.formatToDecimalPlaces(self.simResult.getPeakKN())}\n"
            f"  Pressure: {self.formatToDecimalPlaces(self.simResult.getMaxPressure())} (Pa)\n"
            f"  Mass Flux: {self.formatToDecimalPlaces(self.simResult.getPeakMassFlux())} (kg/(m^2*s)) \n "
            f"  Mach Number: {self.formatToDecimalPlaces(self.simResult.getPeakMachNumber())} \n"
            f"  Average Thrust: {self.formatToDecimalPlaces(self.simResult.getAverageForce())} (N) \n")

  def generalValues(self):
    return (f"General Values\n"
            f"ISP: {self.formatToDecimalPlaces(self.simResult.getISP())}\n"
            f" Burn Time: {self.formatToDecimalPlaces(self.simResult.getBurnTime())} (s) \n"
            f"Average Pressure: {self.formatToDecimalPlaces(self.simResult.getAveragePressure())} (Pa) \n"
            f"Initial Kn: {self.formatToDecimalPlaces(self.simResult.getInitialKN())}\n"
            f"Delievered Impulse: {self.formatToDecimalPlaces(self.simResult.getImpulse())} (N*s) \n")

  def formatToDecimalPlaces(self, num, numDec=2):
    return format(num, "." + str(numDec) + "f")
    
  # Brief - print out the statistics of the given nozzle
  # param nozzle - nozzle dictionary 
  def nozzleStatistics(self):
    return (f"\nCritical Nozzle Dimensions\n\n"
            f"    Exit Half Angle: {format(self.nozzle['divAngle'],".1f")} deg     Throat Diameter: {format(self.nozzle['throat'] * 100,".1f")} cm\n\n"
            f"    Convergence Half Angle : {format(self.nozzle['convAngle'],".1f")} deg    Throat Length: {format((self.nozzle['throatLength'] * 100),".1f")} cm\n"
            f"\n"
            f" Expansion ratio: {format(self.getExpansionRatio(self.nozzle['throat'],self.nozzle['exit']),".2f")}\n")
  
  # returns the extended nozzle stats 
  def extendedNozzleStatistics(self):

    units ={
      'divAngle' : 'deg',
      'throat' : 'm',
      'convAngle' : 'deg',
      'throatLength': 'm',
      'nozzleLength' : 'm',
      'nozzleDia' : 'm'
    }

    dim = 'Complete Nozzle Statistics: \n\n'

    for key in self.nozzle.keys():
      if key in units:
        dim += key + ' : ' + str(self.nozzle[key]) + ' - ' + units[key] + '\n'

    for key in self.NIconfig.keys():
      if key in units:
        dim += key + ' : ' + str(self.NIconfig[key]) + ' - ' + units[key] + '\n'

    dim += '\nSearch Preference   : ' + self.NIconfig['preference'] 
    dim += '\nEfficiency          : ' + str(self.NIconfig['Efficiency'])
    dim += '\nErosion Coefficient : ' + str(self.NIconfig['ErosionCoef'])
    dim += '\nSlag Coefficient    : ' + str(self.NIconfig['SlagCoef'])

    return dim

  # Brief - calculate the expansion ratio of the given nozzle
  # param throatDia - diameter of the nozzle throat
  # pararm exitDia - exit diameter of the nozzle
  # return - the given nozzles expansion ratio
  def getExpansionRatio(self, throatDia, exitDia):
    return (math.pow(exitDia,2))/(math.pow(throatDia,2))
      
  # Brief - breaks down thrust curve and exports it as a CSV
  # param filename - Name of the csv file, must end in csv
  def exportThrustCurve(self, filename):
    if '.csv' not in filename:
      filename += '.csv'
    with open(filename, mode='w', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(["Time (s)", "Thrust (N)"])
      for t, f in zip(self.simResult.channels['time'].getData(), self.simResult.channels['force'].getData()):
        writer.writerow([t, f])

  # Breif - Saves extended nozzle stats to a txt file
  def exportNozzleStats(self, filename):
    if '.txt' not in filename:
      filename += '.txt'
    with open(filename, mode='w', newline='') as file:
      file.write(self.extendedNozzleStatistics())
      