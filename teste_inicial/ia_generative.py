import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as gemini
from IPython.display import Image as IPImage
from PIL import Image

def carrega_chave():  
    _ = load_dotenv(find_dotenv())
    chave = os.getenv("GOOGLE_API_KEY")
    gemini.configure(api_key=chave)  
    print("Chave reconhecida com sucesso!")
    return chave

def verifica_chave(): 
    return find_dotenv()

def list_models():
    modelos = gemini.list_models() 
    for model in modelos:
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)



def config_models():
    gemini.GenerativeModel('gemini-1.5-flash',generation_config=gemini.GenerationConfig(max_output_tokens=2000,temperature=0.9))

def gerar_texto(prompt):
        model = gemini.GenerativeModel('gemini-1.5-flash') 
        resposta = model.generate_content(prompt)
        return resposta
    
def chat_history(prompt, history=None):
    if history is None:
        history = []
    
    model = gemini.GenerativeModel('gemini-1.5-flash')
    history.append({"role": "user", "content": prompt})
    resposta = model.generate_content(prompt)
    history.append({"role": "assistant", "content": resposta})
    for message in history:
        print(f"{message['role'].capitalize()}: {message['content']}")
    
    return resposta, history

def get_image():
        img = Image.open(r'img\ovo.png')
        return img

def analise_imagem(img):
        model = gemini.GenerativeModel('gemini-1.5-flash') 
        resposta =  model.generate_content(img)
        return resposta



def main():
    """Função principal para executar o fluxo de trabalho.""" 
    chave = carrega_chave()
    
    #print(dir(gemini))
    list_models()
    
    # Usando só texto
    #prompt = "Explique porque os gatos caem em pé"
    # resultado = gerar_texto(prompt)
    # print(resultado)
    
    # Usando  imagem
    # img = get_image()
    # if img:
    #     img.show()
    #resultado = analise_imagem(img)
    #print(resultado)
    
    #chat_history(prompt,None)

if __name__ == "__main__":
    main()