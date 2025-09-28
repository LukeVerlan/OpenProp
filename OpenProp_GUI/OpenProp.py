# MAIN
#
# Handles user input and calls upon sub files depending on what the user wants to do 

import json

# File handling libraries
import sys

# GUI library
import tkinter as tk
from tkinter import ttk 
import PIL

# Custom files
import FileUpload
import save_configs
import config_creators

# Nozzle Iterator import
from NozzleIterator import nozzle_iterator_gui

# Tool Files
from impulseCalcGUI import ImpulseCalculatorApp
from impulseCalc.graphingTools import FlightDataPlotter
from impulseCalc import ImpulseCalculator # Module for ImpulseCalculator.main
from thrustCurveSimulationApp import ThrustCurveFlightSimApp

from CurativeCalculator import CurativeCalculator

# @Breif Main function of OpenProp, initializes the GUI and sets up the main page
def main(): 

  global configs

  configs = {}

  # Apply default OpenMotor Settings
  configs["Motor"] = {

        "SimulationParameters" : {
            "maxPressure" : 10000000,
            "maxMassFlux" : 1406,
            "maxMachNumber" : 0.8,
            "minPortThroat" : 2,
            "flowSeparationWarnPercent" : 0.15
        },

        "SimulationBehavior" : {
            "burnoutWebThres" : 0.000025,
            "burnoutThrustThres" : 0.001,
            "timestep" : 0.03,
            "ambPressure" : 101325,
            "mapDim" : 750,
            "sepPressureRatio" : 0.3
        }
    }
  
  flight_plotter_instance = FlightDataPlotter(output_dir="flight_plots")
  
  # ---------------------------------------------------
  # FOR UPLOAD DEV WORK COMMENT OUT FOR USER EXPERIENCE
  # ---------------------------------------------------

  # with open('./NozzleIterator/config.json', 'r') as file:
  #   configs = json.load(file)

  # initialize main GUI page
  gui = tk.Tk()
  gui.title('OpenProp')
  gui.geometry("1000x600")
  gui.resizable(True, True)

  # --- configure root grid ---
  gui.rowconfigure(0, weight=1)   # logo row
  gui.rowconfigure(1, weight=3)   # main content row
  gui.columnconfigure(0, weight=1)
  gui.columnconfigure(1, weight=1)

  # --- logo frame ---
  OPimDir = FileUpload.resource_path("./OP_ASSEM.jpg")
  OPim = PIL.Image.open(OPimDir)
  tk_OPim = PIL.ImageTk.PhotoImage(OPim)

  logoFrame = tk.Frame(gui, borderwidth=1, relief='solid')
  logoFrame.grid(row=0, column=0, columnspan=2, sticky='nsew')
  logoFrame.rowconfigure(0, weight=1)
  logoFrame.columnconfigure(0, weight=1)

  logoLabel = tk.Label(logoFrame, image=tk_OPim)
  logoLabel.grid(row=0, column=0, sticky='nsew')
  logoLabel.image = tk_OPim  

  # --- functions frame ---
  functionsFrame = ttk.Frame(gui, padding=10)
  functionsFrame.grid(row=1, column=0, sticky="nsew")
  functionsFrame.rowconfigure(list(range(5)), weight=1)  # evenly spread rows
  functionsFrame.columnconfigure(0, weight=1)

  functionsLabel = tk.Label(functionsFrame, text="Functions", font=("Arial", 14, "bold"))
  functionsLabel.grid(row=0, column=0, sticky="nsew")

  nozzleBtn = ttk.Button(functionsFrame, text="Nozzle Iterator",
                        command=lambda: NozzleIteratorGUI(gui, configs))
  nozzleBtn.grid(row=1, column=0, sticky="nsew")

  impulseBtn = ttk.Button(functionsFrame, text="Impulse Calculator", 
                          command=lambda: ImpulseCalculatorApp(gui, flight_plotter_instance, configs))
  impulseBtn.grid(row=2, column=0, sticky="nsew")

  seriesBtn = ttk.Button(functionsFrame, text="Flight Simulation w/ Thrust Curve", 
                        command=lambda: ThrustCurveFlightSimGUI(gui, flight_plotter_instance, configs))
  seriesBtn.grid(row=3, column=0, sticky="nsew")

  # --- configurations frame ---
  configsFrame = tk.Frame(gui, padx=10, pady=10)
  configsFrame.grid(row=1, column=1, sticky="nsew")
  configsFrame.rowconfigure(list(range(6)), weight=1)
  configsFrame.columnconfigure(0, weight=1)

  configsLabel = tk.Label(configsFrame, text="Settings", font=("Arial", 14, "bold"))
  configsLabel.grid(row=0, column=0, sticky="nsew")

  createConfigBtn = ttk.Button(configsFrame, text="Config Settings",
                              command=lambda: handleCreateConfig(gui))
  createConfigBtn.grid(row=1, column=0, sticky="nsew")

  # Start GUI
  gui.mainloop()

def ThrustCurveFlightSimGUI(master_gui, plotter_instance, configs):
  ThrustCurveFlightSimApp(master_gui, plotter_instance, configs)
  
def NozzleIteratorGUI(gui, configs):
    nozzle_iterator_gui.run_gui(gui, configs)

# @Brief Handles the creation of the configuration GUI, allows user to create or upload configs
# @param gui - The main GUI window
def handleCreateConfig(gui):
  popup = tk.Toplevel(gui)
  
  popup.transient(gui) # Keep it on top of main window
  popup.grab_set()   

  popup.columnconfigure(0, weight=1)
  popup.columnconfigure(1, weight=2)
  popup.columnconfigure(2, weight=1)
  popup.geometry("1300x600") # width px by height px
  popup.resizable(False, False)

  optionsFrame = tk.Frame(popup)
  optionsFrame.grid(row=0, column=0, rowspan=10, sticky='nsew')

  fakeLabelFrame =tk.Frame(popup)
  fakeLabelFrame.grid(row=0, column=1, sticky='nsew', padx=2)

  fakeFrame = tk.Frame(popup)
  fakeFrame.grid(row=1,column=1, sticky='nsew', padx=2)

  propConfigLabel = tk.Button(optionsFrame, text="Create Propellant",command=lambda: config_creators.createPropellant(popup, configs))
  propConfigLabel.grid(row=0,column=0,sticky='nsew', pady=2)

  grainConfigLabel = tk.Button(optionsFrame, text="Create Grain Geometry",command=lambda: config_creators.createGrainGeometry(popup,configs))
  grainConfigLabel.grid(row=1,column=0,sticky='nsew', pady=2)

  NIConfigLabel = tk.Button(optionsFrame, text="Create Nozzle Iterator Config",command=lambda: config_creators.createNozzleIterator(popup,configs))
  NIConfigLabel.grid(row=2,column=0,sticky='nsew', pady=2)

  OMConfigLabel = tk.Button(optionsFrame, text="Create OpenMotor settings config",command=lambda: config_creators.createOMsettings(popup,configs))
  OMConfigLabel.grid(row=3,column=0,sticky='nsew', pady=2)
  
  ICConfigLabel = tk.Button(optionsFrame, text="Create Impulse Calculator config",command=lambda: config_creators.createImpulseCalculator(popup,configs))
  ICConfigLabel.grid(row=4,column=0,sticky='nsew', pady=2)

  ICUploadLabel = tk.Button(optionsFrame, text="Upload Impulse Calculator config",command=lambda: FileUpload.uploadConfig(popup, configs, 'ImpulseCalculator'))
  ICUploadLabel.grid(row=5,column=0,sticky='nsew', pady=2)

  propUploadLabel = tk.Button(optionsFrame, text="Upload Propellant config",command=lambda:FileUpload.uploadConfig(popup, configs, 'Propellant'))
  propUploadLabel.grid(row=6,column=0,sticky='nsew', pady=2)

  grainUploadLabel = tk.Button(optionsFrame, text="Upload Grain config",command=lambda: FileUpload.uploadConfig(popup, configs,'Grains'))
  grainUploadLabel.grid(row=7,column=0,sticky='nsew', pady=2)

  NIUploadLabel = tk.Button(optionsFrame, text="Upload Nozzle Iterator Config",command=lambda: FileUpload.uploadConfig(popup, configs, 'Nozzle'))
  NIUploadLabel.grid(row=8,column=0,sticky='nsew', pady=2)

  OMCUploadLabel = tk.Button(optionsFrame, text="Uplaod Open Motor config",command=lambda:FileUpload.uploadConfig(popup, configs, 'Motor'))
  OMCUploadLabel.grid(row=9,column=0,sticky='nsew', pady=2)
  
  preSavedConfigLabel = tk.Button(optionsFrame, text="Upload complete preset",command=lambda: FileUpload.uploadConfig(popup, configs, 'All'))
  preSavedConfigLabel.grid(row=10,column=0,sticky='nsew', pady=2)

  propSaveLabel = tk.Button(optionsFrame, text="Save Propellant config",command=lambda: save_configs.saveCurrentConfigs(popup, 'Propellant', configs))
  propSaveLabel.grid(row=11,column=0,sticky='nsew', pady=2)

  grainSaveLabel = tk.Button(optionsFrame, text="Save Grain config",command=lambda: save_configs.saveCurrentConfigs(popup, 'Grains', configs))
  grainSaveLabel.grid(row=12,column=0,sticky='nsew', pady=2)

  NIUSaveLabel = tk.Button(optionsFrame, text="Save Nozzle Iterator Config",command=lambda: save_configs.saveCurrentConfigs(popup, 'Nozzle', configs))
  NIUSaveLabel.grid(row=13,column=0,sticky='nsew', pady=2)

  OMSaveLabel = tk.Button(optionsFrame, text="Save Open Motor config",command=lambda:  save_configs.saveCurrentConfigs(popup, 'Motor', configs))
  OMSaveLabel.grid(row=14,column=0,sticky='nsew', pady=2)

  saveConfigs = tk.Button(optionsFrame, text="Save All Current Configs",command=lambda: save_configs.saveCurrentConfigs(popup, 'All', configs))
  saveConfigs.grid(row=15,column=0,sticky='nsew', pady=2)

  ICSaveLabel = tk.Button(optionsFrame, text="Save Impulse Calculator config",command=lambda: save_configs.saveCurrentConfigs(popup, 'ImpulseCalculator', configs))
  ICSaveLabel.grid(row=16,column=0,sticky='nsew', pady=2)
  
# Standard Boiler plate to run the main function 
# Freezes main when subproccess is running as an exe
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()  # Required when using multiprocessing in PyInstaller on Windows

    # Prevent the GUI from starting in subprocesses when frozen into an .exe
    if sys.argv[0].endswith("OpenProp.exe") or sys.argv[0].endswith("OpenProp.py"):
        main()


