import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from datetime import datetime, timedelta

from parse import *

class FileGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual-Axis Graph Viewer")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.selected_vars = []  # Up to 2 selected variable names

        # Generate dummy data as [(x, y), ...] pairs
        base_time = datetime.strptime("11:23:00", "%H:%M:%S")
        self.dummy_data = [
            Dataset("Temperature", "C", [(base_time + timedelta(seconds=5 * i), 22 + 5 * math.sin(i / 2)) for i in range(10)]),
            Dataset("Current", "A", [(base_time + timedelta(seconds=5 * i), 8 + math.sin(i)) for i in range(10)]),
            Dataset("Voltage", "V", [(base_time + timedelta(seconds=5 * i), 12 if i % 2 == 0 else 15) for i in range(10)]),
            Dataset("Speed", "mph", [(base_time + timedelta(seconds=5 * i), 25 + 5 * math.log(i + 2)) for i in range(10)]),
        ]

        self.all_vars = [data.name for data in self.dummy_data]

        self.setup_ui()
        self.canvas = None

    def on_close(self):
        plt.close('all')  # Close any lingering matplotlib figures
        self.root.destroy()

    def setup_ui(self):
        # Open file button
        self.open_button = tk.Button(self.root, text="Open File", command=self.open_file)
        self.open_button.pack(pady=10)

        # Frame to hold plot and variable list
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Plot area
        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.pack(side="left", fill="both", expand=True)

        # Variable list area (hidden initially)
        self.var_frame = tk.Frame(self.main_frame)

        self.var_label = tk.Label(self.var_frame, text="Select up to 2 variables:")
        self.var_label.pack()

        self.var_listbox = tk.Listbox(self.var_frame, selectmode="multiple", exportselection=False)
        for var in self.all_vars:
            self.var_listbox.insert(tk.END, var)
        self.var_listbox.pack(pady=5)

        self.var_listbox.bind('<<ListboxSelect>>', self.on_variable_select)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open a file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            print(f"Selected file: {file_path}")
            try:
                with open(file_path, 'r') as file:
                    parse_file(file)
            except Exception as e:
                print(f"Failed to open file: {e}")
                return
            
            self.var_frame.pack(side="right", fill="y", padx=10)  # Show var list
            self.plot_data()
        else:
            print("No file selected.")

    def on_variable_select(self, event):
        selection = self.var_listbox.curselection()
        if len(selection) > 2:
            # Revert selection to last valid state
            for i in range(len(self.all_vars)):
                self.var_listbox.selection_clear(i)
            for var in self.selected_vars:
                idx = self.all_vars.index(var)
                self.var_listbox.selection_set(idx)
            messagebox.showwarning("Limit Exceeded", "Please select up to 2 variables.")
        else:
            self.selected_vars = [self.all_vars[i] for i in selection]
            print(f"Selected variables: {self.selected_vars}")
            self.plot_data()

    def plot_data(self):
        fig, ax1 = plt.subplots(figsize=(6, 4))
        ax2 = None

        if len(self.selected_vars) >= 1:
            data1 = next(d for d in self.dummy_data if d.name == self.selected_vars[0])
            x1, y1 = zip(*data1.data)
            ax1.plot(x1, y1, label=data1.name, color='tab:blue')
            ax1.set_ylabel(f"{data1.name} ({data1.unit})", color='tab:blue')
            ax1.tick_params(axis='y', labelcolor='tab:blue')

        if len(self.selected_vars) == 2:
            data2 = next(d for d in self.dummy_data if d.name == self.selected_vars[1])
            x2, y2 = zip(*data2.data)
            ax2 = ax1.twinx()
            ax2.plot(x2, y2, label=data2.name, color='tab:red')
            ax2.set_ylabel(f"{data2.name} ({data2.unit})", color='tab:red')
            ax2.tick_params(axis='y', labelcolor='tab:red')

        ax1.set_xlabel("Time")
        ax1.set_title("Dummy Data Plot")

        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        fig.autofmt_xdate()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileGraphApp(root)
    root.mainloop()
