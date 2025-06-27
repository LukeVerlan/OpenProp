# IMPULSE CALCULATOR
#
# This is a comprehensive approximate impulse calculator to reach a desired rocket apogee
# This object takes in an openRocket .ork file and a desired apogee, spits out a ballpark
# estimate of the amount of impulse required to get to that height

class ImpulseCalculator:

  def __init__(desiredApogee):
    self.GRAVITY = 9.80665
    self.APOGEE = desiredApogee
    self.AIR_DENSITY = 1.225

