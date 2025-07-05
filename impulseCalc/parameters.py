import constants as constants

desiredApogee = 3048.0  # Desired apogee in meters
deltaT = 0.01  # Time step in seconds
railAngle = 3 * 0.017453292519943295  # Rail angle in radians
launchSiteElevation = 848 # Launch site elevation in meters
dragArea = 0.0176  # Drag area in square meters
dragCoefficient = 0.75  # Drag coefficient of rocket
windVelocity =  -2.5 # Wind velocity in m/s (negative for headwind)
dryMass = 17.64 # Dry mass of the rocket in kg
propelantMass = 8.04 # Mass of the propellant in kg
surfacePressure = 100948.25 # atmospheric pressure at the launch site in Pascals
surfaceTemperature = 313.0 # temperature at the launch site in Kelvin
apogeeThreshold = 0.01
burnTimeRange = 0.3
burnTimeStep = 0.05
minAvgTtW = 6.0