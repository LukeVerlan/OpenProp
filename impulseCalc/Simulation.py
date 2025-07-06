import math
import parameters

class SimulationTools:

    def __init__(self, constants, parameters, elevationProperties_arg): 
        self.elevationProperties = elevationProperties_arg
        self.constants = constants
        self.parameters = parameters


    def getWetMass(avgThrust, burnTime):
            wetMass = parameters.noMotorMass + (1.6 * ((avgThrust * burnTime) / parameters.specificImpulse) + .354)  # found a regression relationship between prop mass and motor mass
            return wetMass

    def runsimulation(self, deltaT, burnTime, avgThrust):
        
        xPosition = 0.0
        yPosition = 0.0 # This is altitude above the launch site
        xVelocity = 0.0
        yVelocity = 0.0
        time = 0.0
        propelantMass = (avgThrust * burnTime) / parameters.specificImpulse
        dryMass = parameters.noMotorMass + (1.6 * propelantMass + .354) - propelantMass
        #print("prop mass = " + str(propelantMass))
        #print("total motor mass  = " + str(1.6 * propelantMass + .354))
        #print("dry mass = " + str(dryMass))

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
        def get_derivatives(current_t, current_state):
            x, y, vx, vy = current_state

            # Calculate current properties based on time and altitude
            current_propellant_mass = calculate_propellant_mass(current_t)
            current_mass = dryMass + current_propellant_mass

            current_air_density = self.elevationProperties.calculate_air_density(y, self.parameters.surfacePressure, self.parameters.surfaceTemperature, self.parameters.launchSiteElevation)

            current_weight_force = self.elevationProperties.calculate_gravity_at_elevation(y, self.parameters.launchSiteElevation) * current_mass
            current_thrust = calculate_thrust(current_t)

            x_thrust = math.sin(parameters.railAngle) * current_thrust
            y_thrust = math.cos(parameters.railAngle) * current_thrust

            # Calculate drag forces
            rel_velocity_x = vx - parameters.windVelocity
            rel_velocity_y = vy
            velocity_magnitude = math.sqrt(rel_velocity_x**2 + rel_velocity_y**2)

            phi = math.atan2(rel_velocity_x, rel_velocity_y) # Angle of the relative velocity vector
            drag_force = 0.5 * current_air_density * (velocity_magnitude)**2 * parameters.dragCoefficient * parameters.dragArea
            x_drag = drag_force * math.sin(phi)
            y_drag = drag_force * math.cos(phi)

            # Net force
            net_force_x = x_thrust - x_drag
            net_force_y = y_thrust - current_weight_force - y_drag

            # Accelerations
            ax = net_force_x / current_mass
            ay = net_force_y / current_mass

            # Return the derivatives: [vx, vy, ax, ay]
            return [vx, vy, ax, ay]

        # Store simulation data for tracking apogee
        max_y_position = 0.0

        # Main simulation loop
        while (yPosition >= 0.0 and yVelocity >= 0.0) and time < 1000: 

            #print("penis " + str(yPosition))
            # Update max_y_position for apogee tracking
            if yPosition > max_y_position:
                max_y_position = yPosition
            
            # RK4 Integration Step
            current_state = [xPosition, yPosition, xVelocity, yVelocity]

            # k1: evaluate derivatives at the beginning of the interval
            k1 = get_derivatives(time, current_state)
            
            # k2: evaluate derivatives at the midpoint using k1 estimate
            state_k2 = [s + 0.5 * d * deltaT for s, d in zip(current_state, k1)]
            k2 = get_derivatives(time + 0.5 * deltaT, state_k2)
            
            # k3: evaluate derivatives at the midpoint using k2 estimate
            state_k3 = [s + 0.5 * d * deltaT for s, d in zip(current_state, k2)]
            k3 = get_derivatives(time + 0.5 * deltaT, state_k3)
            
            # k4: evaluate derivatives at the end of the interval using k3 estimate
            state_k4 = [s + d * deltaT for s, d in zip(current_state, k3)]
            k4 = get_derivatives(time + deltaT, state_k4)

            # Update state variables using the weighted average of the k values
            xPosition += (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) / 6.0 * deltaT
            yPosition += (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) / 6.0 * deltaT
            xVelocity += (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]) / 6.0 * deltaT
            yVelocity += (k1[3] + 2*k2[3] + 2*k3[3] + k4[3]) / 6.0 * deltaT

            # Update time
            time += deltaT

        return max_y_position

    
