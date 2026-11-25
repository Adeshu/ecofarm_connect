from django import template

register = template.Library()

@register.filter
def split(value, key):
    """Splits the string by the given key"""
    return value.split(key)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return None
    

@register.filter
def index(sequence, position):
    try:
        return sequence[int(position)]
    except (IndexError, ValueError, TypeError):
        return None


@register.filter
def trim(value):  # sourcery skip: assign-if-exp, reintroduce-else
    if isinstance(value, str):
        return value.strip()
    return value



@register.filter
def get_item(dictionary, key):  # sourcery skip: assign-if-exp, reintroduce-else
    """Get an item from a dictionary"""
    if dictionary is None:
        return None
    return dictionary.get(key)
