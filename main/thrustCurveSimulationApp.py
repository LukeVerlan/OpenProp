import tkinter as tk
from tkinter import ttk, messagebox, filedialog as fd
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
# Assuming FileUpload contains FileUpload.hasConfigs and .uploadConfig
import FileUpload

# --- Import actual ElevationProperties and consts ---
# IMPORTANT: You need to replace 'your_module_path' with the actual path
# to your ElevationProperties class (e.g., from impulseCalc.elevationTools import ElevationProperties)
from impulseCalc.elevationProperties import elevationDepProperties
import impulseCalc.constants as consts

# Import the separated ThrustCurveSimulator class
from thrustCurveSim.thrustCurveSimulation import ThrustCurveSimulator

# Column indices for the flight_data_array (simFlightData)
# These are still defined but will NOT be passed to FlightDataPlotter directly
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


class ThrustCurveFlightSimApp:
    def __init__(self, master_gui, plotter_instance, initial_configs):
        print("Initializing Thrust Curve Flight Simulation GUI...")
        self.master_gui = master_gui
        self.plotter = plotter_instance
        self.configs = initial_configs

        # --- Data Storage for Simulation Results (Instance Variables) ---
        self.sim_stats = None
        self.flight_data_array = None

        # --- Store parsed nozzle stats ---
        self.nozzle_stats_data = {} # Will store dict from parsing the nozzle stats file

        # --- Tkinter StringVars for Dynamic UI Updates ---
        self.thrust_curve_filepath_var = tk.StringVar(value="No file selected.")
        self.nozzle_stats_filepath_var = tk.StringVar(value="No file selected.")
        self.sim_status_var = tk.StringVar(value="Status: Ready to run simulation.")

        # Simulation Statistics
        self.avg_thrust_var = tk.StringVar(value="Avg Thrust: N/A")
        self.burn_time_var = tk.StringVar(value="Burn Time: N/A")
        self.apogee_var = tk.StringVar(value="Apogee: N/A")
        self.max_velocity_var = tk.StringVar(value="Max Velocity: N/A")
        self.max_acceleration_var = tk.StringVar(value="Max Acceleration: N/A")

        # Configuration Readout StringVars
        self.config_readout_vars = {}

        # Plot Selection
        self.selected_plot_type_dropdown_var = tk.StringVar(value="Run Simulation First")

        # --- Tkinter PhotoImage References (CRITICAL for preventing garbage collection) ---
        self.current_plot_photo = None
        self.open_plot_windows = {}
        self.next_window_id = 0

        # --- Build the GUI ---
        self._setup_ui()
        
        # --- Populate initial config readout values AFTER UI is set up ---
        self._initialize_config_readouts()
        self._update_run_button_state() # Set initial run button state


    def _initialize_config_readouts(self):
        """
        Initializes/updates StringVars for displaying various configuration parameters.
        This method ONLY sets the values of the StringVars, it does NOT create or destroy labels.
        Labels are created once in _setup_ui and _update_config_readout_labels.
        """
        config_info_map = self._get_config_info_map()

        for path_str, (label_text, format_spec, multiplier_str) in config_info_map.items():
            value = "N/A"

            is_nozzle_stats_key = False
            # Check if this key corresponds to a value expected from the nozzle stats file
            for nozzle_key_map in [
                "Nozzle.throat", "Nozzle.throatLength", "Nozzle.divAngle", "Nozzle.convAngle",
                "Nozzle.Search Preference", "Nozzle.Efficiency", "Nozzle.ErosionCoef", "Nozzle.SlagCoef",
                "Nozzle.nozzleDia", "Nozzle.nozzleLength"
            ]:
                if path_str == nozzle_key_map:
                    is_nozzle_stats_key = True
                    break

            if is_nozzle_stats_key:
                # Extract the key as it appears in nozzle_stats_data
                # Convert from map key to file key if necessary (e.g., Nozzle.ErosionCoef -> Erosion Coefficient)
                key_in_stats = path_str.replace("Nozzle.", "")
                if key_in_stats == "ErosionCoef": key_in_stats = "Erosion Coefficient"
                elif key_in_stats == "SlagCoef": key_in_stats = "Slag Coefficient"

                if key_in_stats in self.nozzle_stats_data:
                    value = self.nozzle_stats_data.get(key_in_stats, "N/A")
                else:
                    value = "N/A"
            else:
                # Traverse the main configs dictionary for other values
                current_config_level = self.configs
                try:
                    path_parts = path_str.split('.')
                    for i, part in enumerate(path_parts):
                        if part.isdigit():
                            part = int(part)
                            if isinstance(current_config_level, list) and 0 <= part < len(current_config_level):
                                current_config_level = current_config_level[part]
                            else:
                                raise KeyError(f"Index {part} out of bounds or not a list at {'.'.join(path_parts[:i])}")
                        else:
                            if isinstance(current_config_level, dict) and part in current_config_level:
                                current_config_level = current_config_level[part]
                            else:
                                raise KeyError(f"Key '{part}' not found at {'.'.join(path_parts[:i])}")
                    value = current_config_level
                except (KeyError, IndexError, TypeError):
                    value = "N/A (Config Missing)"

            # Removed special handling for Grains.count as it's being removed from display

            formatted_value = "N/A"
            if isinstance(value, (int, float)):
                try:
                    value_for_eval = float(value)
                    formatted_value = f"{eval(f'{value_for_eval}{multiplier_str}'):{format_spec}}"
                except Exception:
                    formatted_value = str(value)
            elif isinstance(value, bool):
                formatted_value = "True" if value else "False"
            else:
                formatted_value = str(value)

            if path_str not in self.config_readout_vars:
                self.config_readout_vars[path_str] = tk.StringVar()
            self.config_readout_vars[path_str].set(f"{label_text}: {formatted_value}")
        
        # After updating all StringVars, refresh the displayed labels
        if hasattr(self, 'config_inner_frame') and self.config_inner_frame.winfo_exists():
            self._update_config_readout_labels()


    def _update_config_readout_labels(self):
        """
        Clears and repopulates the actual Tkinter Label widgets in config_inner_frame
        based on the current values in self.config_readout_vars.
        This ensures the UI reflects the latest config data, organized with headers.
        """
        # Destroy all existing widgets in config_inner_frame
        for widget in self.config_inner_frame.winfo_children():
            widget.destroy()

        config_info_map = self._get_config_info_map()

        # Define the order and sections for display
        display_order = {
            "Propellant": [],
            "Nozzle": [], # Renamed to simplify, assuming all are shown under one 'Nozzle' header now
            "Launch and rocket parameters": [] # CHANGED HEADER TEXT HERE
        }

        # Populate display_order with keys from config_info_map
        for key in config_info_map.keys():
            if key.startswith("Propellant."):
                display_order["Propellant"].append(key)
            elif key.startswith("Nozzle."):
                display_order["Nozzle"].append(key) # All nozzle keys under this header
            elif key.startswith("ImpulseCalculator."):
                display_order["Launch and rocket parameters"].append(key) # CHANGED HERE
        
        # Now, create labels with headers
        for header, keys in display_order.items():
            if not keys: # Skip if no items for this header
                continue
            
            tk.Label(self.config_inner_frame, text=header, font=("Arial", 10, "bold"), anchor='w').pack(fill='x', padx=5, pady=(8, 2))
            
            keys.sort(key=lambda k: list(config_info_map.keys()).index(k) if k in config_info_map else k)

            for key in keys:
                if key in self.config_readout_vars:
                    var = self.config_readout_vars[key]
                    tk.Label(self.config_inner_frame, textvariable=var, wraplength=280, justify='left').pack(anchor='w', padx=5, pady=1, fill='x')

        self.config_inner_frame.update_idletasks()
        self.config_inner_frame.master.configure(scrollregion = self.config_inner_frame.master.bbox("all"))


    def _setup_ui(self):
        """Sets up all Tkinter widgets and their initial layout."""
        self.popup = tk.Toplevel(self.master_gui)
        self.popup.transient(self.master_gui)
        self.popup.grab_set()
        self.popup.geometry("1300x800")
        self.popup.resizable(True, True)
        self.popup.title("Thrust Curve Flight Simulation")
        self.popup.protocol("WM_DELETE_WINDOW", self._on_popup_close)

        self.popup.rowconfigure(0, weight=1)
        self.popup.columnconfigure(0, weight=1)
        self.popup.columnconfigure(1, weight=3)

        # --- Left Panel ---
        self.left_panel_frame = tk.Frame(self.popup, borderwidth=1, relief="solid")
        self.left_panel_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.left_panel_frame.columnconfigure(0, weight=1)
        self.left_panel_frame.rowconfigure(0, weight=0)
        self.left_panel_frame.rowconfigure(1, weight=0)
        self.left_panel_frame.rowconfigure(2, weight=0)
        self.left_panel_frame.rowconfigure(3, weight=0)
        self.left_panel_frame.rowconfigure(4, weight=2)
        self.left_panel_frame.rowconfigure(5, weight=1)


        # Title Label
        tk.Label(self.left_panel_frame, text="Thrust Curve Flight Simulation", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, sticky='ew')

        # Simulation Status Label
        tk.Label(self.left_panel_frame, textvariable=self.sim_status_var, font=("Arial", 10)).grid(row=1, column=0, pady=2, padx=2, sticky='ew')

        # --- File Selection Frame (Combines Thrust Curve and Nozzle Stats) ---
        self.file_selection_container_frame = tk.LabelFrame(self.left_panel_frame, text="Input Files", borderwidth=1, relief="groove")
        self.file_selection_container_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.file_selection_container_frame.columnconfigure(0, weight=1)
        self.file_selection_container_frame.columnconfigure(1, weight=0)

        # Thrust Curve File Selection
        tk.Label(self.file_selection_container_frame, text="Thrust Curve:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        tk.Label(self.file_selection_container_frame, textvariable=self.thrust_curve_filepath_var, wraplength=200, justify='left').grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(self.file_selection_container_frame, text="Select Thrust Curve", command=self._select_thrust_curve_file, font=("Arial", 9)).grid(row=1, column=1, padx=5, pady=2, sticky='e')

        # Nozzle Stats File Selection (NEW)
        tk.Label(self.file_selection_container_frame, text="Nozzle Stats:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky='w', padx=5, pady=(5,2))
        tk.Label(self.file_selection_container_frame, textvariable=self.nozzle_stats_filepath_var, wraplength=200, justify='left').grid(row=3, column=0, padx=5, pady=2, sticky='ew')
        tk.Button(self.file_selection_container_frame, text="Select Nozzle Stats", command=self._select_nozzle_stats_file, font=("Arial", 9)).grid(row=3, column=1, padx=5, pady=2, sticky='e')


        # Run/Exit Buttons frame
        self.button_frame = tk.Frame(self.left_panel_frame)
        self.button_frame.grid(row=3, column=0, sticky='nsew', pady=5, padx=5)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.runButton = tk.Button(self.button_frame, text="Run Flight Simulation",
                                     command=self.runThrustCurveSim, borderwidth=1, relief='solid',
                                     font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049")
        self.runButton.grid(row=0, column=0, sticky='nsew', pady=0, padx=2)


        tk.Button(self.button_frame, text="Exit", command=self._on_popup_close, borderwidth=1, relief='solid',
                  font=("Arial", 10)).grid(row=0, column=1, pady=0, padx=2, sticky='nsew')


        # Configuration Readout Area
        self.config_readout_frame = tk.LabelFrame(self.left_panel_frame, text="Current Configurations", borderwidth=1, relief="groove")
        self.config_readout_frame.grid(row=4, column=0, sticky='nsew', padx=5, pady=5)
        self.config_readout_frame.columnconfigure(0, weight=1)

        config_canvas = tk.Canvas(self.config_readout_frame)
        config_canvas.pack(side="left", fill="both", expand=True)
        config_scrollbar = ttk.Scrollbar(self.config_readout_frame, orient="vertical", command=config_canvas.yview)
        config_scrollbar.pack(side="right", fill="y")
        config_canvas.configure(yscrollcommand=config_scrollbar.set)

        self.config_inner_frame = tk.Frame(config_canvas)
        self.config_canvas_window_id = config_canvas.create_window((0, 0), window=self.config_inner_frame, anchor="nw")
        
        self.config_inner_frame.bind("<Configure>", lambda e: config_canvas.configure(scrollregion = config_canvas.bbox("all")))
        config_canvas.bind('<Configure>', lambda e: config_canvas.itemconfigure(self.config_canvas_window_id, width=e.width))
        
        self.config_inner_frame.columnconfigure(0, weight=1)

        # Simulation Summary Display Area
        self.summary_frame = tk.LabelFrame(self.left_panel_frame, text="Simulation Summary", borderwidth=1, relief="groove")
        self.summary_frame.grid(row=5, column=0, sticky='nsew', padx=5, pady=5)
        self.summary_frame.columnconfigure(0, weight=1)

        tk.Label(self.summary_frame, textvariable=self.avg_thrust_var).pack(anchor='w', padx=5, pady=2)
        tk.Label(self.summary_frame, textvariable=self.burn_time_var).pack(anchor='w', padx=5)
        tk.Label(self.summary_frame, textvariable=self.apogee_var).pack(anchor='w', padx=5)
        tk.Label(self.summary_frame, textvariable=self.max_velocity_var).pack(anchor='w', padx=5)
        tk.Label(self.summary_frame, textvariable=self.max_acceleration_var).pack(anchor='w', padx=5)


        # --- Right Panel ---
        self.right_panel_frame = tk.Frame(self.popup, borderwidth=1, relief="solid")
        self.right_panel_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.right_panel_frame.columnconfigure(0, weight=1)
        self.right_panel_frame.rowconfigure(0, weight=0)
        self.right_panel_frame.rowconfigure(1, weight=0)
        self.right_panel_frame.rowconfigure(2, weight=1)

        self.plot_select_frame = tk.LabelFrame(self.right_panel_frame, text="Select Plot Type", borderwidth=1, relief="groove")
        self.plot_select_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.plot_select_frame.columnconfigure(0, weight=1)

        self.plot_type_dropdown = ttk.OptionMenu(self.plot_select_frame, self.selected_plot_type_dropdown_var, "Run Simulation First", "Run Simulation First")
        self.plot_type_dropdown.config(width=50, state='disabled')
        self.plot_type_dropdown.pack(pady=5)
        
        self.open_new_window_btn = tk.Button(self.right_panel_frame, text="Open Plot in New Window",
                                             command=self._open_plot_in_new_window,
                                             state='disabled', font=("Arial", 10))
        self.open_new_window_btn.grid(row=1, column=0, pady=5, sticky='ew', padx=5)

        self.plot_display_label = tk.Label(self.right_panel_frame, text="Plot will appear here.",
                                            borderwidth=1, relief='solid', bg="lightgray")
        self.plot_display_label.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

        messagebox.showwarning("Files Saved Locally", "Warning: This tool saves graphs locally as image files in a temporary flight_plots folder. There is currently no way to disable this functionality. The folder is fully cleared upon closing Impulse Calcuator")



    def _get_config_info_map(self):
        """
        Helper to centralize the config info map.
        Updated to reflect the new desired configurations, no detailed grain info.
        """
        return {
            "Propellant.name": ("Propellant Name", "", ""),
            "Propellant.density": ("Propellant Density (Kg/m^3)", ".2f", ""),
            "Propellant.tabs.0.maxPressure": ("Propellant Max Pressure (Pa)", ".2f", ""),
            "Propellant.tabs.0.minPressure": ("Propellant Min Pressure (Pa)", ".2f", ""),
            "Propellant.tabs.0.a": ("Propellant Burn Rate Coef (m/(s*Pa^n))", ".4e", ""),
            "Propellant.tabs.0.n": ("Propellant Burn Rate Exponent", ".3f", ""),
            "Propellant.tabs.0.k": ("Propellant Specific Heat Ratio", ".2f", ""),
            "Propellant.tabs.0.t": ("Propellant Combustion Temp (K)", ".2f", ""),
            "Propellant.tabs.0.m": ("Propellant Exhaust Molar Mass (g/mol)", ".2f", ""),

            # Nozzle properties from the TXT file (keys here match how they are stored in self.nozzle_stats_data)
            "Nozzle.throat": ("Nozzle Throat (m)", ".4f", ""),
            "Nozzle.throatLength": ("Nozzle Throat Length (m)", ".4f", ""),
            "Nozzle.divAngle": ("Nozzle Divergence Angle (deg)", ".2f", ""),
            "Nozzle.convAngle": ("Nozzle Convergence Angle (deg)", ".2f", ""),
            "Nozzle.nozzleDia": ("Nozzle Diameter (m)", ".4f", ""),
            "Nozzle.nozzleLength": ("Nozzle Length (m)", ".4f", ""),
            "Nozzle.Search Preference": ("Nozzle Search Preference", "", ""),
            "Nozzle.Efficiency": ("Nozzle Efficiency (0.##)", ".2f", ""),
            "Nozzle.ErosionCoef": ("Nozzle Erosion Coefficient (s/(m·Pa))", ".4e", ""),
            "Nozzle.SlagCoef": ("Nozzle Slag Coefficient ((m·Pa)/s)", ".4e", ""),

            # ImpulseCalculator properties - CHANGED HEADER TEXT HERE
            "ImpulseCalculator.surfacePressure": ("Surface Pressure (Pa)", ".2f", ""),
            "ImpulseCalculator.surfaceTemperature": ("Surface Temperature (K)", ".2f", ""),
            "ImpulseCalculator.windVelocity": ("Wind Velocity (m/s)", ".2f", ""),
            "ImpulseCalculator.railAngle": ("Rail Angle (rad)", ".3f", ""),
            "ImpulseCalculator.launchSiteElevation": ("Launch Site Elevation (m)", ".2f", ""),
            "ImpulseCalculator.dragArea": ("Drag Area (m²)", ".4f", ""),
            "ImpulseCalculator.dragCoefficient": ("Drag Coefficient", ".2f", ""),
            "ImpulseCalculator.noMotorMass": ("No Motor Mass (kg)", ".2f", ""),
            "ImpulseCalculator.specificImpulse": ("Specific Impulse (N*s/kg)", ".3f", ""),
            "ImpulseCalculator.deltaT": ("Flight Sim Timestep (s)", ".3f", ""),
    }


    def _parse_nozzle_stats_file(self, filepath):
        """
        Parses the nozzle statistics from the given text file.
        Returns a dictionary of parsed stats.
        """
        stats = {}
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("Complete Nozzle Statistics:"):
                        continue
                    
                    if ':' in line:
                        try:
                            key_part, value_part = line.split(':', 1)
                            key = key_part.strip()
                            value_str = value_part.strip()

                            # Remove unit if present (e.g., " - m" or "(m·Pa)/s")
                            if " - " in value_str:
                                value_str = value_str.split(" - ")[0].strip()
                            elif " (" in value_str: # Catch "((m·Pa)/s)"
                                value_str = value_str.split(" (")[0].strip()

                            try:
                                stats[key] = float(value_str)
                            except ValueError:
                                stats[key] = value_str
                        except ValueError:
                            pass
        except Exception as e:
            messagebox.showerror("File Read Error", f"Error reading nozzle statistics file: {e}")
            print(f"Error parsing nozzle stats file: {e}")
            return {}
        return stats


    def _select_thrust_curve_file(self):
        filepath = fd.askopenfilename(
            title="Select Thrust Curve File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self.thrust_curve_filepath_var.set(filepath)
        else:
            self.thrust_curve_filepath_var.set("No file selected.")
        self._update_run_button_state()


    def _select_nozzle_stats_file(self):
        filepath = fd.askopenfilename(
            title="Select Nozzle Statistics File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self.nozzle_stats_filepath_var.set(filepath)
            self.nozzle_stats_data = self._parse_nozzle_stats_file(filepath)
        else:
            self.nozzle_stats_filepath_var.set("No file selected.")
            self.nozzle_stats_data = {}
        
        self._initialize_config_readouts()
        self._update_run_button_state()


    def _update_run_button_state(self):
        """Checks if all necessary conditions are met to enable the run button."""
        thrust_curve_selected = os.path.exists(self.thrust_curve_filepath_var.get())
        nozzle_stats_selected = os.path.exists(self.nozzle_stats_filepath_var.get()) and bool(self.nozzle_stats_data)
        configs_present = FileUpload.hasConfigs(self.configs, 'ImpulseCalculator')

        if thrust_curve_selected and nozzle_stats_selected and configs_present:
            self.runButton.config(state='normal', bg="#4CAF50", fg="white")
            self.sim_status_var.set("Status: Ready to run simulation with all files and configs.")
        else:
            self.runButton.config(state='disabled', bg="#cccccc", fg="black")
            status_parts = []
            if not thrust_curve_selected: status_parts.append("Thrust Curve File")
            if not nozzle_stats_selected: status_parts.append("Nozzle Stats File (and data)")
            if not configs_present: status_parts.append("Required Configs")
            self.sim_status_var.set(f"Status: Missing: {', '.join(status_parts)}.")


    def _run_simulation_core(self, config_dict, thrust_curve_filepath):
        """
        Runs the actual flight simulation using the ThrustCurveSimulator class.

        Args:
            config_dict (dict): The parsed configuration dictionary.
            thrust_curve_filepath (str): Path to the thrust curve CSV file.

        Returns:
            tuple: (sim_stats_dict, flight_data_array)
        """
        if not os.path.exists(thrust_curve_filepath):
            raise FileNotFoundError(f"Thrust curve file not found: {thrust_curve_filepath}")

        deltaT = config_dict["ImpulseCalculator"].get("deltaT", 0.01)

        ep_instance = elevationDepProperties(consts) 
        simulator = ThrustCurveSimulator(consts, config_dict, ep_instance) 

        sim_stats, flight_data_array = simulator.runsimulation(deltaT, thrust_curve_filepath)

        return sim_stats, flight_data_array


    def runThrustCurveSim(self):
        messagebox.showwarning("Fuel Configuration", "Warning: This tool does not read the grain geometry/configuration. The nozzle information (from the txt) and fuel are displayed for reference only. Only the uploaded thrust curve affects the simulation.")

        thrust_curve_filepath = self.thrust_curve_filepath_var.get()
        nozzle_stats_filepath = self.nozzle_stats_filepath_var.get()

        if not os.path.exists(thrust_curve_filepath) or not os.path.exists(nozzle_stats_filepath) or not bool(self.nozzle_stats_data):
            messagebox.showerror("File Error", "Both thrust curve and nozzle statistics files must be selected and valid.")
            self.sim_status_var.set("Status: Error - Missing required files or invalid nozzle data.")
            return
        
        self.runButton.config(state='disabled')
        self.sim_status_var.set("Status: Running simulation...")
        self.popup.update_idletasks()

        try:
            temp_configs_for_sim = copy.deepcopy(self.configs) 

            if "Nozzle" not in temp_configs_for_sim:
                temp_configs_for_sim["Nozzle"] = {}
            
            # This mapping needs to be precise based on your ThrustCurveSimulator's expected config structure.
            # I am making assumptions here; adjust these mappings as per your simulator's actual requirements.
            nozzle_key_mapping = {
                "throat": "minDia",
                "throatLength": "minLen",
                "divAngle": "exitHalf",
                "convAngle": "minHalfConv",
                "nozzleDia": "nozzleDia",
                "nozzleLength": "nozzleLength",
                "Search Preference": "preference",
                "Efficiency": "Efficiency",
                "Erosion Coefficient": "ErosionCoef",
                "Slag Coefficient": "SlagCoef",
            }

            for file_key, file_value in self.nozzle_stats_data.items():
                if file_key in nozzle_key_mapping:
                    temp_configs_for_sim["Nozzle"][nozzle_key_mapping[file_key]] = file_value
                # else: # Option to add unmapped keys directly if simulator expects them
                #     temp_configs_for_sim["Nozzle"][file_key] = file_value


            sim_stats, flight_data_array = self._run_simulation_core(temp_configs_for_sim, thrust_curve_filepath)

            self.sim_stats = sim_stats
            self.flight_data_array = flight_data_array

        except Exception as e:
            messagebox.showerror("Simulation Error", f"An error occurred during simulation: {e}\nCheck console for details.")
            print(f"Simulation Error: {e}")
            self.sim_stats = None
            self.flight_data_array = None
            self.sim_status_var.set("Status: Simulation failed.")
        finally:
            self._update_summary_display()
            self._display_flight_details()
            self._update_run_button_state()


    def _update_summary_display(self):
        if self.sim_stats:
            self.avg_thrust_var.set(f"Avg Thrust: {self.sim_stats.get('avg_thrust', 0):.2f} N")
            self.burn_time_var.set(f"Burn Time: {self.sim_stats.get('burn_time', 0):.2f} s")
            self.apogee_var.set(f"Apogee: {self.sim_stats.get('apogee', 0):.2f} m")
            self.max_velocity_var.set(f"Max Velocity: {self.sim_stats.get('max_velocity', 0):.2f} m/s")
            self.max_acceleration_var.set(f"Max Acceleration: {self.sim_stats.get('max_acceleration', 0):.2f} m/s²")
        else:
            self.avg_thrust_var.set("Avg Thrust: N/A")
            self.burn_time_var.set("Burn Time: N/A")
            self.apogee_var.set("Apogee: N/A")
            self.max_velocity_var.set("Max Velocity: N/A")
            self.max_acceleration_var.set("Max Acceleration: N/A")

        self._initialize_config_readouts()

    def _display_flight_details(self, *args):
        if self.flight_data_array is None or len(self.flight_data_array) == 0:
            self.avg_thrust_var.set("Avg Thrust: N/A")
            self.burn_time_var.set("Burn Time: N/A")
            self.apogee_var.set("Apogee: N/A")
            self.max_velocity_var.set("Max Velocity: N/A")
            self.max_acceleration_var.set("Max Acceleration: N/A")
            self._populate_plot_type_dropdown(clear_only=True)
            return

        self._populate_plot_type_dropdown()


    def _populate_plot_type_dropdown(self, clear_only=False):
        if hasattr(self, 'plot_type_dropdown') and self.plot_type_dropdown.winfo_exists():
            self.plot_type_dropdown.destroy()

        plot_type_options = []
        if clear_only or self.flight_data_array is None or len(self.flight_data_array) == 0:
            plot_type_options.append("Run Simulation First")
            initial_selection = "Run Simulation First"
            dropdown_state = 'disabled'
            btn_state = 'disabled'
            plot_label_text = "Plot will appear here."
            plot_label_image = ''
            self.current_plot_photo = None
        else:
            plot_type_options.append("All Plots")
            if hasattr(self.plotter, 'available_plot_types') and self.plotter.available_plot_types:
                plot_type_options.extend(sorted([p.replace('_', ' ').title() for p in self.plotter.available_plot_types]))
            
            initial_selection = "All Plots"
            dropdown_state = 'normal'
            btn_state = 'normal'
            plot_label_text = ""
            plot_label_image = None

        self.selected_plot_type_dropdown_var.set(initial_selection)

        self.plot_type_dropdown = ttk.OptionMenu(
            self.plot_select_frame, 
            self.selected_plot_type_dropdown_var, 
            initial_selection,
            *plot_type_options
        )
        self.plot_type_dropdown.config(width=50, state=dropdown_state)
        self.plot_type_dropdown.pack(pady=5)

        self.selected_plot_type_dropdown_var.trace_add("write", self._display_selected_plot)

        self.open_new_window_btn.config(state=btn_state)
        self.plot_display_label.config(image=plot_label_image, text=plot_label_text)

        if not clear_only:
            self._display_selected_plot()


    def _display_selected_plot(self, *args):
        """
        Displays the selected plot in the main plot display area within the GUI.
        Removed direct column arguments as plotter is assumed to handle them.
        """
        plot_type_selection_readable = self.selected_plot_type_dropdown_var.get()

        if self.flight_data_array is None or len(self.flight_data_array) == 0 or "Run Simulation First" in plot_type_selection_readable:
            self.plot_display_label.config(image='', text="Plot will appear here.")
            self.current_plot_photo = None
            return

        try:
            flight_data_array = self.flight_data_array
            base_title = "Thrust Curve Flight Simulation Result"

            plot_types_arg = None
            if plot_type_selection_readable != "All Plots":
                plot_types_arg = plot_type_selection_readable.replace(' ', '_').lower()

            filepath = self.plotter.get_or_create_plot_file(
                flight_data_array=flight_data_array,
                base_title=base_title,
                plot_types=plot_types_arg
                # Removed direct column arguments: time_col, x_pos_col, etc.
            )

            if filepath and os.path.exists(filepath):
                image = Image.open(filepath)
                label_width = self.plot_display_label.winfo_width()
                label_height = self.plot_display_label.winfo_height()

                if label_width < 100: label_width = 800
                if label_height < 100: label_height = 600

                img_width, img_height = image.size
                if img_width > 0 and img_height > 0:
                    aspect_ratio = img_width / img_height
                    target_width = label_width
                    target_height = int(target_width / aspect_ratio)

                    if target_height > label_height:
                        target_height = label_height
                        target_width = int(target_height * aspect_ratio)

                    image = image.resize((max(1, target_width), max(1, target_height)), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                self.plot_display_label.config(image=photo, text="")
                self.current_plot_photo = photo
            else:
                self.plot_display_label.config(image='', text="Plot file not found or could not be generated.")
                self.current_plot_photo = None
                messagebox.showerror("Plot Error", f"Could not load or generate plot: {filepath}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying the plot: {e}\nCheck console for details.")
            print(f"Error in _display_selected_plot: {e}")
            self.plot_display_label.config(image='', text="Error loading plot.")
            self.current_plot_photo = None

    def _open_plot_in_new_window(self):
        """
        Opens the currently selected plot in a new Tkinter Toplevel window.
        Removed direct column arguments as plotter is assumed to handle them.
        """
        plot_type_selection_readable = self.selected_plot_type_dropdown_var.get()

        if self.flight_data_array is None or len(self.flight_data_array) == 0 or "Run Simulation First" in plot_type_selection_readable:
            messagebox.showwarning("Selection Required", "Please run simulation and select a plot type first.")
            return

        try:
            flight_data_array = self.flight_data_array
            base_title = "Thrust Curve Flight Simulation Result"

            plot_types_arg = None
            if plot_type_selection_readable != "All Plots":
                plot_types_arg = plot_type_selection_readable.replace(' ', '_').lower()

            filepath = self.plotter.get_or_create_plot_file(
                flight_data_array=flight_data_array,
                base_title=base_title,
                plot_types=plot_types_arg
                # Removed direct column arguments: time_col, x_pos_col, etc.
            )

            if filepath and os.path.exists(filepath):
                new_window_id = self.next_window_id
                self.next_window_id += 1
                plot_window = tk.Toplevel(self.popup)
                plot_window.title(f"{base_title} - {plot_type_selection_readable}")
                plot_window.geometry("800x600")
                plot_window.transient(self.popup)

                plot_window.update_idletasks()
                image = Image.open(filepath)

                image.thumbnail((plot_window.winfo_width() - 20, plot_window.winfo_height() - 20), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                plot_label = tk.Label(plot_window, image=photo)
                plot_label.pack(expand=True, fill="both")

                plot_label.image = photo
                self.open_plot_windows[new_window_id] = (plot_window, photo)

                plot_window.protocol("WM_DELETE_WINDOW", lambda id=new_window_id: self._close_plot_window(id))

            else:
                messagebox.showerror("Plot Error", f"Could not load or generate plot for new window: {filepath}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while opening plot in new window: {e}\nCheck console for details.")
            print(f"Error in _open_plot_in_new_window: {e}")

    def _close_plot_window(self, window_id):
        if window_id in self.open_plot_windows:
            window, _ = self.open_plot_windows.pop(window_id)
            window.destroy()
            print(f"Closed plot window ID: {window_id}")

    def _on_popup_close(self):
        for window_id in list(self.open_plot_windows.keys()):
            self._close_plot_window(window_id)

        plt.close('all')

        if os.path.exists('flight_plots'):
            try:
                shutil.rmtree('flight_plots')
            except OSError as e:
                print(f"Error removing directory flight_plots: {e}")
        os.makedirs('flight_plots', exist_ok=True)

        self.popup.destroy()