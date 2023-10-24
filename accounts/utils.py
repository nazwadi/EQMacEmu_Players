from hashlib import sha1


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sha1_password(password: str) -> str:
    """Returns the sha1 hash of a plain text password

    The TAKP database stores the sha1 hash of account passwords
    """
    message = sha1()
    message.update(bytes(password,
                     encoding="utf8"))
    password = message.hexdigest()
    return password
