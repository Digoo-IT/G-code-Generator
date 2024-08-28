class GCodeGenerator:
    @staticmethod
    def generate_gcode(self):
        if len(self.points) < 2:
            self.show_error("You need at least two points to generate a path.")
            return

        gcode = []

        # Initial setup commands
        gcode.extend([
            "M64 P0",
            "M65 P1",
            "",
            "; Set feed rate for the painting process",
            "G1 F10000",
            ""
        ])

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

        gcode = ""
        current_x = 0
        current_y = 0

        for i, laptop in enumerate(laptop_setup.laptops):
            gcode += f"(Laptop {i+1} Position)\n"
            gcode += f"G0 X{current_x + laptop.x} Y{current_y + laptop.y} Z{laptop.z}\n"
            gcode += GCodeGenerator.paint_laptop(laptop)
            
            # Move to the next laptop position
            current_x += laptop_setup.spacing_x
            current_y += laptop_setup.spacing_y
        
        return gcode

    @staticmethod
    def paint_laptop(laptop):
        gcode = f"(Start Painting on Laptop at X{laptop.x}, Y{laptop.y})\n"
        
        # Simulate top painting
        for step in range(laptop.steps_top):
            gcode += f"G1 X{laptop.x} Y{laptop.y} Z{laptop.z} A{laptop.a} B{laptop.b} (Top Step {step + 1})\n"
        
        # Simulate side painting
        for step in range(laptop.steps_side):
            gcode += f"G1 X{laptop.x} Y{laptop.y} Z{laptop.z} A{laptop.a + 45} B{laptop.b} (Side Step {step + 1})\n"
        
        return gcode
