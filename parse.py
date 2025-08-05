from collections import defaultdict

def parse_factor(frac: str):
    split = frac.split('^')
    return split[0], 1 if len(split) < 2 else int(split[1])

def parse_factors(factors: str):
    return defaultdict(int, dict(parse_factor(c) for c in factors.split('*')))

def parse_fraction(fracstr: str):
    return [parse_factors(b) for b in fracstr.split('/')]

def parse(strinput: str):
    *fractions, input = strinput.replace(',', '').split(' ')
    
    return [parse_fraction(a) for a in fractions], parse_factors(input)

def parse_program(strinput: str):
    return [parse_fraction(a) for a in strinput.split(' ')]

def display_output(output: dict[str, int]):
    return '*'.join(base if power == 1 else f'{base}^{power}' for base, power in output.items() if power != 0)
    