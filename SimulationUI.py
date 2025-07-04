class SimulationUI:

  def __init__(self, simResult):
    self.simResult = simResult

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

  def saveCSV(self, fileName):
    with open(fileName, "w") as f: 
      f.write(self.simResult.getCSV())

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
  

          
  