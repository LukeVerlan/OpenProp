from tkinter import filedialog as fd 
import json
import tkinter as tk
import guiFunction

def uploadConfig(popup, configs, type):
	
		guiFunction.clearWidgetColumn(popup,1)
		guiFunction.createLabelFrame(popup, "Upload " + type + " config")

		frame = guiFunction.createBaseFrame(popup)

		uploadButton = tk.Button(frame, text='Upload', command=lambda:commitConfig(configs, frame, type))
		uploadButton.grid(row=0,column=0)

def commitConfig(configs, frame, type):
    configPath = fd.askopenfilename()
    with open(configPath, "r") as f:
        config = json.load(f)

    validLabel = tk.Label(frame, text="Valid Config")
    invalidLabel = tk.Label(frame, text="Invalid Config")

    if hasConfigs(config, type):
        validLabel.grid(row=0, column=1)
        addToConfigs(configs, config, type)
        print(configs)
    else:
        invalidLabel.grid(row=0, column=1)


def addToConfigs(configs, config, type):

  if type == 'All':
    configs["Grains"] = config["Grains"]
    configs["Motor"] = config["Motor"]
    configs["Nozzle"] = config["Nozzle"]
    configs["Propellant"] = config["Propellant"]
  elif type == 'Grains':
    configs['Grains'] = config["Grains"]
  elif type == 'Motor':
    configs['Motor'] = config['Motor']
  elif type == 'Nozzle':
    configs['Nozzle'] = config['Nozzle']
  elif type == 'Propellant':
    configs['Propellant'] = config['Propellant']

def hasConfigs(config, type):
    if type == 'All':
        required_keys = ["Propellant", "Grains", "Motor", "Nozzle"]
    elif type == 'Grains':
        required_keys = ["Grains"]
    elif type == 'Propellant':
        required_keys = ["Propellant"]
    elif type == 'Nozzle':
        required_keys = ['Nozzle']
    elif type == 'Motor':
        required_keys = ['Motor']
        
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