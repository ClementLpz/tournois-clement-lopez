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
    matches_per_round = 2 ** (round - 1)
    start = sum(2 ** i for i in range(round - 1))
    end = start + matches_per_round
    return matches[start:end]
