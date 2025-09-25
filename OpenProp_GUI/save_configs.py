import guiFunction
import FileUpload
import tkinter as tk

def saveCurrentConfigs(popup, type, configs):

  guiFunction.clearWidgetColumn(popup, 1)

  guiFunction.createLabelFrame(popup, "Save " + type + " Settings")
  frame = guiFunction.createBaseFrame(popup)
  
  frame.rowconfigure(0,weight=1)

  if FileUpload.hasConfigs(configs, type):
    if type == 'All':
      cfg = configs
    elif type == 'Grains': 
      cfg = configs['Grains']
    elif type == 'Propellant':
      cfg = configs['Propellant']

    elif type == 'Motor':
      cfg = configs['Motor']
    elif type == 'Nozzle':
      cfg = configs['Nozzle']

    elif type == 'ImpulseCalculator':
      cfg = configs['ImpulseCalculator']

    saveButton = tk.Button(frame, text='Save', command=lambda:FileUpload.cfgToJson(cfg, frame))
    saveButton.grid(row=0,column=0, sticky="ew")
  else:
    invalidLabel = tk.Label(frame,text= type + " Config Not Found")
    invalidLabel.grid(row=0, column=0, sticky='ew')