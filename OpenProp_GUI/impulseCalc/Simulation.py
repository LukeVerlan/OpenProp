import math
import numpy as np

class SimulationTools:

    def __init__(self, constants, importedDict, elevationProperties_arg):
        self.elevationProperties = elevationProperties_arg
        self.constants = constants
        self.configDict = importedDict


    def getWetMass(self, avgThrust, burnTime):
        wetMass = self.configDict["noMotorMass"] + (1.6 * ((avgThrust * burnTime) / self.configDict["specificImpulse"]) + .354)  # found a regression relationship between prop mass and motor mass
        return wetMass

    def runsimulation(self, deltaT, burnTime, avgThrust, saveData):

        # Initialize a Python list to store data from each iteration
        flight_data_list = []

        xPosition = 0.0
        yPosition = 0.0 # This is altitude above the launch site
        xVelocity = 0.0
        yVelocity = 0.0
        time = 0.0
        propelantMass = (avgThrust * burnTime) / self.configDict["specificImpulse"]
        dryMass = self.configDict["noMotorMass"] + (1.6 * propelantMass + .354) - propelantMass

        # Helper functions for propellant mass and thrust within the runsimulation scope
        def calculate_propellant_mass(current_time):
            if current_time < burnTime:
                return propelantMass * (1 - current_time / burnTime)
            else:
                return 0.0

        def calculate_thrust(current_time):
            if current_time < burnTime:
                return avgThrust
            else:
                return 0.0

        # RK-4 function for getting the derivatives
        # Now returns: [vx, vy, ax, ay], x_thrust, y_thrust, x_drag, y_drag, ax, ay (the last two are redundant with [2] and [3] but useful for clarity)
        def get_derivatives(current_t, current_state):
            x, y, vx, vy = current_state

            # Calculate current properties based on time and altitude
            current_propellant_mass = calculate_propellant_mass(current_t)
            current_mass = dryMass + current_propellant_mass

            current_air_density = self.elevationProperties.calculate_air_density(y, self.configDict["surfacePressure"], self.configDict["surfaceTemperature"], self.configDict["launchSiteElevation"])

            current_weight_force = self.elevationProperties.calculate_gravity_at_elevation(y, self.configDict["launchSiteElevation"]) * current_mass
            current_thrust = calculate_thrust(current_t)

            x_thrust = math.sin(self.configDict["railAngle"]) * current_thrust
            y_thrust = math.cos(self.configDict["railAngle"]) * current_thrust

            # Calculate drag forces
            rel_velocity_x = vx - self.configDict["windVelocity"]
            rel_velocity_y = vy
            velocity_magnitude = math.sqrt(rel_velocity_x**2 + rel_velocity_y**2)

            phi = math.atan2(rel_velocity_x, rel_velocity_y) # Angle of the relative velocity vector
            drag_force = 0.5 * current_air_density * (velocity_magnitude)**2 * self.configDict["dragCoefficient"] * self.configDict["dragArea"]
            x_drag = drag_force * math.sin(phi)
            y_drag = drag_force * math.cos(phi)
            #print("ydrag: " +str(y_drag) +  "ythrust: " + str(y_thrust))
            # Net force
            net_force_x = x_thrust - x_drag
            net_force_y = y_thrust - current_weight_force - y_drag

            # Accelerations
            ax = net_force_x / current_mass
            ay = net_force_y / current_mass

            # Return the derivatives along with the forces and accelerations for saving
            return [vx, vy, ax, ay], x_thrust, y_thrust, x_drag, y_drag, ax, ay

        # Store simulation data for tracking apogee
        max_y_position = 0.0

        # Main simulation loop
        while (yPosition >= 0.0 and yVelocity >= 0.0) and time < 1000:

            # Update max_y_position for apogee tracking
            if yPosition > max_y_position:
                max_y_position = yPosition

            # RK4 Integration Step
            current_state = [xPosition, yPosition, xVelocity, yVelocity]

            # k1: evaluate derivatives at the beginning of the interval
            derivs_k1, x_thrust_k1, y_thrust_k1, x_drag_k1, y_drag_k1, ax_k1, ay_k1 = get_derivatives(time, current_state)

            if saveData:
                # Append all desired data points for the current iteration
                flight_data_list.append([
                    time,
                    xPosition,
                    yPosition,
                    xVelocity,
                    yVelocity,
                    x_thrust_k1, # Forces and accelerations are recorded at the start of the interval (k1)
                    y_thrust_k1,
                    x_drag_k1,
                    y_drag_k1,
                    ax_k1,
                    ay_k1
                ])

            # k2: evaluate derivatives at the midpoint using k1 estimate
            state_k2 = [s + 0.5 * d * deltaT for s, d in zip(current_state, derivs_k1)]
            derivs_k2, _, _, _, _, _, _ = get_derivatives(time + 0.5 * deltaT, state_k2) # Only need the derivatives here

            # k3: evaluate derivatives at the midpoint using k2 estimate
            state_k3 = [s + 0.5 * d * deltaT for s, d in zip(current_state, derivs_k2)]
            derivs_k3, _, _, _, _, _, _ = get_derivatives(time + 0.5 * deltaT, state_k3)

            # k4: evaluate derivatives at the end of the interval using k3 estimate
            state_k4 = [s + d * deltaT for s, d in zip(current_state, derivs_k3)]
            derivs_k4, _, _, _, _, _, _ = get_derivatives(time + deltaT, state_k4)

            # Update state variables using the weighted average of the k values
            xPosition += (derivs_k1[0] + 2*derivs_k2[0] + 2*derivs_k3[0] + derivs_k4[0]) / 6.0 * deltaT
            yPosition += (derivs_k1[1] + 2*derivs_k2[1] + 2*derivs_k3[1] + derivs_k4[1]) / 6.0 * deltaT
            xVelocity += (derivs_k1[2] + 2*derivs_k2[2] + 2*derivs_k3[2] + derivs_k4[2]) / 6.0 * deltaT
            yVelocity += (derivs_k1[3] + 2*derivs_k2[3] + 2*derivs_k3[3] + derivs_k4[3]) / 6.0 * deltaT

            # Update time
            time += deltaT

        # Convert the list of lists to a NumPy array after the loop
        simFlightData = np.array(flight_data_list)

        return max_y_position, simFlightData