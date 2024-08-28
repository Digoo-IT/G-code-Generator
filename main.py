from laptop_config import Laptop, LaptopSetup
from gcode_generator import GCodeGenerator

def get_laptop_data():
    print("Enter the coordinates and angles for the laptop:")
    x = float(input("X coordinate: "))
    y = float(input("Y coordinate: "))
    z = float(input("Z coordinate: "))
    a = float(input("A angle (degrees): "))
    b = float(input("B angle (degrees): "))
    steps_top = int(input("Number of steps for painting on top: "))
    steps_side = int(input("Number of steps for painting on sides: "))
    
    return Laptop(x, y, z, a, b, steps_top, steps_side)

def main():
    print("Welcome to Laptop Painter")
    
    laptops = []
    num_laptops = int(input("Enter the number of laptops: "))
    
    for i in range(num_laptops):
        print(f"\nLaptop {i+1}:")
        laptop = get_laptop_data()
        laptops.append(laptop)
    
    spacing_x = float(input("Enter the spacing between laptops on the X axis: "))
    spacing_y = float(input("Enter the spacing between laptops on the Y axis: "))
    
    laptop_setup = LaptopSetup(laptops, spacing_x, spacing_y)
    print(f"\nLaptop setup configuration:\n{laptop_setup}")
    
    # Generate G-code
    gcode = GCodeGenerator.generate_gcode(laptop_setup)
    print("\nGenerated G-code:\n")
    print(gcode)

if __name__ == "__main__":
    main()
