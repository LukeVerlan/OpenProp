import  matplotlib.pyplot as plt
import  tkinter as tk
from    tkinter import filedialog as fd
import  PIL 
import  NozzleIterator.NozzleIterator as NozzleIterator # System directory runs out of file openprop.py is ran
from    NozzleIterator.SimulationUI   import SimulationUI
import  copy
import FileUpload


def run_gui(gui, configs):
    import threading
    import gc
    
    stop_event = threading.Event()

    def on_popup_close():
        stop_event.set()     # signal worker to stop
        plt.close('all')
        popup.destroy()

    popup = tk.Toplevel()
    popup.transient(gui)  # Keep it on top of main window
    popup.grab_set()
    popup.protocol("WM_DELETE_WINDOW", on_popup_close)

    popup.geometry("1300x720")
    popup.resizable(False, False)

    OPimDir = FileUpload.resource_path("./OpenPropLogo.png")
    OPim = PIL.Image.open(OPimDir)
    resizedOPim = OPim.resize((200, 625))
    tk_OPim = PIL.ImageTk.PhotoImage(resizedOPim)

    labelFrame = tk.Frame(popup, borderwidth=1, relief="solid")
    labelFrame.grid(row=0, column=0, sticky='nsew')
    labelFrame.columnconfigure(0, weight=1)
    labelFrame.rowconfigure([0, 1], weight=1)

    logoFrame = tk.Frame(popup, borderwidth=1, relief='solid')
    logoFrame.grid(row=1, column=0, sticky='nsw')
    logoLabel = tk.Label(logoFrame, image=tk_OPim)
    logoLabel.grid(row=0, column=0, sticky='nsew')
    logoLabel.image = tk_OPim

    graphsFrame = tk.Frame(popup)
    graphsFrame.grid(row=0, column=1, sticky='nsew', rowspan=2)
    graphsFrame.rowconfigure([0, 1, 2, 3], weight=1)

    functionsFrame = tk.Frame(popup, borderwidth=1, relief='solid')
    functionsFrame.grid(row=0, column=2, sticky='nsew', rowspan=2)
    functionsFrame.columnconfigure(0, weight=1)

    label = tk.Label(labelFrame, text="Nozzle Iterator Configuration", font=('Arial', 10, 'bold'))
    label.grid(row=0, column=0, pady=1, sticky='nsew')

    # Exit button with cleanup
    exitButton = tk.Button(labelFrame, text="exit", command=on_popup_close, borderwidth=1, relief='solid')
    exitButton.grid(row=3, column=0, pady=1, sticky='nsew')

    isValidLabel = tk.Label(labelFrame, text="")
    isValidLabel.grid(row=1, column=0, pady=2, padx=2, sticky='nsew')

    runButton = tk.Button(labelFrame, text="Run Nozzle Iterator", state='disabled')
    runButton.grid(row=2, column=0, sticky='nsew')

    placeholder_canvas = tk.Canvas(graphsFrame, width=750, height=440, highlightthickness=0)
    placeholder_canvas.grid(row=1, column=0, sticky='nsew', pady=2, columnspan=2)
    text_id = placeholder_canvas.create_text(375, 220, text="No simulation results yet", font=('Arial', 16), fill='gray')

    simSuccesslabel = tk.Label(graphsFrame, text="")
    simSuccesslabel.grid(row=0, column=0, sticky='ew', columnspan=2)

    simResultsPeak = tk.Label(graphsFrame, text="", justify='left')
    simResultsPeak.grid(row=2, column=0, sticky='nsew', pady=2)

    simResultsGeneral = tk.Label(graphsFrame, text="", justify='left')
    simResultsGeneral.grid(row=2, column=1, sticky='nsew', pady=2)

    nozzleResults = tk.Label(graphsFrame, text="", borderwidth=1, relief='solid', justify='left')
    nozzleResults.grid(row=3, column=0, sticky='nsew', pady=2, columnspan=2)

    printAsCSVbutton = tk.Button(functionsFrame, text='Save Thrust Curve as CSV', borderwidth=1, relief='solid', state='disabled')
    printAsCSVbutton.grid(row=0, column=0, sticky='nsew')

    saveButton = tk.Button(functionsFrame, text='Save Nozzle Statistics as txt', borderwidth=1, relief='solid', state='disabled')
    saveButton.grid(row=1, column=0, sticky='nsew', pady=2)

    configText = tk.Text(functionsFrame, height=30, width=40, wrap='word', borderwidth=1, relief='solid')
    configText.grid(row=2, column=0, sticky='nsew', pady=(10, 0))

    scroll = tk.Scrollbar(functionsFrame, command=configText.yview)
    scroll.grid(row=2, column=1, sticky='ns', pady=(10, 0))
    configText.config(yscrollcommand=scroll.set)
    configText.config(state='disabled')

    simGraph = None  # To hold the simulation graph label widget

    if FileUpload.hasConfigs(configs, 'NozzleIterator'):
        isValidLabel.config(text="Valid Config Found", fg="green")
        runButton.config(state='normal', command=lambda: runNozzleIterator())

        unit_map = {
            "minDia": "m",
            "maxDia": "m",
            "minLen": "m",
            "maxLen": "m",
            "exitHalf": "deg",
            "SlagCoef": "(m·Pa)/s",
            "ErosionCoef": "s/(m·Pa)",
            "Efficiency": "",
            "nozzleDia": "m",
            "nozzleLength": "m",
            "minHalfConv": "deg",
            "maxHalfConv": "deg",
            "iteration_step_size": "m",
            "preference": "",
            "parallel_mode": "",
            "iteration_threads": "",
            "exitDia": "m"
        }

        configText.config(state='normal')
        configText.delete('1.0', tk.END)
        configText.insert(
            '1.0',
            '\n'.join([
                f"{key} : {value} {unit_map.get(key, '')}".strip()
                for key, value in configs["Nozzle"].items()
            ])
        )
        configText.config(state='disabled')

    else:
        isValidLabel.config(text='Invalid Config', fg="red")
        runButton.config(state='disabled')

    def runNozzleIterator():
        nonlocal simGraph
        placeholder_canvas.itemconfig(text_id, text='Running...')
        popup.update()

        def worker():
            if stop_event.is_set():
                return
            NIconfig = copy.deepcopy(configs)
            simRes, nozzleDict, nozzleIteratorParams = NozzleIterator.main(NIconfig)
            if not stop_event.is_set():
                popup.after(0, update_gui, simRes, nozzleDict, nozzleIteratorParams)

        def update_gui(simRes, nozzleDict, nozzleIteratorParams):
            if not popup.winfo_exists():
                return  # window was closed, skip GUI update
            nonlocal simGraph
            result = SimulationUI(simRes, nozzleDict, nozzleIteratorParams)

            if result is not None:
                simImage = result.plotSim()
                resized = simImage.resize((740, 440))
                tk_simImage = PIL.ImageTk.PhotoImage(resized)

                simSuccesslabel.config(text="Simulation Results")

                # Destroy old image widget and clear reference
                if simGraph is not None:
                    simGraph.destroy()
                    simGraph.image = None
                    simGraph = None

                simGraph = tk.Label(graphsFrame, image=tk_simImage, borderwidth=1, relief='solid')
                simGraph.grid(row=1, column=0, sticky='nsew', pady=2, columnspan=2)
                simGraph.image = tk_simImage

                simResultsPeak.config(text=result.peakValues())
                simResultsGeneral.config(text=result.generalValues())
                nozzleResults.config(text=result.nozzleStatistics())

                printAsCSVbutton.config(state='normal', command=lambda: result.exportThrustCurve(fd.asksaveasfilename()))
                saveButton.config(state='normal', command=lambda: result.exportNozzleStats(fd.asksaveasfilename()))

                placeholder_canvas.itemconfig(text_id, text='')  # Clear placeholder text

                plt.close('all')  # Close matplotlib figures

                gc.collect()  # Force garbage collection

            else:
                simSuccesslabel.config(text="No valid nozzle found, please change your settings")
                placeholder_canvas.itemconfig(text_id, text="No simulation results yet")

        threading.Thread(target=worker, daemon=True).start()
