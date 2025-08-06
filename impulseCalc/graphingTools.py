# graphingTools.py

import matplotlib.pyplot as plt
import numpy as np
import math
import os
from PIL import Image, ImageTk # ImageTk is used by ImpulseCalculatorApp, not directly in plotter

# --- Standalone helper function for tabular data output ---
def print_flight_data(flight_data_array, print_interval=5.0):
    """
    Prints a summary of simulation flight data at specified time intervals.
    (This function is as you provided, with the minor drag component correction)
    """
    if flight_data_array.size == 0:
        print("No flight data to display.")
        return

    next_print_time = 0.0

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
                x_drag = flight_data_array[row_index, X_DRAG_COL] # Corrected from Y_DRAG_COL
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
    print("\n--- End of Flight Data for flight above ---\n")


# --- FlightDataPlotter Class ---
class FlightDataPlotter:
    """
    A class to construct matplotlib Figure objects for flight data and save them as images.
    It also manages the paths of created plot files.
    """
    def __init__(self, output_dir="flight_plots"):
        # Define column indices as class attributes for easy access
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

        self.plot_output_dir = output_dir
        os.makedirs(self.plot_output_dir, exist_ok=True)

        self.saved_plot_paths = {} # Dictionary to store plot_key: file_path

        # Map plot_type strings to helper methods and their required data
        # This will be populated fully on the first call to plot_flight_data
        self._plot_configurations_map = {}
        self.available_plot_types = [] # Public list of available plot type keys


    # --- Private Helper Methods for Individual Plots (As you provided, UNCHANGED) ---
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


    def _generate_plot_filename(self, base_title, plot_types):
        """Helper to generate a consistent filename based on title and plot types."""
        sanitized_title = "".join(c for c in base_title if c.isalnum() or c in (' ', '.', '_')).replace(' ', '_')
        if plot_types and isinstance(plot_types, list):
            type_suffix = "_".join(plot_types)
        elif plot_types and isinstance(plot_types, str):
            type_suffix = plot_types
        else:
            type_suffix = "all"
        # Ensure suffix doesn't start or end with underscore if base_title ends with one
        type_suffix = type_suffix.strip('_')
        return f"{sanitized_title.strip('_')}_{type_suffix}.png"


    def plot_flight_data(self, flight_data_array, title="Flight Simulation Data", plot_types=None, save_to_file=True):
        """
        Constructs a new matplotlib Figure object containing the plot(s).
        If save_to_file is True, it saves the plot as an image and returns the filepath.
        Otherwise, it returns the Figure object.
        """
        # Basic input validation
        if not isinstance(flight_data_array, np.ndarray) or flight_data_array.ndim != 2:
            print("Error: flight_data_array must be a 2D NumPy array.")
            return None if save_to_file else None
        if flight_data_array.shape[1] != 11:
            print(f"Error: flight_data_array must have 11 columns. Found {flight_data_array.shape[1]}.")
            return None if save_to_file else None
        if flight_data_array.shape[0] == 0:
            print("No data to plot in the provided array.")
            return None if save_to_file else None

        # Extract data columns
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

        # Calculate magnitudes
        total_velocity_magnitude = np.sqrt(x_vel**2 + y_vel**2)
        total_thrust_magnitude = np.sqrt(x_thrust**2 + y_thrust**2)
        total_drag_magnitude = np.sqrt(x_drag**2 + y_drag**2)
        total_acceleration_magnitude = np.sqrt(ax_data**2 + ay_data**2)

        # Initialize plot configurations map (if not already done)
        if not self._plot_configurations_map:
            self._plot_configurations_map = {
                "position_time": (self._plot_position_time, (time, x_pos, y_pos)),
                "trajectory": (self._plot_trajectory, (x_pos, y_pos)),
                "velocity_time": (self._plot_velocity_components_time, (time, x_vel, y_vel)),
                "total_speed_time": (self._plot_total_speed_time, (time, total_velocity_magnitude)),
                "thrust_components_time": (self._plot_thrust_components_time, (time, x_thrust, y_thrust)),
                "drag_components_time": (self._plot_drag_components_time, (time, x_drag, y_drag)),
                "acceleration_components_time": (self._plot_acceleration_components_time, (time, ax_data, ay_data)),
                "total_acceleration_magnitude_time": (self._plot_total_acceleration_magnitude_time, (time, total_acceleration_magnitude)),
            }
            self.available_plot_types = list(self._plot_configurations_map.keys())

        # Determine which plots to generate
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
        if num_plots_to_generate == 0:
            print("No plots to generate based on selection.")
            return None if save_to_file else None

        # Create NEW Figure and Axes based on number of plots
        if num_plots_to_generate == 1:
            fig, ax_obj_single = plt.subplots(1, 1, figsize=(10, 6))
            ax_objs_iterable = [ax_obj_single]
        else:
            nrows = math.ceil(math.sqrt(num_plots_to_generate))
            ncols = math.ceil(num_plots_to_generate / nrows)
            if nrows == 1 and num_plots_to_generate > 1: # For 1 row, multiple columns
                ncols = num_plots_to_generate
            elif nrows > 1 and ncols == 1 and num_plots_to_generate > 1: # For 1 column, multiple rows
                 ncols = 2 # At least 2 columns if multiple rows and only 1 column was calculated

            fig, ax_objs_array = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows))
            ax_objs_iterable = ax_objs_array.flatten()

        fig.suptitle(title, fontsize=16 if num_plots_to_generate > 1 else 14)

        # Populate the subplots
        for i, plot_type_key in enumerate(plots_to_generate):
            ax_current = ax_objs_iterable[i]
            # Ensure the configuration map is updated with current data
            # This is a bit redundant if map is static, but ensures fresh data is used
            plot_func, plot_args_template = self._plot_configurations_map[plot_type_key]
            # Reconstruct plot_args with current data
            if plot_type_key == "position_time": plot_args = (time, x_pos, y_pos)
            elif plot_type_key == "trajectory": plot_args = (x_pos, y_pos)
            elif plot_type_key == "velocity_time": plot_args = (time, x_vel, y_vel)
            elif plot_type_key == "total_speed_time": plot_args = (time, total_velocity_magnitude)
            elif plot_type_key == "thrust_components_time": plot_args = (time, x_thrust, y_thrust)
            elif plot_type_key == "drag_components_time": plot_args = (time, x_drag, y_drag)
            elif plot_type_key == "acceleration_components_time": plot_args = (time, ax_data, ay_data)
            elif plot_type_key == "total_acceleration_magnitude_time": plot_args = (time, total_acceleration_magnitude)
            else: plot_args = plot_args_template # Fallback

            plot_func(ax_current, *plot_args)

        # Clean up unused subplots for dynamic grids (if any remain)
        if num_plots_to_generate > 1 and num_plots_to_generate < len(ax_objs_iterable):
            for j in range(num_plots_to_generate, len(ax_objs_iterable)):
                fig.delaxes(ax_objs_iterable[j])

        # Final Layout Adjustments
        if num_plots_to_generate > 1:
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.subplots_adjust(hspace=0.55, wspace=0.3)
        else: # Single plot layout
            plt.tight_layout(rect=[0, 0.03, 1, 0.9])

        if save_to_file:
            filename = self._generate_plot_filename(title, plot_types)
            filepath = os.path.join(self.plot_output_dir, filename)

            try:
                fig.savefig(filepath, dpi=300)
                plt.close(fig) # Close the figure immediately after saving
                plot_key = f"{title}_{'_'.join(plot_types) if isinstance(plot_types, list) else plot_types or 'all'}"
                self.saved_plot_paths[plot_key] = filepath
                return filepath
            except Exception as e:
                print(f"Error saving plot to {filepath}: {e}")
                plt.close(fig)
                return None
        else:
            return fig

    def get_or_create_plot_file(self, flight_data_array, base_title, plot_types=None):
        """
        Checks if a plot image already exists and is tracked. If not, it generates and saves it.
        Returns the file path.
        """
        # Create a consistent key for the saved_plot_paths dictionary
        plot_key = f"{base_title}_{'_'.join(plot_types) if isinstance(plot_types, list) else plot_types or 'all'}"
        filename = self._generate_plot_filename(base_title, plot_types)
        expected_filepath = os.path.join(self.plot_output_dir, filename)

        if plot_key in self.saved_plot_paths and os.path.exists(self.saved_plot_paths[plot_key]):
            # print(f"Plot '{plot_key}' already exists at {self.saved_plot_paths[plot_key]}. Using existing file.")
            return self.saved_plot_paths[plot_key]
        elif os.path.exists(expected_filepath):
            # File exists but wasn't tracked (e.g., from previous run of the application)
            self.saved_plot_paths[plot_key] = expected_filepath
            # print(f"Plot file found at {expected_filepath}. Tracking it.")
            return expected_filepath
        else:
            print(f"Plot '{plot_key}' not found. Generating and saving...")
            # Call the main plotting method to create and save the figure
            generated_filepath = self.plot_flight_data(
                flight_data_array=flight_data_array,
                title=base_title,
                plot_types=plot_types,
                save_to_file=True # Always save when called this way
            )
            if generated_filepath:
                self.saved_plot_paths[plot_key] = generated_filepath
                print(f"Plot '{plot_key}' generated and saved to {generated_filepath}.")
            return generated_filepath

    def get_saved_plot_path(self, plot_key):
        """Retrieves the file path for a saved plot by its unique key."""
        return self.saved_plot_paths.get(plot_key)

    def list_saved_plots(self):
        """Lists all the unique keys and their corresponding file paths for plots."""
        if not self.saved_plot_paths:
            print("No plots have been saved or tracked by this plotter instance yet.")
        else:
            print("\n--- Saved Plots ---")
            for key, path in self.saved_plot_paths.items():
                print(f"- {key}: {path}")
            print("-------------------\n")
    
    def clear_all_plots(self):
        """
        Clears the in-memory cache and deletes all plot files from the output directory.
        This should be called when new simulation data is available.
        """
        self.saved_plot_paths = {}
        try:
            if os.path.exists(self.plot_output_dir):
                for filename in os.listdir(self.plot_output_dir):
                    filepath = os.path.join(self.plot_output_dir, filename)
                    if os.path.isfile(filepath) and filepath.endswith('.png'):
                        os.remove(filepath)
                print(f"Cleared all plot files from {self.plot_output_dir}")
        except OSError as e:
            print(f"Error clearing plot directory {self.plot_output_dir}: {e}")