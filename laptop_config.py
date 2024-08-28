class Laptop:
    def __init__(self, x, y, z, a, b, steps_top, steps_side):
        self.x = x
        self.y = y
        self.z = z
        self.a = a
        self.b = b
        self.steps_top = steps_top
        self.steps_side = steps_side

    def __str__(self):
        return (f"X: {self.x}, Y: {self.y}, Z: {self.z}, "
                f"A: {self.a}°, B: {self.b}°, "
                f"Steps Top: {self.steps_top}, Steps Side: {self.steps_side}")

class LaptopSetup:
    def __init__(self, laptops, spacing_x, spacing_y):
        self.laptops = laptops
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y

    def __str__(self):
        setup_str = f"Spacing - X: {self.spacing_x}, Y: {self.spacing_y}\n"
        for i, laptop in enumerate(self.laptops, start=1):
            setup_str += f"Laptop {i}: {laptop}\n"
        return setup_str
