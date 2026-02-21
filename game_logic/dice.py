import random

def roll(dice_string: str) -> int:
    """'NdM' 형태의 문자열을 받아 주사위를 굴린 합계를 반환합니다. (예: '2d6')"""
    num_dice, die_type = map(int, dice_string.split('d'))
    return sum(random.randint(1, die_type) for _ in range(num_dice))
