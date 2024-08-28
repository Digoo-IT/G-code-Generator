import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NozzlePathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nozzle Path Planner")

        self.points = []
        self.spray_actions = []
        self.corners = []
        self.axis_values = []  # Store (A, B) values for each point
        self.shape_drawn = False  # Track if the shape has been drawn
        self.current_laptop = 1

        self.create_widgets()
        self.setup_plot()

    def create_widgets(self):
        # Frame for the corner inputs
        corner_frame = ttk.Frame(self.root, padding=10)
        corner_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        ttk.Label(corner_frame, text=f"Laptop {self.current_laptop} Corners (X, Y):", font='Arial 10 bold').grid(row=0, column=0, columnspan=3)

        ttk.Label(corner_frame, text="Corner 1:").grid(row=1, column=0, padx=5, pady=5)
        self.corner1_x_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner1_x_entry.grid(row=1, column=1, padx=5, pady=5)
        self.corner1_y_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner1_y_entry.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(corner_frame, text="Corner 2:").grid(row=2, column=0, padx=5, pady=5)
        self.corner2_x_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner2_x_entry.grid(row=2, column=1, padx=5, pady=5)
        self.corner2_y_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner2_y_entry.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(corner_frame, text="Corner 3:").grid(row=3, column=0, padx=5, pady=5)
        self.corner3_x_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner3_x_entry.grid(row=3, column=1, padx=5, pady=5)
        self.corner3_y_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner3_y_entry.grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(corner_frame, text="Corner 4:").grid(row=4, column=0, padx=5, pady=5)
        self.corner4_x_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner4_x_entry.grid(row=4, column=1, padx=5, pady=5)
        self.corner4_y_entry = ttk.Entry(corner_frame, width=10, bootstyle="info")
        self.corner4_y_entry.grid(row=4, column=2, padx=5, pady=5)

        self.draw_shape_button = ttk.Button(corner_frame, text="Draw Shape", command=self.draw_shape, bootstyle="success-outline")
        self.draw_shape_button.grid(row=5, column=0, columnspan=3, pady=10)

        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        ttk.Label(control_frame, text="Spray Action:", font='Arial 10 bold').grid(row=0, column=0, padx=5, pady=5)
        self.spray_action_var = tk.StringVar(value="Start")
        ttk.OptionMenu(control_frame, self.spray_action_var, "Start", "Start", "Stop", "Resume", bootstyle="info").grid(row=0, column=1, padx=5, pady=5)

        self.clear_button = ttk.Button(control_frame, text="Clear All", command=self.clear_all, bootstyle="danger-outline")
        self.clear_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.generate_path_button = ttk.Button(control_frame, text="Generate G-code", command=self.generate_gcode, bootstyle="warning-outline")
        self.generate_path_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Add a frame for the plot and G-code output on the right side
        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Add a text box for displaying the generated G-code
        self.gcode_output = tk.Text(right_frame, height=10, width=50)
        self.gcode_output.grid(row=1, column=0, padx=10, pady=10)

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

            # Plot the point
            self.ax.plot(x, y, 'ro')
            self.ax.annotate(f"{spray_action}", (x, y), textcoords="offset points", xytext=(5, 5), ha='center')

            if spray_action.lower() in ["start", "resume"]:
                # Create entry fields for A and B axes
                a_label = ttk.Label(self.root, text="A:", font='Arial 8 bold')
                a_entry = ttk.Entry(self.root, width=5, bootstyle="info")
                b_label = ttk.Label(self.root, text="B:", font='Arial 8 bold')
                b_entry = ttk.Entry(self.root, width=5, bootstyle="info")

                # Place the entry fields above the plot (as per your image)
                a_label.place(x=event.x + 50, y=event.y - 40)
                a_entry.place(x=event.x + 70, y=event.y - 40)
                b_label.place(x=event.x + 50, y=event.y - 10)
                b_entry.place(x=event.x + 70, y=event.y - 10)

                # Add a button to confirm the axis values
                save_button = ttk.Button(self.root, text="Save", bootstyle="success")
                save_button.place(x=event.x + 50, y=event.y + 20)

                def save_axis_values():
                    try:
                        a_value = float(a_entry.get())
                        b_value = float(b_entry.get())
                        self.axis_values.append((a_value, b_value))
                        a_label.destroy()
                        a_entry.destroy()
                        b_label.destroy()
                        b_entry.destroy()
                        save_button.destroy()
                        # Show the A and B values next to the point
                        self.ax.annotate(f"A:{a_value}, B:{b_value}", (x, y), textcoords="offset points", xytext=(10, -10), ha='center', color='blue')
                        self.canvas.draw()
                    except ValueError:
                        self.show_error("Please enter valid numbers for A and B axes.")

                save_button.config(command=save_axis_values)

            else:
                self.axis_values.append((0, 0))  # Default A, B values for "Stop"

            # Draw the path if there are at least two points
            if len(self.points) > 1:
                x_vals, y_vals = zip(*self.points)
                self.ax.plot(x_vals, y_vals, 'b-')  # Draw the path

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

    def clear_all(self):
        self.points = []
        self.spray_actions = []
        self.axis_values = []  # Clear axis values
        self.shape_drawn = False
        self.initialize_plot()  # Clear the plot and reset

    def ask_another_laptop(self):
        response = tk.messagebox.askyesno("Another Laptop?", "Do you want to add another laptop?")
        if response:
            self.current_laptop += 1
            self.clear_all()  # Clear only the points and A/B values, keep the shape
            self.root.title(f"Nozzle Path Planner - Laptop {self.current_laptop}")
        else:
            self.ask_generate_gcode()

    def ask_generate_gcode(self):
        response = tk.messagebox.askyesno("Generate G-code", "Do you want to generate the G-code?")
        if response:
            self.generate_gcode()

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
            a_value, b_value = self.axis_values[i]

            # Move to start point with A and B axis values
            gcode.append(f"; Move to point {i+1}")
            gcode.append(f"G0 X{start_point[0]:.2f} Y{start_point[1]:.2f} Z0 A{a_value} B{b_value}")

            # Handle spray actions
            if spray_action.lower() == "start":
                gcode.append("M64 P1 (CYL ON) ; Turn on the spray")
            elif spray_action.lower() == "stop":
                gcode.append("M65 P1 (CYL OFF) ; Turn off the spray")

            # Move to end point while spraying
            gcode.append(f"G1 X{end_point[0]:.2f} Y{end_point[1]:.2f} Z0 A{a_value} B{b_value}")

            if spray_action.lower() == "stop":
                # Stop spraying at the end of the segment if it's a stop point
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
        error_window = ttk.Window(self.root, title="Error")
        ttk.Label(error_window, text=message, padding=10).pack()
        ttk.Button(error_window, text="Close", command=error_window.destroy, bootstyle="danger").pack(pady=5)

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")  # You can choose from various themes like 'darkly', 'flatly', etc.
    app = NozzlePathApp(root)
    root.mainloop()
