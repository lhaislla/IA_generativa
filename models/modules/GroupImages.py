import pandas as pd
import numpy as np

from PIL import Image
import os
import random

def redimensionar_imagens(imagens, tamanho_padrao):
    imagens_redimensionadas = []
    for imagem in imagens:
        img = Image.open(imagem)
        img = img.resize(tamanho_padrao)
        imagens_redimensionadas.append(img)
    return imagens_redimensionadas

def juntar_imagens_em_matriz(imagens, linhas, colunas, tamanho_padrao):
    imagens_redimensionadas = redimensionar_imagens(imagens, tamanho_padrao)

    largura_imagem, altura_imagem = tamanho_padrao

    largura_total = colunas * largura_imagem
    altura_total = linhas * altura_imagem
    
    nova_imagem = Image.new('RGB', (largura_total, altura_total))

    for i in range(linhas):
        for j in range(colunas):
            idx = i * colunas + j
            if idx < len(imagens_redimensionadas):
                x_offset = j * largura_imagem
                y_offset = i * altura_imagem
                nova_imagem.paste(imagens_redimensionadas[idx], (x_offset, y_offset))
    
    return nova_imagem

def get_sample_one_type(df, type, amount):

    if amount % 2 != 0:
        raise Exception('A quantidade deve ser par')
    
    filter_df = df[df['OVOSCOPIA'] == type]

    if amount > filter_df.shape[0]:
        raise Exception(f'A quantidade maior que a quantidade de ovo do tipo {type}')

    return filter_df.sample(amount)


def get_sample_mixed_type(df, amount_each_type):

    sample = []
    
    for type in range(1,5):
        filter_df = df[df['OVOSCOPIA'] == type]

        for item in filter_df.sample(amount_each_type).apply(lambda x: [x['path_image'], type], axis = 1).tolist():
            sample.append(item)
    random.shuffle(sample)
    return sample

def load_real_classification():
    real_label_eggs = pd.read_excel(os.path.join(os.getcwd(), 'IAGenOvoscopia', 'OVOSCOPIA-1RODADA - Sem 28dias.xlsx'))
    real_label_eggs.columns = ["N_OVO", "OVOSCOPIA", 'TEMPO', 'observações']

    return real_label_eggs

df_eggs = load_real_classification()
df_eggs["path_image"] = [os.path.join(os.getcwd(), "images", "unique_eggs", f"ovo_{i}.jpg") for i in range(1,801)]

tamanho_padrao = (329,412)


if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'types', 'type 1'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'types', 'type 1'))

if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'types', 'type 2'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'types', 'type 2'))

if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'types', 'type 3'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'types', 'type 3'))

if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'types', 'type 4'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'types', 'type 4'))

import shutil

for item in df_eggs.iterrows():
    shutil.copy(item[1]['path_image'], os.path.join(os.getcwd(), "images", "types", f'type { item[1]['OVOSCOPIA']}', item[1]['path_image'].split('\\')[-1]))


# Creating 5x4 one type

if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'matrix_unique_type', '5x4'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'matrix_unique_type', '5x4'))


for type in range(1,5):
    sample_20_eggs = get_sample_one_type(df_eggs, type, 20)

    image = juntar_imagens_em_matriz(sample_20_eggs['path_image'].tolist(), 4, 5, tamanho_padrao)
    image.save(os.path.join(os.getcwd(), "images", "matrix_unique_type", '5x4', f"type_{type}.jpg"))

# Creating 5x4 mixed type

if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'matrix_mixed_type', '5x4'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'matrix_mixed_type', '5x4'))

for i in range(1,6):

    list_sample_20_eggs = get_sample_mixed_type(df_eggs, 5)

    eggs_mixed = pd.DataFrame([i+1 for i in range(len(list_sample_20_eggs))], columns=['number'])
    eggs_mixed['classification'] = list(map(lambda x: x[1], list_sample_20_eggs))

    eggs_mixed.to_csv(os.path.join(os.getcwd(), "images", "matrix_mixed_type", '5x4', f"reference_{i}.csv"), sep=';', index=False)

    path_images = list(map(lambda x: x[0], list_sample_20_eggs))

    image = juntar_imagens_em_matriz(path_images, 4, 5, tamanho_padrao)
    image.save(os.path.join(os.getcwd(), "images", "matrix_mixed_type", '5x4', f"mixed_type_{i}.jpg"))
    

# Creating 2x2 one type

if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'matrix_unique_type', '2x2'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'matrix_unique_type', '2x2'))


for type in range(1,5):
    sample_4_eggs = get_sample_one_type(df_eggs, type, 4)

    image = juntar_imagens_em_matriz(sample_4_eggs['path_image'].tolist(), 2, 2, tamanho_padrao)
    image.save(os.path.join(os.getcwd(), "images", "matrix_unique_type", '2x2', f"type_{type}.jpg"))

# Creating 5x4 test types
if (not os.path.isdir(os.path.join(os.getcwd(), 'images', 'treated_images'))):
    os.makedirs(os.path.join(os.getcwd(), 'images', 'treated_images'))

for i in range(df_eggs.shape[0] // 20):
    
    imagens = df_eggs.loc[i*20:(i+1)*20 - 1, 'path_image'].tolist()

    imagem_unica = juntar_imagens_em_matriz(imagens, 4, 5, tamanho_padrao)

    imagem_unica.save(os.path.join(os.getcwd(), "images", "treated_images", f"sample_{i+1}.jpg"))