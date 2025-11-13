import adsk.core, adsk.fusion, traceback

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
