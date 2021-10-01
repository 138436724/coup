"""
玩家角色信息:
    币数目、身份牌、身份牌数目
    玩家的技能: 本身技能和身份技能
    本身技能: 收入、援助、质疑、政变
    角色技能: 公爵(税收、阻止)、队长(抢夺、阻止)、大使(换牌，阻止)、刺客(刺杀)、夫人(阻止)
"""


class Player:
    coins = 2
    close_identities = []
    open_identities = ["XX", "XX"]

    def __init__(self):
        self.coins = 2
        self.close_identities.clear()
        self.open_identities = ["XX", "XX"]

    # 收入
    async def get_one_coin(self):
        self.coins += 1

    # 援助
    async def get_two_coins(self):
        self.coins += 2

    # 政变
    async def coup(self):
        self.coins -= 7

    # 公爵(税收、阻止)
    async def get_three_coins(self):
        self.coins += 3

    # 队长(抢夺、阻止)
    async def rob_two_coins(self, num):
        self.coins += num

    async def was_rob_coins(self):
        if self.coins >= 2:
            self.coins -= 2
            return 2
        elif self.coins == 1:
            self.coins = 0
            return 1
        else:
            self.coins = 0
            return 0

    # 大使(换牌，阻止)
    async def change_two_cards(self, cards: list):
        self.close_identities += cards
        return self.close_identities

    # 删牌
    async def delete_two_cards(self, num):
        m, n = max(num), min(num)
        if (self.close_identities[m - 1] != "XX") and (self.close_identities[n - 1] != "XX"):
            card = [self.close_identities.pop(n - 1), self.close_identities.pop(m - 1)]
            return card
        else:
            return None

    # 刺客(刺杀)
    async def stab(self):
        self.coins -= 3
