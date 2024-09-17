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
    Contexto:A ovoscopia é um método técnico utilizado na inspeção da qualidade interna e externa dos ovos, sendo amplamente empregada em incubatórios e na produção comercial de ovos. Este processo envolve a passagem de luz intensa através da casca do ovo, permitindo ao avaliador observar detalhes internos e detectar possíveis defeitos. 
    Por meio dessa técnica, o avaliador pode identificar fissuras na casca, irregularidades no desenvolvimento do embrião e anomalias na câmara de ar. A análise da câmara de ar é crucial, pois ela deve estar localizada de forma estável em uma das extremidades do ovo e apresentar um tamanho adequado. Desvios desse padrão podem indicar problemas de armazenamento ou deterioração.
    Além disso, a ovoscopia permite observar a presença de manchas internas, indicativas de contaminação por fungos ou bactérias, e distinguir a opacidade interna, que pode sinalizar contaminação ou deterioração avançada, caso as partes internas do ovo não sejam visíveis. Dessa forma, a técnica é essencial para garantir que os ovos sejam adequados para consumo ou incubação.

    Persona: Você deve assumir o papel de uma zootecnista avícola especialista em avaliação de ovos, responsável por analisar imagens de ovos fornecidas e classificá-los com base nas características observadas. A tarefa consiste em avaliar a qualidade da casca e outras características internas utilizando a técnica de ovoscopia.

    Pontos a serem analisados:
    - Câmara de ar: Uma câmara de ar deslocada ou muito grande pode indicar perda de qualidade. Em ovos frescos, a câmara de ar deve estar pequena e localizada em uma das extremidades.
    - Manchas internas: Manchas escuras, pontos ou linhas no interior do ovo podem sugerir a presença de mofo ou bactérias, tornando-o impróprio para consumo.
    - Opacidade interna: Se o ovo apresentar um interior completamente escuro, sem distinção clara das partes internas, isso é um indício de contaminação ou deterioração.

    Critérios de análise:
    1. A imagem conterá 15 ovos dispostos verticalmente em uma matriz de 3 linhas por 5 colunas.
    2. Ignore os ovos dispostos horizontalmente, pois estão vazios e não precisam ser avaliados.
    3. Para cada ovo na matriz, classifique a qualidade da casca de acordo com a seguinte escala de 1 a 4:
    - 1: Qualidade muito boa.
    - 2: Qualidade boa.
    - 3: Qualidade regular.
    - 4: Qualidade ruim.
    4. A numeração dos ovos segue a ordem de baixo para cima e da esquerda para a direita.

    Formato do resultado:
    - O resultado da análise deve ser gerado em um arquivo CSV com duas colunas:
    - Número do ovo: A ordem dos ovos conforme descrita.
    - Classificação: A nota da qualidade da casca (1 a 4).
    - O formato CSV deve utilizar o ponto e vírgula ";" como separador, conforme o exemplo abaixo:
    ovo1;1
    ovo2;3
    ovo3;2
    
    Exemplo de referência:
    1. Para facilitar a classificação, você receberá uma imagem inicial de referência, contendo 4 ovos dispostos horizontalmente, com as seguintes classificações:
    - O ovo mais à esquerda será classificado como 1 (qualidade muito boa).
    - O ovo mais à direita será classificado como 4 (qualidade ruim).
    2. Utilize essa imagem como base comparativa para as avaliações posteriores. Além da comparação visual, considere as observações de ovoscopia mencionadas para a classificação final.

    Esquemas de treinamento:
    - Você também receberá imagens de exemplo seguidas por arquivos CSV contendo a classificação correta de cada ovo. Esses exemplos servirão para familiarização e não requerem respostas, pois são parte do treinamento para a tarefa principal.

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

    # Carregar as imagens base de classificações
    base_images = ["img/Imagem base.png", "img/Imagem base_2.png", "img/Imagem base_3.png"]
    base_image_references = [load_image_to_gemini(os.path.join(os.getcwd(), img)) for img in base_images]
    map_file_reference = load_all_egg_images_to_gemini(images_eggs_path)
    files_gemini = list(map(lambda x: x[1], map_file_reference.values()))
    LoadImage.wait_for_files_active(base_image_references + files_gemini)
    instruction = create_instruction()
    egg_ia_gen = EggModelGen()
    egg_ia_gen.create_model(initial_instruction=instruction)
    example = map_file_reference[images_eggs_path[0]]
    chat_session = egg_ia_gen.model.start_chat(
        history=[
            {
                "role": "user",
                "parts": base_image_references + [
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
