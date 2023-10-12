from random import shuffle
from .EnumInGame import IDENTITY, OPERATION, OTHER_OPERATION
from .PlayerInGame import Player


class Master:
    async def __init__(self, num: int):
        self.players: dict[int, Player] = {}  # 记录参与人员，为{qq : player}
        self.players_num: int = num  # 确定参与人数

        # 记录本轮玩家的行为
        self.action_reocrd: list[list] = []  # 记录格式[qq, operation,qq]

        # self.identity_card = []  # 需要换掉的身份
        # self.ambassador_cards = []
        # self.survivor_num = num  # 记录存活，为1时自动结束

        # 身份牌
        self.identities = [
            IDENTITY.DUKE,
            IDENTITY.ASSASSIN,
            IDENTITY.CONTESSA,
            IDENTITY.CAPTAIN,
            IDENTITY.AMBASSADOR,
        ] * 4
        shuffle(self.identities)

    # 每局结束之后为下一局做准备
    async def __round_init(self):
        # 重置标志
        self.action_chain = []
        # 检查存活人数
        if len(self.players) == 1:
            for qq_number in self.players.keys():
                return qq_number
        else:
            return

    # 加入游戏
    async def __join_game(self, qq_number):
        if len(self.players) >= self.players_num:
            return OTHER_OPERATION.GAME_FULL

        cards = await self.__draw_cards()
        player = Player(cards)
        self.players[qq_number] = player

    # 抽卡
    async def __draw_cards(self):
        return [self.identities.pop(), self.identities.pop()]

    # 查询
    async def __inquiry_info(self):
        message: str = ""
        for value in self.players.values():
            message += await value.inquiry_all()
        return message

    # 处理一般技能
    async def operation_processing(
        self, victimizer_qq: int, action: OPERATION, victim_qq: int, num=-1
    ):
        """
        技能处理
        @parama:
            victimizer_qq: int 加害者编号
            action: OPERATION 操作类型
            victim_qq: int 受害者编号
            num: int 这个参数用于处理政变等需要开牌的情况
        @return: None
        """
        self.action_reocrd.append([victimizer_qq, action, victim_qq])

        victimizer_player = self.players[victimizer_qq]
        victim_player = self.players[victim_qq]

        # 立即结算的操作
        if action == OPERATION.INCOME:
            await victimizer_player.add_coins(1)

        # 需要给出具体受害者的第几张牌的操作
        elif action == OPERATION.ASSASSIN:
            await victimizer_player.sub_coins(3)
            await victim_player.open_cards(num)
        elif action == OPERATION.COUP:
            await victimizer_player.sub_coins(7)
            await victim_player.open_cards(num)

        # 自己选开第几张牌的操作
        elif action == OPERATION.DOUBT:
            await victim_player.open_cards(num)

        # 其他非阻止操作，但是只涉及金币的
        elif action == OPERATION.FOREIGE_AID:
            await victimizer_player.add_coins(2)
        elif action == OPERATION.DUKE:
            await victimizer_player.add_coins(3)
        elif action == OPERATION.CAPTAIN:
            coins_num = await victim_player.get_coins()
            if coins_num >= 2:
                await victimizer_player.add_coins(2)
                await victim_player.sub_coins(2)
            else:
                await victimizer_player.add_coins(coins_num)
                await victim_player.sub_coins(coins_num)

        # 大使的换牌
        elif action == OPERATION.AMBASSADOR:
            await victimizer_player.set_cards(cards)

        # 关于阻止的处理
        elif action == OPERATION.DUKE_BLOCK:
            await player.set_cards()
