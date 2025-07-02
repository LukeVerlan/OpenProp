# IMPULSE CALCULATOR
#
# This is a comprehensive approximate impulse calculator to reach a desired rocket apogee
# This object takes in an openRocket .ork file and a desired apogee, spits out a ballpark
# estimate of the amount of impulse required to get to that height
import numpy as np
from motorlib import constants
import math

deltaT = 0.01  # Time step for simulation in seconds

railAngle = 0.0174533 * 3 # 3 degree in radians
railLength = 4
dragArea = 0.018145
dragCoefficient = 0.75
windVelocity = -5
dryMass = 17.64
propelantMass = 25.71 - 17.64  # Wet mass minus dry mass
gravity = 9.80665
surfacePressure = 101325
surfaceTemperature = 300
burnRate = 2.0175  # kg/s

burnTime = propelantMass / burnRate  # Time in seconds to burn all the propellant
avgThrust = 2500
 

class ImpulseCalculator:

    def calculate_air_density(self, h: float, P0: float, T0: float) -> float:
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
        exponent_base = (gravity * constants.molarMass) / (constants.tempLapseRate * constants.univGasConstant)
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
        

    def runsimulation(self):
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
            currentAirDensity = self.calculate_air_density(yPosition, surfacePressure, surfaceTemperature)
            dragForce = 0.5  * currentAirDensity* (velocityMagnitude) ** 2 * dragCoefficient * dragArea
            phi = math.atan2(relVelocityX, relVelocityY)  # Angle of the relative velocity vector
            xDrag = dragForce * math.sin(phi)
            yDrag = dragForce * math.cos(phi)
            weightForce = gravity * currentMass
            
            # Net force
            netForceX = xThrust - xDrag
            netForceY = yThrust - weightForce - yDrag
            
            # Update velocity and altitude
            xAcceleration = netForceX / currentMass
            yAcceleration = netForceY / currentMass
            xVelocity += xAcceleration * deltaT
            yVelocity += yAcceleration * deltaT
            yPosition += yVelocity * deltaT
            xPosition += xVelocity * deltaT
            
            # Update time
            time += deltaT

        return yPosition, time  # Return the final altitude as apogee


if __name__ == "__main__":
    calculator = ImpulseCalculator()

    for iter in range(20):
        propelantMass = 4.0 + iter * 0.5  # Vary propellant mass from 4.0 kg to 14.0 kg
        burnTime = propelantMass / burnRate
        apogee, time = calculator.runsimulation()
        print(f"Propellant mass: {propelantMass:.2f} kg, Calculated apogee altitude: {apogee:.2f} meters, apogee time: {time:.2f} seconds")
    
    #apogee = calculator.runsimulation()
    #print(f"Calculated apogee altitude: {apogee:.2f} meters")
