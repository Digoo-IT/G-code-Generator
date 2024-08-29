import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

class NozzlePathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laptop Painting and Nozzle Path Planner")

        self.selected_laptop = None
        self.laptops = []
        self.templates = {}
        self.current_template = tk.StringVar(value="Select Template")

        self.template_points = []
        self.template_spray_actions = []
        self.template_axis_values = []  # Store (A, B, Z) values for each template point

        self.last_a_value = 0  # Last entered A value
        self.last_b_value = 0  # Last entered B value
        self.last_z_value = 0  # Last entered Z value

        self.laptop_assignments = {}  # Track template assignments to laptops

        self.create_widgets()  # Initialize widgets and then load templates
        self.load_templates()  # Load templates from file if available

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Template creation and management
        self.template_frame = ttk.Frame(main_frame, padding=10)
        self.template_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.clear_button = ttk.Button(control_frame, text="Clear Template", command=self.clear_template, bootstyle="danger-outline")
        self.clear_button.pack(pady=10)

        self.save_template_button = ttk.Button(control_frame, text="Save Template", command=self.save_template, bootstyle="success-outline")
        self.save_template_button.pack(pady=10)

        self.template_name_entry = ttk.Entry(control_frame, width=20, bootstyle="info")
        self.template_name_entry.pack(pady=10)
        self.template_name_entry.insert(0, "Template Name")

        ttk.Label(control_frame, text="Spray Action:", font='Arial 10 bold').pack(pady=5)
        self.spray_action_var = tk.StringVar(value="Start")
        ttk.OptionMenu(control_frame, self.spray_action_var, "Start", "Start", "Stop", "Resume", bootstyle="info").pack(pady=5)

        self.template_dropdown = ttk.OptionMenu(control_frame, self.current_template, "Select Template")
        self.template_dropdown.pack(pady=10)

        self.assign_template_button = ttk.Button(control_frame, text="Assign Template", command=self.assign_template_to_laptop, bootstyle="primary-outline")
        self.assign_template_button.pack(pady=10)

        # G-code generation and copy buttons
        self.generate_code_button = ttk.Button(control_frame, text="Generate G-code", command=self.generate_gcode, bootstyle="warning-outline")
        self.generate_code_button.pack(pady=10)

        self.copy_button = ttk.Button(control_frame, text="Copy G-code", command=self.copy_gcode, bootstyle="primary-outline")
        self.copy_button.pack(pady=10)

        self.clear_table_button = ttk.Button(control_frame, text="Clear Table", command=self.clear_table, bootstyle="danger-outline")
        self.clear_table_button.pack(pady=10)

        # Textbox for displaying G-code
        self.gcode_output = tk.Text(control_frame, height=10, width=40)
        self.gcode_output.pack(pady=10)

        # Table display and template assignment area
        self.canvas_frame = ttk.Frame(main_frame, padding=10)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Template Creation Canvas
        self.template_canvas_frame = ttk.Frame(self.template_frame, padding=10)
        self.template_canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.template_canvas, self.template_ax = self.create_plot(self.template_canvas_frame, "Template Creation")
        self.template_canvas.mpl_connect("button_press_event", self.on_template_click)

        # Table with laptops Canvas
        self.table_canvas_frame = ttk.Frame(self.canvas_frame, padding=10)
        self.table_canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.table_canvas, self.ax = self.create_plot(self.table_canvas_frame, "Table Layout")
        self.draw_table_with_laptops()

    def create_plot(self, parent_frame, title):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title(title)
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas, ax

    def draw_table_with_laptops(self):
        table_width = 1500
        table_height = 3000
        laptop_width = 320
        laptop_height = 430
        x_gap = 20
        y_gap = 50
        margin = 100  # Margin around the entire grid of laptops

        # Calculate total area needed for laptops and gaps
        total_laptops_width = 4 * laptop_width + 3 * x_gap
        total_laptops_height = 6 * laptop_height + 5 * y_gap

        # Center the laptops on the table with the margin around them
        x_offset = (table_width - total_laptops_width) / 2
        y_offset = (table_height - total_laptops_height) / 2

        # Adjust the coordinate system for the table with margin
        self.ax.set_xlim(0 - margin, table_width + margin)
        self.ax.set_ylim(0 - margin, table_height + margin)
        self.ax.add_patch(Rectangle((0, 0), table_width, table_height, fill=None, edgecolor='black'))

        laptop_number = 1
        for row in range(6):
            for col in range(4):
                x = col * (laptop_width + x_gap) + x_offset
                y = row * (laptop_height + y_gap) + y_offset
                laptop = Rectangle((x, y), laptop_width, laptop_height, fill=None, edgecolor='blue')
                self.ax.add_patch(laptop)
                text = self.ax.text(x + laptop_width / 2, y + laptop_height / 2, str(laptop_number), color="black", ha='center', va='center', fontsize=8)
                text.set_picker(True)  # Enable picking for the laptop number
                self.laptops.append((laptop, laptop_number, (x, y, laptop_width, laptop_height), text))
                laptop_number += 1

        self.ax.set_aspect('equal')
        self.table_canvas.draw()
        self.table_canvas.mpl_connect("pick_event", self.on_laptop_number_click)

    def on_template_click(self, event):
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            self.template_points.append((x, y))
            spray_action = self.spray_action_var.get()
            self.template_spray_actions.append(spray_action)

            self.template_ax.plot(x, y, 'ro')
            self.template_ax.annotate(f"{spray_action}", (x, y), textcoords="offset points", xytext=(5, 5), ha='center')

            self.show_abz_popup(x, y, is_template=True)

            if len(self.template_points) > 1:
                x_vals, y_vals = zip(*self.template_points)
                self.template_ax.plot(x_vals, y_vals, 'b-')

            self.template_canvas.draw()

    def on_laptop_number_click(self, event):
        if event.artist in [l[3] for l in self.laptops]:  # Check if the clicked artist is a laptop number
            for laptop, number, (lx, ly, width, height), text in self.laptops:
                if event.artist == text:
                    self.selected_laptop = number
                    self.highlight_laptop(lx, ly, width, height, self.current_template.get())
                    self.laptop_assignments[number] = self.current_template.get()
                    self.table_canvas.draw()
                    break

    def highlight_laptop(self, x, y, width, height, template_name):
        # Highlight the laptop with a different color and display the template name at the top
        self.ax.add_patch(Rectangle((x, y), width, height, fill=True, color='green', alpha=0.3))
        self.ax.text(x + width / 2, y + height + 5, template_name, color="black", ha='center', va='bottom', fontsize=8)
        self.ax.text(x + width / 2, y + height / 2, self.selected_laptop, color="black", ha='center', va='center', fontsize=10)

    def show_abz_popup(self, x, y, is_template=False):
        popup = tk.Toplevel(self.root)
        popup.title("Enter A, B & Z Values")

        tk.Label(popup, text="Enter A value:").grid(row=0, column=0, padx=10, pady=10)
        a_entry = ttk.Entry(popup, width=10, bootstyle="info")
        a_entry.grid(row=0, column=1, padx=10, pady=10)
        a_entry.insert(0, self.last_a_value)

        tk.Label(popup, text="Enter B value:").grid(row=1, column=0, padx=10, pady=10)
        b_entry = ttk.Entry(popup, width=10, bootstyle="info")
        b_entry.grid(row=1, column=1, padx=10, pady=10)
        b_entry.insert(0, self.last_b_value)

        tk.Label(popup, text="Enter Z value:").grid(row=2, column=0, padx=10, pady=10)
        z_entry = ttk.Entry(popup, width=10, bootstyle="info")
        z_entry.grid(row=2, column=1, padx=10, pady=10)
        z_entry.insert(0, self.last_z_value)

        def save_abz_values():
            try:
                a_value = float(a_entry.get())
                b_value = float(b_entry.get())
                z_value = float(z_entry.get())

                if is_template:
                    self.template_axis_values.append((a_value, b_value, z_value))
                    self.template_ax.annotate(f"A:{a_value}, B:{b_value}, Z:{z_value}", (x, y), textcoords="offset points", xytext=(10, -10), ha='center', color='blue')
                    self.template_canvas.draw()
                else:
                    self.template_axis_values.append((a_value, b_value, z_value))
                    self.ax.annotate(f"A:{a_value}, B:{b_value}, Z:{z_value}", (x, y), textcoords="offset points", xytext=(10, -10), ha='center', color='blue')
                    self.table_canvas.draw()

                self.last_a_value = a_value
                self.last_b_value = b_value
                self.last_z_value = z_value
                popup.destroy()
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter valid numbers for A, B, and Z axes.")

        save_button = ttk.Button(popup, text="Save", command=save_abz_values, bootstyle="success")
        save_button.grid(row=3, column=0, columnspan=2, pady=10)

        popup.transient(self.root)
        popup.grab_set()
        self.root.wait_window(popup)

    def save_template(self):
        template_name = self.template_name_entry.get()
        if template_name:
            self.templates[template_name] = (self.template_points.copy(), self.template_spray_actions.copy(), self.template_axis_values.copy())
            self.update_template_dropdown()
            self.save_templates_to_file()  # Save templates to file
            tk.messagebox.showinfo("Template Saved", f"Template '{template_name}' saved successfully!")
        else:
            tk.messagebox.showerror("Error", "Please enter a template name.")

    def update_template_dropdown(self):
        menu = self.template_dropdown["menu"]
        menu.delete(0, "end")
        for template_name in self.templates.keys():
            menu.add_command(label=template_name, command=lambda value=template_name: self.current_template.set(value))

    def assign_template_to_laptop(self):
        selected_template = self.current_template.get()
        if selected_template in self.templates:
            self.table_canvas.mpl_connect("pick_event", self.on_laptop_number_click)
        else:
            tk.messagebox.showerror("Error", "Please select a valid template.")

    def generate_gcode(self):
        gcode = []
        gcode.append("M64 P0 ; Ensure nozzle is off initially")
        gcode.append("M65 P1 ; Reset")
        gcode.append("")
        gcode.append("; Set feed rate for the painting process")
        gcode.append("G1 F10000")
        gcode.append("")

        previous_position = None

        for laptop_number, template_name in sorted(self.laptop_assignments.items()):
            points, spray_actions, axis_values = self.templates[template_name]
            x, y, _, _ = [l[2] for l in self.laptops if l[1] == laptop_number][0]

            if previous_position:
                gcode.append(f"G0 X{previous_position[0]:.2f} Y{previous_position[1]:.2f}")
            else:
                gcode.append(f"G0 X{x:.2f} Y{y:.2f}")

            for i in range(len(points)):
                px, py = points[i]
                a_value, b_value, z_value = axis_values[i]
                action = spray_actions[i]

                gcode.append(f"G1 X{x + px:.2f} Y{y + py:.2f} Z{z_value:.2f} A{a_value} B{b_value}")
                gcode.append("G4 P0.1 ; Small pause to ensure position is reached")

                if action.lower() == "start":
                    gcode.append("M64 P1 ; Turn on the spray")
                    gcode.append("G4 P0.02 ; Slightly longer dwell to ensure spray turns on fully")
                elif action.lower() == "stop":
                    gcode.append("G4 P0.02 ; Slightly longer dwell to ensure spray turns off")
                    gcode.append("M65 P1 ; Turn off the spray")
                    gcode.append("G4 P1 ; Dwell for 1 second to ensure spray is completely off and any drips are cleared")

                if i < len(points) - 1:
                    next_px, next_py = points[i + 1]
                    gcode.append(f"G1 X{x + next_px:.2f} Y{y + next_py:.2f} Z{z_value:.2f} A{a_value} B{b_value}")

            previous_position = (x + points[-1][0], y + points[-1][1])

        gcode.append("; Return to Home Position")
        gcode.append("G1 X0 Y0 Z0 A0 B0")
        gcode.append("")
        gcode.append("M30 ; End of program")

        gcode_str = "\n".join(gcode)
        self.gcode_output.delete(1.0, tk.END)
        self.gcode_output.insert(tk.END, gcode_str)
        print(gcode_str)  # Optionally print the G-code to the console for debugging

    def clear_template(self):
        self.template_ax.cla()
        self.template_points.clear()
        self.template_spray_actions.clear()
        self.template_axis_values.clear()

        # Adjusting the template canvas with margin around the template
        template_width = 320  # Laptop width
        template_height = 430  # Laptop height
        margin = 100  # Margin around the template

        self.template_ax.set_xlim(-margin, template_width + margin)
        self.template_ax.set_ylim(-margin, template_height + margin)
        self.template_ax.add_patch(Rectangle((0, 0), template_width, template_height, fill=None, edgecolor='black'))

        self.template_canvas.draw()

    def clear_table(self):
        self.ax.cla()
        self.laptop_assignments.clear()
        self.laptops.clear()
        self.draw_table_with_laptops()

    def copy_gcode(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.gcode_output.get(1.0, tk.END))
        tk.messagebox.showinfo("Copied", "G-code has been copied to clipboard.")

    def save_templates_to_file(self):
        with open('templates.json', 'w') as f:
            json.dump(self.templates, f)

    def load_templates(self):
        if os.path.exists('templates.json'):
            with open('templates.json', 'r') as f:
                self.templates = json.load(f)
            self.update_template_dropdown()

if __name__ == "__main__":
    root = ttkb.Window(themename="flatly")
    app = NozzlePathApp(root)
    root.mainloop()
