"""
玩家角色信息: 币数目、身份牌

角色技能应该由Master调度，Player只需要提供对币和身份的操作即可

很符合现实，上帝进行调度，玩家只关心自己
"""
from .ExceptionInGame import NotAGoodNumber, NotAGoodType
from .EnumInGame import IDENTITY


class Player:
    async def __init__(self, cards: list):
        """
        构造函数
        @parama: cards 身份牌列表
        @return: None
        """
        if type(cards) != list:
            raise NotAGoodType("参数应该是列表类型")
        self.__coins = 2  # 初始2个金币
        self.__ID_cards = cards  # 初始身份牌
        self.__open_ID_cards = []  # 初始无翻开的身份牌, 需要专门的函数处理成字符串返回给master

    async def set_cards(self, cards: list):
        """
        为大使提供的操作
        @parama: cards 身份牌列表
        @return: None
        """
        if type(cards) != list:
            raise NotAGoodType("参数应该是列表类型")
        self.__ID_cards = cards

    async def open_cards(self, num: int):
        """
        需要开牌的操作
        @parama: num 开第几张牌
        @return: None
        """
        if num >= len(self.__ID_cards):
            raise NotAGoodNumber("应该提供一个不超过当前玩家未翻开牌数量的数")

        self.__open_ID_cards = [self.__ID_cards.pop(num)]

    async def ask_card(self, card: IDENTITY):
        """
        被质疑的时候被询问是否有某张牌
        @parama: card 卡牌
        @return: bool
        """
        if type(card) != IDENTITY:
            raise NotAGoodType("参数应该是枚举类型")
        if card in self.__ID_cards:
            return True
        else:
            return False

    async def get_cards(self):
        """
        查询现在打开的身份牌
        @parama: None
        @return: None
        """
        return self.__open_ID_cards

    async def get_coins(self):
        """
        查询现在玩家的金币数
        @parama: None
        @return: None
        """
        return self.__coins

    async def add_coins(self, num: int):
        """
        角色收入
        @parama: num 收入的金币数量
        @return: None
        """
        if num not in [1, 2, 3]:
            raise NotAGoodNumber("角色收入应该是1, 2, 3中的一个数")
        self.__coins += num

    async def sub_coins(self, num: int):
        """
        角色支付
        @parama: num 收入的金币数量
        @return: None
        """
        if num not in [1, 2, 3, 7]:
            raise NotAGoodNumber("角色支出应该是1, 2, 3, 7中的一个数")
        self.__coins -= num

    async def inquiry_all(self):
        """
        查询角色的公开信息
        @parama: None
        @return: str
        """
        return f"币：{self.__coins}，身份牌：" + " ".join(self.__open_ID_cards)

    # 主动技能:
    #     收入
    #     援助
    #     质疑
    #     政变
    #
    # 被动能力:
    #     开牌
    #     查询
    #
    # 角色技能:
    #     公爵(税收、阻止)
    #     队长(抢夺、阻止)
    #     大使(换牌、阻止、删牌)
    #     刺客(刺杀)
    #     夫人(阻止)

    # # 收入
    # async def income(self):
    #     self.__coins += 1
    #
    # # 援助
    # async def assistance(self):
    #     self.__coins += 2
    #
    # # 质疑
    # async def doubt(self):
    #     pass
    #
    # # 政变
    # async def coup(self):
    #     self.__coins -= 7
    #
    # # 开牌
    # async def expose(self, num: int):
    #     num -= 1
    #     card = self.__ID_cards.pop(num)
    #     self.__open_ID_cards.append(card)
    #
    # # 查询
    # async def inquiry(self):
    #     return " ".join(self.__open_ID_cards)
    #
    # # 公爵(税收、阻止)
    # async def taxation(self):
    #     self.__coins += 3
    #
    # # 队长(抢夺、阻止)
    # async def snatch(self, num: int):
    #     self.__coins += num
    #
    # async def was_snatch(self):
    #     if self.__coins >= 2:
    #         self.__coins -= 2
    #         return 2
    #     elif self.__coins == 1:
    #         self.__coins = 0
    #         return 1
    #     else:
    #         self.__coins = 0
    #         return 0
    #
    # # 大使(换牌、阻止、删牌)
    # async def replace(self, cards: list):
    #     self.__ID_cards += cards
    #     return self.__ID_cards
    #
    # async def discard(self, num: int):
    #     num -= 1
    #     # 这张牌是被换走的牌
    #     card = self.__ID_cards.pop(num)
    #     return card
    #     # m, n = max(num), min(num)
    #     # if (self.close_identities[m - 1] != "XX") and (self.close_identities[n - 1] != "XX"):
    #     #     card = [self.close_identities.pop(
    #     #         m - 1), self.close_identities.pop(n - 1)]
    #     #     return card
    #     # else:
    #     #     return None
    #
    # # 刺客(刺杀)
    # async def stab(self):
    #     self.__coins -= 3
