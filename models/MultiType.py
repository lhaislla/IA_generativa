import os
import sys
import pandas as pd
from models.modules.LoadImage import LoadImage
from models.modules.EggModelGen import EggModelGen
from models.DefaultConfig import DefaultConfig
from models.modules.ImagesLoader import get_paths_original_data

class MultiTypeEggModel(DefaultConfig):

    def __init__(self):
        super().__init__()

    def load_training_info(self):
        df_training = pd.read_excel("img\ovoscopia_treino.xlsx")
        return df_training.set_index('nome_img')

    def load_training_images(self):
        img_folders = ["tipo1", "tipo2", "tipo3", "tipo4"]
        img_directory = os.path.join(os.getcwd(), "img")
        type_images_path = []
        
        for folder in img_folders:
            folder_path = os.path.join(img_directory, folder)  
            if not os.path.exists(folder_path):
                print(f"Pasta não encontrada: {folder_path}")
                continue
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(folder_path, file_name)
                    type_images_path.append(image_path)

        map_file_type_reference = self.load_all_egg_images_to_gemini(type_images_path)

        files_gemini_types = list(map(lambda x: x[1], map_file_type_reference.values()))
        LoadImage.wait_for_files_active(files_gemini_types)

        df_training_info = self.load_training_info()

        return map_file_type_reference, df_training_info

    def load_classification_images(self, folders):
        images_eggs_path = []
    
        for folder in folders:
            paths = get_paths_original_data(folder)  
            images_eggs_path.extend(paths)

        map_file_reference = self.load_all_egg_images_to_gemini(images_eggs_path)
        files_gemini = list(map(lambda x: x[1], map_file_reference.values()))
        LoadImage.wait_for_files_active(files_gemini)

        return map_file_reference, files_gemini

    def create_instruction(self, prompt_file):
        with open(os.path.join(os.getcwd(), "models", "prompts", prompt_file), 'r', encoding='utf-8') as file:
            linhas = "".join(file.readlines())
        return linhas

def mainMultiType(temperature=1.0, prompt_file='multitype_short.txt',test_path_dir= os.path.join(os.getcwd(), "img"), result_prompt='result.csv'):
 
    model = MultiTypeEggModel()
    images_path, df_training_info = model.load_training_images()

    train_prompt = []
    train_files_gemini = []
    for image, result in images_path.items():
        file_gemini = model.load_image_to_gemini(image)

        train_prompt.append(file_gemini)
        train_files_gemini.append(file_gemini)
        train_prompt.append(result)

    prompt = model.create_instruction(prompt_file)

    LoadImage.wait_for_files_active(train_files_gemini)

    if not os.path.isdir(os.path.join(os.getcwd(), "results")):
        os.makedirs(os.path.join(os.getcwd(), "results"))

    egg_ia_gen = EggModelGen(temperature=temperature)
    egg_ia_gen.create_model(initial_instruction=prompt)

    examples = train_prompt[:]
    
    for path in images_path.keys():
        example = images_path[path]
        csv_example = model.generate_training_example(df_training_info, example[0][0], example[0][1])
        examples.append(csv_example)
        
        if len(examples) >= 14:  
            break

    chat_session = egg_ia_gen.model.start_chat(
        history=[
            {
                "role": "user",
                "parts": train_prompt + examples,  
            },
        ]
    )

    for i, file_gemini in enumerate(train_files_gemini):
        response = chat_session.send_message(file_gemini)
        result_df = model.result_to_dataframe(response.text)
        result_df["number"] = range((i * 15) + 1, ((i + 1) * 15) + 1)

        if not os.path.isdir("./result"):
            os.makedirs("./result")

        result_df.to_csv(f"./result/result_{(i * 15) + 1}_to_{((i + 1) * 15) + 1}.csv", sep=";", index=False)

if __name__ == "__main__":

    [_, temperature, prompt_file, test_path_dir, result_prompt] = sys.argv
    print([_, temperature, prompt_file, test_path_dir, result_prompt])
    mainMultiType(prompt_file=prompt_file, test_path_dir=test_path_dir, result_prompt=result_prompt)
