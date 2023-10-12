"""
玩家角色信息: 币数目、身份牌

角色技能应该由Master调度，Player只需要提供对币和身份的操作即可

很符合现实，上帝进行调度，玩家只关心自己
"""
from .ExceptionInGame import NotAGoodNumber, NotAGoodType
from .EnumInGame import IDENTITY

from typing import List


class Player:
    async def __init__(self, cards: List[IDENTITY]):
        """
        构造函数
        @parama: cards 身份牌列表
        @return: None
        """
        if type(cards) != list:
            raise NotAGoodType("参数应该是列表类型")
        self.__coins: int = 2  # 初始2个金币
        self.__ID_cards: List[IDENTITY] = cards  # 初始身份牌
        self.__open_ID_cards: List[IDENTITY] = []

    async def set_cards(self, cards: List[IDENTITY]):
        """
        为大使提供的操作
        @parama: cards 身份牌列表
        @return: None
        """
        if type(cards) != list:
            raise NotAGoodType("参数应该是列表类型")
        self.__ID_cards += cards

    async def del_cards(self, nums: List):
        """
        为大使提供的操作
        @parama: nums 要丢弃的身份牌
        @return: list 丢地的身份牌
        """
        nums.sort()

        return [self.__ID_cards.pop(nums[1]), self.__ID_cards.pop(nums[0])]

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
        message = f"币：{self.__coins}，身份牌："

        for identity in self.__open_ID_cards:
            if identity == IDENTITY.DUKE:
                message += "公爵"
            elif identity == IDENTITY.ASSASSIN:
                message += "刺客"
            elif identity == IDENTITY.CONTESSA:
                message += "夫人"
            elif identity == IDENTITY.CAPTAIN:
                message += "队长"
            elif identity == IDENTITY.AMBASSADOR:
                message += "大使"

        return message
