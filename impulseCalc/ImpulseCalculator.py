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
        currentDeltaT = parameters.deltaT # adjust deltaT to get accurate apogees faster
        while apogee <= (1 + parameters.apogeeThreshold) * parameters.desiredApogee: # this condition does nothing, idk what to change it to

            burnTime += parameters.burnTimeStep  # iterates through burnTimes with chosen precision
            #print("increasing burn time to: " + str(burnTime))

            try: # sets upper bound to the last/smallest thrust that has passed. always works since burn time up --> next thrust must be lower
                lowBound = min((set([row[0] for row in passingThrustBurntimeApogeeSet])))/3
            except ValueError:  # if the set is empty, set to minTtW value
                lowBound = SimulationTools.getWetMass(avgThrust, burnTime) * constants.standardGravity * parameters.minAvgTtW # default big value if no successful runs yet

            try: # sets upper bound to the last/smallest thrust that has passed. always works since burn time up --> next thrust must be lower
                highBound = min((set([row[0] for row in passingThrustBurntimeApogeeSet])))
            except ValueError:  # if the set is empty, set highBound to a default value
                highBound = SimulationTools.getWetMass(avgThrust, burnTime) * constants.standardGravity * 10**4 # default big value if no successful runs yet

            if avgThrust < SimulationTools.getWetMass(avgThrust, burnTime) * constants.standardGravity * parameters.minAvgTtW and not len(passingThrustBurntimeApogeeSet) == 0 :
                break
            # if abs((highBound - lowBound))/ lowBound < parameters.bisectionBoundPercDiff:  # if the bounds are too close together, break the loop
            #     print("Bounds too close together, breaking loop")
            #     break

            count = 0
            print("Starting new iteration with burn time = " + str(burnTime))
            while apogee <= (1 + parameters.apogeeThreshold) * parameters.desiredApogee or apogee >= (1 - parameters.apogeeThreshold) * parameters.desiredApogee:  # loop until the apogee is within 5% of the desired apogee
                avgThrust = (lowBound + highBound)/2  # set the average thrust to the midpoint of the bounds
                #print("running sim with deltaT " +str(currentDeltaT))
                apogee = simulation.runsimulation(currentDeltaT, burnTime, avgThrust) # runs the sim!!!!! with the currents values!!
                print(str(count) + ". apogee: " + str(apogee) + ", avgThrust: " + str(avgThrust))
                count += 1
                currentDeltaT = .6 * currentDeltaT #cuts deltaT down every single run and adjusts deltaT smoothly to avoid sudden changes in apo due to euler stepper quirks. important for accurate results

                if apogee >= (1 + parameters.apogeeThreshold) * parameters.desiredApogee:
                    highBound = avgThrust  # if the apogee is too high, set the high bound to the current average thrust
                    #print("apogee too high, setting high bound to: " + str(highBound))
                    if abs((highBound - lowBound))/ lowBound < parameters.bisectionBoundPercDiff:  # if the bounds are too close together, break the loop
                        print("Bounds too close together, breaking loop")
                        currentDeltaT = parameters.deltaT
                        #print("reset deltaT" + str(currentDeltaT))
                        break
                elif apogee <= (1 - parameters.apogeeThreshold) * parameters.desiredApogee: 
                    lowBound = avgThrust  # if the apogee is too low, set the low bound to the current average thrust
                    #print("apogee too low, setting low bound to: " + str(lowBound))
                    if abs((highBound - lowBound))/ lowBound < parameters.bisectionBoundPercDiff:  # if the bounds are too close together, break the loop
                        print("Bounds too close together, breaking loop")
                        currentDeltaT = parameters.deltaT
                        #print("reset deltaT" + str(currentDeltaT))
                        break
                else: 
                    passingThrustBurntimeApogeeSet.append((avgThrust, burnTime, apogee))  # store successful runs
                    #print("delta T for successful sim " + str(currentDeltaT))
                    print("logged successful run with avgThrust: " + str(avgThrust) + " burnTime: " + str(burnTime) + " apogee: " + str(apogee))
                    currentDeltaT = parameters.deltaT
                    #print("reset deltaT " + str(currentDeltaT))
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

        return min(passingImpulses), passingImpulses[round(.25*len(passingImpulses))-1], passingImpulses[round(.5*len(passingImpulses))-1], passingImpulses[round(.75*len(passingImpulses))-1], max(passingImpulses), len(passingImpulses), np.mean(passingImpulses), passingThrustBurntimeApogeeSet  
    #return the minimum, 25th, 50th, 75th, and maximum impulse values calculated from the successful runs, the total number of impulses calculated, the mean impulse value, and the passing thrust, burn time, and apogee sets
                
    def __init__(self, simulation_obj): # Add this constructor
        self.simulation = simulation_obj


if __name__ == "__main__":
    elevationProps = elevationDepProperties(constants)  #create the elevationProps object
    simulation = SimulationTools(constants, parameters, elevationProps)  #create the simulation object
    calculator = ImpulseCalculator(simulation) # Pass the simulation object here
    possibleImpulseInfo = calculator.calculate_Impulse_needed() # run the impulse calc
    #print(simulation.runsimulation(0.002, 4.0, 2500.0))
    #actually runs the impulse calculator and returns the possible impulse information

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
        if count % (round(len(possibleImpulseInfo)/6)) == 0:   #prints a sample of all passing triplets, i dont remember why its not just count % 3
            print(f"Thrust: {thrust:.2f} N, Burn time: {burn_time:.2f} s, Apogee: {apogee:.2f} m")

    
