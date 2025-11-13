# Tray Builder -- Fusion 360 Automation Script

This Fusion 360 script automatically builds custom trays by importing,
aligning, and exporting parametric component shapes stored inside a
Fusion Team Project folder. It is designed to eliminate all manual
assembly steps and produce ready-to-export 3D STEP files with zero user
interaction.

## Features

### ✔ Automatic Shape Discovery

-   Reads a hyphen-separated sequence such as:

        X3-G1-X2

-   Locates each corresponding Fusion design file inside a project
    folder (default: `RevD`).

-   Validates that all required shapes exist before continuing.

### ✔ Fully Automated Shape Insertion

-   Inserts each shape into a new assembly document.
-   Tries both regular insert and versioned insert to maximize
    compatibility.
-   Errors are reported only if a shape cannot be placed.

### ✔ Intelligent Face-to-Face Alignment

Each component is scanned for its two flat end faces along the X-axis: -
Left face → normal ≈ -X - Right face → normal ≈ +X

The script automatically: 1. Detects planar end faces\
2. Computes their world-space centers\
3. Translates each next shape so its left face touches the previous
shape's right face\
4. Produces a perfectly flush, non-overlapping chain

### ✔ Auto-Save

After assembly is completed, the script: - Saves the file to the Fusion
Team project root folder\
- Names it: `Tray_<SHAPE_SEQUENCE>`

### ✔ STEP Export

A STEP file is automatically written to a local path such as:

    C:/Users/Issac/Desktop/Fusion360_Exports/X3-G1-X2.step

### ✔ Auto-Close

Automatically closes the design document when done.

## How It Works

1.  Define your tray sequence:

    ``` python
    TARGET_FILE_NAME = "X3-G1-X2"
    ```

2.  Script splits the sequence into individual shape names.

3.  Searches the Fusion Team project folder (`RevD`) for matching
    shapes.

4.  Inserts each shape into the current design.

5.  Aligns shapes end-to-end.

6.  Saves the assembled tray.

7.  Exports a STEP file.

8.  Closes the document.

## Folder Requirements

Your Fusion Team project must contain: - A folder named: `RevD` - Inside
it, Fusion documents named: `X3   G1   X2   ...`

## Configuration Variables

  Variable               Purpose
  ---------------------- --------------------------------------
  `TARGET_FILE_NAME`     The sequence of shapes to assemble
  `TARGET_FOLDER_NAME`   Folder containing shape design files
  Export path            Output location for STEP export

## Supported Use Cases

-   Generating parametric trays\
-   Rapid design automation\
-   Configurable mechanical assemblies\
-   3D-printable modular components

## Example

Setting:

    TARGET_FILE_NAME = "X3-G1-G2-G3"

Produces: - A fully aligned 4-part tray\
- A Fusion design named: `Tray_X3-G1-G2-G3` - A STEP file:
`X3-G1-G2-G3.step`

## Notes

-   Fully automatic---no user input required.
-   Works with any number of shapes.
-   Shapes must have planar ends aligned with the X-axis.
