from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter
@stringfilter
def grep(value, arg):
    pattern = re.compile(arg)
    lines = [line for line in re.split(r'[\r\n]', value) if pattern.search(line)]
    return '\n'.join(lines)
grep.needs_autoescape = True

@register.filter
@stringfilter
def grepv(value, arg, autoescape=None):
    pattern = re.compile(arg)
    lines = [line for line in re.split(r'[\r\n]', value) if not pattern.search(line)]
    return '\n'.join(lines)
grepv.needs_autoescape = True
    
