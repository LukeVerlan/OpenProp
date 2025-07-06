
desiredApogee = 3048.0  # Desired apogee in meters
deltaT = 0.01  # Time step in seconds
railAngle = 3 * 0.017453292519943295  # Rail angle in radians
launchSiteElevation = 848.0 # Launch site elevation in meters
dragArea = 0.0176  # Drag area in square meters
dragCoefficient = 0.75  # Drag coefficient of rocket
windVelocity =  -2.5 # Wind velocity in m/s (negative for headwind)
noMotorMass = 17.64 # Mass of the rocket WITH NO MOTOR
surfacePressure = 100948.25 # atmospheric pressure at the launch site in Pascals
surfaceTemperature = 313.0 # temperature at the launch site in Kelvin
specificImpulse = 230 * 9.8065 # the avereage (roughly) specific impulse of commertically available motors measured in seconds, converted to Ns/kg. When we integrate with nozzle iterator this crude solution won't be necessary
apogeeThreshold = 0.005 # within what percentage of apogee we want but decimals
burnTimeRange = 0.4 # within what percent of the average burn time do we want to consider burn times
burnTimeStep = 0.1 # step size of burn time iteration
minAvgTtW = 6.0 # minimum thrust to weight we are ok with
bisectionBoundPercDiff = 0.00001 # percent error between thrust value bounds at which we cut off the sim bc theyre too close