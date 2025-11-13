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

        # Normal insert
        try:
            occ = rootComp.occurrences.addByInsert(df, transform, False)
            if occ:
                inserted_occurrences.append(occ)
                ui.messageBox(f"Inserted '{df.name}'")
                continue
        except Exception as e:
            ui.messageBox(f"Normal insert failed for {df.name}:\n\n{e}")

        # Versioned insert
        try:
            occ = rootComp.occurrences.addByInsert(df, transform, False, 1)
            if occ:
                inserted_occurrences.append(occ)
                ui.messageBox(f"Inserted (versioned) '{df.name}'")
                continue
        except Exception as e:
            ui.messageBox(f"Versioned insert failed for {df.name}:\n\n{e}")

        # Failure
        ui.messageBox(f"FAILED to insert '{df.name}'")

    return inserted_occurrences



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
            ui.messageBox(f'Could not find {TARGET_FOLDER_NAME} folder anywhere.')
            return

        project_folder_files = {df.name: df for df in project_folder.dataFiles}

        missing = []
        found_files = []

        for shape in shapes:
            if shape in project_folder_files:
                found_files.append(project_folder_files[shape])
            else:
                missing.append(shape)

        if missing:
            ui.messageBox("Missing:\n" + "\n".join(missing))
            return

        # Insert ALL shapes
        inserted_occ = insert_all_shapes(found_files, rootComp, ui)

        if not inserted_occ:
            ui.messageBox("No shapes were inserted.")
            return

        ui.messageBox(
            f"SUCCESS: Inserted all {len(inserted_occ)} shapes.\n\n"
            "Next: Auto-align shapes."
        )

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
