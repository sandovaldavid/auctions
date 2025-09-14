from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def addclass(field, css):
    """Add CSS class to form field"""
    return field.as_widget(attrs={"class": css})
