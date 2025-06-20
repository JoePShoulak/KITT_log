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
        self.root.geometry("1200x900")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.selected_vars = []  # Up to 2 selected variable names
        self.all_vars = []
        self.dataset = []
        self.errors = []
        self.show_errors = tk.BooleanVar(value=False)

        self.setup_ui()
        self.canvas = None

    def on_close(self):
        plt.close('all')  # Close any lingering matplotlib figures
        self.root.destroy()

    def setup_ui(self):
        # Frame to hold plot and variable list
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Plot area
        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.pack(side="left", fill="both", expand=True)

        # Variable list area (hidden initially)
        self.var_frame = tk.Frame(self.main_frame)

        # Open file button (now outside var_frame and above it)
        self.open_button = tk.Button(self.main_frame, text="Open File", command=self.open_file)
        self.open_button.pack(side="right", anchor="n", padx=10, pady=(0, 5))

        self.date_label = tk.Label(self.var_frame, text="")
        self.date_label.pack(pady=(0, 5))

        self.var_label = tk.Label(self.var_frame, text="Select up to 2 variables:")
        self.var_label.pack()

        self.var_listbox = tk.Listbox(self.var_frame, selectmode="multiple", exportselection=False)
        self.var_listbox.pack(pady=5)
        self.var_listbox.bind('<<ListboxSelect>>', self.on_variable_select)

        # Error checkbox
        self.error_checkbox = tk.Checkbutton(self.var_frame, text="Show Errors", variable=self.show_errors, command=self.plot_data)
        self.error_checkbox.pack(pady=5)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open a file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.")]
        )
        if file_path:
            print(f"Selected file: {file_path}")
            try:
                with open(file_path, 'r') as file:
                    self.dataset, self.errors = parse_file(file)
            except Exception as e:
                print(f"Failed to open file: {e}")
                return

            self.all_vars = [data.name for data in self.dataset]
            self.var_listbox.delete(0, tk.END)
            for var in self.all_vars:
                self.var_listbox.insert(tk.END, var)

            # Extract date from filename
            try:
                filename = file_path.split("/")[-1]
                timestamp = filename.split("_")[1][:4]  # MMDD
                month = timestamp[:2]
                day = timestamp[2:4]
                self.date_label.config(text=f"Date: {month}/{day}")
            except:
                self.date_label.config(text="")

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
        x_limits = []

        if len(self.selected_vars) >= 1:
            data1 = next(d for d in self.dataset if d.name == self.selected_vars[0])
            x1, y1 = zip(*data1.data)
            ax1.plot(x1, y1, label=data1.name, color='tab:blue')
            ax1.set_ylabel(f"{data1.name} - {data1.unit}", color='tab:blue', labelpad=10)
            ax1.tick_params(axis='y', labelcolor='tab:blue')
            x_limits.extend([min(x1), max(x1)])

        if len(self.selected_vars) == 2:
            data2 = next(d for d in self.dataset if d.name == self.selected_vars[1])
            x2, y2 = zip(*data2.data)
            ax2 = ax1.twinx()
            ax2.plot(x2, y2, label=data2.name, color='tab:red')
            ax2.set_ylabel(f"{data2.name} - {data2.unit}", color='tab:red', labelpad=10)
            ax2.tick_params(axis='y', labelcolor='tab:red')
            x_limits.extend([min(x2), max(x2)])

        if self.show_errors.get():
            error_times = [err_time for err_time, _ in self.errors]
            for err_time, message in self.errors:
                ax1.axvline(x=err_time, color='red', linestyle='dotted', linewidth=1)
                ax1.text(err_time, 1.02, message, rotation=45, transform=ax1.get_xaxis_transform(),
                         color='red', fontsize=8, ha='left', va='bottom')
            if not x_limits:
                x_limits.extend([min(error_times), max(error_times)])

        if x_limits:
            margin = timedelta(seconds=5)
            ax1.set_xlim(x_limits[0] - margin, x_limits[1] + margin)

        ax1.set_xlabel("Time")
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
