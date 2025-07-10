from tkinter import filedialog as fd 
import json
import tkinter as tk
import guiFunction

def uploadCompleteConfig(popup):

  labelFrame = guiFunction.createLabelFrame(popup, "Upload Complete config")

  frame = guiFunction.createBaseFrame(popup)

  uploadButton = tk.Button(frame, text='Upload', command=lambda:commitConfig(frame, 'All'))
  uploadButton.grid(row=0,column=0)

def commitConfig(configs, frame, type):
    configPath = fd.askopenfilename()
    with open(configPath, "r") as f:
        config = json.load(f)

    validLabel = tk.Label(frame, text="Valid Config")
    invalidLabel = tk.Label(frame, text="Invalid Config")

    if type == 'All':
        if has_all_top_configs(config):
            validLabel.grid(row=0, column=1)
            addToConfigs(config, type)
        else:
            invalidLabel.grid(row=0, column=1)

def addToConfigs(configs, config, type):

  if type == 'All':
    configs["Grains"] = config["Grains"]
    configs["Motor"] = config["Motor"]
    configs["Nozzle"] = config["Nozzle"]
    configs["Propellant"] = config["Propellant"]

def has_all_top_configs(config):
    required_keys = ["Propellant", "Grains", "Nozzle", "Motor"]
    return all(key in config for key in required_keys)

def cfgToJson(cfg,frame):
    # Prompt user to select save location
    file_path = fd.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Save Config As"
    )

    validLabel = tk.Label(frame, text="Successfully Saved")
    invalidLabel = tk.Label(frame,text="Failed to Save")

    if file_path:
        try:
            with open(file_path, 'w') as f:
                json.dump(cfg, f, indent=4)
            validLabel.grid(row=0, column=1)
        except Exception as e:
            invalidLabel.grid(row=0, column=1)