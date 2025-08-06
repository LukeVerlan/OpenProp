
import numpy as np
import math
import os

# --- Import actual ElevationProperties and consts ---
from impulseCalc.elevationProperties import elevationDepProperties



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
            
            current_air_density = self.elevationProperties.calculate_air_density(
                y,
                self.configDict["ImpulseCalculator"]["surfacePressure"],
                self.configDict["ImpulseCalculator"]["surfaceTemperature"],
                self.configDict["ImpulseCalculator"]["launchSiteElevation"]
            )

            current_weight_force = self.elevationProperties.calculate_gravity_at_elevation(
                y,
                self.configDict["ImpulseCalculator"]["launchSiteElevation"]
            ) * current_mass

            current_thrust = np.interp(current_t, thrust_time_points, thrust_values, left=0.0, right=0.0)

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
            
            # --- FOCUSED DEBUGGING PRINTS (only for t=0.0 or near burnout) ---
            # Print for a window of 0.5 seconds before and after burnout
            # if current_t == 0.0 or (current_t > burnTime - 0.5 and current_t < burnTime + 0.5): 
            #     print(f"\n--- Forces & Accel (t={current_t:.4f}s) ---")
            #     print(f"  Current Mass: {current_mass:.4f} kg")
            #     print(f"  Weight Force: {current_weight_force:.2f} N")
            #     print(f"  Interpolated Thrust (Total): {current_thrust:.2f} N")
            #     print(f"  Y-Thrust Component: {y_thrust:.2f} N (railAngle={self.configDict['ImpulseCalculator']['railAngle']:.3f} rad)")
            #     print(f"  Y-Drag Component: {y_drag:.2f} N (Vmag={velocity_magnitude:.2f}, AirDen={current_air_density:.4f})")
            #     print(f"  Net Force Y: {net_force_y:.2f} N")
            #     print(f"  Acceleration Y (ay): {ay:.2f} m/s^2")
            #     print(f"  Net Force X: {net_force_x:.2f} N")
            #     print(f"  Acceleration X (ax): {ax:.2f} m/s^2")
            #     print(f"  Total Acceleration Magnitude: {math.sqrt(ax**2 + ay**2):.2f} m/s^2") # Direct calculation here
            #     print(f"--------------------------------------------------\n")


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
        max_iterations = 200000 # Increased max_iterations for longer simulations
        
        # Loop condition: Continue as long as rocket is above ground (or slightly below for plotting)
        # OR if it's still moving upwards. Also, respect time and iteration limits.
        while (not apogeeReached or not takeOff) and time < 1000 :
            iteration_count += 1
            #if iteration_count % 1 == 0:
                #print(f"Simulating... Time: {time:.2f}s, Altitude: {yPosition:.2f}m, Velocity: {yVelocity:.2f}m/s")    

            if yPosition > max_y_position:
                max_y_position = yPosition

            current_state = [xPosition, yPosition, xVelocity, yVelocity]

            
            derivs_k1, x_thrust_k1, y_thrust_k1, x_drag_k1, y_drag_k1, ax_k1, ay_k1 = \
                get_derivatives(time, current_state)

            if takeOff and yVelocity <=0:
                apogeeReached = True
                #print("apogee reached")

            if yPosition > 0 and yVelocity > 0:
                if not takeOff:
                    yPosition = 0
                    xPosition = 0
                    xVelocity = 0
                    yVelocity = 0
                    ax_k1 = 0
                    ay_k1 = 0
                takeOff = True
                #print("takeoff set to true")

            if yPosition < 0:
                yPosition = 0
                xPosition = 0
                xVelocity = 0
                yVelocity = 0
                ax_k1 = 0
                ay_k1 = 0
            
            if iteration_count == 1:
                ax_k1 = 0
                ay_k1 = 0

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
                print("saved data")

            current_velocity_magnitude = math.sqrt(xVelocity**2 + yVelocity**2)
            if current_velocity_magnitude > max_velocity:
                max_velocity = current_velocity_magnitude

            # Calculate and store current acceleration magnitude for this point
            current_total_acceleration_magnitude = math.sqrt(ax_k1**2 + ay_k1**2)
            if current_total_acceleration_magnitude > max_acceleration:
                max_acceleration = current_total_acceleration_magnitude

            # Note: The 'current_thrust' variable used below is from the get_derivatives call for k1.
            # This is fine for printing purposes as it reflects the thrust at the start of the interval.
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
            
            # Corrected print statement: Use total_thrust_magnitude_k1 for 'Thrust'
            # current_thrust (from get_derivatives) is not directly available here, but x_thrust_k1 and y_thrust_k1 are.
            # We already calculated current_total_acceleration_magnitude.
            # Let's calculate total_thrust_magnitude_k1 for the print.
            total_thrust_magnitude_k1 = math.sqrt(x_thrust_k1**2 + y_thrust_k1**2)
            if iteration_count % 1 == 0:
                print(f"Iteration {iteration_count}: Time={time:.2f}s, Alt={yPosition:.2f}m, V_y={yVelocity:.2f}m/s, Ay={ay_k1:.2f}m/s^2, Thrust={total_thrust_magnitude_k1:.2f}N, Total Accel Mag={current_total_acceleration_magnitude:.2f}m/s^2, CumImp={cumulative_impulse:.2f}Ns")
                print(f"  Flags: apogeeReached={apogeeReached}, takeOff={takeOff}")


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

        return sim_stats_dict, simFlightData