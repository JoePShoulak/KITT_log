import tkinter as tk

def on_click():
    print("Clicked!")

# Create the main window
root = tk.Tk()
root.title("Simple Button")
root.geometry("200x100")

# Create a button
button = tk.Button(root, text="Click Me", command=on_click)
button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
