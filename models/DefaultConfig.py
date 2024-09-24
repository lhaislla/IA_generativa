import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as gemini
import pandas as pd
from models.modules.LoadImage import LoadImage

class DefaultConfig:

    def __init__(self):

        self.result_dataframe = pd.read_excel("./IAGenOvoscopia/OVOSCOPIA-1RODADA - Sem 28dias.xlsx")

        self.GEMINI_KEY = self.load_key()

    def load_key(self):
        _ = load_dotenv(find_dotenv())
        chave = os.getenv("GOOGLE_API_KEY")
        gemini.configure(api_key=chave)
        print("Chave reconhecida com sucesso!")
        return chave
    
    def create_column_reference_dataframe(self, new_column):
        self.result_dataframe[new_column] = None

    def update_value_rerence_dataframe(self, index, column, value):
        self.result_dataframe.loc[index,column] = value
    
    def add_item_to_dataframe(self, df, values):
        df = df.append(values, ignore_index=True)

        return df
    
    def load_image_to_gemini(self, path):
        """Função para dar upload dos dados no gemini"""
        file_gemini = LoadImage.upload_file_to_gemini(path)

        return file_gemini
    
    def load_all_egg_images_to_gemini(self, path_images):

        map_file_reference = {}

        i = 0

        for p,path in enumerate(path_images):
            start = i 

            if p%14 == 13:
                i += 5
            else:
                i += 15

            end = i

            file_gemini = self.load_image_to_gemini(path)
            map_file_reference[path] = [(start, end), file_gemini]

        return map_file_reference
    
    def result_to_dataframe(self, string_result):

        rows = string_result.split("\n")

        columns = rows[0].split(";")

        rows_csv = list(map(lambda x: x.split(";"), rows[1:]))

        return pd.DataFrame(rows_csv, columns=columns)