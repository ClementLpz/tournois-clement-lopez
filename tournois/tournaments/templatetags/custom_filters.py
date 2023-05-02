from django import template
import math

register = template.Library()

@register.filter
def log2(value):
    try:
        # Convert the input value to a float
        float_value = float(value)
        return math.log2(float_value)
    except ValueError:
        # Return an error message if the conversion fails
        return "Invalid input for log2 function"

@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def get_matches_for_round(matches, round):
    matches_per_round = 2 ** (round - 1)
    start = sum(2 ** i for i in range(round - 1))
    end = start + matches_per_round
    return matches[start:end]

@register.filter
def matches_for_round(matches, round_number):
    return matches.filter(round=round_number)

@register.filter
def to_int(value):
    return int(value)

@register.filter
def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
    
@register.filter
def round(matches, r):
    return [match for match in matches if match.round == r]

@register.filter
def add_half(value):
    return int(value + value/2)