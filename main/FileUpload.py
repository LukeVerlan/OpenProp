from tkinter import filedialog as fd 
import json
import tkinter as tk
import guiFunction

# @brief Uploads a configuration file and updates the configs dictionary.
# @param popup The popup window where the upload button is located.
# @param configs The dictionary containing the current configurations.
# @param type The type of configuration being uploaded (e.g., 'All', 'Grains', 'Motor', 'Nozzle', 'Propellant').
def uploadConfig(popup, configs, type):
	
		guiFunction.clearWidgetColumn(popup,1)
		guiFunction.createLabelFrame(popup, "Upload " + type + " config")

		frame = guiFunction.createBaseFrame(popup)

		uploadButton = tk.Button(frame, text='Upload', command=lambda:commitConfig(configs, frame, type))
		uploadButton.grid(row=0,column=0)

# @brief Commits the configuration from a file to the configs dictionary.
# @param configs The dictionary containing the current configurations.
# @param frame The frame where the upload button is located.
# @param type The type of configuration being uploaded (e.g., 'All', 'Grains', 'Motor', 'Nozzle', 'Propellant').
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

# @brief Adds the configuration from the uploaded file to the configs dictionary.
# @param configs The dictionary containing the current configurations.
# @param config The configuration dictionary loaded from the file.
# @param type The type of configuration being uploaded (e.g., 'All', 'Grains', 'Motor', 'Nozzle', 'Propellant').
def addToConfigs(localConfig, externalConfig, type):

  if type == 'All':
    localConfig["Grains"] = externalConfig["Grains"]
    localConfig["Motor"] = externalConfig["Motor"]
    localConfig["Nozzle"] = externalConfig["Nozzle"]
    localConfig["Propellant"] = externalConfig["Propellant"]
    localConfig["ImpulseCalculator"] = externalConfig[""]
  elif type == 'Grains':
    localConfig['Grains'] = externalConfig["Grains"]
  elif type == 'Motor':
    localConfig['Motor'] = externalConfig['Motor']
  elif type == 'Nozzle':
    localConfig['Nozzle'] = externalConfig['Nozzle']
  elif type == 'Propellant':
    localConfig['Propellant'] = externalConfig['Propellant']

# @brief Checks if the configuration dictionary has the required keys for the specified type.
# @param config The configuration dictionary to check.
# @param type The type of configuration being checked (e.g., 'All', 'Grains', 'Motor', 'Nozzle', 'Propellant').
# @return True if the configuration dictionary has the required keys, False otherwise.
def hasConfigs(config, type):
    if type == 'All':
        required_keys = ["Propellant", "Grains", "Motor", "Nozzle, ImpulseCalculator"]
    elif type == 'NozzleIterator':
        required_keys = ["Propellant", "Grains", "Motor", "Nozzle"]
    elif type == 'Grains':
        required_keys = ["Grains"]
    elif type == 'Propellant':
        required_keys = ["Propellant"]
    elif type == 'Nozzle':
        required_keys = ['Nozzle']
    elif type == 'Motor':
        required_keys = ['Motor']
    elif type == 'ImpulseCalculator':
        required_keys = ['ImpulseCalculator']
        
        
    return all(key in config for key in required_keys)

# @brief Converts the configuration dictionary to a JSON file and prompts the user to save it.
# @param cfg The configuration dictionary to convert.
# @param frame The frame where the save button is located.
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