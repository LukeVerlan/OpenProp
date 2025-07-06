# MAIN
#
# Handles user input are calls upon sub files depending on what the user wants to do 

# File handling libraries
import os 
from pathlib import Path

# GUI library
import tkinter as tk
from tkinter import ttk 


def main(): 

  gui = tk.Tk()
  gui.title('OpenProp')

  frame = tk.Frame(gui)
  frame.grid(row=0, column=0, columnspan=1, sticky="nsew",)

  nozzleBtn = tk.Button(frame, text="Nozzle Iterator",command=runNozzleIterator)
  nozzleBtn.grid(row= 0, column=0, sticky="ew")

  impulseBtn = tk.Button(frame, text="Impulse Calculator", command=runImpulseCalc)
  impulseBtn.grid(row=1, column=0, sticky="ew")

  curativeBtn = tk.Button(frame, text="Curative Calculator",command=runCurativeCalculator)
  curativeBtn.grid(row=2, column=0, sticky="ew")

  seriesBtn = tk.Button(frame, text="Nozzle Iterator & Impulse Calculator",command=runSeries)
  seriesBtn.grid(row=3,column=0, sticky="ew")

  gui.mainloop()

def runNozzleIterator():
  pass

def runImpulseCalc():
  pass

def runSeries():
  pass

def runCurativeCalculator():
  pass


if __name__ == '__main__':
  main()