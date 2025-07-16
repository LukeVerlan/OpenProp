import numpy as np
import constants as constants
import parameters as parameters
import statistics 
import math
from elevationProperties import elevationDepProperties  # Import the elevation properties module
from Simulation import SimulationTools  # Import the Simulation class from the Simulation module
from graphingTools import FlightDataPlotter, display_flight_plot_on_demand 
import matplotlib.pyplot as plt



class ImpulseCalculator:

    def __init__(self, simulation_obj): # Add this constructor
        self.simulation = simulation_obj


    def calculate_Impulse_needed(self):
        """
        takes in the parameters of the rocket and the desired apogee, iterates through a bunch of burn times and average thrust values by running a simulation for each and finding whether they reached the desired apogee. returns the thrust, burn time, and apogee for each successful run.
        Also returns the minimum, 25th, 50th, 75th, and maximum impulse values calculated from the successful runs.
        """
        # Changed to combinedSuccessfulData to store ((summary_tuple), sim_data_array)
        combinedSuccessfulData = []
        
        avgThrust = 0.0
        burnTime = 0.0
        
        apogee = 0.0
        currentDeltaT = parameters.deltaT # adjust deltaT to get accurate apogees faster
        
        # RESTORED ORIGINAL OUTER WHILE LOOP CONDITION
        while apogee <= (1 + parameters.apogeeThreshold) * parameters.desiredApogee:

            burnTime += parameters.burnTimeStep  # iterates through burnTimes with chosen precision
            #print("increasing burn time to: " + str(burnTime))

            # RESTORED ORIGINAL lowBound / highBound INITIALIZATION LOGIC
            try: # sets upper bound to the last/smallest thrust that has passed. always works since burn time up --> next thrust must be lower
                lowBound = min((set([row[0][0] for row in combinedSuccessfulData])))/3 # Access avgThrust from the summary tuple
            except ValueError:  # if the set is empty, set to minTtW value
                lowBound = SimulationTools.getWetMass(avgThrust, burnTime) * constants.standardGravity * parameters.minAvgTtW # default big value if no successful runs yet

            try: # sets upper bound to the last/smallest thrust that has passed. always works since burn time up --> next thrust must be lower
                highBound = min((set([row[0][0] for row in combinedSuccessfulData]))) # Access avgThrust from the summary tuple
            except ValueError:  # if the set is empty, set highBound to a default value
                highBound = SimulationTools.getWetMass(avgThrust, burnTime) * constants.standardGravity * 10**4 # default big value if no successful runs yet

            # RESTORED ORIGINAL BREAK CONDITION FOR OUTER LOOP
            if avgThrust < SimulationTools.getWetMass(avgThrust, burnTime) * constants.standardGravity * parameters.minAvgTtW and not len(combinedSuccessfulData) == 0 :
                break
            
            # if abs((highBound - lowBound))/ lowBound < parameters.bisectionBoundPercDiff:  # if the bounds are too close together, break the loop
            #    print("Bounds too close together, breaking loop")
            #    break

            count = 0
            print("Starting new iteration with burn time = " + str(burnTime))
            
            # RESTORED ORIGINAL INNER WHILE LOOP CONDITION
            while apogee <= (1 + parameters.apogeeThreshold) * parameters.desiredApogee or apogee >= (1 - parameters.apogeeThreshold) * parameters.desiredApogee:  # loop until the apogee is within 5% of the desired apogee
                avgThrust = (lowBound + highBound)/2  # set the average thrust to the midpoint of the bounds
                #print("running sim with deltaT " +str(currentDeltaT))
                apogee, placeHolder = self.simulation.runsimulation(currentDeltaT, burnTime, avgThrust, bool(False)) # runs the sim!!!!! with the currents values!!
                print(str(count) + ". apogee: " + str(apogee) + ", avgThrust: " + str(avgThrust))
                count += 1
                currentDeltaT = .9 * currentDeltaT #cuts deltaT down every single run and adjusts deltaT smoothly to avoid sudden changes in apo due to euler stepper quirks. important for accurate results

                if apogee >= (1 + parameters.apogeeThreshold) * parameters.desiredApogee:
                    highBound = avgThrust  # if the apogee is too high, set the high bound to the current average thrust
                    #print("apogee too high, setting high bound to: " + str(highBound))
                    # RESTORED ORIGINAL BREAK CONDITION AND DELTAT RESET
                    if abs((highBound - lowBound))/ lowBound < parameters.bisectionBoundPercDiff:  # if the bounds are too close together, break the loop
                        print("Bounds too close together, breaking loop")
                        currentDeltaT = parameters.deltaT
                        #print("reset deltaT" + str(currentDeltaT))
                        break
                elif apogee <= (1 - parameters.apogeeThreshold) * parameters.desiredApogee: 
                    lowBound = avgThrust  # if the apogee is too low, set the low bound to the current average thrust
                    #print("apogee too low, setting low bound to: " + str(lowBound))
                    # RESTORED ORIGINAL BREAK CONDITION AND DELTAT RESET
                    if abs((highBound - lowBound))/ lowBound < parameters.bisectionBoundPercDiff:  # if the bounds are too close together, break the loop
                        print("Bounds too close together, breaking loop")
                        currentDeltaT = parameters.deltaT
                        #print("reset deltaT" + str(currentDeltaT))
                        break
                else: # This means apogee is within the desired threshold, so it's a successful run
                    apogee2, simData = self.simulation.runsimulation(currentDeltaT, burnTime, avgThrust, bool(True))
                    # Store successful runs: ((avgThrust, burnTime, apogee), simData_array)
                    combinedSuccessfulData.append(((avgThrust, burnTime, apogee2), simData))
                    
                    #print("delta T for successful sim " + str(currentDeltaT))
                    print("logged successful run with avgThrust: " + str(avgThrust) + " burnTime: " + str(burnTime) + " apogee: " + str(apogee))
                    currentDeltaT = parameters.deltaT
                    #print("reset deltaT " + str(currentDeltaT))
                    break # Break the inner loop since a successful thrust was found for this burnTime

        # Sort the combined data by avgThrust (the first element of the summary tuple's first element)
        combinedSuccessfulData.sort(key=lambda x: x[0][0]) 
        
        # Unpack the combined data into two separate lists for return
        passingThrustBurntimeApogeeSet = [item[0] for item in combinedSuccessfulData]
        listOfSuccessfulSimData = [item[1] for item in combinedSuccessfulData]

        return passingThrustBurntimeApogeeSet, listOfSuccessfulSimData
                
def process_data(passingThrustBurntimeApogeeSet, listOfSuccessfulSimData):
    """
    Filters successful simulation data based on burn time and calculates impulse statistics.

    Args:
        passingThrustBurntimeApogeeSet (list): List of (thrust, burn_time, apogee) tuples.
        listOfSuccessfulSimData (list): List of numpy arrays, each being a simData array.

    Returns:
        tuple: (min_impulse, q1_impulse, median_impulse, q3_impulse, max_impulse,
                num_impulses, mean_impulse, filtered_passingThrustBurntimeApogeeSet,
                filtered_listOfSuccessfulSimData)
    """
    if not passingThrustBurntimeApogeeSet:
        print("No successful data to process.")
        return 0, 0, 0, 0, 0, 0, 0, [], []

    # Create a list of (summary_tuple, sim_data_array) pairs for joint filtering
    # This assumes passingThrustBurntimeApogeeSet and listOfSuccessfulSimData are already aligned and sorted
    combined_data_for_filtering = list(zip(passingThrustBurntimeApogeeSet, listOfSuccessfulSimData))

    second_column_values = [row[0][1] for row in combined_data_for_filtering] # Extract burn time from the summary tuple
    
    # Handle case where all burn times are the same or list is too small for statistics
    if len(set(second_column_values)) < 2: # If all burn times are identical or only one unique value
        initial_mean_col1 = second_column_values[0] if second_column_values else 0
    else:
        initial_mean_col1 = statistics.mean(set(second_column_values))

    lower_bound_col1 = (1 - parameters.burnTimeRange) * initial_mean_col1
    upper_bound_col1 = (1 + parameters.burnTimeRange) * initial_mean_col1
    
    filtered_combined_data = []

    for summary_tuple, sim_data_array in combined_data_for_filtering:
        current_burn_time = summary_tuple[1] # burn time is the second element in the summary tuple
        if lower_bound_col1 <= current_burn_time <= upper_bound_col1:
            filtered_combined_data.append((summary_tuple, sim_data_array))

    # Unpack the filtered combined data back into two separate lists
    filtered_passingThrustBurntimeApogeeSet = [item[0] for item in filtered_combined_data]
    filtered_listOfSuccessfulSimData = [item[1] for item in filtered_combined_data]

    passingImpulses = []
    for thrust, burn_time, apogee in filtered_passingThrustBurntimeApogeeSet:
        impulse = thrust * burn_time
        passingImpulses.append(impulse)
    
    # Ensure there are enough data points for quartiles
    if not passingImpulses:
        return 0, 0, 0, 0, 0, 0, 0, filtered_passingThrustBurntimeApogeeSet, filtered_listOfSuccessfulSimData

    # Sort impulses for quartile calculation
    passingImpulses.sort()

    min_impulse = passingImpulses[0]
    q1_impulse = passingImpulses[max(0, round(.25 * len(passingImpulses)) - 1)]
    median_impulse = passingImpulses[max(0, round(.5 * len(passingImpulses)) - 1)]
    q3_impulse = passingImpulses[max(0, round(.75 * len(passingImpulses)) - 1)]
    max_impulse = passingImpulses[-1]
    mean_impulse = np.mean(passingImpulses)
    
    return min_impulse, q1_impulse, median_impulse, q3_impulse, max_impulse, \
           len(passingImpulses), mean_impulse, filtered_passingThrustBurntimeApogeeSet, \
           filtered_listOfSuccessfulSimData
               
def print_flight_data(flight_data_array, print_interval=2.0):
    """
    Prints a summary of simulation flight data at specified time intervals.

    Args:
        flight_data_array (np.ndarray): A NumPy array containing flight data.
                                        Expected column order:
                                        [time, xPosition, yPosition, xVelocity, yVelocity,
                                         x_thrust, y_thrust, x_drag, y_drag, ax, ay]
        print_interval (float): The time interval (in seconds) at which to print data.
    """
    if flight_data_array.size == 0:
        print("No flight data to display.")
        return

    next_print_time = 0.0

    TIME_COL = 0; X_POS_COL = 1; Y_POS_COL = 2; X_VEL_COL = 3; Y_VEL_COL = 4; X_THRUST_COL = 5; Y_THRUST_COL = 6; X_DRAG_COL = 7 
    Y_DRAG_COL = 8; X_ACCEL_COL = 9; Y_ACCEL_COL = 10  


    print(f"\n--- Flight Data (printed every {print_interval:.1f} seconds) ---")
    print("-------------------------------------------------------------------")

    for row_index in range(flight_data_array.shape[0]):
        current_time = flight_data_array[row_index, TIME_COL]

        if current_time >= next_print_time - 1e-9:
            if row_index == 0 or current_time >= next_print_time:
                xPosition = flight_data_array[row_index, X_POS_COL]
                yPosition = flight_data_array[row_index, Y_POS_COL]
                xVelocity = flight_data_array[row_index, X_VEL_COL]
                yVelocity = flight_data_array[row_index, Y_VEL_COL] 
                x_thrust = flight_data_array[row_index, X_THRUST_COL]
                y_thrust = flight_data_array[row_index, Y_THRUST_COL]
                x_drag = flight_data_array[row_index, X_DRAG_COL]
                y_drag = flight_data_array[row_index, Y_DRAG_COL]
                ax = flight_data_array[row_index, X_ACCEL_COL]
                ay = flight_data_array[row_index, Y_ACCEL_COL]

                print(f"--- Time: {current_time:.2f} s ---")
                print(f"  Position: x={xPosition:.2f} m, y={yPosition:.2f} m")
                print(f"  Velocity: vx={xVelocity:.2f} m/s, vy={yVelocity:.2f} m/s")
                print(f"  Thrust Components: Fx={x_thrust:.2f} N, Fy={y_thrust:.2f} N")
                print(f"  Drag: Dx={x_drag:.2f} N, Dy={y_drag:.2f} N")
                print(f"  Acceleration: ax={ax:.2f} m/s^2, ay={ay:.2f} m/s^2")
                print("-" * 20)

                next_print_time = math.ceil((current_time + 1e-9) / print_interval) * print_interval

if __name__ == "__main__":
    elevationProps = elevationDepProperties(constants)
    simulation = SimulationTools(constants, parameters, elevationProps)
    calculator = ImpulseCalculator(simulation)

    initial_summary_data, initial_sim_data = calculator.calculate_Impulse_needed()

    # Pass both lists to process_data for joint filtering and sorting.
    # process_data returns the filtered versions of both lists.
    min_imp, q1_imp, med_imp, q3_imp, max_imp, num_imp, mean_imp, \
    filtered_passingThrustBurntimeApogeeSet, filtered_listOfSuccessfulSimData = \
        process_data(initial_summary_data, initial_sim_data)


    #prints all of the information input by the user
    print("Impulse Calculator Inputs:")
    print(f"Desired apogee: {parameters.desiredApogee:.2f} m")
    print(f"Rail angle: {parameters.railAngle:.2f} radians")
    print(f"Launch site elevation: {parameters.launchSiteElevation:.2f} m")
    print(f"Drag area: {parameters.dragArea:.4f} m^2")
    print(f"Drag coefficient: {parameters.dragCoefficient:.2f}")
    print(f"Wind velocity: {parameters.windVelocity:.2f} m/s")
    print(f"Dry mass: {parameters.noMotorMass:.2f} kg")
    print(f"Surface pressure: {parameters.surfacePressure:.2f} Pa")
    print(f"Surface temperature: {parameters.surfaceTemperature:.2f} K")
    print(f"Delta T: {parameters.deltaT:.2f} s")
    

    #prints all of the interesting information from the impulse calculator
    print("\nImpulse Calculator Results (Filtered by Burn Time):")
    print(f"Minimum impulse needed: {min_imp:.2f} N*s")
    print(f"25th percentile impulse: {q1_imp:.2f} N*s")
    print(f"50th percentile impulse: {med_imp:.2f} N*s")
    print(f"75th percentile impulse: {q3_imp:.2f} N*s")
    print(f"Maximum impulse needed: {max_imp:.2f} N*s")
    print(f"Total number of impulses calculated (after filtering): {num_imp}")
    print(f"Mean impulse needed: {mean_imp:.2f} N*s")
        
    # Prints a somewhat representative set of thrust, burn time, and apogee values from the filtered data
    print("\nFiltered Thrust, Burn Time, Apogee Sets:")
    for thrust, burn_time, apogee in filtered_passingThrustBurntimeApogeeSet:
        print(f"Thrust: {thrust:.2f} N, Burn time: {burn_time:.2f} s, Apogee: {apogee:.2f} m")

    # --- THIS IS THE UPDATED BLOCK YOU PROVIDED, INTEGRATING ON-DEMAND PLOTTING ---
    print("\n=======================================================")
    print("Detailed Data for Each Filtered Successful Flight")
    print("=======================================================\n")

    print_every_nth_flight = 5 # YOU CAN CHANGE THIS VALUE (renamed from print_detailed_every_nth_flight for consistency with your variable name)
    
    # This list will store data needed to CONSTRUCT plots on demand, not the plots themselves
    collectible_plot_data = [] 

    # Instantiate plotter once outside the loop for efficiency
    plotter = FlightDataPlotter()

    for i, (summary_tuple, flight_data_array) in enumerate(zip(filtered_passingThrustBurntimeApogeeSet, filtered_listOfSuccessfulSimData)):
        if (i + 1) % print_every_nth_flight == 0: # Check if it's the Nth flight
            # Unpack the summary tuple for this specific flight
            thrust, burn_time, apogee = summary_tuple 
            
            print(f"\n--- Detailed Flight Data for Flight #{i+1} (Flight {i+1} of {len(filtered_listOfSuccessfulSimData)}) ---")
            print(f"Thrust: {thrust:.2f} N, Burn time: {burn_time:.2f} s, Apogee: {apogee:.2f} m") 
            print_flight_data(flight_data_array, print_interval=2.0) # Using your print_interval=2.0 from the example
            print(f"--- End Detailed Flight Data for Flight #{i+1} ---\n")

            # Prepare data for ON-DEMAND plot
            plot_title = f"Flight #{i+1} (T={thrust:.2f}N, Bt={burn_time:.2f}s, Apogee={apogee:.2f}m)"
            
            # Instead of appending the fig object, append the data and title needed to create it
            collectible_plot_data.append((flight_data_array, plot_title)) 

    # These print statements should be outside the loop to avoid repetition
    print(f"\nCollected {len(collectible_plot_data)} plot data references (for on-demand plotting).")
    print("To display a specific plot, call display_flight_plot_on_demand(plotter, collectible_plot_data, index).")
    print("For example: display_flight_plot_on_demand(plotter, collectible_plot_data, 0) to show the first plot.")

    # This part should be after the main loop and the preceding print statements
    if collectible_plot_data:
        # Call the on-demand display function here
        display_flight_plot_on_demand(plotter, collectible_plot_data, 0, plot_types='position_time')
        display_flight_plot_on_demand(plotter, collectible_plot_data, 0, plot_types='velocity_time')
        display_flight_plot_on_demand(plotter, collectible_plot_data, 0, plot_types='acceleration_components_time') 
        '''
        plot types:
        "position_time", "trajectory", "velocity_time", "total_speed_time", "thrust_components_time", "drag_components_time", "acceleration_components_time", "total_acceleration_magnitude_time"
        '''
    else:
        print("\nNo plot data references were collected to display.")
