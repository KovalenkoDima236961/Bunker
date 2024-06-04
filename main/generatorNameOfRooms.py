import random


def generate_random_name(length=10):
    all_char = 'qwertyuioplkjhgfdsazxcvbnm1234567890'
    return ''.join(random.choice(all_char) for _ in range(length))
