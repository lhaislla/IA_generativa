import os
import sys

from models.Unique import main as mainUnique
from models.Matrix_mix import main as mainMixed




if __name__ == "__main__":

    print(sys.argv)
    if len(sys.argv) < 2:
        raise Exception("Deve-se conter pelo menos comando")

    command = sys.argv[1]

    if command == "split_images":
        import models.modules.split_images

    if command == "group":
        import models.modules.GroupImages

    if command == "mixed":
        if len(sys.argv) < 6:
            raise Exception("Deve-se conter 6 entradas")
        
        temperature = float(sys.argv[2])
        prompt_path = sys.argv[3]
        images_path = sys.argv[4]
        result_path = sys.argv[5]

        mainMixed(temperature,prompt_path, images_path, result_path)

    if command == "unique":
        if len(sys.argv) < 6:
            raise Exception("Deve-se conter 6 entradas")
        
        temperature = float(sys.argv[2])
        prompt_path = sys.argv[3]
        images_path = sys.argv[4]
        result_path = sys.argv[5]

        mainUnique(temperature, prompt_path, images_path, result_path)