from pathlib import Path


def load_folder(folder):

    folder = Path(folder)
    files = []
    
    for file in sorted(folder.iterdir()):

        file_dict = {}
        if(file.suffix != ".md"):
            continue
        text = file.read_text(encoding="utf-8")
        
        file_dict["id"] = file.stem
        file_dict["source"] = file.name
        file_dict["text"] = text

        files.append(file_dict)

    return files
        

if __name__ == "__main__":
    load_folder('data/corpus')
        
    