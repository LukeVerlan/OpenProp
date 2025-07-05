import numpy as np
import constants as constants
import parameters as parameters
import statistics 
from elevationProperties import elevationDepProperties  # Import the elevation properties module
from Simulation import SimulationTools  # Import the Simulation class from the Simulation module

class ImpulseCalculator:

    def calculate_Impulse_needed(self):
        """
        takes in the parameters of the rocket and the desired apogee, iterates through a bunch of burn times and average thrust values by running a simulation for each and finding whether they reached the desired apogee. returns the thrust, burn time, and apogee for each successful run.
        Also returns the minimum, 25th, 50th, 75th, and maximum impulse values calculated from the successful runs.
        """
        passingThrustBurntimeApogeeSet = [] #initialize the list of passing thrust, burn time, and apogee sets
        avgThrust = 0.0
        burnTime = 0.0
        ##### needs to dynamcally set propellant mass and dry mass according to avg thrust and burn time 

        apogee = 0.0
        while apogee <= (1 + parameters.apogeeThreshold) * parameters.desiredApogee:

            burnTime += parameters.burnTimeStep  # want to set this to an input variable later
            print("increasing burn time to: " + str(burnTime))

            lowBound = parameters.dryMass * constants.standardGravity * parameters.minAvgTtW
            try: 
                highBound = statistics.median(set([row[0] for row in passingThrustBurntimeApogeeSet])) 
            except statistics.StatisticsError:  # if the set is empty, set highBound to a default value
                highBound = parameters.dryMass * constants.standardGravity * 10**5 # default value if no successful runs yet


            if abs((highBound - lowBound))/ lowBound < 0.01:  # if the bounds are too close together, break the loop
                print("Bounds too close together, breaking loop")
                break


            while apogee <= (1 + parameters.apogeeThreshold) * parameters.desiredApogee or apogee >= (1 - parameters.apogeeThreshold) * parameters.desiredApogee:  # loop until the apogee is within 5% of the desired apogee
                avgThrust = (lowBound + highBound)/2  # set the average thrust to the midpoint of the bounds
                apogee = simulation.runsimulation(parameters.deltaT, burnTime, avgThrust)

                if apogee >= (1 + parameters.apogeeThreshold) * parameters.desiredApogee:
                    highBound = avgThrust  # if the apogee is too high, set the high bound to the current average thrust
                    print("apogee too high, setting high bound to: " + str(highBound))
                    if abs((highBound - lowBound))/ lowBound < 0.01:  # if the bounds are too close together, break the loop
                        print("Bounds too close together, breaking loop")
                        break
                elif apogee <= (1 - parameters.apogeeThreshold) * parameters.desiredApogee: 
                    lowBound = avgThrust  # if the apogee is too low, set the low bound to the current average thrust
                    print("apogee too low, setting low bound to: " + str(lowBound))
                    if abs((highBound - lowBound))/ lowBound < 0.01:  # if the bounds are too close together, break the loop
                        print("Bounds too close together, breaking loop")
                        break
                else: 
                    passingThrustBurntimeApogeeSet.append((avgThrust, burnTime, apogee))  # store successful runs
                    print("logged successful run with avgThrust: " + str(avgThrust) + " burnTime: " + str(burnTime) + " apogee: " + str(apogee))
                    break

        passingThrustBurntimeApogeeSet.sort()  # Sort by thrust for data organization

        second_column_values = [row[1] for row in passingThrustBurntimeApogeeSet] # Extract the second column (burn time) values for filtering
        initial_mean_col1 = statistics.mean(set(second_column_values)) #reference again the mean of all unuqie burn time values to cut out unusually high or low burnt times. BREAKS DOWN WITH SMALL STEPS IN BURN TIME???
        lower_bound_col1 = (1 - parameters.burnTimeRange) * initial_mean_col1 #set bounds
        upper_bound_col1 = (1 + parameters.burnTimeRange)* initial_mean_col1
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
                
    def __init__(self, simulation_obj): # Add this constructor
        self.simulation = simulation_obj


if __name__ == "__main__":
    elevationProps = elevationDepProperties(constants) 
    simulation = SimulationTools(constants, parameters, elevationProps)
    calculator = ImpulseCalculator(simulation) # Pass the simulation object here
    possibleImpulseInfo = calculator.calculate_Impulse_needed()
    #actually runs the impulse calculator and returns the possible impulse information

    #prints all of the information input by the user
    print("Impulse Calculator Inputs:")
    print(f"Desired apogee: {parameters.desiredApogee:.2f} m")
    print(f"Rail angle: {parameters.railAngle:.2f} radians")
    print(f"Launch site elevation: {parameters.launchSiteElevation:.2f} m")
    print(f"Drag area: {parameters.dragArea:.4f} m^2")
    print(f"Drag coefficient: {parameters.dragCoefficient:.2f}")
    print(f"Wind velocity: {parameters.windVelocity:.2f} m/s")
    print(f"Dry mass: {parameters.dryMass:.2f} kg") # remember this is funky wunky and will need to not be a constant 
    print(f"Surface pressure: {parameters.surfacePressure:.2f} Pa")
    print(f"Surface temperature: {parameters.surfaceTemperature:.2f} K")
    print(f"Delta T: {parameters.deltaT:.2f} s")
    

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
        if count % 1 == 0:
            print(f"Thrust: {thrust:.2f} N, Burn time: {burn_time:.2f} s, Apogee: {apogee:.2f} m")

    
