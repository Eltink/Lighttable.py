import os
import shutil

def copia_arquivo(source_dir, filename, destination_dir, filetype='jpg', delay=10):
    """Copies a file from a source location to a destination location.

    Parameters:
    - src:      a string representing the source file path.
    - filename: a string representing the name of the file.
    - dst:      a string representing the destination file path.
    - filetype: a string representing the file type. Default value is 'jpg'.
    - delay:    an integer representing the delay time in seconds. Default value is 10.

    Returns: None
    """

    caminho_imagem_base_de_dados = os.path.join(source_dir, filename)  # complete file location
    # testing if all necessary paths exists
    for test_case in [source_dir, destination_dir, caminho_imagem_base_de_dados]:
        if not os.path.exists(test_case):
            print(f"{test_case} doesnt exist")  # f: replace any {} with that variable.
            return

    shutil.copy(caminho_imagem_base_de_dados, destination_dir)

    return
