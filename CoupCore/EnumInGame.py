from enum import Enum


# 游戏中的身份牌
class IDENTITY(Enum):
    DUKE = 1
    ASSASSIN = 2
    CONTESSA = 3
    CAPTAIN = 4
    AMBASSADOR = 5


# 游戏中的操作
class OPERATION(Enum):
    # 基本操作
    PASS = 1
    INCOME = 2
    FOREIGE_AID = 3
    COUP = 4
    DOUBT = 5
    BLOCK = 6
    OPEN = 7
    # 角色技能
    DUKE = 8
    ASSASSIN = 9
    CONTESSA = 10
    CAPTAIN = 11
    AMBASSADOR = 12
    AMBASSADOR_DELETE = 13


# 游戏正式开始之前和结束之后的操作
class OTHER_OPERATION(Enum):
    JOIN_GAME = 1
    GAME_FULL = 2
    # GAME_END = 3
