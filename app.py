import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class NozzlePathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nozzle Path Planner")
        self.style = ttk.Style("flatly")  # You can choose different themes here

        # Data storage
        self.points = []  # Stores tuples of (x, y)
        self.spray_actions = []  # Stores 'Start', 'Stop', or 'Resume'
        self.axis_values = []  # Stores tuples of (A, B)
        self.corners = []  # Stores corner points
        self.shape_drawn = False  # Flag to check if shape is drawn

        self.create_widgets()
        self.setup_plot()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Left frame for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        # Frame for corner inputs
        corner_frame = ttk.LabelFrame(control_frame, text="Shape Corners", padding=10, bootstyle="primary")
        corner_frame.pack(fill=X, pady=10)

        # Corner entries
        self.corner_entries = []
        for i in range(4):
            frame = ttk.Frame(corner_frame)
            frame.pack(fill=X, pady=5)
            ttk.Label(frame, text=f"Corner {i+1} (X, Y):", width=15).pack(side=LEFT)
            x_entry = ttk.Entry(frame, width=10)
            x_entry.pack(side=LEFT, padx=5)
            y_entry = ttk.Entry(frame, width=10)
            y_entry.pack(side=LEFT, padx=5)
            self.corner_entries.append((x_entry, y_entry))

        # Draw shape button
        self.draw_shape_button = ttk.Button(corner_frame, text="Draw Shape", command=self.draw_shape, bootstyle="success")
        self.draw_shape_button.pack(pady=5, fill=X)

        # Frame for point controls
        point_frame = ttk.LabelFrame(control_frame, text="Point Controls", padding=10, bootstyle="info")
        point_frame.pack(fill=X, pady=10)

        # Spray action selection
        ttk.Label(point_frame, text="Spray Action:").pack(anchor=W)
        self.spray_action_var = tk.StringVar(value="Start")
        action_options = ["Start", "Stop", "Resume"]
        self.spray_action_menu = ttk.OptionMenu(point_frame, self.spray_action_var, "Start", *action_options)
        self.spray_action_menu.pack(fill=X, pady=5)

        # Instruction label
        ttk.Label(point_frame, text="Click on the plot to add points.", foreground="gray").pack(anchor=W, pady=5)

        # Clear and generate buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=X, pady=10)

        self.clear_button = ttk.Button(button_frame, text="Clear All", command=self.clear_all, bootstyle="danger")
        self.clear_button.pack(side=LEFT, expand=True, fill=X, padx=5)

        self.generate_gcode_button = ttk.Button(button_frame, text="Generate G-code", command=self.generate_gcode, bootstyle="warning")
        self.generate_gcode_button.pack(side=LEFT, expand=True, fill=X, padx=5)

        # G-code output
        gcode_frame = ttk.LabelFrame(control_frame, text="Generated G-code", padding=10, bootstyle="secondary")
        gcode_frame.pack(fill=BOTH, expand=True, pady=10)

        self.gcode_output = tk.Text(gcode_frame, height=20)
        self.gcode_output.pack(fill=BOTH, expand=True)

    def setup_plot(self):
        # Right frame for plot
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        # Matplotlib figure and canvas
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("X Axis")
        self.ax.set_ylabel("Y Axis")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def draw_shape(self):
        try:
            # Retrieve corner points
            self.corners = []
            for x_entry, y_entry in self.corner_entries:
                x = float(x_entry.get())
                y = float(y_entry.get())
                self.corners.append((x, y))

            # Clear previous plot
            self.clear_plot()

            # Draw shape
            x_vals, y_vals = zip(*self.corners)
            self.ax.plot(x_vals + (x_vals[0],), y_vals + (y_vals[0],), 'g-', linewidth=2)
            self.canvas.draw()

            self.shape_drawn = True

        except ValueError:
            self.show_error("Please enter valid numeric values for all corner points.")

    def on_click(self, event):
        if self.shape_drawn and event.inaxes is not None:
            x, y = event.xdata, event.ydata
            spray_action = self.spray_action_var.get()

            # If action is 'Start' or 'Resume', prompt for A and B values
            if spray_action in ['Start', 'Resume']:
                a, b = self.prompt_axis_values()
                if a is None or b is None:
                    return  # User canceled input

                self.axis_values.append((a, b))
            else:
                # For 'Stop' action, A and B default to 0
                self.axis_values.append((0, 0))

            # Store point and action
            self.points.append((x, y))
            self.spray_actions.append(spray_action)

            # Plot point
            self.ax.plot(x, y, 'ro')
            self.ax.annotate(f"{spray_action}\nA:{self.axis_values[-1][0]} B:{self.axis_values[-1][1]}",
                             (x, y), textcoords="offset points", xytext=(5,5), ha='left', fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))

            # Draw path lines
            if len(self.points) > 1:
                x_vals, y_vals = zip(*self.points)
                self.ax.plot(x_vals, y_vals, 'b--', linewidth=1)

            self.canvas.draw()

    def prompt_axis_values(self):
        """Prompt user to input A and B axis values."""
        dialog = ttk.Toplevel(self.root)
        dialog.title("Enter A and B Axis Values")
        dialog.geometry("300x200")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Enter A and B axis values:", font='Helvetica 12 bold').pack(pady=10)

        # A axis input
        a_frame = ttk.Frame(dialog)
        a_frame.pack(pady=5, fill=X, padx=20)
        ttk.Label(a_frame, text="A Axis:", width=10).pack(side=LEFT)
        a_var = tk.DoubleVar()
        a_entry = ttk.Entry(a_frame, textvariable=a_var)
        a_entry.pack(side=LEFT, fill=X, expand=True)
        a_entry.focus()

        # B axis input
        b_frame = ttk.Frame(dialog)
        b_frame.pack(pady=5, fill=X, padx=20)
        ttk.Label(b_frame, text="B Axis:", width=10).pack(side=LEFT)
        b_var = tk.DoubleVar()
        b_entry = ttk.Entry(b_frame, textvariable=b_var)
        b_entry.pack(side=LEFT, fill=X, expand=True)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)

        def submit():
            try:
                a = a_var.get()
                b = b_var.get()
                dialog.destroy()
                return a, b
            except tk.TclError:
                self.show_error("Please enter valid numeric values for A and B axes.")

        def cancel():
            dialog.destroy()
            return None, None

        submit_button = ttk.Button(button_frame, text="Submit", command=submit, bootstyle="success")
        submit_button.pack(side=LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel, bootstyle="danger")
        cancel_button.pack(side=LEFT, padx=10)

        # Wait for dialog to close
        self.root.wait_window(dialog)

        # Retrieve values
        try:
            a = a_var.get()
            b = b_var.get()
            return a, b
        except tk.TclError:
            return None, None

    def clear_plot(self):
        """Clears the matplotlib plot."""
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("X Axis")
        self.ax.set_ylabel("Y Axis")
        self.ax.grid(True)
        self.canvas.draw()

    def clear_all(self):
        """Clears all data and plots."""
        self.points.clear()
        self.spray_actions.clear()
        self.axis_values.clear()
        self.corners.clear()
        self.shape_drawn = False
        self.clear_plot()
        self.gcode_output.delete(1.0, tk.END)

    def generate_gcode(self):
        if not self.points:
            self.show_error("No points to generate G-code.")
            return

        gcode = []

        # Initial setup commands
        gcode.append("; Begin G-code")
        gcode.append("M64 P0 ; Initialize")
        gcode.append("M65 P1 ; Initialize")
        gcode.append("G21 ; Set units to millimeters")
        gcode.append("G90 ; Absolute positioning")
        gcode.append("G1 F1000 ; Set feed rate")
        gcode.append("")

        for i, point in enumerate(self.points):
            x, y = point
            a, b = self.axis_values[i]
            action = self.spray_actions[i]

            gcode.append(f"; Move to Point {i+1}")
            gcode.append(f"G0 X{x:.2f} Y{y:.2f} Z0 A{a:.2f} B{b:.2f}")

            if action == "Start":
                gcode.append("M64 P1 ; Spray ON")
            elif action == "Stop":
                gcode.append("M65 P1 ; Spray OFF")

            # For 'Resume', do not toggle spray, assume it's already on

            gcode.append("")

        # Ensure spray is off at the end
        if self.spray_actions[-1] != "Stop":
            gcode.append("M65 P1 ; Spray OFF")

        gcode.append("; End of G-code")

        gcode_str = "\n".join(gcode)
        self.gcode_output.delete(1.0, tk.END)
        self.gcode_output.insert(tk.END, gcode_str)

    def show_error(self, message):
        error_dialog = ttk.Messagebox.show_error(title="Error", message=message)

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = NozzlePathApp(root)
    root.mainloop()
