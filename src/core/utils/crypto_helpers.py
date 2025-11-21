import hashlib
import json

def calculate_hash(data):
    """
    Вычисляет SHA-256 хеш для переданных данных.

    Args:
        data: Объект Python (обычно dict или list), который нужно захешировать.

    Returns:
        str: HEX-представление SHA-256 хеша.
    """
    # Преобразуем данные в строку JSON с сортировкой ключей для детерминированности
    json_string = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(json_string).hexdigest()

def validate_hash(hash_string, data):
    """
    Проверяет, соответствует ли переданный хеш вычисленному хешу данных.

    Args:
        hash_string (str): Предполагаемый хеш.
        data: Объект Python, для которого вычисляется хеш.

    Returns:
        bool: True, если хеши совпадают, иначе False.
    """
    computed_hash = calculate_hash(data)
    return computed_hash == hash_string
