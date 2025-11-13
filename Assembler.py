import adsk.core, adsk.fusion, traceback

TARGET_FILE_NAMES = [
    "X3-G1-X2",
    "X2-G1-G1-X3",
    "G1-G2-G3-X1-X2",
]

TARGET_FOLDER_NAME = "RevD"


def split_file_name(name):
    """
    Splits the target filename pattern into individual shape identifiers.

    Parameters
    ----------
    name : str
        A hyphen-separated string (e.g., "X3-G1-X2").

    Returns
    -------
    list[str]
        A list of tokens extracted from the pattern (e.g., ["X3", "G1", "X2"]).
    """
    return name.split('-')


def findFolderRecursive(parentFolder, targetName):
    """
    Recursively searches through Fusion 360 project folders to find a folder by name.

    Parameters
    ----------
    parentFolder : adsk.core.DataFolder
        The starting folder for the recursive search.
    targetName : str
        The name of the folder to locate.

    Returns
    -------
    adsk.core.DataFolder or None
        The found folder, or None if no matching folder exists.
    """
    for f in parentFolder.dataFolders:
        if f.name == targetName:
            return f
    for f in parentFolder.dataFolders:
        found = findFolderRecursive(f, targetName)
        if found:
            return found
    return None


def insert_all_shapes(shape_files, rootComp, ui):
    """
    Inserts all provided shape files into the active design as occurrences.

    Parameters
    ----------
    shape_files : list[adsk.core.DataFile]
        A list of cloud DataFiles representing inserted component templates.
    rootComp : adsk.fusion.Component
        The root component of the active design.
    ui : adsk.core.UserInterface
        Fusion UI object for displaying messages.

    Returns
    -------
    list[adsk.fusion.Occurrence]
        All successfully inserted occurrences.
    """
    inserted_occurrences = []

    for df in shape_files:
        transform = adsk.core.Matrix3D.create()

        # Try normal insert
        try:
            occ = rootComp.occurrences.addByInsert(df, transform, False)
            if occ:
                inserted_occurrences.append(occ)
                continue
        except:
            pass

        # Try versioned insert
        try:
            occ = rootComp.occurrences.addByInsert(df, transform, False, 1)
            if occ:
                inserted_occurrences.append(occ)
                continue
        except Exception as e:
            ui.messageBox(f"FAILED to insert '{df.name}':\n{e}")

    return inserted_occurrences


def get_end_faces_and_centers(occ):
    """
    Identifies the left and right planar end faces of a shape occurrence,
    based on world-space X-axis direction.

    The function:
      - Identifies planar faces whose normals align with ±X.
      - Selects the two most extreme faces along X.
      - Computes their world-space center points.

    Parameters
    ----------
    occ : adsk.fusion.Occurrence
        The occurrence to analyze.

    Returns
    -------
    (left_face, right_face, left_center, right_center)
        left_face  : planar face with normal ~ -X
        right_face : planar face with normal ~ +X
        left_center, right_center : world-space center points (adsk.core.Point3D)

        Returns (None, None, None, None) if no suitable faces are found.
    """
    comp = occ.component
    if not comp or comp.bRepBodies.count == 0:
        return None, None, None, None

    x_axis = adsk.core.Vector3D.create(1, 0, 0)
    transform = occ.transform

    left_face = None
    right_face = None
    left_center = None
    right_center = None
    left_x = float('inf')
    right_x = float('-inf')

    for body in comp.bRepBodies:
        for face in body.faces:
            plane = adsk.core.Plane.cast(face.geometry)
            if not plane:
                continue

            n = plane.normal.copy()
            n.transformBy(transform)
            dot = n.dotProduct(x_axis)

            if abs(dot) < 0.95:
                continue

            p = face.pointOnFace.copy()
            p.transformBy(transform)
            x = p.x

            # left face
            if dot < 0:
                if x < left_x:
                    left_x = x
                    left_face = face
                    left_center = p

            # right face
            elif dot > 0:
                if x > right_x:
                    right_x = x
                    right_face = face
                    right_center = p

    return left_face, right_face, left_center, right_center


def auto_align_face_to_face(occ_list, ui):
    """
    Sequentially aligns a list of occurrences end-to-end along the X-axis,
    by matching each shape's left flat face to the previous shape's right flat face.

    Parameters
    ----------
    occ_list : list[adsk.fusion.Occurrence]
        Occurrences to align in order.
    ui : adsk.core.UserInterface
        Fusion UI for status/error messages.

    Returns
    -------
    None
    """
    if len(occ_list) < 2:
        ui.messageBox("Not enough shapes to align.")
        return

    prev_occ = occ_list[0]
    _, rf, _, rc = get_end_faces_and_centers(prev_occ)

    if not rf or not rc:
        ui.messageBox(f"Could not find right end face on '{prev_occ.name}'.")
        return

    for i in range(1, len(occ_list)):
        curr_occ = occ_list[i]
        lf2, _, lc2, _ = get_end_faces_and_centers(curr_occ)

        if not lf2 or not lc2:
            ui.messageBox(f"Could not find left end face on '{curr_occ.name}' (skipped).")
            continue

        dx = rc.x - lc2.x
        dy = rc.y - lc2.y
        dz = rc.z - lc2.z

        move_vec = adsk.core.Vector3D.create(dx, dy, dz)
        move_matrix = adsk.core.Matrix3D.create()
        move_matrix.translation = move_vec

        current_transform = curr_occ.transform
        current_transform.transformBy(move_matrix)
        curr_occ.transform = current_transform

        # Update chain
        _, rf_next, _, rc_next = get_end_faces_and_centers(curr_occ)
        if rf_next and rc_next:
            rc = rc_next
            prev_occ = curr_occ


def save_design_as_sequence(ui, tray_name):
    """
    Saves the current Fusion document to the cloud project folder using a name
    derived from TARGET_FILE_NAME.

    Parameters
    ----------
    ui : adsk.core.UserInterface
        UI for displaying failure or success messages.

    Returns
    -------
    None
    """
    app = adsk.core.Application.get()
    project = app.data.activeProject
    save_folder = project.rootFolder
    file_name = f"Tray_{tray_name}"

    try:
        doc = app.activeDocument
        doc.saveAs(file_name, save_folder, "Auto-generated tray", "")
    except Exception as e:
        ui.messageBox(f"Save failed:\n{e}")


def export_step(design, ui, full_path):
    """
    Exports the current design as a STEP file.

    Parameters
    ----------
    design : adsk.fusion.Design
        The active Fusion design.
    ui : adsk.core.UserInterface
        For showing success or failure messages.
    full_path : str
        Absolute file path to export to.

    Returns
    -------
    None
    """
    try:
        exportMgr = design.exportManager
        stepOptions = exportMgr.createSTEPExportOptions(full_path)
        exportMgr.execute(stepOptions)
    except Exception as e:
        ui.messageBox(f"STEP Export failed:\n{e}")


# ------------------------------------------------------------
# MAIN SCRIPT
# ------------------------------------------------------------
def run(context):
    """
    Main entry point for the script.

    Steps executed:
      1. Load target shapes from Fusion cloud folder.
      2. Insert all shapes into the design.
      3. Align shapes face-to-face along the X-axis.
      4. Save the resulting assembly using an auto-generated name.
      5. Export the final design as a STEP file.

    Parameters
    ----------
    context :
        Fusion 360 script context (unused).

    Returns
    -------
    None
    """
    ui = None

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        for TARGET_FILE_NAME in TARGET_FILE_NAMES:

            # Create a fresh Fusion design for each tray
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(app.activeProduct)

            rootComp = design.rootComponent
            shapes = split_file_name(TARGET_FILE_NAME)

            project = app.data.activeProject
            project_folder = findFolderRecursive(project.rootFolder, TARGET_FOLDER_NAME)

            if project_folder is None:
                ui.messageBox(f'Folder "{TARGET_FOLDER_NAME}" not found.')
                return

            project_files = {df.name: df for df in project_folder.dataFiles}

            missing = [s for s in shapes if s not in project_files]
            if missing:
                ui.messageBox(f"Missing files for {TARGET_FILE_NAME}:\n" + "\n".join(missing))
                continue

            found_files = [project_files[s] for s in shapes]

            # Insert shapes
            inserted = insert_all_shapes(found_files, rootComp, ui)
            if not inserted:
                ui.messageBox(f"No shapes inserted for {TARGET_FILE_NAME}.")
                continue

            # Align shapes
            auto_align_face_to_face(inserted, ui)

            # Save to cloud
            save_design_as_sequence(ui, TARGET_FILE_NAME)

            # Export to STEP
            export_step(design, ui, f"C:/Users/Issac/Desktop/Fusion360_Exports/{TARGET_FILE_NAME}.step")

            # Close document to prepare for next tray
            try:
                app.activeDocument.close(False)
            except Exception as e:
                ui.messageBox(f"Document close failed:\n{e}")

        ui.messageBox("Files Completed")

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
