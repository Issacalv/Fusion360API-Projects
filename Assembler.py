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


def insert_shape_file(file, rootComp, ui):

    transform = adsk.core.Matrix3D.create()

    try:
        ui.messageBox("Attempting normal insert (isReferencedComponent=False)...")
        occ = rootComp.occurrences.addByInsert(file, transform, False)
        return occ
    except Exception as e:
        ui.messageBox(f"Normal insert failed with error:\n\n{e}")

    try:
        ui.messageBox("Attempting version=1 insert (isReferencedComponent=False)...")
        occ = rootComp.occurrences.addByInsert(file, transform, False, 1)
        return occ
    except Exception as e:
        ui.messageBox(f"Version=1 insert failed with error:\n\n{e}")

    return None


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

        first_file = found_files[0]

        ui.messageBox(
            f"INSERT TEST:\n\n"
            f"Name: {first_file.name}\n"
            f"Extension: {first_file.fileExtension}\n"
            f"ID: {first_file.id}\n"
        )

        occ = insert_shape_file(first_file, rootComp, ui)

        if occ:
            ui.messageBox(f"SUCCESS: Inserted shape '{first_file.name}'")
        else:
            ui.messageBox(f"Insert failed.\nCheck error messages shown.")

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
