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
    # 角色技能
    DUKE = 6
    DUKE_BLOCK = 7
    ASSASSIN = 8
    CONTESSA = 9
    CAPTAIN = 10
    CAPTAIN_BLOCK = 11
    AMBASSADOR = 12
    AMBASSADOR_BLOCK = 13


# 游戏正式开始之前和结束之后的操作
class OTHER_OPERATION(Enum):
    JOIN_GAME = 1
    GAME_FULL = 2
    # GAME_END = 3
