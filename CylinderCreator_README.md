# Cylindrical Pattern Generator for Fusion 360

This script creates a sequence of extruded cylinders inside an Autodesk
Fusion 360 design.\
Cylinders alternate between two radii and are spaced along the Z-axis at
regular intervals.

## Features

-   Automatically generates a new Fusion 360 design document.
-   Creates a user-defined number of cylinders.
-   Alternates between two radius sizes (`BIGGEST_RADIUS` and
    `SMALLEST_RADIUS`).
-   Places each cylinder at the origin before moving it along the
    Z-axis.
-   Fully scripted creation and movement of bodies using Fusion 360's
    API.

## How It Works

1.  The script starts by creating a new Fusion Design document and
    obtaining its root component.
2.  For each index in `TOTAL_CYLINDERS`:
    -   A circle is sketched on the XY construction plane.
    -   It is extruded upward into a cylindrical body of height
        `HEIGHT`.
    -   Even-indexed cylinders use the large radius; odd-indexed
        cylinders use the smaller one.
    -   Cylinders after the first are moved along the Z-axis by
        `10 * index` units.
3.  Any errors encountered are reported using a Fusion 360 message box.

## Configuration

``` python
TOTAL_CYLINDERS = 10        # Total number of cylinders to generate
BIGGEST_RADIUS = 10         # Radius for even-indexed cylinders
SMALLEST_RADIUS = 5         # Radius for odd-indexed cylinders
HEIGHT = 10                 # Extrusion height of each cylinder
```

## Requirements

-   Autodesk Fusion 360 with scripting access enabled
-   Python environment within Fusion 360 (uses `adsk.core` and
    `adsk.fusion` APIs)

## Usage

1.  Open Fusion 360.
2.  Go to **UTILITIES → Add-ins → Scripts and Add-ins**.
3.  Create a new script or load this one.
4.  Run the script from the Scripts and Add-ins panel.
5.  A new design will be created containing the generated cylinder
    sequence.

## File Structure

    script.py

## Error Handling

If something goes wrong during execution, Fusion 360 will display a
message box containing the full traceback to help debug the issue.
