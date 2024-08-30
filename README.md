# G-Code Generator for Laptop Painting

## Overview

This application is a G-code generator designed for automating the painting process of multiple laptops arranged on a table. The application allows you to create and manage templates for nozzle paths, assign these templates to individual laptops, and generate the corresponding G-code for CNC machines or robotic arms.

## Features

- **Table and Laptop Visualization**: Visual representation of a table with laptops arranged in a grid. Each laptop can be selected by clicking on its number.
- **Template Management**: Create, edit, and save templates for nozzle paths. Templates can include multiple points, each with customizable A, B, and Z axis values.
- **Assign Templates**: Assign saved templates to specific laptops on the table. The assigned template name is displayed on the selected laptop.
- **Undo/Redo Functionality**: Undo or redo actions when adding points to a template, allowing for flexible editing.
- **G-Code Generation**: Generate G-code for the entire setup, including all assigned laptops. The generated G-code can be copied to the clipboard for use in CNC machines.
- **Persistent Templates**: Save templates to a file, ensuring they persist between sessions. Templates can be reloaded when the application is restarted.

## Installation

### Prerequisites

- Python 3.8 or higher
- Required Python libraries: `tkinter`, `ttkbootstrap`, `matplotlib`

