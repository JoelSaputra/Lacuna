from pathlib import Path


def load_folder(folder):
    folder = Path(folder)
    for file in sorted(folder.iterdir()):
        print(file)




if __name__ == "__main__":
    load_folder('data/corpus')
        
    