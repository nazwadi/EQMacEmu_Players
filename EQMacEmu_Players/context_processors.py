def navigation_context(request):
    """Add navigation context to all templates"""
    nav_section = 'database'  # default

    # Determine nav section from URL
    if 'items' in request.path or 'npcs' in request.path:
        nav_section = 'database'
    elif 'magelo' in request.path or 'transfer' in request.path:
        nav_section = 'tools'
    elif 'accounts' in request.path:
        nav_section = 'account'

    return {
        'nav_section': nav_section,
        'nav_page': request.resolver_match.url_name if request.resolver_match else None,
    }