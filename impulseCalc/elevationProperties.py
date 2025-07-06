class elevationDepProperties:

    def calculate_gravity_at_elevation(self, h, elevation):
        """
        Calculates the gravitational acceleration at a given altitude above sea level.

        Args:
            h: Altitude above sea level in meters (m).
            elevation: Elevation of the launch site above sea level 

        Returns:
            Gravitational acceleration at the given altitude in meters per second squared (m/s^2)
            
        """
        gLocal = self.constants.standardGravity * (self.constants.earthRadius / (self.constants.earthRadius + h + elevation))**2
        return gLocal
    
    def calculate_air_density(self, h, P0, T0, elevation):
        """
        Calculates air density as a function of altitude, given surface conditions,
        using the Ideal Gas Law and a standard atmospheric lapse rate model.

        Assumes dry air and a constant temperature lapse rate in the troposphere.

        Args:
            h: Altitude above the surface in meters (m).
            P0: Absolute atmospheric pressure at the surface (h=0) in Pascals (Pa).
            T0: Absolute temperature at the surface (h=0) in Kelvin (K).
            elevation: Elevation of the launch site above sea level 
        Returns:
            float: Air density at the given altitude in kilograms per cubic meter (kg/m^3).
        """

        # Calculate the exponent term (constant for the model)
        exponent_base = (self.calculate_gravity_at_elevation(h, elevation) * self.constants.molarMass) / (self.constants.tempLapseRate * self.constants.univGasConstant)
        exponent = exponent_base - 1

        # Calculate temperature at altitude 
        Th = T0 - (self.constants.tempLapseRate * h)
        if Th <= 0:
            raise ValueError("Calculated temperature at altitude is non-positive, "
                            "indicating altitude is likely beyond troposphere limits or T0 is too low.")

        # Calculate density at altitude 
        rho_0 = P0 / (self.constants.specGasConstant * T0)

        # Apply the full formula
        temperature_ratio = Th / T0

        if temperature_ratio < 0:
            raise ValueError("Temperature ratio (Th/T0) is negative, calculation not possible.")

        rho_h = rho_0 * (temperature_ratio ** exponent)

        return rho_h

    def __init__(self, constants):
        self.constants = constants

