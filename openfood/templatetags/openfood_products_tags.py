from django import template

register = template.Library()

@register.filter
def keyvalue(dict, key):    
    try:
        return dict[key]
    except KeyError:
        return ''

@register.filter
def quote(text):
    """
    Unused: just a test.
    """
    return "&laquo; {} &raquo;".format(text)