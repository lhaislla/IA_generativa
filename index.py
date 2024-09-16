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

    csv_result += "(EXAMPLE)\n" + csv_result

    return csv_result

def to_text_csv(df: pd.DataFrame, start, end):
    """Função que pega o gabarito existente e faz um recorte de acordo com um range"""

    output = "number;classification\n"

    classification_image = df.loc[start:end,['OVOSCOPIA']].copy()
    classification_image['number'] = range(1,16)

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

    for path in path_images:
        start, end = (i*15)+1, (i+1)*15

        file_gemini = load_image_to_gemini(path)
        map_file_reference[path] = [(start, end), file_gemini]

    return map_file_reference

def main():
    """Função principal para executar o fluxo de trabalho."""

    load_key()

    df = pd.read_excel("./IAGenOvoscopia/OVOSCOPIA-1RODADA - Sem 28dias.xlsx")
    folders = ["0 DIAS - FRESCOS", "14 DIAS", "21 DIAS", "7 DIAS"]
    
    # Pegar todos os paths das imagens
    images_eggs_path = load_folders(os.getcwd(), folders)

    # Dar upload das imagem base das classificações
    first_image_reference = load_image_to_gemini( os.path.join(os.getcwd(), "img/Imagem base.png"))
    # Dar upload nas demais imagens que serão utilizadas no projeto. É retornado um dicionário onde a chave é o path, e o valor é um array com o primeiro
    # index tendo informação do intervalo da numeração dos ovos que a imagem se encontra, o segundo index é o file gerado pelo gemini ao dar upload 
    map_file_reference = load_all_egg_images_to_gemini(images_eggs_path)


    files_gemini = list(map(lambda x: x[1], map_file_reference.values()))

    #Aguardar o upload
    LoadImage.wait_for_files_active([first_image_reference] + files_gemini)

    # Pegar instrução inicial para o modelo
    instruction = create_instruction()

    egg_ia_gen = EggModelGen()

    egg_ia_gen.create_model(initial_instruction=instruction)

    #Carregar o primeira imagem como exemplo
    example = map_file_reference[images_eggs_path[0]]

    chat_session = egg_ia_gen.model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                   first_image_reference,
                   example[1],
                   generate_training_example(df, example[0][0] - 1, example[0][1] - 1)
                ],
            },
        ]
    )

    #Guardando o resultado de cada imagem em um csv
    for i,file_gemini in enumerate(files_gemini):
        response = chat_session.send_message(file_gemini)

        result_df = result_to_dataframe(response.text)
        result_df["number"] = range((i*15) + 1, ((i+1)*15) + 1)

        if (not os.path.isdir("./result")):
            os.makedirs("./result")

        result_df.to_csv(f"./result/result_{(i*15) + 1}_to_{((i+1)*15) + 1}.csv", sep=";",index=False)


if __name__ == "__main__":
    main()
