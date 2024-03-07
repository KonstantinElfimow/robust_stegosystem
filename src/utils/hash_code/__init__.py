import hashlib
import io
import struct


class HashCode:
    # задаем значения по умолчанию для параметров класса
    hash_name = 'sha512_256'
    iterations = 4096
    key_len = 16

    # метод для генерации хэш-кода
    def __new__(cls, *, s: str, salt: str):
        # преобразуем и соль в байтовые строки
        s_bytes = s.encode('utf-8')
        salt_salt = salt.encode('utf-8')
        # генерируем хэш-код на основе пароля и соли с помощью функции pbkdf2_hmac из модуля hashlib
        bytes_value = hashlib.pbkdf2_hmac(
            hash_name=cls.hash_name,
            password=s_bytes,
            salt=salt_salt,
            iterations=cls.iterations,
            dklen=cls.key_len
        )

        # преобразуем байты хэш-кода в строку в шестнадцатеричном формате
        string_io = io.StringIO()
        for i in bytes_value:
            a = struct.pack('B', i).hex()
            string_io.write(a)
        hex_value = string_io.getvalue()

        # возвращаем строковое значение хэш-кода
        return hex_value
