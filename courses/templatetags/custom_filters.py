from django import template

register = template.Library()

@register.filter
def index(value, arg):
    """Return the list item at the given index."""
    try:
        return value[int(arg)]
    except (IndexError, TypeError, ValueError):
        return None

@register.filter
def split(value, arg):
    """Split string by delimiter"""
    return value.split(arg)

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
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value

