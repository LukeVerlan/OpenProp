# MAIN
#
# Handles user input are calls upon sub files depending on what the user wants to do 

# File handling libraries
import os 
from pathlib import Path
import subprocess as sub
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# GUI library
import tkinter as tk
from tkinter import ttk 
from tkinter import filedialog as fd 


def main(): 

  # initialize main GUI page
  gui = tk.Tk()
  gui.title('OpenProp')

  gui.rowconfigure(0, weight=1)
  gui.columnconfigure(0, weight=1)
  gui.columnconfigure(1, weight=1)

  # Functions
  functionsFrame = ttk.Frame(gui)
  functionsFrame.grid(row=0, column=0, columnspan=1, sticky="nsew")

  functionsFrame.rowconfigure([1, 2, 3, 4], weight=1)  # Allow buttons to expand vertically
  functionsFrame.columnconfigure(0, weight=1)         # Allow buttons to fill horizontally

  functionsLabel = tk.Label(functionsFrame, text="Functions")
  functionsLabel.grid(row=0, column=0, sticky="nsew")

  nozzleBtn = ttk.Button(functionsFrame, text="Nozzle Iterator",command=runNozzleIterator)
  nozzleBtn.grid(row= 1, column=0, sticky="nsew")

  impulseBtn = ttk.Button(functionsFrame, text="Impulse Calculator", command=runImpulseCalc)
  impulseBtn.grid(row=2, column=0, sticky="nsew")

  curativeBtn = ttk.Button(functionsFrame, text="Curative Calculator",command=runCurativeCalculator)
  curativeBtn.grid(row=3, column=0, sticky="nsew")

  seriesBtn = ttk.Button(functionsFrame, text="Nozzle Iterator & Impulse Calculator",command=runSeries)
  seriesBtn.grid(row=4,column=0, sticky="nsew")

  # Configurations 
  configsFrame = tk.Frame(gui)
  configsFrame.grid(row=0,column=1,sticky="nsew")

  configsFrame.rowconfigure([1, 2, 3, 4], weight=1)
  configsFrame.columnconfigure(0, weight=1)

  configsLabel = tk.Label(configsFrame, text="Config Creators")
  configsLabel.grid(row=0, column=0, sticky = "nsew")

  nozzleConfigBtn = ttk.Button(configsFrame, text="Nozzle Iterator Config",command=createNIConfig)
  nozzleConfigBtn.grid(row= 1, column=0, sticky="nsew")

  impulseConfigBtn = ttk.Button(configsFrame, text="Impulse Calculator Config", command=createImpulseConfig)
  impulseConfigBtn.grid(row=2, column=0, sticky="nsew")

  curativeConfigBtn = ttk.Button(configsFrame, text="Curative Calculator Config",command=createCurativeConfig)
  curativeConfigBtn.grid(row=3, column=0, sticky="nsew")

  seriesConfigBtn = ttk.Button(configsFrame, text="Nozzle Iterator & Impulse Calculator Config",command=createSeriesConfig)
  seriesConfigBtn.grid(row=4,column=0, sticky="nsew")

  gui.mainloop()

def runNozzleIterator():
  config = fd.askopenfilename()
  if config is not None:  
    sub.run([sys.executable, "NozzleIterator/NozzleIterator.py", config], check=True)

def createNIConfig():
  pass

def createImpulseConfig():
  pass

def createCurativeConfig():
  pass

def createSeriesConfig():
  pass
  
def runImpulseCalc():
  pass

def runSeries():
  pass

def runCurativeCalculator():
  pass


if __name__ == '__main__':
  main()