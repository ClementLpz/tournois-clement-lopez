from django import template
import math

register = template.Library()

@register.filter
def log2(value):
    return int(math.log2(value))

@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def get_matches_for_round(matches, round):
    start = (2 ** (round - 1)) - 1
    end = (2 ** round) - 1
    return matches[start:end]


