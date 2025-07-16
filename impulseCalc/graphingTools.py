import matplotlib.pyplot as plt
import numpy as np
import math

# Standalone helper function to construct and display a plot on demand
def display_flight_plot_on_demand(plotter_instance, plot_data_ref_list, index, plot_types=None):
    """
    Constructs and displays a specific plot from stored data references.

    Args:
        plotter_instance (FlightDataPlotter): An instance of the FlightDataPlotter class.
        plot_data_ref_list (list): A list of tuples, where each tuple is
                                   (flight_data_array, plot_title).
        index (int): The 0-based index of the plot to display from the list.
        plot_types (list or str, optional): Specifies which plot(s) to generate (e.g., "trajectory").
                                       If None, all 8 plots are generated.
                                       See FlightDataPlotter.plot_flight_data for valid options.
    """
    if not isinstance(plot_data_ref_list, list):
        print("Error: plot_data_ref_list must be a list of (data, title) tuples.")
        return
    if not (0 <= index < len(plot_data_ref_list)):
        print(f"Error: Index {index} is out of bounds. List has {len(plot_data_ref_list)} plots (0 to {len(plot_data_ref_list)-1}).")
        return

    flight_data_array, plot_title_base = plot_data_ref_list[index]
    
    # Modify display title based on specific plot types selected
    if isinstance(plot_types, str):
        display_title = f"{plot_title_base} - {plot_types.replace('_', ' ').title()}"
    elif isinstance(plot_types, list) and plot_types:
        # For multiple selected plots, list the types in the title
        selected_titles = [pt.replace('_', ' ').title() for pt in plot_types]
        display_title = f"{plot_title_base} - Custom View: {', '.join(selected_titles)}"
    else: # All plots
        display_title = plot_title_base

    print(f"\nAttempting to display plot for: {display_title} (Index {index})...")
    
    # Call the plotter instance's method to construct the plot (it returns the figure)
    fig = plotter_instance.plot_flight_data(flight_data_array, title=display_title, plot_types=plot_types)
    
    if fig:
        plt.show(block=True) # Display the newly constructed plot
        plt.close(fig) # Close the figure immediately after it's been shown and closed by user
    else:
        print(f"Failed to construct plot for index {index}.")


class FlightDataPlotter:
    """
    A class to construct matplotlib Figure objects for flight data.
    Each call to plot_flight_data creates a new figure tailored to the requested plots.
    """
    def __init__(self):
        # Define column indices as class attributes for easy access by helper methods
        self.TIME_COL = 0
        self.X_POS_COL = 1
        self.Y_POS_COL = 2
        self.X_VEL_COL = 3
        self.Y_VEL_COL = 4
        self.X_THRUST_COL = 5
        self.Y_THRUST_COL = 6
        self.X_DRAG_COL = 7
        self.Y_DRAG_COL = 8
        self.X_ACCEL_COL = 9
        self.Y_ACCEL_COL = 10
        
    def _plot_position_time(self, ax, time, x_pos, y_pos):
        ax.plot(time, x_pos, label='X Position (m)', color='blue')
        ax.plot(time, y_pos, label='Y Position (Altitude) (m)', color='red')
        ax.set_title('Position vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Position (m)')
        ax.legend()
        ax.grid(True)

    def _plot_trajectory(self, ax, x_pos, y_pos):
        ax.plot(x_pos, y_pos, label='Trajectory', color='green')
        ax.set_title('Trajectory (Altitude vs. Horizontal Distance)')
        ax.set_xlabel('Horizontal Distance (m)')
        ax.set_ylabel('Altitude (m)')
        ax.grid(True)
        ax.autoscale(enable=True, axis='both', tight=True) 
        
    def _plot_velocity_components_time(self, ax, time, x_vel, y_vel):
        ax.plot(time, x_vel, label='X Velocity (m/s)', color='blue')
        ax.plot(time, y_vel, label='Y Velocity (m/s)', color='red')
        ax.set_title('Velocity Components vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Velocity (m/s)')
        ax.legend()
        ax.grid(True)

    def _plot_total_speed_time(self, ax, time, total_velocity_magnitude):
        ax.plot(time, total_velocity_magnitude, label='Total Speed (m/s)', color='purple')
        ax.set_title('Total Speed vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Speed (m/s)')
        ax.legend()
        ax.grid(True)

    def _plot_thrust_components_time(self, ax, time, x_thrust, y_thrust):
        ax.plot(time, x_thrust, label='X Thrust (N)', color='blue')
        ax.plot(time, y_thrust, label='Y Thrust (N)', color='red')
        ax.set_title('Thrust Components vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Force (N)')
        ax.legend()
        ax.grid(True)
        
    def _plot_drag_components_time(self, ax, time, x_drag, y_drag):
        ax.plot(time, x_drag, label='X Drag (N)', color='blue')
        ax.plot(time, y_drag, label='Y Drag (N)', color='red')
        ax.set_title('Drag Components vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Force (N)')
        ax.legend()
        ax.grid(True)

    def _plot_acceleration_components_time(self, ax, time, ax_data, ay_data):
        ax.plot(time, ax_data, label='X Acceleration (m/s^2)', color='blue')
        ax.plot(time, ay_data, label='Y Acceleration (m/s^2)', color='red')
        ax.set_title('Acceleration Components vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Acceleration (m/s^2)')
        ax.legend()
        ax.grid(True)

    def _plot_total_acceleration_magnitude_time(self, ax, time, total_acceleration_magnitude):
        ax.plot(time, total_acceleration_magnitude, label='Total Acceleration Magnitude (m/s^2)', color='brown')
        ax.set_title('Total Acceleration Magnitude vs. Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Acceleration (m/s^2)')
        ax.legend()
        ax.grid(True)


    def plot_flight_data(self, flight_data_array, title="Flight Simulation Data", plot_types=None): # plot_types is list or str or None
        """
        Constructs and returns a new matplotlib Figure object containing the plot(s).
        If plot_types is a list of strings, only those specified plots are created.
        If plot_types is a single string, that single plot is created.
        If plot_types is None or an empty/invalid list, all 8 subplots are created.
        Does NOT show or close the plot.

        Args:
            flight_data_array (np.ndarray): A 2D NumPy array containing flight data.
                                            Expected 11 columns in this order:
                                            [time, xPosition, yPosition, xVelocity, yVelocity,
                                             x_thrust, y_thrust, x_drag, y_drag, ax, ay]
            title (str, optional): The main title for the plot. Defaults to "Flight Simulation Data".
            plot_types (list or str, optional): Specifies which plot(s) to generate. 
                                                If a list of strings: generate specified plots.
                                                If a single string: generate that one plot.
                                                If None or invalid: generate all 8 plots.
                                                Valid options are accessible via self.available_plot_types.
        
        Returns:
            matplotlib.figure.Figure: The Figure object containing the plot(s), or None if no data.
        """
        # Basic input validation
        if not isinstance(flight_data_array, np.ndarray) or flight_data_array.ndim != 2:
            print("Error: flight_data_array must be a 2D NumPy array.")
            return None
        if flight_data_array.shape[1] != 11:
            print(f"Error: flight_data_array must have 11 columns. Found {flight_data_array.shape[1]}.")
            return None
        if flight_data_array.shape[0] == 0:
            print("No data to plot in the provided array.")
            return None

        # Extract data columns (using self.COL constants)
        time = flight_data_array[:, self.TIME_COL]
        x_pos = flight_data_array[:, self.X_POS_COL]
        y_pos = flight_data_array[:, self.Y_POS_COL]
        x_vel = flight_data_array[:, self.X_VEL_COL]
        y_vel = flight_data_array[:, self.Y_VEL_COL]
        x_thrust = flight_data_array[:, self.X_THRUST_COL]
        y_thrust = flight_data_array[:, self.Y_THRUST_COL]
        x_drag = flight_data_array[:, self.X_DRAG_COL]
        y_drag = flight_data_array[:, self.Y_DRAG_COL]
        ax_data = flight_data_array[:, self.X_ACCEL_COL] 
        ay_data = flight_data_array[:, self.Y_ACCEL_COL]

        # Calculate magnitudes (needed regardless of plot_type)
        total_velocity_magnitude = np.sqrt(x_vel**2 + y_vel**2)
        total_thrust_magnitude = np.sqrt(x_thrust**2 + y_thrust**2) 
        total_drag_magnitude = np.sqrt(x_drag**2 + y_drag**2)
        total_acceleration_magnitude = np.sqrt(ax_data**2 + ay_data**2)

        # Mapping of plot_type strings to helper methods and their required data
        plot_configurations_current_data = {
            "position_time": (self._plot_position_time, (time, x_pos, y_pos)),
            "trajectory": (self._plot_trajectory, (x_pos, y_pos)),
            "velocity_time": (self._plot_velocity_components_time, (time, x_vel, y_vel)),
            "total_speed_time": (self._plot_total_speed_time, (time, total_velocity_magnitude)),
            "thrust_components_time": (self._plot_thrust_components_time, (time, x_thrust, y_thrust)),
            "drag_components_time": (self._plot_drag_components_time, (time, x_drag, y_drag)),
            "acceleration_components_time": (self._plot_acceleration_components_time, (time, ax_data, ay_data)),
            "total_acceleration_magnitude_time": (self._plot_total_acceleration_magnitude_time, (time, total_acceleration_magnitude)),
        }
        self.available_plot_types = list(plot_configurations_current_data.keys()) # Update class attribute


        # --- Determine which plots to generate ---
        plots_to_generate = []
        if plot_types is None: # Default: generate all
            plots_to_generate = self.available_plot_types
        elif isinstance(plot_types, str): # Single plot type as a string
            if plot_types in self.available_plot_types:
                plots_to_generate = [plot_types]
            else:
                print(f"Warning: Invalid single plot_type '{plot_types}'. Generating all plots.")
                plots_to_generate = self.available_plot_types
        elif isinstance(plot_types, list): # List of plot types
            for pt in plot_types:
                if pt in self.available_plot_types:
                    plots_to_generate.append(pt)
                else:
                    print(f"Warning: Invalid plot type '{pt}' found in list. Skipping.")
            if not plots_to_generate: # If list was empty or contained no valid types
                print("Warning: No valid plot types specified in the list. Generating all plots.")
                plots_to_generate = self.available_plot_types
        else: # Invalid type for plot_types
            print(f"Warning: Invalid type for plot_types: {type(plot_types)}. Generating all plots.")
            plots_to_generate = self.available_plot_types


        num_plots_to_generate = len(plots_to_generate)

        # --- Create NEW Figure and Axes based on number of plots ---
        if num_plots_to_generate == 0:
            print("No plots to generate.")
            return None
        elif num_plots_to_generate == 1:
            fig, ax_obj_single = plt.subplots(1, 1, figsize=(10, 6))
            # CORRECTED: Ensure ax_objs_iterable is always an iterable
            ax_objs_iterable = [ax_obj_single] 
        else: # Multiple plots (subset or all 8)
            # Dynamic grid calculation for optimal layout
            nrows = math.ceil(math.sqrt(num_plots_to_generate))
            ncols = math.ceil(num_plots_to_generate / nrows)
            
            # Ensure ncols is at least 2 for better default aesthetic unless only 1 row
            if nrows == 1 and num_plots_to_generate > 1:
                ncols = num_plots_to_generate
            elif nrows > 1 and ncols == 1 and num_plots_to_generate > 1:
                 ncols = 2 # At least two columns for multiple rows.

            fig, ax_objs_array = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows))
            # CORRECTED: Ensure ax_objs_iterable is always an iterable (NumPy flat array)
            ax_objs_iterable = ax_objs_array.flatten() 

        fig.suptitle(title, fontsize=16 if num_plots_to_generate > 1 else 14)

        # --- Populate the subplots ---
        # The loop now consistently iterates over ax_objs_iterable
        for i, plot_type_key in enumerate(plots_to_generate):
            ax_current = ax_objs_iterable[i] 
            plot_func, plot_args = plot_configurations_current_data[plot_type_key]
            
            plot_func(ax_current, *plot_args)

        # --- Clean up unused subplots for dynamic grids (if any remain) ---
        # This part now consistently uses ax_objs_iterable and len()
        if num_plots_to_generate > 1 and num_plots_to_generate < len(ax_objs_iterable):
            for j in range(num_plots_to_generate, len(ax_objs_iterable)):
                fig.delaxes(ax_objs_iterable[j])

        # --- Final Layout Adjustments ---
        if num_plots_to_generate > 1:
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.subplots_adjust(hspace=0.55, wspace=0.3)
        else: # Single plot layout
            plt.tight_layout(rect=[0, 0.03, 1, 0.9])

        return fig