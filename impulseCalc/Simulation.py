import math
from elevationProperties import elevationDepProperties

class SimulationTools:

    def __init__(self, constants, parameters, elevationProperties_arg): # Rename argument for clarity
        self.elevationProperties = elevationProperties_arg # Use the passed instance
        self.constants = constants
        self.parameters = parameters


    def runsimulation(self, deltaT, burnTime, avgThrust): # Removed parameters and elevationProperties args, using self.
        # This function runs the simulation to calculate the apogee altitude
        xPosition = 0.0
        yPosition = 0.0 # This is altitude *above the launch site*
        xVelocity = 0.0
        yVelocity = 0.0
        xAcceleration = 0.0
        yAcceleration = 0.0
        time = 0.0

        # Helper function for propellant mass within the runsimulation scope
        def calculate_propellant_mass(current_time):
            if current_time < burnTime:
                # Assuming parameters.propelantMass is the TOTAL propellant mass
                return self.parameters.propelantMass * (1 - current_time / burnTime)
            else:
                return 0.0

        # Helper function for thrust within the runsimulation scope
        def calculate_thrust(current_time):
            if current_time < burnTime:
                return avgThrust
            else:
                return 0.0

        while (yPosition == 0.0 or yVelocity >= 0.0) and time < 300: # yPosition can be slightly negative due to calculation quirks

            # print("started sim")
            # print("current vals: " + str(yPosition))
            yPosition += yVelocity * deltaT # This is technically using the updated velocity for the whole deltaT
            xPosition += xVelocity * deltaT # This is technically using the updated velocity for the whole deltaT
            xVelocity += xAcceleration * deltaT 
            yVelocity += yAcceleration * deltaT

            currentPropelantMass = calculate_propellant_mass(time) # Call the local helper
            currentMass = self.parameters.dryMass + currentPropelantMass
            currentAirDensity = self.elevationProperties.calculate_air_density(yPosition, self.parameters.surfacePressure, self.parameters.surfaceTemperature, self.parameters.launchSiteElevation)
            currentWeightForce = self.elevationProperties.calculate_gravity_at_elevation(yPosition, self.parameters.launchSiteElevation, ) * currentMass

            currentThrust = calculate_thrust(time) # Call the local helper

            xThrust = math.sin(self.parameters.railAngle) * currentThrust
            yThrust = math.cos(self.parameters.railAngle) * currentThrust

            # Calculate drag and weight forces
            relVelocityX = xVelocity - self.parameters.windVelocity
            relVelocityY = yVelocity
            velocityMagnitude = math.sqrt(relVelocityX**2 + relVelocityY**2)

            phi = math.atan2(relVelocityX, relVelocityY) # Angle of the relative velocity vector

            dragForce = 0.5 * currentAirDensity * (velocityMagnitude) ** 2 * self.parameters.dragCoefficient * self.parameters.dragArea
            xDrag = dragForce * math.sin(phi)
            yDrag = dragForce * math.cos(phi)

            # Net force
            netForceX = xThrust - xDrag
            netForceY = yThrust - currentWeightForce - yDrag

            xAcceleration = netForceX / currentMass
            yAcceleration = netForceY / currentMass

            # Update time
            time += deltaT

        return yPosition # Return the final altitude as apogee
    
