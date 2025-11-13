import adsk.core, adsk.fusion, traceback

"""
Creates an alternating series of extruded cylindrical bodies in an Autodesk Fusion 360
design. The script generates a set number of cylinders, alternating between two radii,
and positions each cylinder along the Z-axis at regular intervals.

Constants:
    TOTAL_CYLINDERS (int): Number of cylinders to create.
    BIGGEST_RADIUS (float): Radius used for even-indexed cylinders.
    SMALLEST_RADIUS (float): Radius used for odd-indexed cylinders.
    HEIGHT (float): Height of each extruded cylinder.

Functions:
    create_cylinder(rootComp, center, radius, height):
        Creates a single cylinder by sketching a circle on the XY plane and
        extruding it as a new body.

        Args:
            rootComp (adsk.fusion.Component): The root component in which the
                cylinder is created.
            center (adsk.core.Point3D): Center point of the sketched circle.
            radius (float): Radius of the cylinder.
            height (float): Extrusion height.

        Returns:
            adsk.fusion.ExtrudeFeature: The resulting extrusion feature.

run(context):
    Entry point for the Fusion 360 script. Initializes a new design, then creates
    multiple cylinders in sequence. Each cylinder alternates between the largest and
    smallest configured radii. All cylinders are created at the origin, and each
    subsequent cylinder (after the first) is translated along the positive Z-axis
    by 10 units multiplied by its index.

    If an error occurs, a message box displays the stack trace for debugging.
"""


TOTAL_CYLINDERS = 10
BIGGEST_RADIUS = 10
SMALLEST_RADIUS = 5
HEIGHT = 10


def create_cylinder(rootComp, center, radius, height):
    sketches = rootComp.sketches
    sketch = sketches.add(rootComp.xYConstructionPlane)
    circles = sketch.sketchCurves.sketchCircles
    circle = circles.addByCenterRadius(center, radius)
    prof = sketch.profiles.item(0)
    
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(height)
    extInput.setDistanceExtent(False, distance)
    return extrudes.add(extInput)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Create a new document.
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent


        for i in range(TOTAL_CYLINDERS):
            # Alternating sizes based on index.
            if i % 2 == 0:
                radius = BIGGEST_RADIUS
            else:
                radius = SMALLEST_RADIUS

            cylinder = create_cylinder(rootComp, adsk.core.Point3D.create(0, 0, 0), radius, HEIGHT)
            
            # Move the cylinder.
            if i > 0:
                transform = adsk.core.Matrix3D.create()
                transform.translation = adsk.core.Vector3D.create(0, 0, 10*i)
                
                moveFeats = rootComp.features.moveFeatures
                bodies_to_move = adsk.core.ObjectCollection.create()
                bodies_to_move.add(cylinder.bodies.item(0))
                
                moveFeatureInput = moveFeats.createInput(bodies_to_move, transform)
                moveFeats.add(moveFeatureInput)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
