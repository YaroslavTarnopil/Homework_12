import secrets

# Генеруємо випадковий секретний ключ
key = secrets.token_hex(32)
print(key)
