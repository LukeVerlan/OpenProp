# IMPULSE CALCULATOR
#
# This is a comprehensive approximate impulse calculator to reach a desired rocket apogee
# This object takes in an openRocket .ork file and a desired apogee, spits out a ballpark
# estimate of the amount of impulse required to get to that height
import numpy as np
import constants
import math
import statistics
 

class ImpulseCalculator:

    def calculate_gravity_at_elevation(self, h, elevation) -> float:
        """
        Calculates the gravitational acceleration at a given altitude above sea level.

        Args:
            h (float): Altitude above sea level in meters (m).

        Returns:
            float: Gravitational acceleration at the given altitude in meters per second squared (m/s^2).
        """
        # Gravitational acceleration decreases with altitude according to the formula:
        gLocal = constants.standardGravity * (constants.earthRadius / (constants.earthRadius + h + elevation))**2
        return gLocal
        

    def calculate_air_density(self, h: float, P0: float, T0: float, elevation) -> float:
        """
        Calculates air density as a function of altitude, given surface conditions,
        using the Ideal Gas Law and a standard atmospheric lapse rate model.

        Assumes dry air and a constant temperature lapse rate in the troposphere.

        Args:
            h (float): Altitude above the surface in meters (m).
            P0 (float): Absolute atmospheric pressure at the surface (h=0) in Pascals (Pa).
            T0 (float): Absolute temperature at the surface (h=0) in Kelvin (K).

        Returns:
            float: Air density at the given altitude in kilograms per cubic meter (kg/m^3).
        """

        # Calculate the exponent term (constant for the model)
        # This is (g0 * M) / (alpha * R_star)
        exponent_base = (self.calculate_gravity_at_elevation(h, elevation) * constants.molarMass) / (constants.tempLapseRate * constants.univGasConstant)
        exponent = exponent_base - 1

        # Calculate temperature at altitude (Th)
        # Ensure T0 - alpha * h doesn't go below 0 (though physical models handle this more gracefully)
        Th = T0 - (constants.tempLapseRate * h)
        if Th <= 0:
            # In a real atmosphere, temperature doesn't drop below absolute zero.
            # This simplification assumes tropospheric conditions.
            # For very high altitudes, different atmospheric layers apply.
            raise ValueError("Calculated temperature at altitude is non-positive, "
                            "indicating altitude is likely beyond troposphere limits or T0 is too low.")

        # Calculate density at altitude (rho_h)
        # The term (P0 / (Rs * T0)) is rho_0 (density at the surface)
        rho_0 = P0 / (constants.specGasConstant * T0)

        # Apply the full formula
        # (Th / T0) represents the temperature ratio
        temperature_ratio = Th / T0

        # Handle potential non-positive base for power function if temperature_ratio is negative
        # This check is primarily for robustness, given Th <= 0 check above
        if temperature_ratio < 0:
            raise ValueError("Temperature ratio (Th/T0) is negative, calculation not possible.")

        rho_h = rho_0 * (temperature_ratio ** exponent)

        return rho_h
    

    def calculate_propellant_mass(self, time: float) -> float:
        """
        Calculate the current mass of the propellant at a given time during the burn.
        
        Args:
            time (float): Time in seconds since the start of the burn.
        
        Returns:
            float: Current mass of the propellant in kilograms.
        """
        if time < burnTime:
            return propelantMass * (1 - time / burnTime)
        else:
            return 0.0
        
    def calculate_thrust(self, time: float) -> float:
        """
        Calculate the thrust at a given time during the burn.
        
        Args:
            time (float): Time in seconds since the start of the burn.
        
        Returns:
            float: Current thrust in Newtons.
        """
        if time < burnTime:
            return avgThrust
        else:
            return 0.0
        

    def runsimulation(self, deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature):
        # This function runs the simulation to calculate the apogee altitude         
        xPosition = 0.0
        yPosition = 0.0
        xVelocity = 0.0
        yVelocity = 0.0
        xAcceleration = 0.0
        yAcceleration = 0.0    
        time = 0.0
        

        while (yPosition == 0.0 or yVelocity > 0.0) and time < 300:
            currentPropelantMass = self.calculate_propellant_mass(time)
            currentThrust = self.calculate_thrust(time)

            xThrust = math.sin(railAngle)*currentThrust
            yThrust = math.cos(railAngle)*currentThrust
            currentMass = dryMass + currentPropelantMass
            
            # Calculate drag and weight forces
            relVelocityX = xVelocity - windVelocity
            relVelocityY = yVelocity
            velocityMagnitude = math.sqrt(relVelocityX**2 + relVelocityY**2)
            currentAirDensity = self.calculate_air_density(yPosition, surfacePressure, surfaceTemperature, launchSiteElevation)
            dragForce = 0.5  * currentAirDensity* (velocityMagnitude) ** 2 * dragCoefficient * dragArea
            phi = math.atan2(relVelocityX, relVelocityY)  # Angle of the relative velocity vector
            xDrag = dragForce * math.sin(phi)
            yDrag = dragForce * math.cos(phi)
            currentWeightForce = self.calculate_gravity_at_elevation(yPosition, launchSiteElevation) * currentMass
            
            # Net force
            netForceX = xThrust - xDrag
            netForceY = yThrust - currentWeightForce - yDrag
            
            # Update position velocity and altitude
            yPosition += yVelocity * deltaT + 0.5 * yAcceleration * deltaT ** 2
            xPosition += xVelocity * deltaT + 0.5 * xAcceleration * deltaT ** 2
            xVelocity += xAcceleration * deltaT
            yVelocity += yAcceleration * deltaT
            xAcceleration = netForceX / currentMass
            yAcceleration = netForceY / currentMass

            # Update time
            time += deltaT
        #print("used simulation function")

        return yPosition, time  # Return the final altitude as apogee

    def calculate_Impulse_needed(self, desiredApogee, deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature):
        """
        takes in the parameters of the rocket and the desired apogee, iterates through a bunch of burn times and average thrust values by running a simulation for each and finding whether they reached the desired apogee. returns the thrust, burn time, and apogee for each successful run.
        Also returns the minimum, 25th, 50th, 75th, and maximum impulse values calculated from the successful runs.
        """
        passingThrustBurntimeApogeeSet = [] #initialize the list of passing thrust, burn time, and apogee sets
        global avgThrust 
        avgThrust = dryMass * constants.standardGravity * 7 # begin iterations at a avgThrust to weight of 7
        global burnTime 
        burnTime = 0.0001 #start with very small but non-zero burn time to avoid division by zero errors
        ##### needs to dynamcally set propellant mass and dry mass according to avg thrust and burn time 

        #counter1 = 0
        #counter2 = 0
        apogee, flightTime = self.runsimulation(deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature) # run sim with initial values and pass apogee into the while loop
        while apogee <= 1.05* desiredApogee: # loop until the burn time is long enough to reach the desired apogee
            #counter1 += 1 # debugging counter
            #if counter1%1 == 0:
            #    print("starting burntime loop" + " counter: " + str(counter1) + " avgThrust: " + str(avgThrust) + " burntime: " + str(burnTime) + " apogee: " + str(apogee))
            while apogee <= 1.05* desiredApogee: #loop until thrust is high enough to reach the desired apogee
                #counter2 += 1 # debugging counter
                #if counter2%50 == 0:
                #    print("starting thrust loop" + " counter: " + str(counter2) + " avgThrust: " + str(avgThrust) + " burntime: " + str(burnTime) + " apogee: " + str(apogee))
                if apogee <= 1.05* desiredApogee and apogee >= .95* desiredApogee: # store successful runs
                    passingThrustBurntimeApogeeSet.append((avgThrust, burnTime, apogee))
                    avgThrust += dryMass*constants.standardGravity * 0.1 # want to set this to an input variable later
                else:
                    # Increase the average thrust to try to reach the desired apogee
                    avgThrust += dryMass*constants.standardGravity * 0.1  # want to set this to an input variable later
                apogee, flightTime = self.runsimulation(deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature)

            avgThrust = dryMass*constants.standardGravity*7 # reset avg thrust to a value of 7 times the weight of the rocket
            apogee, flightTime = self.runsimulation(deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature) #run sim with initial values and pass apogee into the while loop
            
            if apogee <= 1.05* desiredApogee and apogee >= .95* desiredApogee: #store successful runs
                passingThrustBurntimeApogeeSet.append((avgThrust, burnTime, apogee))
                burnTime += 0.1  # want to set this to an input variable later
            else:
                # Increase the average thrust to try to reach the desired apogee
                burnTime += 0.1  # want to set this to an input variable later
            apogee, flightTime = self.runsimulation(deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature)

        passingThrustBurntimeApogeeSet.sort()  # Sort by thrust for data organization

        second_column_values = [row[1] for row in passingThrustBurntimeApogeeSet] # Extract the second column (burn time) values for filtering
        initial_mean_col1 = statistics.mean(set(second_column_values)) #reference again the mean of all unuqie burn time values to cut out unusually high or low burnt times. BREAKS DOWN WITH SMALL STEPS IN BURN TIME???
        lower_bound_col1 = 0.5 * initial_mean_col1 #set bounds
        upper_bound_col1 = 1.5 * initial_mean_col1
        filtered_passingThrustBurntimeApogeeSet = []

        for row in passingThrustBurntimeApogeeSet:
            if lower_bound_col1 <= row[1] <= upper_bound_col1:
                filtered_passingThrustBurntimeApogeeSet.append(row) #create placeholder which only takes in rows with satisfactory burn times

        passingThrustBurntimeApogeeSet = filtered_passingThrustBurntimeApogeeSet #update list after filtering

        passingImpulses = [] #initialize the list of passing impulses
        for thrust, burn_time, apogee in passingThrustBurntimeApogeeSet:
            impulse = thrust * burn_time 
            passingImpulses.append(impulse) # fill the list using the table of passing thrust, burn time, and apogees

        return min(passingImpulses), passingImpulses[round(.25*len(passingImpulses))], passingImpulses[round(.5*len(passingImpulses))], passingImpulses[round(.75*len(passingImpulses))], max(passingImpulses), len(passingImpulses), np.mean(passingImpulses), passingThrustBurntimeApogeeSet  
    #return the minimum, 25th, 50th, 75th, and maximum impulse values calculated from the successful runs, the total number of impulses calculated, the mean impulse value, and the passing thrust, burn time, and apogee sets
                

if __name__ == "__main__":

    # the necessary user inputs for running the simulations and the impulse calculator

    desiredApogee = 3048.0  # Desired apogee in meters
    deltaT = 0.01  # Time step for simulation in seconds

    railAngleDeg = 3.0  # Angle of the launch rail in degrees
    railAngle = constants.radPerDegree * railAngleDeg # launch rail angle in radians, assumed in the direction of wind
    railLength = 4.0 # length of the launch rail in meters, currently unused
    launchSiteElevation = 848.0  # Elevation of the launch site in meters
    dragArea = 0.018145 # drag facing area in square meters, needs to be dynamically set based on rocket axis and drag vector
    dragCoefficient = 0.75 #drag coefficient, needs to be dynamically set based on rocket axis and drag vector
    windVelocity = -2.5 # assumed constant the whole way up, ideally should be increasing with altitude

    dryMass = 17.64  #this is funky wunky bc it is connected with propellant mass, so it needs to be dynamically set based on the average thrust and burn time
    propelantMass = 25.71 - 17.64  # really needs to be dynamically set based on the average thrust and burn time, but for now it is a constant

    surfacePressure = 100948.25 # atmospheric pressure at the launch site in Pascals
    surfaceTemperature = 313.0 # temperature at the launch site in Kelvin
    #burnRate = 2.0175  # kg/s
    #burnTime = 4.0  # Time in seconds to burn all the propellant
    #avgThrust = 2500.0


    calculator = ImpulseCalculator() #initializes the impulse calculator object
    possibleImpulseInfo = calculator.calculate_Impulse_needed(desiredApogee, deltaT, railAngle, railLength, launchSiteElevation, dragArea, dragCoefficient, windVelocity, dryMass, propelantMass, surfacePressure, surfaceTemperature)  #actually runs the impulse calculator and returns the possible impulse information

    #prints all of the information input by the user
    print("Impulse Calculator Inputs:")
    print(f"Desired apogee: {desiredApogee:.2f} m")
    print(f"Rail angle: {railAngleDeg:.2f} degrees")
    print(f"Rail length: {railLength:.2f} m")
    print(f"Launch site elevation: {launchSiteElevation:.2f} m")
    print(f"Drag area: {dragArea:.4f} m^2")
    print(f"Drag coefficient: {dragCoefficient:.2f}")
    print(f"Wind velocity: {windVelocity:.2f} m/s")
    print(f"Dry mass: {dryMass:.2f} kg") # remember this is funky wunky and will needs to not be a constant 
    print(f"Propellant mass: {propelantMass:.2f} kg") # ^^^^^^^^^
    print(f"Surface pressure: {surfacePressure:.2f} Pa")
    print(f"Surface temperature: {surfaceTemperature:.2f} K")
    print(f"Delta T: {deltaT:.2f} s")
    

    #prints all of the interesting information from the impulse calculator
    print("Impulse Calculator Results:")
    print(f"Minimum impulse needed: {possibleImpulseInfo[0]:.2f} N*s")
    print(f"25th percentile impulse: {possibleImpulseInfo[1]:.2f} N*s")
    print(f"50th percentile impulse: {possibleImpulseInfo[2]:.2f} N*s")
    print(f"75th percentile impulse: {possibleImpulseInfo[3]:.2f} N*s")
    print(f"Maximum impulse needed: {possibleImpulseInfo[4]:.2f} N*s")
    print(f"Total number of impulses calculated: {possibleImpulseInfo[5]}")
    print(f"Mean impulse needed: {possibleImpulseInfo[6]:.2f} N*s")

    #prings a somewhat representative set of thrust, burn time, and apogee values
    print("Thrust, burn time, apogee sets:")
    count = 0
    for thrust, burn_time, apogee in possibleImpulseInfo[7]: #prints every nth thrust, burn time, and apogee set
        count += 1
        if count % 10 == 0:
            print(f"Thrust: {thrust:.2f} N, Burn time: {burn_time:.2f} s, Apogee: {apogee:.2f} m")

    
