import math
import random  # unused import to test detection

def process_data(numbers):
    total = 0
    for n in numbers:
        for i in range(3):   # nested loop → deep nesting
            total += n * i
    return total

def long_function_example():
    # intentionally long function (more than 30 lines)
    data = []
    for i in range(40):
        data.append(i ** 2)
    result = sum(data)
    return result

x = 10  # unused variable
