import adsk.core, adsk.fusion, traceback

TARGET_FILE_NAME = "X3-G1-G2-G1-G2-G3"
TARGET_FOLDER_NAME = "RevD"

def split_file_name(name):
    return name.split('-')

def findFolderRecursive(parentFolder, targetName):
    for f in parentFolder.dataFolders:
        if f.name == targetName:
            return f
    for f in parentFolder.dataFolders:
        found = findFolderRecursive(f, targetName)
        if found:
            return found
    return None

def insert_all_shapes(shape_files, rootComp, ui):
    inserted_occurrences = []

    for df in shape_files:
        ui.messageBox(f"Inserting '{df.name}'...")
        transform = adsk.core.Matrix3D.create()

        try:
            occ = rootComp.occurrences.addByInsert(df, transform, False)
            if occ:
                inserted_occurrences.append(occ)
                continue
        except:
            pass

        try:
            occ = rootComp.occurrences.addByInsert(df, transform, False, 1)
            if occ:
                inserted_occurrences.append(occ)
                continue
        except Exception as e:
            ui.messageBox(f"FAILED to insert '{df.name}':\n{e}")

    return inserted_occurrences


def auto_align_bounding_boxes(occ_list, ui):

    if len(occ_list) < 2:
        ui.messageBox("Not enough shapes to align.")
        return

    ui.messageBox("Starting bounding-box alignment...")

    TOLERANCE = 0.01  # slight negative offset to remove tiny gaps

    for i in range(1, len(occ_list)):
        prev_occ = occ_list[i - 1]
        curr_occ = occ_list[i]

        prev_box = prev_occ.boundingBox
        curr_box = curr_occ.boundingBox

        prev_max_x = prev_box.maxPoint.x
        curr_min_x = curr_box.minPoint.x

        offset_x = prev_max_x - curr_min_x - TOLERANCE

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(offset_x, 0, 0)

        new_transform = curr_occ.transform
        new_transform.transformBy(transform)
        curr_occ.transform = new_transform

    ui.messageBox("Alignment complete (flush).")


def run(context):

    ui = None
    
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('No active Fusion design.')
            return

        rootComp = design.rootComponent

        shapes = split_file_name(TARGET_FILE_NAME)

        project = app.data.activeProject
        project_folder = findFolderRecursive(project.rootFolder, TARGET_FOLDER_NAME)

        if project_folder is None:
            ui.messageBox(f'Could not find folder "{TARGET_FOLDER_NAME}".')
            return

        project_folder_files = {df.name: df for df in project_folder.dataFiles}

        missing = []
        found_files = []
        for s in shapes:
            if s in project_folder_files:
                found_files.append(project_folder_files[s])
            else:
                missing.append(s)

        if missing:
            ui.messageBox("Missing files:\n" + "\n".join(missing))
            return

        inserted_occ = insert_all_shapes(found_files, rootComp, ui)
        if not inserted_occ:
            ui.messageBox("No shapes inserted.")
            return

        auto_align_bounding_boxes(inserted_occ, ui)

        ui.messageBox(
            f"SUCCESS!\n\n"
            f"Inserted {len(inserted_occ)} shapes and aligned them flush."
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
