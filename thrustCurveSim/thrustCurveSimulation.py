# import numpy as np
# import math
# import os

# # --- Import actual ElevationProperties and consts ---
# # IMPORTANT: You need to replace 'your_module_path' with the actual path
# # to your ElevationProperties class (e.g., from impulseCalc.elevationTools import ElevationProperties)
# from impulseCalc.elevationProperties import elevationDepProperties
# #from impulseCalc.constants import constants


# # Column indices for the flight_data_array (simFlightData)
# # These should match how the simulation function populates the array.
# # Ensure these match the expectations of FlightDataPlotter as well.
# TIME_COL = 0
# X_POS_COL = 1
# Y_POS_COL = 2
# X_VEL_COL = 3
# Y_VEL_COL = 4
# X_THRUST_COL = 5
# Y_THRUST_COL = 6
# X_DRAG_COL = 7
# Y_DRAG_COL = 8
# X_ACCEL_COL = 9
# Y_ACCEL_COL = 10


# class ThrustCurveSimulator: # Renamed from _ThrustCurveSimulator for external use
#     """
#     Encapsulates the flight simulation logic, adapted to use a thrust curve.
#     This class is intended to be called by ThrustCurveFlightSimApp.
#     """
#     def __init__(self, constants, importedDict, elevationProperties_arg):
#         self.elevationProperties = elevationProperties_arg
#         self.constants = constants
#         self.configDict = importedDict
        
#         # Removed the redundant self.g0 line.
#         # It is correctly accessed via self.constants.standardGravity or through self.elevationProperties.

#     def runsimulation(self, deltaT, thrust_curve_filepath, saveData=True):
#         """
#         Runs the flight simulation using a provided thrust curve.

#         Args:
#             deltaT (float): Time step for the simulation.
#             thrust_curve_filepath (str): Path to the CSV file containing thrust and time data.
#             saveData (bool): Whether to save detailed flight data.

#         Returns:
#             tuple: (sim_stats_dict, simFlightData)
#                 sim_stats_dict: Dictionary containing simulation summary statistics.
#                 simFlightData: NumPy array with detailed flight data.
#         """
#         # Load thrust curve data from the provided filepath
#         if not os.path.exists(thrust_curve_filepath):
#             raise FileNotFoundError(f"Thrust curve file not found: {thrust_curve_filepath}")
#         try:
#             # Assuming header row, time in col 0, thrust in col 1
#             thrust_curve_data = np.loadtxt(thrust_curve_filepath, delimiter=',', skiprows=1)
#             if thrust_curve_data.ndim != 2 or thrust_curve_data.shape[1] < 2:
#                 raise ValueError("Thrust curve CSV must have at least two columns (time, thrust).")
#             # Ensure thrust_curve_data is sorted by time for interpolation
#             thrust_curve_data = thrust_curve_data[thrust_curve_data[:, 0].argsort()]

#         except Exception as e:
#             raise ValueError(f"Error loading thrust curve data from {thrust_curve_filepath}: {e}")

#         # Initialize a Python list to store data from each iteration
#         flight_data_list = []

#         xPosition = 0.0
#         yPosition = 0.0 # This is altitude above the launch site
#         xVelocity = 0.0
#         yVelocity = 0.0
#         time = 0.0

#         # Extract time and thrust arrays from thrust_curve_data
#         thrust_time_points = thrust_curve_data[:, 0]
#         thrust_values = thrust_curve_data[:, 1]

#         burnTime = thrust_time_points[-1] if len(thrust_time_points) > 0 else 0.0

#         # Calculate total impulse from the thrust curve
#         total_impulse = np.trapz(thrust_values, thrust_time_points)

#         # Calculate total propellant mass based on total impulse and specific impulse
#         # Changed default specific impulse to 2200 as per previous discussion
#         specific_impulse = self.configDict["ImpulseCalculator"].get("specificImpulse", 2200) # N*s/kg
#         if specific_impulse == 0:
#             raise ValueError("Specific Impulse cannot be zero.")
#         total_propellant_mass = total_impulse / specific_impulse

#         # Calculate initial total mass of the rocket
#         # Replicating original mass calculation structure for consistency
#         # Assuming 'noMotorMass' is the dry mass of the rocket without propellant/motor casing
#         # And (1.6 * total_propellant_mass + .354) represents the motor casing and structural factor
#         dryMass = self.configDict["ImpulseCalculator"].get("noMotorMass", 1.0) + (1.6 * total_propellant_mass + 0.354) - total_propellant_mass


#         # RK-4 function for getting the derivatives
#         # Now returns: [vx, vy, ax, ay], x_thrust, y_thrust, x_drag, y_drag, ax, ay (the last two are redundant with [2] and [3] but useful for clarity)
#         def get_derivatives(current_t, current_state):
#             x, y, vx, vy = current_state

#             # Calculate current properties based on time and altitude
#             # Mass calculation based on propellant depletion from thrust curve
#             current_thrust_at_t = np.interp(current_t, thrust_time_points, thrust_values, left=0.0, right=0.0)
            
#             # Approximate propellant mass remaining for current_t based on total impulse and specific impulse
#             # This is a simplified approach. A more accurate model would track mass flow rate.
#             # For now, we'll use a simple linear depletion based on burnTime and total_propellant_mass
#             # or based on cumulative impulse. Sticking to cumulative impulse for consistency.
            
#             # The mass calculation in the loop will use 'cumulative_impulse' which is updated per step.
#             # So, current_propellant_mass is derived from that.
#             current_propellant_mass = max(0.0, total_propellant_mass - (cumulative_impulse / specific_impulse))
#             current_mass = dryMass + current_propellant_mass # Using the calculated dryMass from above

#             current_air_density = self.elevationProperties.calculate_air_density(
#                 y,
#                 self.configDict["ImpulseCalculator"]["surfacePressure"],
#                 self.configDict["ImpulseCalculator"]["surfaceTemperature"],
#                 self.configDict["ImpulseCalculator"]["launchSiteElevation"]
#             )

#             current_weight_force = self.elevationProperties.calculate_gravity_at_elevation(
#                 y,
#                 self.configDict["ImpulseCalculator"]["launchSiteElevation"]
#             ) * current_mass

#             # Get thrust from the thrust curve at current_t
#             current_thrust = np.interp(current_t, thrust_time_points, thrust_values, left=0.0, right=0.0)

#             x_thrust = math.sin(self.configDict["ImpulseCalculator"]["railAngle"]) * current_thrust
#             y_thrust = math.cos(self.configDict["ImpulseCalculator"]["railAngle"]) * current_thrust

#             # Calculate drag forces
#             rel_velocity_x = vx - self.configDict["ImpulseCalculator"]["windVelocity"]
#             rel_velocity_y = vy
#             velocity_magnitude = math.sqrt(rel_velocity_x**2 + rel_velocity_y**2)

#             # Avoid division by zero if velocity is zero
#             phi = math.atan2(rel_velocity_x, rel_velocity_y) if velocity_magnitude > 1e-6 else 0.0

#             drag_force = 0.5 * current_air_density * (velocity_magnitude)**2 * \
#                          self.configDict["ImpulseCalculator"]["dragCoefficient"] * \
#                          self.configDict["ImpulseCalculator"]["dragArea"]
#             x_drag = drag_force * math.sin(phi)
#             y_drag = drag_force * math.cos(phi)
            
#             # Net force
#             net_force_x = x_thrust - x_drag
#             net_force_y = y_thrust - current_weight_force - y_drag

#             # Accelerations
#             ax = net_force_x / current_mass
#             ay = net_force_y / current_mass

#             # Return the derivatives along with the forces and accelerations for saving
#             return [vx, vy, ax, ay], x_thrust, y_thrust, x_drag, y_drag, ax, ay

#         # Store simulation data for tracking apogee
#         max_y_position = 0.0
#         max_velocity = 0.0
#         max_acceleration = 0.0
#         total_thrust_sum = 0.0
#         thrust_sample_count = 0
#         cumulative_impulse = 0.0 # Initialize cumulative impulse for the loop

#         # Main simulation loop
#         while (yPosition >= 0.0 or yVelocity > 0.0) and time < 1000: # Continue until ground hit and descent or max time
#             # Update max_y_position for apogee tracking
#             if yPosition > max_y_position:
#                 max_y_position = yPosition

#             # RK4 Integration Step
#             current_state = [xPosition, yPosition, xVelocity, yVelocity]

#             # k1: evaluate derivatives at the beginning of the interval
#             derivs_k1, x_thrust_k1, y_thrust_k1, x_drag_k1, y_drag_k1, ax_k1, ay_k1 = \
#                 get_derivatives(time, current_state) # Removed cumulative_impulse from get_derivatives args as it's a closure

#             # Record current state and forces/accelerations for plotting
#             if saveData:
#                 flight_data_list.append([
#                     time,
#                     xPosition,
#                     yPosition,
#                     xVelocity,
#                     yVelocity,
#                     x_thrust_k1, # Forces and accelerations are recorded at the start of the interval (k1)
#                     y_thrust_k1,
#                     x_drag_k1,
#                     y_drag_k1,
#                     ax_k1,
#                     ay_k1
#                 ])

#             # Update max velocity and acceleration
#             current_velocity_magnitude = math.sqrt(xVelocity**2 + yVelocity**2)
#             if current_velocity_magnitude > max_velocity:
#                 max_velocity = current_velocity_magnitude

#             current_acceleration_magnitude = math.sqrt(ax_k1**2 + ay_k1**2)
#             if current_acceleration_magnitude > max_acceleration:
#                 max_acceleration = current_acceleration_magnitude

#             # Calculate average thrust during burn
#             if time <= burnTime and np.interp(time, thrust_time_points, thrust_values, left=0.0, right=0.0) > 0:
#                 total_thrust_sum += np.interp(time, thrust_time_points, thrust_values, left=0.0, right=0.0)
#                 thrust_sample_count += 1

#             # k2: evaluate derivatives at the midpoint using k1 estimate
#             state_k2 = [s + 0.5 * d * deltaT for s, d in zip(current_state, derivs_k1)]
#             derivs_k2, _, _, _, _, _, _ = get_derivatives(time + 0.5 * deltaT, state_k2) # Removed cumulative_impulse

#             # k3: evaluate derivatives at the midpoint using k2 estimate
#             state_k3 = [s + 0.5 * d * deltaT for s, d in zip(current_state, derivs_k2)]
#             derivs_k3, _, _, _, _, _, _ = get_derivatives(time + 0.5 * deltaT, state_k3)

#             # k4: evaluate derivatives at the end of the interval using k3 estimate
#             state_k4 = [s + d * deltaT for s, d in zip(current_state, derivs_k3)]
#             derivs_k4, _, _, _, _, _, _ = get_derivatives(time + deltaT, state_k4)

#             # Update state variables using the weighted average of the k values
#             xPosition += (derivs_k1[0] + 2*derivs_k2[0] + 2*derivs_k3[0] + derivs_k4[0]) / 6.0 * deltaT
#             yPosition += (derivs_k1[1] + 2*derivs_k2[1] + 2*derivs_k3[1] + derivs_k4[1]) / 6.0 * deltaT
#             xVelocity += (derivs_k1[2] + 2*derivs_k2[2] + 2*derivs_k3[2] + derivs_k4[2]) / 6.0 * deltaT
#             yVelocity += (derivs_k1[3] + 2*derivs_k2[3] + 2*derivs_k3[3] + derivs_k4[3]) / 6.0 * deltaT

#             # Update time
#             time += deltaT

#             # Update cumulative impulse for the next iteration's mass calculation
#             next_thrust = np.interp(time, thrust_time_points, thrust_values, left=0.0, right=0.0)
#             cumulative_impulse += (np.interp(time - deltaT, thrust_time_points, thrust_values, left=0.0, right=0.0) + next_thrust) / 2.0 * deltaT


#         # Convert the list of lists to a NumPy array after the loop
#         simFlightData = np.array(flight_data_list)

#         # Calculate average thrust during the actual burn time (if any thrust was produced)
#         avg_thrust_actual = total_thrust_sum / thrust_sample_count if thrust_sample_count > 0 else 0.0

#         sim_stats_dict = {
#             "avg_thrust": avg_thrust_actual,
#             "burn_time": burnTime, # This is the duration of the thrust curve
#             "apogee": max_y_position,
#             "max_velocity": max_velocity,
#             "max_acceleration": max_acceleration
#         }

#         return sim_stats_dict, simFlightData

import numpy as np
import math
import os

# --- Import actual ElevationProperties and consts ---
from impulseCalc.elevationProperties import elevationDepProperties
#import consts


# Column indices for the flight_data_array (simFlightData)
TIME_COL = 0
X_POS_COL = 1
Y_POS_COL = 2
X_VEL_COL = 3
Y_VEL_COL = 4
X_THRUST_COL = 5
Y_THRUST_COL = 6
X_DRAG_COL = 7
Y_DRAG_COL = 8
X_ACCEL_COL = 9
Y_ACCEL_COL = 10


class ThrustCurveSimulator:
    def __init__(self, constants, importedDict, elevationProperties_arg):
        self.elevationProperties = elevationProperties_arg
        self.constants = constants
        self.configDict = importedDict
        
    def runsimulation(self, deltaT, thrust_curve_filepath, saveData=True):
        """
        Runs the flight simulation using a provided thrust curve.
        """
        print(f"\n--- Starting ThrustCurveSimulator.runsimulation ---")
        print(f"Config Dict: {self.configDict}")
        print(f"Thrust Curve Filepath: {thrust_curve_filepath}")

        # Load thrust curve data from the provided filepath
        if not os.path.exists(thrust_curve_filepath):
            raise FileNotFoundError(f"Thrust curve file not found: {thrust_curve_filepath}")
        try:
            thrust_curve_data = np.loadtxt(thrust_curve_filepath, delimiter=',', skiprows=1)
            if thrust_curve_data.ndim != 2 or thrust_curve_data.shape[1] < 2:
                raise ValueError("Thrust curve CSV must have at least two columns (time, thrust).")
            thrust_curve_data = thrust_curve_data[thrust_curve_data[:, 0].argsort()]
            print(f"Loaded thrust curve data shape: {thrust_curve_data.shape}")
            print(f"First 5 thrust curve points:\n{thrust_curve_data[:5]}")
            print(f"Last 5 thrust curve points:\n{thrust_curve_data[-5:]}")

        except Exception as e:
            raise ValueError(f"Error loading thrust curve data from {thrust_curve_filepath}: {e}")

        flight_data_list = []

        xPosition = 0.0
        yPosition = 0.0
        xVelocity = 0.0
        yVelocity = 0.0
        time = 0.0

        thrust_time_points = thrust_curve_data[:, 0]
        thrust_values = thrust_curve_data[:, 1]

        burnTime = thrust_time_points[-1] if len(thrust_time_points) > 0 else 0.0
        print(f"Burn Time (from thrust curve): {burnTime:.2f} s")

        total_impulse = np.trapz(thrust_values, thrust_time_points)
        print(f"Total Impulse (from thrust curve): {total_impulse:.2f} Ns")

        specific_impulse = self.configDict["ImpulseCalculator"].get("specificImpulse", 2200)
        if specific_impulse == 0:
            raise ValueError("Specific Impulse cannot be zero.")
        total_propellant_mass = total_impulse / specific_impulse
        print(f"Specific Impulse: {specific_impulse:.2f} Ns/kg")
        print(f"Total Propellant Mass: {total_propellant_mass:.4f} kg")

        noMotorMass = self.configDict["ImpulseCalculator"].get("noMotorMass", 1.0)
        dryMass = noMotorMass + (1.6 * total_propellant_mass + 0.354) - total_propellant_mass
        print(f"No Motor Mass (from config): {noMotorMass:.2f} kg")
        print(f"Calculated Dry Mass: {dryMass:.4f} kg")


        cumulative_impulse = 0.0 

        def get_derivatives(current_t, current_state):
            x, y, vx, vy = current_state

            current_propellant_mass = max(0.0, total_propellant_mass - (cumulative_impulse / specific_impulse))
            current_mass = dryMass + current_propellant_mass 
            
            # Debugging mass calculation
            # print(f"  t={current_t:.2f}s, CumImp={cumulative_impulse:.2f}, PropMass={current_propellant_mass:.4f}, TotalMass={current_mass:.4f}kg")

            current_air_density = self.elevationProperties.calculate_air_density(
                y,
                self.configDict["ImpulseCalculator"]["surfacePressure"],
                self.configDict["ImpulseCalculator"]["surfaceTemperature"],
                self.configDict["ImpulseCalculator"]["launchSiteElevation"]
            )
            # print(f"  t={current_t:.2f}s, Alt={y:.2f}m, AirDensity={current_air_density:.4f}kg/m^3")


            current_weight_force = self.elevationProperties.calculate_gravity_at_elevation(
                y,
                self.configDict["ImpulseCalculator"]["launchSiteElevation"]
            ) * current_mass
            # print(f"  t={current_t:.2f}s, WeightForce={current_weight_force:.2f}N")


            current_thrust = np.interp(current_t, thrust_time_points, thrust_values, left=0.0, right=0.0)
            # print(f"  t={current_t:.2f}s, Interpolated Thrust={current_thrust:.2f}N")

            x_thrust = math.sin(self.configDict["ImpulseCalculator"]["railAngle"]) * current_thrust
            y_thrust = math.cos(self.configDict["ImpulseCalculator"]["railAngle"]) * current_thrust

            rel_velocity_x = vx - self.configDict["ImpulseCalculator"]["windVelocity"]
            rel_velocity_y = vy
            velocity_magnitude = math.sqrt(rel_velocity_x**2 + rel_velocity_y**2)

            phi = math.atan2(rel_velocity_x, rel_velocity_y) if velocity_magnitude > 1e-6 else 0.0

            drag_force = 0.5 * current_air_density * (velocity_magnitude)**2 * \
                         self.configDict["ImpulseCalculator"]["dragCoefficient"] * \
                         self.configDict["ImpulseCalculator"]["dragArea"]
            x_drag = drag_force * math.sin(phi)
            y_drag = drag_force * math.cos(phi)
            
            net_force_x = x_thrust - x_drag
            net_force_y = y_thrust - current_weight_force - y_drag

            ax = net_force_x / current_mass
            ay = net_force_y / current_mass
            # print(f"  t={current_t:.2f}s, NetFx={net_force_x:.2f}, NetFy={net_force_y:.2f}, ax={ax:.2f}, ay={ay:.2f}")


            return [vx, vy, ax, ay], x_thrust, y_thrust, x_drag, y_drag, ax, ay

        max_y_position = 0.0
        max_velocity = 0.0
        max_acceleration = 0.0
        total_thrust_sum = 0.0
        thrust_sample_count = 0
        cumulative_impulse = 0.0 

        takeOff = False
        apogeeReached = False
        # Main simulation loop
        iteration_count = 0
        max_iterations = 20000 # Safety break to prevent infinite loops
        while (not apogeeReached or not takeOff) and time < 1000 :
            iteration_count += 1
            if iteration_count % 1 == 0:
                print(f"Simulating... Time: {time:.2f}s, Altitude: {yPosition:.2f}m, Velocity: {yVelocity:.2f}m/s")
            
            if takeOff and yVelocity <=0:
                apogeeReached = True

            if yPosition > 0 and yVelocity > 0:
                if not takeOff:
                    yPosition = 0
                    xPosition = 0
                    xVelocity = 0
                    yVelocity = 0
                takeOff = True
                
                print("set takeoff to true")
            else:
                yVelocity = 0
                xVelocity = 0
                xPosition = 0
                yPosition = 0 

            
            if yPosition > max_y_position:
                max_y_position = yPosition

            current_state = [xPosition, yPosition, xVelocity, yVelocity]

            derivs_k1, x_thrust_k1, y_thrust_k1, x_drag_k1, y_drag_k1, ax_k1, ay_k1 = \
                get_derivatives(time, current_state)

            if saveData:
                flight_data_list.append([
                    time,
                    xPosition,
                    yPosition,
                    xVelocity,
                    yVelocity,
                    x_thrust_k1,
                    y_thrust_k1,
                    x_drag_k1,
                    y_drag_k1,
                    ax_k1,
                    ay_k1
                ])

            current_velocity_magnitude = math.sqrt(xVelocity**2 + yVelocity**2)
            if current_velocity_magnitude > max_velocity:
                max_velocity = current_velocity_magnitude

            current_acceleration_magnitude = math.sqrt(ax_k1**2 + ay_k1**2)
            if current_acceleration_magnitude > max_acceleration:
                max_acceleration = current_acceleration_magnitude

            if time <= burnTime and np.interp(time, thrust_time_points, thrust_values, left=0.0, right=0.0) > 0:
                total_thrust_sum += np.interp(time, thrust_time_points, thrust_values, left=0.0, right=0.0)
                thrust_sample_count += 1

            state_k2 = [s + 0.5 * d * deltaT for s, d in zip(current_state, derivs_k1)]
            derivs_k2, _, _, _, _, _, _ = get_derivatives(time + 0.5 * deltaT, state_k2)

            state_k3 = [s + 0.5 * d * deltaT for s, d in zip(current_state, derivs_k2)]
            derivs_k3, _, _, _, _, _, _ = get_derivatives(time + 0.5 * deltaT, state_k3)

            state_k4 = [s + d * deltaT for s, d in zip(current_state, derivs_k3)]
            derivs_k4, _, _, _, _, _, _ = get_derivatives(time + deltaT, state_k4)

            xPosition += (derivs_k1[0] + 2*derivs_k2[0] + 2*derivs_k3[0] + derivs_k4[0]) / 6.0 * deltaT
            yPosition += (derivs_k1[1] + 2*derivs_k2[1] + 2*derivs_k3[1] + derivs_k4[1]) / 6.0 * deltaT
            xVelocity += (derivs_k1[2] + 2*derivs_k2[2] + 2*derivs_k3[2] + derivs_k4[2]) / 6.0 * deltaT
            yVelocity += (derivs_k1[3] + 2*derivs_k2[3] + 2*derivs_k3[3] + derivs_k4[3]) / 6.0 * deltaT

            time += deltaT

            next_thrust = np.interp(time, thrust_time_points, thrust_values, left=0.0, right=0.0)
            cumulative_impulse += (np.interp(time - deltaT, thrust_time_points, thrust_values, left=0.0, right=0.0) + next_thrust) / 2.0 * deltaT 
            print(f"Iteration {iteration_count}: Time={time:.2f}s, Altitude={yPosition:.2f}m, Velocity={yVelocity:.2f}m/s, Acceleration={"penos"}m/s^2, Thrust={"penis"}N, Cumulative Impulse={cumulative_impulse:.2f}Ns")
            print("apogeeReached " + str(apogeeReached) + " takeoff " + str(takeOff))

        simFlightData = np.array(flight_data_list)

        avg_thrust_actual = total_thrust_sum / thrust_sample_count if thrust_sample_count > 0 else 0.0

        sim_stats_dict = {
            "avg_thrust": avg_thrust_actual,
            "burn_time": burnTime,
            "apogee": max_y_position,
            "max_velocity": max_velocity,
            "max_acceleration": max_acceleration
        }
        print(f"--- Simulation Finished ---")
        print(f"Final Sim Stats: {sim_stats_dict}")
        print(f"Total data points collected: {simFlightData.shape[0] if simFlightData.size > 0 else 0}")
        print(f"--- End of ThrustCurveSimulator.runsimulation ---\n")

        return sim_stats_dict, simFlightData