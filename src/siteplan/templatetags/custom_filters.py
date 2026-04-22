from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def excerpt(value, num_words=140):
    text = strip_tags(value)
    words = text.split()[:num_words]
    return ' '.join(words) + ' ...'