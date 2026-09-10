test = """
import random

def test_func():
    return random.randint(1, 9)
"""

exec(test)

print(test_func())