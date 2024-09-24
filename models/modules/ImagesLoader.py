import os

def get_paths_original_data():

    base_path = os.getcwd()
    #folders = ["0 DIAS - FRESCOS",  "7 DIAS", "14 DIAS", "21 DIAS"]
    folders = ["0 DIAS - FRESCOS"]
    paths = []
    for folder in folders:
        folder_path = os.path.join(base_path, "IAGenOvoscopia", folder, "Fotos bluebox")
        if not os.path.exists(folder_path):
            print(f"Pasta não encontrada: {folder_path}")
            continue

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, file_name)
                paths.append(image_path)
    
    return paths