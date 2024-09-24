import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as gemini
import pandas as pd
from EggModelGen import EggModelGen
from LoadImage import LoadImage
from io import StringIO

def load_key():
    _ = load_dotenv(find_dotenv())
    chave = os.getenv("GOOGLE_API_KEY")
    gemini.configure(api_key=chave)
    print("Chave reconhecida com sucesso!")
    return chave

def create_instruction():
    prompt = """
    A ovoscopia é um método utilizado para avaliar a qualidade dos ovos, especialmente em processos de incubação e produção de ovos comerciais.
        A técnica consiste em observar o interior do ovo por meio de uma luz intensa, geralmente em um ambiente escuro, para verificar a presença de anomalias, 
        como fissuras na casca, problemas no desenvolvimento do embrião ou alterações na câmara de ar.

        Você é uma zootecnista avícola especializada na avaliação de ovos. E irá classificar os ovos a partir de uma imagem provida como entrada no prompt.

    Deve ser análise os seguintes pontos na imagem:
    - Câmara de ar deslocada ou muito grande. No ovo fresco, a câmara de ar fica fixa em uma extremidade, pequena e estável.
    - A presença de manchas escuras, pontos ou linhas dentro do ovo pode indicar a formação de mofo ou o desenvolvimento de bactérias, tornando-o impróprio para consumo.
    - Se o interior do ovo aparece completamente escuro, sem a distinção das partes internas, é um sinal de contaminação ou deterioração.

    A imagem conterá ovos dispostos verticalmente, com um total de 15 ovos. Classifique a qualidade da casca de cada ovo usando a escala de 1 a 4,
    sendo 1 para uma qualidade  'muito boa' e 4 para 'muito ruim'. Os ovos dispostos horizontalmente estão vazios e não devem ser considerados.

    Na imagem há 15 ovos distribuidos numa matriz com 3 linhas e 5 colunas. O resultado deve ser em formato csv com as coluna do número do ovo e sua classificação
    separada por ";". O número do ovo na ordem da baixo para cima da esquerda para direita.

    Como primeira instrução, a primeira imagem com um exemplo de referência da classificação de 1 a 4 de cada ovo. A imagem conterá 4 ovos dispostos horizontalmente, sendo o mais a esquerda classificado com 1 e o mais a direita classificado como 4. Para classificar os ovos veja qual que mais se aproxima da referência proposta. Leve em consideração também a análise da ovoscopia;
    Logo após terá o esquema de uma imagem seguida de um csv, eles servirão de exemplos de algumas classificações já existentes. Cada csv é a classificação correta ser retornado de acordo com a imagem dos ovos anexada. Nesses casos, não precisa retornar nada pois de trata de casos de treinamento para você ter como referência.
    """
    return prompt
 
def load_folders(base_path, folders):

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

def load_image_to_gemini(path):
    """Função para dar upload dos dados no gemini"""
    file_gemini = LoadImage.upload_file_to_gemini(path)

    return file_gemini

def generate_training_example( df: pd.DataFrame, start, end):
    """Função que gera um texto prompt como exemplo para treinamento do modelo"""

    csv_result = to_text_csv(df,start, end)

    csv_string  = "(EXAMPLE)\n" + csv_result

    return csv_string

def to_text_csv(df: pd.DataFrame, start, end):
    """Função que pega o gabarito existente e faz um recorte de acordo com um range"""

    output = "number;classification\n"

    classification_image = df.loc[start:end-1,['OVOSCOPIA']].copy()
    classification_image['number'] = range(1,end-start+1)

    for row in classification_image.iterrows():
        output += f"{row[1].number};{row[1].OVOSCOPIA}\n"

    return output

def result_to_dataframe(string_result):

    rows = string_result.split("\n")

    columns = rows[0].split(";")

    rows_csv = list(map(lambda x: x.split(";"), rows[1:]))

    return pd.DataFrame(rows_csv, columns=columns).iloc[:15,:]

def load_all_egg_images_to_gemini(path_images):

    map_file_reference = {}
    i = 0
    for p,path in enumerate(path_images):
        start = i 
        if p%14 == 13:
            i += 5
        else:
            i += 15
        end = i
        file_gemini = load_image_to_gemini(path)
        map_file_reference[path] = [(start, end), file_gemini]

    return map_file_reference


def load_training_info():
    df_training = pd.read_excel("img\ovoscopia_treino.xlsx")
    return df_training.set_index('nome_img') 

def load_training_images():
    img_folders = ["mista", "tipo1", "tipo2", "tipo3", "tipo4"]
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
    map_file_type_reference = load_all_egg_images_to_gemini(type_images_path)
    files_gemini_types = list(map(lambda x: x[1], map_file_type_reference.values()))
    LoadImage.wait_for_files_active(files_gemini_types)
    df_training_info = load_training_info() 
    
    return map_file_type_reference, df_training_info  

def load_classification_images(folders):
    images_eggs_path = load_folders(os.getcwd(), folders)
    map_file_reference = load_all_egg_images_to_gemini(images_eggs_path)
    files_gemini = list(map(lambda x: x[1], map_file_reference.values()))
    LoadImage.wait_for_files_active(files_gemini)
   
    return map_file_reference, files_gemini



def save_prompt_to_excel():
    prompt = create_instruction()
    file_path = "./analise.xlsx"
    if isinstance(prompt, str):
        prompt = [prompt] 
    analise_df = pd.DataFrame(prompt, columns=["prompt"])
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path) 
        if existing_df.isnull().all(axis=1).iloc[0]:
            existing_df.iloc[0] = analise_df.iloc[0]
        else:
            existing_df = pd.concat([analise_df, existing_df], ignore_index=True) 
        analise_df = existing_df
    analise_df.to_excel(file_path, index=False)


def main():
    load_key()
    df = pd.read_excel("./IAGenOvoscopia/OVOSCOPIA-1RODADA - Sem 28dias.xlsx")
    folders = ["0 DIAS - FRESCOS",  "7 DIAS", "14 DIAS", "21 DIAS"]
    #folders = ["0 DIAS - FRESCOS"]
    map_file_training_reference, df_training_info = load_training_images()  
    training_images = [file_gemini for _, file_gemini in map_file_training_reference.values()]
    map_file_reference, files_gemini = load_classification_images(folders)

    instruction = create_instruction()
    egg_ia_gen = EggModelGen()
    egg_ia_gen.create_model(initial_instruction=instruction)

    examples = []
    for path in list(map_file_reference.keys()):
        example = map_file_reference[path]
        csv_example = generate_training_example(df, example[0][0], example[0][1])
        examples.append(csv_example)
        
        if len(examples) >= 14:  
            break

    chat_session = egg_ia_gen.model.start_chat(
        history=[
            {
                "role": "user",
                "parts": training_images + examples,  
            },
        ]
    )

    for i, file_gemini in enumerate(files_gemini):
        response = chat_session.send_message(file_gemini)
        result_df = result_to_dataframe(response.text)
        result_df["number"] = range((i * 15) + 1, ((i + 1) * 15) + 1)

        if not os.path.isdir("./result"):
            os.makedirs("./result")

        result_df.to_csv(f"./result/result_{(i * 15) + 1}_to_{((i + 1) * 15) + 1}.csv", sep=";", index=False)
    
    save_prompt_to_excel()


if __name__ == "__main__":
    main()