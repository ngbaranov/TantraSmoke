MAX_MESSAGE_LENGTH = 4000  # немного меньше лимита Telegram

def chunk_text(text, max_length=4000):
    """Разбиваем текст на части до 4000 символов (лимит Telegram)."""
    lines = text.split('\n')
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += "\n" + line if current_chunk else line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
