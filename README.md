# Projeto de Generative AI

Este projeto utiliza a API do Google Generative AI para gerar conteúdo textual e analisar imagens. Ele demonstra como configurar a API, gerar texto baseado em prompts e analisar imagens com um modelo específico.

## Funcionalidades

- **Carregar Chave da API**: Configura a chave da API do Google Generative AI a partir de um arquivo `.env`.
- **Gerar Texto**: Utiliza um modelo para gerar conteúdo textual com base em um prompt.
- **Histórico de Chat**: Mantém um histórico de conversas e gera respostas com base em um prompt, exibindo o histórico completo.
- **Analisar Imagem**: Carrega e analisa imagens usando o modelo de geração de conteúdo.

## Pré-requisitos

- Python 3.x
- Bibliotecas Python: `python-dotenv`, `google-generativeai`, `Pillow`, `IPython`

## Instalação

1. **Clone o Repositório**
   ``git clone https://github.com/lhaislla/IA_generativa``
   ``cd IA_generativa``
2. **Crie um ambiente virtual do python: `` python -m venv venv``**
3. **Durante a criação do ambiente virtual, o VSCode irá abrir um popup confirmando se você deseja utilizar o python do ambiente virtual detectado. Confirme. Em seguida, abra um novo terminal (clicando no +) para que a instalação surta efeito.**
4. **Atualize o pip: ``python -m pip install --upgrade pip``**
6. **Atualize as libs: `` -r requirements.txt --upgrade``**
7. **Rode o sistema: ``python .\ia_generative.py``**
