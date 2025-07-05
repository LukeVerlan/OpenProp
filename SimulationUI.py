# SIMULATION UI
#
# This class is used to save simulation results and present the Data clealy. 

import csv 

class SimulationUI:

  # Breif - Constructor
  # param simResult - an openMotor simulation result
  def __init__(self, simResult):
    self.simResult = simResult

  # Brief - creates a plot of the thrust curve for the given simulation
  def plotThrustCurve(self):
      import matplotlib.pyplot as plt
      time = self.simResult.channels['time'].getData()
      thrust = self.simResult.channels['force'].getData()
      plt.plot(time, thrust)
      plt.title("Thrust Curve")
      plt.xlabel("Time (s)")
      plt.ylabel("Thrust (N)")
      plt.grid(True)
      plt.show()

  # Brief - Saves the simulation to a CSV
  # param fileName - name of the file to save to
  def saveCSV(self, fileName):
    with open(fileName, "w") as f: 
      f.write(self.simResult.getCSV())

  # Brief - Returns a string of all useful values of a motor simulation
  # return - formatted string of peak and general values
  def peakValues(self):
    return (f"Peak values\n"
            f"  Kn: {self.simResult.getPeakKN()}\n"
            f"  Pressure: {self.simResult.getMaxPressure()}\n"
            f"  Mass Flux: {self.simResult.getPeakMassFlux()}\n"
            f"  Mach Number: {self.simResult.getPeakMachNumber()}\n"
            f"\n"
            f"General Values\n"
            f"  ISP: {self.simResult.getISP()}\n"
            f"  Burn Time: {self.simResult.getBurnTime()}\n"
            f"  Average Pressure: {self.simResult.getAveragePressure()}\n"
            f"  Initial Kn: {self.simResult.getInitialKN()}\n"
            f"  Total Delievered Impulse: {self.simResult.getImpulse()}\n"
            f"  Average Thrust: {self.simResult.getAverageForce()}\n")
  
  # Brief - breaks down thrust curve and exports it as a CSV
  # param filename - Name of the csv file, must end in csv
  def exportThrustCurve(self, filename):
      with open(filename, mode='w', newline='') as file:
          writer = csv.writer(file)
          writer.writerow(["Time (s)", "Thrust (N)"])
          for t, f in zip(self.simResult.channels['time'].getData(), self.simResult.channels['force'].getData()):
              writer.writerow([t, f])
    

          
  