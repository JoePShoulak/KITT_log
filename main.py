import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

from parse import *

class KITTLogGrapher: # TODO: Rename to Bonnie
    def __init__(self, root):
        self.root = root
        self.root.title("KITT Log Grapher")
        self.root.geometry("300x100")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.selected_vars = []
        self.all_vars = []
        self.dataset = []
        self.errors = []
        self.show_errors = tk.BooleanVar(value=False)

        self.canvas = None
        self.setup_ui()

    def style_axis(self, ax, with_grid=False):
        ax.set_facecolor("black")
        ax.tick_params(axis="both", colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
        if with_grid:
            ax.grid(True, color="gray")

    def on_close(self):
        plt.close('all')
        self.root.destroy()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root)

        self.open_button = ttk.Button(self.root, text="Open File", command=self.open_file)
        self.open_button.pack(expand=True)

        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.pack(side="left", fill="both", expand=True)

        self.var_frame = ttk.Frame(self.main_frame)
        self.date_label = ttk.Label(self.var_frame, text="")
        self.var_label = ttk.Label(self.var_frame, text="Select up to 2 variables:")
        self.var_listbox = tk.Listbox(self.var_frame, selectmode="multiple", exportselection=False)
        self.var_listbox.bind('<<ListboxSelect>>', self.on_variable_select)
        self.error_checkbox = ttk.Checkbutton(self.var_frame, text="Show Errors", variable=self.show_errors, command=self.plot_data)

    def prepare_window(self, file_path):
        self.all_vars = [data.name for data in self.dataset]
        self.var_listbox.delete(0, tk.END)

        for var in self.all_vars:
            self.var_listbox.insert(tk.END, var)

        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.date_label.config(text=parse_filename(file_path))
        self.date_label.pack(pady=(0, 5))

        self.open_button.pack_forget()
        self.open_button.pack(in_=self.var_frame, pady=(0, 5))

        self.var_label.pack()
        self.var_listbox.pack(pady=5)

        self.error_checkbox.pack(pady=5)

        self.var_frame.pack(side="right", fill="y", padx=10)
        self.root.geometry("1200x900")

        self.plot_data()

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Open a file", filetypes=[("Text Files", "*.txt")] )
        if not file_path: return

        try:
            with open(file_path, 'r') as file:
                self.dataset, self.errors = parse_file(file)

                if len(self.dataset) == 0:
                    messagebox.showwarning("File Error", "No data in the file. Is this a valid log file?")
                    return

        except Exception:
            messagebox.showwarning("File Error", "Invalid data. Is this a valid log file?")
            return

        self.prepare_window(file_path)

    def on_variable_select(self, _):
        selection = self.var_listbox.curselection()

        if len(selection) > 2:
            for i in range(len(self.all_vars)):
                self.var_listbox.selection_clear(i)

            for var in self.selected_vars:
                idx = self.all_vars.index(var)
                self.var_listbox.selection_set(idx)

            messagebox.showwarning("Limit Exceeded", "Please select up to 2 variables.")
        else:
            self.selected_vars = [self.all_vars[i] for i in selection]
            self.plot_data()

    def update_plot(self, idx, ax1, x_limits):
        dataset = next(d for d in self.dataset if d.name == self.selected_vars[idx])
        color = 'tab:blue' if idx == 0 else 'tab:red'
        ax = ax1 if idx == 0 else ax1.twinx()
        if idx == 1:
            self.style_axis(ax)

        x, y = zip(*dataset.data)
        ax.plot(x, y, label=dataset.name, color=color)
        ax.set_ylabel(f"{dataset.name} - {dataset.unit}", color=color, labelpad=10)
        ax.tick_params(axis='y', labelcolor=color)
        x_limits.extend([min(x), max(x)])

    def plot_data(self):
        fig, ax1 = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("black")
        self.style_axis(ax1, with_grid=True)
        x_limits = []

        if len(self.selected_vars) >= 1:
            self.update_plot(0, ax1, x_limits)
            
        if len(self.selected_vars) == 2:
            self.update_plot(1, ax1, x_limits)

        if self.show_errors.get():
            error_times = [err_time for err_time, _ in self.errors]

            for err_time, message in self.errors:
                ax1.axvline(x=err_time, color='red', linestyle='dotted', linewidth=1)
                ax1.text(err_time, 1.02, message, rotation=45, transform=ax1.get_xaxis_transform(), color='red', fontsize=8, ha='left', va='bottom')

            if not x_limits and error_times:
                x_limits.extend([min(error_times), max(error_times)])

        if x_limits:
            margin = timedelta(seconds=5)
            ax1.set_xlim(x_limits[0] - margin, x_limits[1] + margin)

        ax1.set_xlabel("Time", color="white")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        fig.autofmt_xdate()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = KITTLogGrapher(root)
    root.mainloop()
