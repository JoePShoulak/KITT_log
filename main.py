import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math

class FileGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual-Axis Graph Viewer")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.selected_vars = []  # Up to 2 selected variable names
        self.all_vars = ["Temperature", "Pressure", "Humidity", "Wind Speed", "Voltage"]
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
            # Placeholder — you'd parse the file here
            self.var_frame.pack(side="right", fill="y", padx=10)  # Show var list
            self.plot_dummy_data()
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
            self.plot_dummy_data()

    def plot_dummy_data(self):
        x = list(range(1, 11))  # x = 1 to 10 for more curve-friendly behavior
        dummy_data = {
            "Temperature": [22 + 5 * math.sin(i / 2) for i in x],              # Sinusoidal
            "Pressure": [100 * (1.05 ** i) for i in x],                        # Exponential
            "Humidity": [25 + 7 * i for i in x],                               # Linear
            "Wind Speed": [3 + 10 * math.log(i + 1) for i in x],               # Logarithmic
            "Voltage": [12 if i % 2 == 0 else 15 for i in x],                  # Square wave
        }

        fig, ax1 = plt.subplots(figsize=(6, 4))
        ax2 = None

        if len(self.selected_vars) >= 1:
            y1 = dummy_data[self.selected_vars[0]]
            ax1.plot(x, y1, label=self.selected_vars[0], color='tab:blue')
            ax1.set_ylabel(self.selected_vars[0], color='tab:blue')
            ax1.tick_params(axis='y', labelcolor='tab:blue')

        if len(self.selected_vars) == 2:
            ax2 = ax1.twinx()
            y2 = dummy_data[self.selected_vars[1]]
            ax2.plot(x, y2, label=self.selected_vars[1], color='tab:red')
            ax2.set_ylabel(self.selected_vars[1], color='tab:red')
            ax2.tick_params(axis='y', labelcolor='tab:red')

        ax1.set_xlabel("Time (arbitrary units)")
        ax1.set_title("Dummy Data Plot")

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileGraphApp(root)
    root.mainloop()