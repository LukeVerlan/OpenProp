import tkinter as tk 
from tkinter import ttk
import configureDictionaries

# @brief Clears all widgets in a specific column of the given frame.
# @param frame The frame from which widgets will be cleared.
# @param col The column index from which widgets will be cleared.
def clearWidgetColumn(frame, col):
  for widget in frame.winfo_children():
    info = widget.grid_info()
    if 'column' in info and info['column'] == col:
      widget.destroy()

# @brief Clears all widgets in the given frame.
# @param frame The frame from which all widgets will be cleared.  
# @return The cleared frame.
def clear(frame):

  for widget in frame.winfo_children():
      widget.destroy()

  return frame

# @brief Creates a settings page with labeled entry boxes and a save button.
# @param configs The dictionary containing the current configurations.
# @param labelName The name of the settings page.
# @param fields A list of field names for the entry boxes.
# @param popup The popup window where the settings page will be created.
# @param dropDown Optional dictionary for dropdown menus.
# @param defaults Optional dictionary for default values in the entry boxes.
def createSettingsPage(configs, labelName, fields, popup, dropDown=None, defaults=None):

  frame = createBaseFrame(popup)
  createLabelFrame(popup,labelName)

  entries = createLabledEntryBoxes(frame, fields, dropDown, defaults)

  saveButton = tk.Button(frame, text="Save Config", command=lambda: saveEntries(configs, entries, labelName, None, frame),
                        borderwidth=1, relief="solid")
  
  saveButton.grid(row=9,column=5, padx=4, pady=4, sticky = 'se')

# @brief Creates a base frame for the settings page.
# @param popup The popup window where the base frame will be created.
# @return The created base frame.
def createBaseFrame(popup):

  frame = tk.Frame(popup, borderwidth=1, relief="solid")
  frame.grid(row=1, column=1, sticky= 'nsew')

  frame.rowconfigure([0,1,2,3], weight=1)
  frame.columnconfigure([0,1,2,3], weight=1)

  return frame

# @brief Creates a labeled frame in the popup window.
# @param popup The popup window where the labeled frame will be created.
# @param labelName The name of the labeled frame.
# @return The created labeled frame.
def createLabelFrame(popup, labelName):

  labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
  labelFrame.grid(row=0,column=1, sticky='nsew')

  frameLabel = tk.Label(labelFrame, text=labelName, anchor="center", justify="center")
  frameLabel.grid(row=0, column=0, sticky = 'nsew')

  labelFrame.columnconfigure(0, weight=1)

  return labelFrame

# @brief Creates labeled entry boxes in the given parent frame.
# @param parent The parent frame where the entry boxes will be created.
# @param fields A list of field names for the entry boxes.
# @param dropDown Optional dictionary for dropdown menus.
# @param defaults Optional dictionary for default values in the entry boxes.
# @return A dictionary containing the created entry boxes and dropdown menus.
def createLabledEntryBoxes(parent, fields, dropDown=None, defaults=None):

  entries = {}
  j = 1
  currIndex = 0 
  for i, field in enumerate(fields):

    # Wrap every 4 columns
    if i > 3:
      i = i % 4
      if i % 4 == 0:
        j += 2 

    label = tk.Label(parent, text=field)
    label.grid(row=j,column=i,sticky='nsew', padx=14, pady=6)

    entry = tk.Entry(parent)

    if defaults and field in defaults:
      entry.insert(0, str(defaults[field]))

    entry.grid(row=j+1, column=i, sticky='nsew', padx=14, pady=4)
    
    entries[field] = entry
    if dropDown is not None and currIndex == len(fields) - 1:
      dropCount = 0
      for key in dropDown:

        label = tk.Label(parent, text=key)
        label.grid(row=j+2,column=dropCount, sticky='nsew', padx=14, pady=6)

        comboBox = ttk.Combobox(parent, values=dropDown[key])
        comboBox.grid(row=j+3,column=dropCount,sticky='nsew', padx=14, pady=6)

        dropCount +=1

        if defaults and key in defaults:
          val = defaults[key]
          if isinstance(val, bool):
            comboBox.set("True" if val else "False")
          else:
            comboBox.set(str(val))
        else:
          comboBox.set("Select Preferece")

        entries[key] = comboBox

    currIndex += 1

  return entries

# @brief Saves the entries from the entry boxes to the configs dictionary.
# @param configs The dictionary containing the current configurations.
# @param entries The dictionary containing the entry boxes.
# @param configName The name of the configuration being saved.
# @param type The type of configuration being saved (e.g., 'Grains', 'Motor', 'Nozzle', 'Propellant').
def saveEntries(configs, entries, configName, type, frame):
    
    entryVals = {}
    for field in entries.keys():
      entryVals[field] = entries[field].get()

    if configureDictionaries.verifyEntryBoxes(entryVals):
      if configName == "Propellant Config":
        configureDictionaries.configurePropellantDict(configs, entryVals)
      elif configName.startswith("OpenMotor"):
        configureDictionaries.configureOMDict(configs, entryVals)
      elif configName == "Nozzle Iterator":
        configureDictionaries.configureNIDict(configs, entryVals)
      elif configName == "Grain":
        configureDictionaries.configureGrainDict(configs, entryVals, type)
      
      successLabel = tk.Label(frame, text ='Save Successful')
      successLabel.grid(row = 10, column=5, sticky= 'se')
    else:
      failureLabel = tk.Label(frame, text ='Invalid Entries ')
      failureLabel.grid(row = 10, column=5, sticky= 'se')

    print(configs)
