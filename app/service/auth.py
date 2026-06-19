import bcrypt


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    Обрезает пароль до 72 байт (ограничение алгоритма bcrypt).
    """
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8")[:72],
        hashed_password.encode("utf-8"),
    )