from django import template

register = template.Library()

@register.filter
def get_option(mcq, option_letter):
    """Get the option text for a given option letter (A, B, C, D)."""
    return getattr(mcq, f'option_{option_letter.lower()}') 