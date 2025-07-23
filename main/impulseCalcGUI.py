# impulse_calculator_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import json
import math
import copy
import matplotlib.pyplot as plt # Needed for plt.close('all') for cleanup
import shutil


# Import modules from your project structure
from impulseCalc.graphingTools import FlightDataPlotter
from impulseCalc.ImpulseCalculator import main as ImpulseCalculator_main
print(f"Type of ImpulseCalculator_main: {type(ImpulseCalculator_main)}")
import FileUpload # Assumed to contain FileUpload.hasConfigs and .uploadConfig

class ImpulseCalculatorApp:
    def __init__(self, master_gui, plotter_instance, initial_configs):
        """
        Initializes the Impulse Calculator GUI application.

        Args:
            master_gui (tk.Tk or tk.Toplevel): The parent Tkinter window (main GUI).
            plotter_instance (FlightDataPlotter): An instance of the FlightDataPlotter for generating plots.
            initial_configs (dict): The global configs dictionary containing all application settings.
        """
        print("initialize impulse calc gui")
        print(initial_configs)
        self.master_gui = master_gui
        self.plotter = plotter_instance
        self.configs = initial_configs # Now passed directly, making the class more independent

        # --- Data Storage for Simulation Results (Instance Variables) ---
        self.imp_data = None # Will store [min_imp, q1_imp, med_imp, q3_imp, max_imp, num_imp, mean_imp]
        self.flight_titles_parsed = [] # e.g., ["Flight 1 (T=X N...)"]
        self.flight_data = [] # List of ((avg_thrust, burn_time, apogee), flight_data_array)

        # --- Tkinter StringVars for Dynamic UI Updates ---
        self.num_successful_sims_var = tk.StringVar(value="Successful Simulations: N/A")

        # Impulse Statistics
        self.min_imp_var = tk.StringVar(value="Min Impulse: N/A")
        self.q1_imp_var = tk.StringVar(value="Q1 Impulse: N/A")
        self.med_imp_var = tk.StringVar(value="Median Impulse: N/A")
        self.q3_imp_var = tk.StringVar(value="Q3 Impulse: N/A")
        self.max_imp_var = tk.StringVar(value="Max Impulse: N/A")
        self.num_imp_var = tk.StringVar(value="Number of Impulses: N/A")
        self.mean_imp_var = tk.StringVar(value="Mean Impulse: N/A")

        # Impulse Calculator User Inputs (from configs["ImpulseCalculator"])
        self.user_input_vars = {} # Dictionary of StringVars for dynamic input display
        self._initialize_user_input_vars() # Helper to set these up from configs

        # Flight Selection & Details
        self.selected_flight_dropdown_var = tk.StringVar(value="No Flights Available")
        self.avg_thrust_var = tk.StringVar(value="Avg Thrust: N/A")
        self.burn_time_detail_var = tk.StringVar(value="Burn Time: N/A")
        self.apogee_detail_var = tk.StringVar(value="Apogee: N/A")
        self.max_velocity_var = tk.StringVar(value="Max Velocity: N/A")
        self.max_acceleration_var = tk.StringVar(value="Max Acceleration: N/A")

        # Plot Selection
        self.selected_plot_type_dropdown_var = tk.StringVar(value="Select a Flight First")

        # --- Tkinter PhotoImage References (CRITICAL for preventing garbage collection) ---
        self.current_plot_photo = None # For the main plot display area
        self.open_plot_windows = {} # To track multiple open plot windows {id: (Toplevel, PhotoImage)}
        self.next_window_id = 0 # Counter for unique window IDs

        # --- Build the GUI ---
        self._setup_ui()

    def _initialize_user_input_vars(self):
        """Initializes/updates StringVars for ImpulseCalculator config display."""
        imp_calc_config = self.configs.get("ImpulseCalculator", {})
        # Define a consistent mapping from config key to readable label and format
        input_info = {
            "surfacePressure": ("Surface Pressure (Pa)", ".2f", ""),
            "surfaceTemperature": ("Surface Temperature (K)", ".2f", ""),
            "windVelocity": ("Wind Velocity (m/s)", ".2f", ""),
            "railAngle": ("Rail Angle (rad)", ".3f", ""),
            "launchSiteElevation": ("Launch Site Elevation (m)", ".2f", ""),
            "dragArea": ("Drag Area (m²)", ".4f", ""),
            "dragCoefficient": ("Drag Coefficient", ".2f", ""),
            "noMotorMass": ("No Motor Mass (kg)", ".2f", ""),
            "specificImpulse": ("Specific Impulse (N*s/kg)", ".3f", ""),
            "desiredApogee": ("Desired Apogee (m)", ".2f", ""),
            "apogeeThreshold": ("Apogee Threshold (%)", ".4f", " * 100"), # Multiplied by 100 for display
            "burnTimeRange": ("Burn Time Range (%)", ".4f", " * 100"),  # Multiplied by 100 for display
            "burnTimeStep": ("Burn Time Step (s)", ".2f", ""),
            "minAvgTtW": ("Min Avg Thrust to Weight", ".2f", ""),
            "bisectionBoundPercDiff": ("Bisection Bound Diff", ".6f", ""),
            "deltaT": ("Flight Sim Timestep (s)", ".3f", "")
        }
        for key, (label_text, format_spec, multiplier_str) in input_info.items():
            value = imp_calc_config.get(key, "N/A")
            formatted_value = "N/A"
            if isinstance(value, (int, float)):
                try:
                    # Safely evaluate multiplier if present
                    # This eval is controlled as multiplier_str is defined internally within this class.
                    value_for_eval = float(value)
                    formatted_value = f"{eval(f'{value_for_eval}{multiplier_str}'):{format_spec}}"
                except Exception:
                    formatted_value = str(value) # Fallback if formatting fails
            elif isinstance(value, bool):
                formatted_value = "True" if value else "False"
            else:
                formatted_value = str(value)

            if key not in self.user_input_vars: # Create StringVar if it doesn't exist
                self.user_input_vars[key] = tk.StringVar()
            self.user_input_vars[key].set(f"{label_text}: {formatted_value}")

    def _setup_ui(self):
        """Sets up all Tkinter widgets and their initial layout."""
        # --- Top-level window setup ---
        self.popup = tk.Toplevel(self.master_gui)
        self.popup.transient(self.master_gui)
        self.popup.grab_set()
        self.popup.geometry("1300x800")
        self.popup.resizable(True, True)
        self.popup.title("Impulse Calculator")
        self.popup.protocol("WM_DELETE_WINDOW", self._on_popup_close) # Custom close handler

        # --- Grid Configuration for popup ---
        self.popup.rowconfigure(0, weight=1) # labelFrame and graphsFrame top portion
        self.popup.rowconfigure(1, weight=0) # logoFrame takes fixed height
        self.popup.columnconfigure(0, weight=0) # Left panel fixed width (content driven)
        self.popup.columnconfigure(1, weight=3) # Right panel for graphs expands

        # --- Left Panel Frames ---
        self.labelFrame = tk.Frame(self.popup, borderwidth=1, relief="solid")
        self.labelFrame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.labelFrame.columnconfigure(0, weight=1) # Allow content to expand horizontally
        # No rowconfigure here; rows will size to content vertically

        self.logoFrame = tk.Frame(self.popup, borderwidth=1, relief='solid')
        self.logoFrame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.logoFrame.columnconfigure(0, weight=1)

        # --- Right Panel Frame ---
        self.graphsFrame = tk.Frame(self.popup, borderwidth=1, relief="solid")
        self.graphsFrame.grid(row=0, column=1, sticky='nsew', rowspan=2, padx=5, pady=5)
        self.graphsFrame.columnconfigure(0, weight=1) # Allow content to expand horizontally
        self.graphsFrame.rowconfigure([0, 1, 2, 3, 4, 5], weight=1) # Rows for dynamic content, row 4 for plot

        # --- Left Panel Content ---
        # Impulse Calculator Configuration Label
        tk.Label(self.labelFrame, text="Impulse Calculator Configuration", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, sticky='ew')

        # Run Button Logic (same as before, using FileUpload.hasConfigs on self.configs)
        if FileUpload.hasConfigs(self.configs, 'ImpulseCalculator'):
            tk.Label(self.labelFrame, text="Valid Config Found", fg="green").grid(row=1, column=0, pady=2, padx=2, sticky='ew')
            self.runButton = tk.Button(self.labelFrame, text="Run Impulse Calculator",
                                       command=self.runImpulseCalcualtor, borderwidth=1, relief='solid',
                                       font=("Arial", 10))
            self.runButton.grid(row=2, column=0, sticky='nsew', pady=5)
        else:
            tk.Label(self.labelFrame, text="No valid config found, please upload or create a config", fg="red").grid(row=1, column=0, sticky='nsew', pady=5)
            self.runButton = tk.Button(self.labelFrame, text="Run Impulse Calculator", state='disabled',
                                       borderwidth=1, relief='solid', font=("Arial", 10))
            self.runButton.grid(row=2, column=0, sticky='nsew', pady=5)

        # Exit Button
        tk.Button(self.labelFrame, text="Exit", command=self._on_popup_close, borderwidth=1, relief='solid',
                  font=("Arial", 10)).grid(row=3, column=0, pady=5, sticky='nsew')

        # --- Summary Display Area ---
        self.summary_frame = tk.LabelFrame(self.labelFrame, text="Simulation Summary", borderwidth=1, relief="groove")
        self.summary_frame.grid(row=4, column=0, sticky='nsew', padx=5, pady=5)
        self.summary_frame.columnconfigure(0, weight=1) # Allow content to expand

        tk.Label(self.summary_frame, textvariable=self.num_successful_sims_var).pack(anchor='w', padx=5, pady=2)

        # Impulse Statistics Frame
        self.impulse_stats_frame = tk.LabelFrame(self.summary_frame, text="Impulse Statistics", borderwidth=1, relief="flat")
        self.impulse_stats_frame.pack(fill='x', padx=5, pady=5)
        self.impulse_stats_frame.columnconfigure(0, weight=1)
        tk.Label(self.impulse_stats_frame, textvariable=self.min_imp_var).pack(anchor='w', padx=5)
        tk.Label(self.impulse_stats_frame, textvariable=self.q1_imp_var).pack(anchor='w', padx=5)
        tk.Label(self.impulse_stats_frame, textvariable=self.med_imp_var).pack(anchor='w', padx=5)
        tk.Label(self.impulse_stats_frame, textvariable=self.q3_imp_var).pack(anchor='w', padx=5)
        tk.Label(self.impulse_stats_frame, textvariable=self.max_imp_var).pack(anchor='w', padx=5)
        tk.Label(self.impulse_stats_frame, textvariable=self.num_imp_var).pack(anchor='w', padx=5)
        tk.Label(self.impulse_stats_frame, textvariable=self.mean_imp_var).pack(anchor='w', padx=5)

        # Impulse Calculator Inputs Frame
        self.inputs_frame = tk.LabelFrame(self.summary_frame, text="Impulse Calculator Inputs", borderwidth=1, relief="flat")
        self.inputs_frame.pack(fill='x', padx=5, pady=5)
        self.inputs_frame.columnconfigure(0, weight=1)
        for key in self.user_input_vars: # Dynamically add labels for each input
            tk.Label(self.inputs_frame, textvariable=self.user_input_vars[key], wraplength=300, justify='left').pack(anchor='w', padx=5, pady=1)


        # --- Right Panel Content ---
        # Flight Selection Dropdown
        self.flight_select_frame = tk.LabelFrame(self.graphsFrame, text="Select Flight", borderwidth=1, relief="groove")
        self.flight_select_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.flight_select_frame.columnconfigure(0, weight=1)
        self.flight_dropdown = ttk.OptionMenu(self.flight_select_frame, self.selected_flight_dropdown_var,
                                              self.selected_flight_dropdown_var.get(), *["No Flights Available"])
        self.flight_dropdown.config(width=50) # Set a reasonable default width
        self.flight_dropdown.pack(pady=5)
        self.selected_flight_dropdown_var.trace_add("write", self._display_flight_details)
        self.flight_dropdown.config(state='disabled') # Initially disabled

        # Detailed Flight Info Display
        self.details_frame = tk.LabelFrame(self.graphsFrame, text="Selected Flight Details", borderwidth=1, relief="groove")
        self.details_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.details_frame.columnconfigure(0, weight=1)
        tk.Label(self.details_frame, textvariable=self.avg_thrust_var).pack(anchor='w', padx=5)
        tk.Label(self.details_frame, textvariable=self.burn_time_detail_var).pack(anchor='w', padx=5)
        tk.Label(self.details_frame, textvariable=self.apogee_detail_var).pack(anchor='w', padx=5)
        tk.Label(self.details_frame, textvariable=self.max_velocity_var).pack(anchor='w', padx=5)
        tk.Label(self.details_frame, textvariable=self.max_acceleration_var).pack(anchor='w', padx=5)

        # Plot Type Selection Dropdown
        self.plot_select_frame = tk.LabelFrame(self.graphsFrame, text="Select Plot Type", borderwidth=1, relief="groove")
        self.plot_select_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.plot_select_frame.columnconfigure(0, weight=1)
        self.plot_type_dropdown = ttk.OptionMenu(self.plot_select_frame, self.selected_plot_type_dropdown_var,
                                                 self.selected_plot_type_dropdown_var.get(), *["Select a Flight First"])
        self.plot_type_dropdown.config(width=50)
        self.plot_type_dropdown.pack(pady=5)
        self.selected_plot_type_dropdown_var.trace_add("write", self._display_selected_plot)
        self.plot_type_dropdown.config(state='disabled') # Initially disabled

        # Button to open plot in new window
        self.open_new_window_btn = tk.Button(self.graphsFrame, text="Open Plot in New Window",
                                             command=self._open_plot_in_new_window,
                                             state='disabled', font=("Arial", 10))
        self.open_new_window_btn.grid(row=3, column=0, pady=5, sticky='ew', padx=5)

        # Main Plot Display Area
        self.plot_display_label = tk.Label(self.graphsFrame, text="Plot will appear here.",
                                            borderwidth=1, relief='solid', bg="lightgray")
        self.plot_display_label.grid(row=4, column=0, sticky='nsew', padx=5, pady=5, rowspan=2)
        self.graphsFrame.rowconfigure(4, weight=5) # Gives this row more vertical space
        self.graphsFrame.rowconfigure(5, weight=1) # Can be used for a scrollbar or other controls


    def runImpulseCalcualtor(self):
        """
        Executes the Impulse Calculator simulation and updates the GUI with results.
        This method is called when the "Run Impulse Calculator" button is pressed.
        """
        # Display "Running..." message
        runningLabel = tk.Label(self.graphsFrame, text="Running...", font=("Arial", 14, "bold"), fg="blue")
        runningLabel.grid(row=4, column=0, sticky='nsew', pady=20, padx=20)
        self.popup.update_idletasks() # Force GUI update to show "Running..."

        try:
            ICconfig = copy.deepcopy(self.configs)
            jsonIC = json.dumps(ICconfig, indent=4)

            # Execute the calculator
            # The return values are impData, flightTitles_raw, and flightData_full
            print("running impulse calculator")
            impData, flightTitles_raw, flightData_full_from_main = ImpulseCalculator_main(jsonIC)

            # Store results in instance variables
            self.imp_data = impData
            self.flight_titles_raw = flightTitles_raw # Store the list of [avgThrust, burnTime, apogee]

            # Assign the returned full flight data (list of arrays) to the correct instance variable
            self.flight_data_arrays = flightData_full_from_main

            # Process flightTitles_raw into descriptive strings
            self.flight_titles_parsed = []
            # Use self.flight_data_arrays in the condition check as that's where the actual array data is stored
            if self.flight_data_arrays and self.flight_titles_raw and \
            len(self.flight_data_arrays) == len(self.flight_titles_raw):
                for i, (avg_thrust, burn_time, apogee_val) in enumerate(self.flight_titles_raw):
                    descriptive_title = f"Flight {i+1} (T={avg_thrust:.2f}N, Bt={burn_time:.2f}s, Apogee={apogee_val:.2f}m)"
                    self.flight_titles_parsed.append(descriptive_title)
            else:
                messagebox.showinfo("Simulation Result", "No successful simulations found or data mismatch.")
                print("No successful simulations were returned or flightTitles/flightData_arrays length mismatch.")
                self.flight_titles_parsed = [] # Ensure it's empty if no valid data
        except Exception as e:
            messagebox.showerror("Simulation Error", f"An error occurred during simulation: {e}\nCheck console for details.")
            print(f"Simulation Error: {e}")
            self.imp_data = None
            self.flight_titles_raw = [] # Clear raw titles on error
            self.flight_data_arrays = [] # Clear arrays on error
            self.flight_titles_parsed = [] # Clear parsed titles on error
        finally:
            runningLabel.destroy() # Remove "Running..." label

        # Update the UI with results
        self._update_summary_display()
        self._populate_flight_dropdown()

        if self.flight_data_arrays:
            # 1. Set the dropdown variable.
            self.selected_flight_dropdown_var.set(self.flight_titles_parsed[0])

            # 2. Force Tkinter to process all pending events, including the StringVar trace.
            #    This is more aggressive than update_idletasks for specific widget updates.
            self.popup.update() # Use popup.update() for full redraw/event processing

            # 3. Manually call _display_flight_details as a fallback if trace still doesn't fire.
            self._display_flight_details()

            # 4. Ensure states are set *after* the update chain is triggered.
            self.flight_dropdown.config(state='normal')
            self.plot_type_dropdown.config(state='normal')
            self.open_new_window_btn.config(state='normal')

        else:
          # If no successful flights
            self.selected_flight_dropdown_var.set("No Flights Available")
            self.flight_dropdown.config(state='disabled')
            self.plot_type_dropdown.config(state='disabled')
            self.open_new_window_btn.config(state='disabled')
            
            self._display_flight_details() 

    def _update_summary_display(self):
        """Updates the labels displaying overall summary, impulse statistics, and user inputs."""
        # Update "Successful Simulations"
        num_successful = len(self.flight_data_arrays) if self.flight_data_arrays else 0
        self.num_successful_sims_var.set(f"Successful Simulations: {num_successful}")

        # Update "Impulse Statistics"
        if self.imp_data and len(self.imp_data) == 7:
            # Assumes imp_data is [min_imp, q1_imp, med_imp, q3_imp, max_imp, num_imp, mean_imp]
            self.min_imp_var.set(f"Min Impulse: {self.imp_data[0]:.2f} Ns")
            self.q1_imp_var.set(f"Q1 Impulse: {self.imp_data[1]:.2f} Ns")
            self.med_imp_var.set(f"Median Impulse: {self.imp_data[2]:.2f} Ns")
            self.q3_imp_var.set(f"Q3 Impulse: {self.imp_data[3]:.2f} Ns")
            self.max_imp_var.set(f"Max Impulse: {self.imp_data[4]:.2f} Ns")
            self.num_imp_var.set(f"Number of Impulses: {int(self.imp_data[5])}") # num_imp is integer count
            self.mean_imp_var.set(f"Mean Impulse: {self.imp_data[6]:.2f} Ns")
        else:
            for var in [self.min_imp_var, self.q1_imp_var, self.med_imp_var, self.q3_imp_var,
                        self.max_imp_var, self.num_imp_var, self.mean_imp_var]:
                var.set("N/A")

        # Update "Impulse Calculator Inputs" (re-run initialization to reflect current configs)
        self._initialize_user_input_vars()

    def _populate_flight_dropdown(self):
        """Populates the flight selection dropdown with processed flight titles."""
        menu = self.flight_dropdown["menu"]
        menu.delete(0, "end") # Clear existing options

        if self.flight_titles_parsed:
            for title in self.flight_titles_parsed:
                menu.add_command(label=title, command=tk._setit(self.selected_flight_dropdown_var, title))
            # Default value is set in runImpulseCalcualtor after population
        else:
            self.selected_flight_dropdown_var.set("No Flights Available")
            menu.add_command(label="No Flights Available", command=tk._setit(self.selected_flight_dropdown_var, "No Flights Available"))

    def _display_flight_details(self, *args):
        """
        Updates the labels displaying detailed information for the selected flight.
        Called when the flight selection dropdown changes via trace.
        """
        selected_text = self.selected_flight_dropdown_var.get()
        '''not self.flight_data or "No Flights Available" in selected_text'''
        if not self.flight_data_arrays:
            # Clear all detail labels if no data or invalid selection
            self.avg_thrust_var.set("Avg Thrust: N/A penis")
            self.burn_time_detail_var.set("Burn Time: N/A")
            self.apogee_detail_var.set("Apogee: N/A")
            self.max_velocity_var.set("Max Velocity: N/A")
            self.max_acceleration_var.set("Max Acceleration: N/A")
            self._populate_plot_type_dropdown(clear_only=True) # Clear plot types and plot area
            return

        try:
            # Find the index of the selected flight using its parsed title
            flight_index = self.flight_titles_parsed.index(selected_text)

            # Access the specific flight summary data from flight_titles_raw
            avg_thrust, burn_time, apogee = self.flight_titles_raw[flight_index]

            # Access the specific flight detailed array data from flight_data_arrays
            flight_data_array = self.flight_data_arrays[flight_index]

            # Update StringVars for detailed flight metrics (as before)
            self.avg_thrust_var.set(f"Avg Thrust: {avg_thrust:.2f} N")
            self.burn_time_detail_var.set(f"Burn Time: {burn_time:.2f} s")
            self.apogee_detail_var.set(f"Apogee: {apogee:.2f} m")

            # Calculate Max Velocity and Max Acceleration from flight_data_array (as before)
            x_vel = flight_data_array[:, self.plotter.X_VEL_COL]
            y_vel = flight_data_array[:, self.plotter.Y_VEL_COL]
            max_velocity = np.max(np.sqrt(x_vel**2 + y_vel**2))
            self.max_velocity_var.set(f"Max Velocity: {max_velocity:.2f} m/s")

            ax_data = flight_data_array[:, self.plotter.X_ACCEL_COL]
            ay_data = flight_data_array[:, self.plotter.Y_ACCEL_COL]
            max_acceleration = np.max(np.sqrt(ax_data**2 + ay_data**2))
            self.max_acceleration_var.set(f"Max Acceleration: {max_acceleration:.2f} m/s²")

            # Now populate the plot type dropdown for this specific flight (as before)
            self._populate_plot_type_dropdown()

        except ValueError:
            messagebox.showwarning("Selection Error", f"Selected flight '{selected_text}' not found in data.")
            print(f"Error: Selected flight '{selected_text}' not found in data.")
            self._populate_plot_type_dropdown(clear_only=True) # Clear plot types and plot area
        except Exception as e:
            messagebox.showerror("Display Error", f"Failed to display flight details: {e}\nCheck console for details.")
            print(f"Error in _display_flight_details: {e}")
            self._populate_plot_type_dropdown(clear_only=True) # Clear plot types and plot area

    def _populate_plot_type_dropdown(self, clear_only=False):
        """
        Populates the plot type dropdown with available options.
        Called when a flight is selected or when clearing.
        """
        menu = self.plot_type_dropdown["menu"]
        menu.delete(0, "end") # Clear existing options

        if clear_only or not self.flight_data_arrays:
            self.selected_plot_type_dropdown_var.set("Select a Flight First")
            menu.add_command(label="Select a Flight First", command=tk._setit(self.selected_plot_type_dropdown_var, "Select a Flight First"))
            self.plot_type_dropdown.config(state='disabled')
            self.open_new_window_btn.config(state='disabled')
            self.plot_display_label.config(image='', text="Plot will appear here.") # Clear plot area
            self.current_plot_photo = None
            return

        plot_type_options = ["All Plots"] + sorted(self.plotter.available_plot_types)
        for opt in plot_type_options:
            readable_label = opt.replace('_', ' ').title() # Convert "position_time" to "Position Time"
            menu.add_command(label=readable_label, command=tk._setit(self.selected_plot_type_dropdown_var, readable_label))

        # Set default selection
        if "All Plots" in plot_type_options:
            self.selected_plot_type_dropdown_var.set("All Plots")
        elif plot_type_options:
            self.selected_plot_type_dropdown_var.set(plot_type_options[0].replace('_', ' ').title())
        else: # Should not happen if plotter.available_plot_types is always populated
            self.selected_plot_type_dropdown_var.set("No Plots Available")

        self.plot_type_dropdown.config(state='normal')
        self.open_new_window_btn.config(state='normal')
        self._display_selected_plot() # Automatically display the default plot for the selected flight

    def _display_selected_plot(self, *args):
        """
        Displays the selected plot in the main plot display area within the GUI.
        Called when the plot type dropdown changes via trace.
        """
        selected_flight_text = self.selected_flight_dropdown_var.get()
        plot_type_selection_readable = self.selected_plot_type_dropdown_var.get()

        if "No Flights Available" in selected_flight_text or "Select a Flight First" in plot_type_selection_readable:
            self.plot_display_label.config(image='', text="Plot will appear here.")
            self.current_plot_photo = None
            return

        try:
            # Get flight index and its full data
            flight_index = self.flight_titles_parsed.index(selected_flight_text)
            flight_data_array = self.flight_data_arrays[flight_index] # Directly access the array
            base_title = self.flight_titles_parsed[flight_index] # Use the parsed title for the plot title

            # Convert readable plot type back to internal key for plotter
            plot_types_arg = None
            if plot_type_selection_readable != "All Plots":
                plot_types_arg = plot_type_selection_readable.replace(' ', '_').lower()

            # Get the filepath from the plotter instance. This will generate/save if needed.
            filepath = self.plotter.get_or_create_plot_file(
                flight_data_array=flight_data_array,
                base_title=base_title, # Pass the descriptive title for filename
                plot_types=plot_types_arg
            )

            if filepath and os.path.exists(filepath):
                image = Image.open(filepath)
                # Dynamic resizing logic to fit the label area
                label_width = self.plot_display_label.winfo_width()
                label_height = self.plot_display_label.winfo_height()

                # Fallback if label hasn't been rendered or is tiny
                if label_width < 100: label_width = 800
                if label_height < 100: label_height = 600

                img_width, img_height = image.size
                if img_width > 0 and img_height > 0: # Avoid division by zero
                    aspect_ratio = img_width / img_height
                    target_width = label_width
                    target_height = int(target_width / aspect_ratio)

                    if target_height > label_height: # If it's too tall
                        target_height = label_height
                        target_width = int(target_height * aspect_ratio)

                    image = image.resize((max(1, target_width), max(1, target_height)), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                self.plot_display_label.config(image=photo, text="")
                self.current_plot_photo = photo # CRITICAL: Keep reference!
            else:
                self.plot_display_label.config(image='', text="Plot file not found or could not be generated.")
                self.current_plot_photo = None
                messagebox.showerror("Plot Error", f"Could not load or generate plot: {filepath}")

        except ValueError:
            messagebox.showwarning("Selection Error", "Please select a valid flight and plot type.")
            self.plot_display_label.config(image='', text="Plot will appear here.")
            self.current_plot_photo = None
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying the plot: {e}\nCheck console for details.")
            print(f"Error in _display_selected_plot: {e}")
            self.plot_display_label.config(image='', text="Error loading plot.")
            self.current_plot_photo = None

    def _open_plot_in_new_window(self):
        """
        Opens the currently selected plot in a new Tkinter Toplevel window.
        Allows for multiple plot windows to be open simultaneously.
        """


        selected_flight_text = self.selected_flight_dropdown_var.get()
        plot_type_selection_readable = self.selected_plot_type_dropdown_var.get()

        
        print(self.flight_titles_parsed)
        print(selected_flight_text)

        if not selected_flight_text or not plot_type_selection_readable:
            messagebox.showwarning("Selection Required", "Please select a flight and a plot type first.")
            return

        try:
            flight_index = self.flight_titles_parsed.index(selected_flight_text)
            print(str(flight_index))
            flight_data_array = self.flight_data_arrays[flight_index] # Directly access the array
            base_title = self.flight_titles_parsed[flight_index] # Use the parsed title for the plot title

            plot_types_arg = None
            if plot_type_selection_readable != "All Plots":
                plot_types_arg = plot_type_selection_readable.replace(' ', '_').lower()
            print(plot_types_arg)
            filepath = self.plotter.get_or_create_plot_file(
                flight_data_array=flight_data_array,
                base_title=base_title,
                plot_types=plot_types_arg
            ) 
            print(filepath)


            if filepath and os.path.exists(filepath):
                print("valid filepath")
                # Create a new Toplevel window for this plot
                new_window_id = self.next_window_id
                self.next_window_id += 1
                plot_window = tk.Toplevel(self.popup)
                plot_window.title(f"{base_title} - {plot_type_selection_readable}")
                plot_window.geometry("800x600") # Default size for new plot window
                plot_window.transient(self.popup) # Optional: keep on top of main Impulse Calculator window
                print("window opened")
                # Load and display the image in the new window
                plot_window.update_idletasks()
                image = Image.open(filepath)
                print("opened image")
                # Resize proportionally to fit typical window or its original size if smaller
                image.thumbnail((plot_window.winfo_width() - 20, plot_window.winfo_height() - 20), Image.Resampling.LANCZOS)
                print("1")
                photo = ImageTk.PhotoImage(image)
                print("2")
                plot_label = tk.Label(plot_window, image=photo)
                plot_label.pack(expand=True, fill="both")
                print("3")
                # Store reference in the label itself AND in our class dictionary
                plot_label.image = photo
                self.open_plot_windows[new_window_id] = (plot_window, photo)
                print("4")
                # Add a close protocol to clean up the reference when the window is closed
                plot_window.protocol("WM_DELETE_WINDOW", lambda id=new_window_id: self._close_plot_window(id))

            else:
                messagebox.showerror("Plot Error", f"Could not load or generate plot for new window: {filepath}")

        except ValueError:
            messagebox.showwarning("Selection Error", "Please select a valid flight and plot type before opening in new window.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while opening plot in new window: {e}\nCheck console for details.")
            print(f"Error in _open_plot_in_new_window: {e}")

    def _close_plot_window(self, window_id):
        """Closes a specific plot window and removes its reference from tracking."""
        if window_id in self.open_plot_windows:
            window, _ = self.open_plot_windows.pop(window_id)
            window.destroy()
            print(f"Closed plot window ID: {window_id}")

    def _on_popup_close(self):
        """
        Handles the closing of the main Impulse Calculator popup.
        Closes all associated plot windows and explicitly closes all Matplotlib figures.
        """
        # Close all dynamically opened plot windows
        for window_id in list(self.open_plot_windows.keys()): # Iterate over a copy of keys
            self._close_plot_window(window_id)

        # Close all Matplotlib figures that might still be open in memory
        # This is a good practice to prevent memory leaks, especially if plots were generated
        # but not explicitly closed by FlightDataPlotter (though it should be).
        plt.close('all')
        shutil.rmtree('flight_plots')
        os.makedirs('flight_plots')

        # Destroy the main Impulse Calculator popup window
        self.popup.destroy()