CHUNK_SIZE = 400
OVERLAP = 40



def split_paragraph(text: str):
    paragraph = text.split("\n\n")
    
    return [p.strip() for p in paragraph if p.strip()]




def chunk(text:str):
    chunk = []
    current = []
    current_words = 0

    paragraphs = split_paragraph(text)

    for paragraph in paragraphs:
        num_words = len(paragraph.split())

        if current and num_words + current_words > CHUNK_SIZE:
            chunk.append("\n\n".join(current))
            current = []
            current_words = 0
            
    
        current.append(paragraph)
        current_words += num_words

    
    if current: 
        chunk.append("\n\n".join(current))

    return chunk   
