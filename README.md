# Projeto de Generative AI

Este projeto utiliza a API do Google Generative AI para classificar imagens de ovos. 

## Funcionalidades

- **Selecionar diferentes modelos de classificação**: Permite a escolha de um modelo para classificar os ovos.
- **Utilizar diferentes prompts**:  Os modelos podem ser executados com prompts personalizados fornecidos pelo usuário.
- **Classificar Imagens**: Carrega e classifica imagens utilizando um modelo de inteligência artificial generativa.

## Pré-requisitos

- Python 3.x

## Instalação

1. **Clone o Repositório**
   ``git clone https://github.com/lhaislla/IA_generativa``
   ``cd IA_generativa``
2. **Crie um ambiente virtual do python: `` python -m venv venv``**
3. **Durante a criação do ambiente virtual, o VSCode irá abrir um popup confirmando se você deseja utilizar o python do ambiente virtual detectado. Confirme. Em seguida, abra um novo terminal (clicando no +) para que a instalação surta efeito.**
4. **Atualize o pip: ``python -m pip install --upgrade pip``**
5. **Atualize as libs: `` pip install -r requirements.txt --upgrade``**
6. **Gerar apikey ``https://aistudio.google.com/app/apikey``**
7. **Criar um arquivo .env e adicionar chave GOOGLE_API_KEY como em env_models**
8. **Para analisar os reusultados, após a execução do modelo de sua escolha rode o ``analysis.ipynb``**

## Execução

1. O arquivo principal para executar os modelos deve ser run.py no root do projeto
2. Deve ser rodado o comando de segmentar as imagens originais em apenas um ovo. Rode `python run.py split_images`
3. Deve ser agrupados os ovos para serem utilizados nos modelos. Rode `python run.py group`
4. Caso deseja rodar o modelo Matrix mix. Rode `python run.py mixed <temperature> <prompt_path> <images_path> <result_path>`
   - temperature: 0 a 2
   - prompt_path: coloque seu prompt na pasta models/prompts e coloque nesse parâmetro o nome que foi colocado para esse prompt
   - images_path: Path das imagens de teste
   - result_path: Qual nome do csv que você quer guardar os resultados (deve ter a extensão .csv)

   Exemplo: `python run.py mixed 1.0 matrix_mix.txt ./images/treated_images/ result.csv`
5. Caso deseja rodar o modelo Unique. Rode `python run.py unique <temperature> <prompt_path> <images_path> <result_path>`
   - temperature: 0 a 2
   - prompt_path: coloque seu prompt na pasta models/prompts e coloque nesse parâmetro o nome que foi colocado para esse prompt
   - images_path: Path das imagens de teste
   - result_path: Qual nome do csv que você quer guardar os resultados (deve ter a extensão .csv)

   Exemplo: `python run.py unique 1.0 unique.txt ./images/unique_eggs/ result.csv`


6. Caso deseje rodar o modelo MultiType. Rode `python run.py multitype <prompt_file> <temperature> <test_path_dir> <result_path>`  
   - prompt_file: coloque seu prompt na pasta `models/prompts` e coloque nesse parâmetro o nome que foi colocado para esse prompt  
   - temperature: valor entre 0 e 2 que controla a criatividade do modelo  
   - test_path_dir: Path das imagens de teste, onde as imagens estão localizadas  
   - result_path: Qual nome do CSV que você quer guardar os resultados (deve ter a extensão .csv)  

   Exemplo: `python run.py multitype 1.0 multitype_longer.txt ./img/ result_multitype.csv`
