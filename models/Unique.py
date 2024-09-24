import os
from models.modules.LoadImage import LoadImage
from models.modules.EggModelGen import EggModelGen
from models.DefaultConfig import DefaultConfig
import pandas as pd
import random

class UniqueEggModel(DefaultConfig):

    def __init__(self):
        super().__init__()

        self.result_dataframe['path_egg'] = [os.path.join(os.getcwd(), 'images', 'unique_eggs' , f"ovo_{i}.jpg") for i in range(1,801)]

    
    def load_train_images(self):
        paths = []

        for type in range(1,5):
            
            sample_type = self.result_dataframe[self.result_dataframe['OVOSCOPIA'] == type].sample(1)

            for _,item in sample_type.iterrows():
                paths.append([item['path_egg'], str(item['OVOSCOPIA'])])    

        random.shuffle(paths)
        return paths
    
    def load_test_images(self, folder_path):
        paths = []

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, file_name)
                paths.append(image_path)

        return sorted(paths, key=lambda i: int(i.split("ovo_")[1].split(".")[0]))
    
    def create_instruction(self,prompt_file):
        with open(os.path.join(os.getcwd(), "models", "prompts", prompt_file), 'r', encoding='utf-8') as file:
            linhas = "".join(file.readlines())
        return linhas
    
    def read_csv(self, file):
        with open(file, 'r', encoding='utf-8') as file:
            linhas = "".join(file.readlines())
        return linhas



def main(temperature=1.0,prompt_file='matrix_mix.txt', test_path_dir=os.path.join(os.getcwd(), "images", "unique_eggs"), result_prompt='result.csv'):
    """Função principal para executar o fluxo de trabalho."""


    model = UniqueEggModel()

    images_path = model.load_train_images()

    train_prompt = []
    train_files_gemini = []
    for image, result in images_path:
        file_gemini = model.load_image_to_gemini(image)

        train_prompt.append(file_gemini)
        train_files_gemini.append(file_gemini)
        train_prompt.append(result)
    
    test_paths = model.load_test_images(test_path_dir)

    prompt = model.create_instruction(prompt_file)

    #Aguardar o upload
    LoadImage.wait_for_files_active(train_files_gemini)
    
    if (not os.path.isdir(os.path.join(os.getcwd(), "results"))):
        os.makedirs(os.path.join(os.getcwd(), "results"))

    egg_ia_gen = EggModelGen(temperature=temperature)

    egg_ia_gen.create_model(initial_instruction=prompt)
    examples = train_prompt[:]
    chat_session = egg_ia_gen.model.start_chat(
        history=[
            {
                "role": "user",
                "parts": examples,
            },
        ]
    )

    if os.path.isfile(f'./results/{result_prompt}'):
        result = pd.read_csv(f'./results/{result_prompt}', sep=";")
    else:
        result = pd.DataFrame([],columns=["number", "classification"])

    for i,test_path in enumerate(test_paths):

        if (result[result['number'] == i+1].shape[0] == 0) :

            print( f"Temperature {temperature}: File ", i+1)

            gemini_path = model.load_image_to_gemini(test_path)

            LoadImage.wait_for_files_active([gemini_path])

            response = chat_session.send_message(gemini_path)

            result.loc[len(result), :] = [i+1, int(response.text)]

            result.to_csv(f'./results/{result_prompt}', sep=";", index=False)
        

import sys
if __name__ == "__main__":
    [_, file_prompt, size_prompt] = sys.argv
    main("unique.txt", os.path.join(os.getcwd(), "images", "unique_eggs"),'result_unique.csv')
    main("unique_high.txt", os.path.join(os.getcwd(), "images", "unique_eggs"), 'result_unique_high.csv')

    