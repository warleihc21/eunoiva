from django import template

register = template.Library()

@register.filter
def get_initials(value):
    """Retorna as iniciais de um nome."""
    if not value:
        return ''  # Retorna uma string vazia se o valor for None ou vazio
    names = value.split()
    initials = ''.join(name[0].upper() for name in names)
    return initials