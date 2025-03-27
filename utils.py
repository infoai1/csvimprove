# 

def chunk_text_with_overlap(text, chunk_size=200, overlap_ratio=0.1):
    """
    Splits the input text into chunks of roughly 'chunk_size' words,
    with each chunk overlapping the previous one by 'overlap_ratio'.
    """
    words = text.split()
    overlap = int(chunk_size * overlap_ratio)
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += (chunk_size - overlap)
    return chunks
