class elevationDepProperties:

    def calculate_gravity_at_elevation(self, h, elevation):
        """
        Calculates the gravitational acceleration at a given altitude above sea level.

        Args:
            h (float): Altitude above sea level in meters (m).

        Returns:
            float: Gravitational acceleration at the given altitude in meters per second squared (m/s^2).
        """
        # Gravitational acceleration decreases with altitude according to the formula:
        gLocal = self.constants.standardGravity * (self.constants.earthRadius / (self.constants.earthRadius + h + elevation))**2
        return gLocal
    
    def calculate_air_density(self, h, P0, T0, elevation):
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
        exponent_base = (self.calculate_gravity_at_elevation(h, elevation) * self.constants.molarMass) / (self.constants.tempLapseRate * self.constants.univGasConstant)
        exponent = exponent_base - 1

        # Calculate temperature at altitude (Th)
        # Ensure T0 - alpha * h doesn't go below 0 (though physical models handle this more gracefully)
        Th = T0 - (self.constants.tempLapseRate * h)
        if Th <= 0:
            # In a real atmosphere, temperature doesn't drop below absolute zero.
            # This simplification assumes tropospheric conditions.
            # For very high altitudes, different atmospheric layers apply.
            raise ValueError("Calculated temperature at altitude is non-positive, "
                            "indicating altitude is likely beyond troposphere limits or T0 is too low.")

        # Calculate density at altitude (rho_h)
        # The term (P0 / (Rs * T0)) is rho_0 (density at the surface)
        rho_0 = P0 / (self.constants.specGasConstant * T0)

        # Apply the full formula
        # (Th / T0) represents the temperature ratio
        temperature_ratio = Th / T0

        # Handle potential non-positive base for power function if temperature_ratio is negative
        # This check is primarily for robustness, given Th <= 0 check above
        if temperature_ratio < 0:
            raise ValueError("Temperature ratio (Th/T0) is negative, calculation not possible.")

        rho_h = rho_0 * (temperature_ratio ** exponent)

        return rho_h

    def __init__(self, constants):
        self.constants = constants

