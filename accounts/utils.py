import ipaddress
from hashlib import sha1

_PRIVATE_NETWORKS = [
    ipaddress.ip_network(cidr) for cidr in (
        '127.0.0.0/8',
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
        '169.254.0.0/16',  # link-local
        '::1/128',
        'fc00::/7',
    )
]


def _is_private(ip_str):
    try:
        addr = ipaddress.ip_address(ip_str.strip())
        return any(addr in net for net in _PRIVATE_NETWORKS)
    except ValueError:
        return True  # treat unparseable values as untrusted


def get_client_ip(request):
    # Cloudflare: set by CF itself, not spoofable when traffic routes through CF
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP', '').strip()
    if cf_ip and not _is_private(cf_ip):
        return cf_ip

    # nginx: commonly set via proxy_set_header X-Real-IP $remote_addr
    real_ip = request.META.get('HTTP_X_REAL_IP', '').strip()
    if real_ip and not _is_private(real_ip):
        return real_ip

    # Load balancers / generic proxies: scan left-to-right for first public IP
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    for ip in xff.split(','):
        ip = ip.strip()
        if ip and not _is_private(ip):
            return ip

    return request.META.get('REMOTE_ADDR', '')


def sha1_password(password: str) -> str:
    """Returns the sha1 hash of a plain text password

    The TAKP database stores the sha1 hash of account passwords
    """
    message = sha1()
    message.update(bytes(password,
                   encoding="utf8"))
    password = message.hexdigest()
    return password
