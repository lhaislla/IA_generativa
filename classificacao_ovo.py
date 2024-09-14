import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as gemini
from PIL import Image
import io

def load_key():
    _ = load_dotenv(find_dotenv())
    chave = os.getenv("GOOGLE_API_KEY")
    gemini.configure(api_key=chave)
    print("Chave reconhecida com sucesso!")
    return chave

def get_image(image_path):
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        print(f"Erro ao abrir a imagem {image_path}: {e}")
        return None

def image_to_bytes(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    return img_byte_arr.getvalue()

def create_prompt(image_path):
    prompt =  (
        f"Você é uma zootecnista avícola especializada na avaliação de ovos. Analise a imagem '{image_path}'. "
        f"A imagem mostra ovos dispostos verticalmente, com um total de 15 ovos. Classifique a qualidade da casca de cada ovo usando a escala de 1 a 4, "
        f"sendo 1 para 'muito ruim' e 4 para 'muito bom'. Os ovos dispostos horizontalmente estão vazios e não devem ser considerados. "
        f"Considere aspectos como a integridade da casca, presença de rachaduras, e uniformidade. Forneça uma análise detalhada e recomendações de melhorias se necessário."
        f" A saída deve conter o número do ovo N_OVO; a OVOSCOPIA; o TEMPO e observações."
    )
    return prompt

def analitics_img(image_path):
    img = get_image(image_path)
    if img:
        img_bytes = image_to_bytes(img)
        model = gemini.GenerativeModel('gemini-1.5-flash')
        
        prompt = create_prompt(image_path)
        
        resposta = model.generate_content(prompt)
        return resposta
    else:
        return "Imagem não carregada."

def load_folders(base_path, folders):
    resultados = {}
    for folder in folders:
        folder_path = os.path.join(base_path, folder, "Fotos bluebox")
        if not os.path.exists(folder_path):
            print(f"Pasta não encontrada: {folder_path}")
            continue

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, file_name)
                print(f"Processando imagem: {image_path}")
                resultado = analitics_img(image_path)
                resultados[file_name] = resultado
    
    return resultados

def gerar_relatorio(resultados):
    relatorio = "Relatório de Classificação de Ovos:\n\n"
    
    for imagem, resultado in resultados.items():
        relatorio += f"Imagem: {imagem}\nResultado: {resultado}\n\n"
    
    return relatorio

def main():
    """Função principal para executar o fluxo de trabalho."""
    load_key()
    base_path = r"C:\Users\lhais\OneDrive\Documentos\Mestrado\IA_generativa\IAGenOvoscopia"
    #folders = ["0 DIAS - FRESCOS", "14 DIAS", "21 DIAS", "7 DIAS"]
    folders = ["0 DIAS - FRESCOS"]
    
    resultados = load_folders(base_path, folders)
    relatorio = gerar_relatorio(resultados)
    print(relatorio)

if __name__ == "__main__":
    main()
