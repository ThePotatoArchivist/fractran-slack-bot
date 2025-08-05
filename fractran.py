from collections import defaultdict
from parse import display_output

letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 51, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def generate_latex(fractions):
    output = ""
    for fraction in fractions:
        output += "\\frac{"
        if len(fraction[0]) == 0:
            output += "1"
        for base, exponent in fraction[0].items():
            output += str(primes[letters.index(base)])
            if exponent > 1:
                output += "^{" + str(exponent) + "}"
            output += " \\cdot "
        if output.endswith(" \\cdot "):
            output = output[:-7]
        output += "}{"
        for base, exponent in fraction[1].items():
            output += str(primes[letters.index(base)])
            if exponent > 1:
                output += "^{" + str(exponent) + "}"
            output += " \\cdot "
        if output.endswith(" \\cdot "):
            output = output[:-7]
        output += "}, "
    if output.endswith(", "):
        output = output[:-2]
    return output

def non_zero_print(d):
    return str({k: v for k, v in d.items() if v != 0}) + '\n'

def do_once(i, fractions):
    output = i.copy()
    for fraction in fractions:
        n = fraction[0]
        d = fraction[1]
        good = True
        for type, num in d.items():
            if i[type] < num:
                good = False
        if good:
            for type, num in d.items():
                output[type] -= num
            for type, num in n.items():
                output[type] += num
            return output
    return "end"

def execute(input, fractions):
    output = []
    i=0
    while True:
        i += 1
        output.append(display_output(input))
        input = do_once(input, fractions)
        if input == "end" or i > 100000:
            return output, i
