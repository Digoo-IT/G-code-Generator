import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NozzlePathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nozzle Path Planner")

        self.points = []
        self.spray_actions = []
        self.corners = []
        self.shape_drawn = False  # Track if the shape has been drawn

        self.create_widgets()
        self.setup_plot()

    def create_widgets(self):
        # Frame for the corner inputs
        corner_frame = ttk.Frame(self.root)
        corner_frame.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(corner_frame, text="Corner 1 (X, Y):").grid(row=0, column=0, padx=5, pady=5)
        self.corner1_x_entry = ttk.Entry(corner_frame, width=10)
        self.corner1_x_entry.grid(row=0, column=1, padx=5, pady=5)
        self.corner1_y_entry = ttk.Entry(corner_frame, width=10)
        self.corner1_y_entry.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(corner_frame, text="Corner 2 (X, Y):").grid(row=1, column=0, padx=5, pady=5)
        self.corner2_x_entry = ttk.Entry(corner_frame, width=10)
        self.corner2_x_entry.grid(row=1, column=1, padx=5, pady=5)
        self.corner2_y_entry = ttk.Entry(corner_frame, width=10)
        self.corner2_y_entry.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(corner_frame, text="Corner 3 (X, Y):").grid(row=2, column=0, padx=5, pady=5)
        self.corner3_x_entry = ttk.Entry(corner_frame, width=10)
        self.corner3_x_entry.grid(row=2, column=1, padx=5, pady=5)
        self.corner3_y_entry = ttk.Entry(corner_frame, width=10)
        self.corner3_y_entry.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(corner_frame, text="Corner 4 (X, Y):").grid(row=3, column=0, padx=5, pady=5)
        self.corner4_x_entry = ttk.Entry(corner_frame, width=10)
        self.corner4_x_entry.grid(row=3, column=1, padx=5, pady=5)
        self.corner4_y_entry = ttk.Entry(corner_frame, width=10)
        self.corner4_y_entry.grid(row=3, column=2, padx=5, pady=5)

        self.draw_shape_button = ttk.Button(corner_frame, text="Draw Shape", command=self.draw_shape)
        self.draw_shape_button.grid(row=4, column=0, columnspan=3, pady=10)

        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, padx=10, pady=10)

        ttk.Label(control_frame, text="Spray Action:").grid(row=0, column=0, padx=5, pady=5)
        self.spray_action_var = tk.StringVar(value="Start")
        ttk.OptionMenu(control_frame, self.spray_action_var, "Start", "Start", "Stop", "Resume").grid(row=0, column=1, padx=5, pady=5)

        self.add_point_button = ttk.Button(control_frame, text="Add Point", command=self.add_point)
        self.add_point_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.clear_button = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        self.clear_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.generate_path_button = ttk.Button(control_frame, text="Generate G-code", command=self.generate_gcode)
        self.generate_path_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Add a text box for displaying the generated G-code
        self.gcode_output = tk.Text(self.root, height=10, width=50)
        self.gcode_output.grid(row=2, column=1, padx=10, pady=10)

    def setup_plot(self):
        self.fig, self.ax = plt.subplots()  # Create the figure and axes
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # Initialize the canvas with the figure
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=10, pady=10)  # Place the canvas in the GUI
        self.canvas.draw()  # Draw the initial empty plot

        self.initialize_plot()  # Now initialize the plot (clear it and set axes)
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def initialize_plot(self):
        """Initializes the plot without any shapes."""
        self.ax.cla()  # Clear the current axes
        self.ax.set_xlim(0, 100)  # Reset X axis limits
        self.ax.set_ylim(0, 100)  # Reset Y axis limits
        self.ax.set_xlabel("X Axis")  # Reset X axis label
        self.ax.set_ylabel("Y Axis")  # Reset Y axis label
        self.ax.grid(True)  # Re-enable the grid
        self.canvas.draw()  # Redraw the canvas

    def on_click(self, event):
        if self.shape_drawn and event.inaxes is not None:  # Only allow point addition if the shape is drawn
            x, y = event.xdata, event.ydata
            self.points.append((x, y))
            spray_action = self.spray_action_var.get()
            self.spray_actions.append(spray_action)
            self.ax.plot(x, y, 'ro')
            self.ax.annotate(f"{spray_action}", (x, y), textcoords="offset points", xytext=(5,5), ha='center')
            self.canvas.draw()

    def draw_shape(self):
        try:
            # Collect corner points from the entries
            corner1 = (float(self.corner1_x_entry.get()), float(self.corner1_y_entry.get()))
            corner2 = (float(self.corner2_x_entry.get()), float(self.corner2_y_entry.get()))
            corner3 = (float(self.corner3_x_entry.get()), float(self.corner3_y_entry.get()))
            corner4 = (float(self.corner4_x_entry.get()), float(self.corner4_y_entry.get()))

            self.corners = [corner1, corner2, corner3, corner4]

            # Clear the plot before drawing the new shape
            self.initialize_plot()

            # Draw the shape by connecting the corners
            x_vals, y_vals = zip(*self.corners)
            self.ax.plot(x_vals + (x_vals[0],), y_vals + (y_vals[0],), 'g-')
            self.canvas.draw()

            self.shape_drawn = True  # Mark that the shape has been drawn

        except ValueError:
            self.show_error("Please enter valid numbers for the corners.")

    def add_point(self):
        if self.shape_drawn and event.inaxes is not None:  # Only allow point addition if the shape is drawn
            x, y = event.xdata, event.ydata
            self.points.append((x, y))
            spray_action = self.spray_action_var.get()
            self.spray_actions.append(spray_action)
            self.ax.plot(x, y, 'ro')
            self.ax.annotate(f"{spray_action}", (x, y), textcoords="offset points", xytext=(5, 5), ha='center')
            self.canvas.draw()

    def clear_all(self):
        self.points = []
        self.spray_actions = []
        self.corners = []
        self.shape_drawn = False
        self.initialize_plot()  # Clear the plot and reset

    def generate_gcode(self):
        if len(self.points) < 2:
            self.show_error("You need at least two points to generate a path.")
            return

        gcode = []
        
        # Initial setup commands
        gcode.append("M64 P0")
        gcode.append("M65 P1")
        gcode.append("")
        gcode.append("; Set feed rate for the painting process")
        gcode.append("G1 F10000")
        gcode.append("")

        # Generate G-code for each segment
        for i in range(len(self.points) - 1):
            start_point = self.points[i]
            end_point = self.points[i + 1]
            spray_action = self.spray_actions[i]

            # Move to start point
            gcode.append(f"; Move to point {i+1}")
            gcode.append(f"G0 X{start_point[0]:.2f} Y{start_point[1]:.2f} Z0 A0 B-5")

            # Handle spray actions
            if spray_action.lower() == "start":
                gcode.append("M64 P1 (CYL ON) ; Turn on the spray")
            elif spray_action.lower() == "stop":
                gcode.append("M65 P1 (CYL OFF) ; Turn off the spray")
            elif spray_action.lower() == "resume":
                gcode.append("M64 P1 (CYL ON) ; Resume the spray")

            # Move to end point while spraying
            gcode.append(f"G1 X{end_point[0]:.2f} Y{end_point[1]:.2f} Z0 A0 B-5")
            
            # Stop spraying at the end of the segment
            gcode.append("M65 P1 (CYL OFF) ; Turn off the spray")
            gcode.append("")

        # Return to home position
        gcode.append("; Return to Home Position")
        gcode.append("G0 X0 Y0 Z0 A0 B0")

        # Join the gcode into a single string
        gcode_str = "\n".join(gcode)

        # Display the generated G-code
        self.gcode_output.delete(1.0, tk.END)
        self.gcode_output.insert(tk.END, gcode_str)

        # Optionally print the generated G-code to the console for debugging
        print(gcode_str)

    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        ttk.Label(error_window, text=message, padding=10).pack()
        ttk.Button(error_window, text="Close", command=error_window.destroy).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = NozzlePathApp(root)
    root.mainloop()
