"""
总控系统
会接收所有消息，然后对对应的输入调用对应的处理函数
"""
from random import shuffle
from .player import Player


class Master:
    # 游戏是否开始、玩家数据、身份牌
    players = {}
    player_num = 0
    is_block = False  # 是否有阻止
    identity_card = ""  # 需要换掉的身份
    # [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ(""代表无人)]
    action_chain = ["", "", "", "", ""]
    ambassador_cards = []
    identities = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4

    def __init__(self, num):
        self.players.clear()
        self.player_num = num  # 确定参与人数
        self.is_block = False  # 是否有阻止
        self.identity_card = ""  # 需要换掉的身份
        self.action_chain = ["", "", "", "", ""]
        self.ambassador_cards = []
        self.identities = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4
        shuffle(self.identities)

    # 分发身份卡
    async def draw_cards(self, qq_number):
        if len(self.players) < self.player_num:
            player = Player()
            player.close_identities = self.identities[0:2]
            del self.identities[0:2]
            self.players[qq_number] = player
            return player.close_identities
        else:
            return None

    # 人齐了才可以开始 / 是否满员
    async def is_full_people(self):
        return len(self.players) == self.player_num

    # 开放的牌会对open进行修改，只要获取open就行
    async def players_info(self):
        msg = ""
        for qq_number, player in self.players.items():
            print(player.coins)
            msg = msg + qq_number + " ".join(player.open_identities) + f"{player.coins}" + "\n"
        return msg

    # 处理质疑的换牌
    async def change_one_card(self, qq_number, num):
        player = self.players[qq_number]
        if player.close_identities[num - 1] == self.identities:
            card = player.close_identities.pop(num - 1)
            player.close_identities.append(self.identities.pop())
            self.identities.append(card)
            shuffle(self.identities)
        else:
            card = player.close_identities.pop((3 - num) - 1)
            player.close_identities.append(self.identities.pop())
            self.identities.append(card)
            shuffle(self.identities)
        return player.close_identities

    # 大使的换牌
    async def change_two_cards(self, qq_number):

        player = self.players[qq_number]
        cards = player.change_two_cards(self.identities[0:2])
        del self.identities[0:2]
        self.ambassador_cards = cards

    # 大使的删牌
    async def delete_cards(self, qq_number: str, card_num: list):
        card = await self.players[qq_number].delete_two_cards(card_num)
        self.identities += card
        shuffle(self.identities)

    # 检查政变和刺杀是否有足够金币
    async def check_coins(self, qq_number, action):
        player = self.players[qq_number]
        if action == "政变":
            # 在外面声明受害者开牌, 这里只减少金币
            return player.coins >= 7
        if action == "刺杀":
            # 在外面声明受害者开牌, 这里只减少金币
            return player.coins >= 3

    # 处理正常操作,参数为: 受害者QQ, 操作, 操作人QQ
    async def operation_event(self):
        qq_number, action, QQ_number = self.action_chain[:3]
        player = self.players[QQ_number]
        if action == "收入":
            await player.get_one_coin()
        elif action == "援助":
            await player.get_two_coins()
        elif action == "税收":
            await player.get_three_coins()
        elif action == "抢夺":
            was_robbed_player = self.players[qq_number]
            num = await was_robbed_player.was_rob_coins()
            await player.rob_two_coins(num)
        elif action == "政变":
            # 在外面声明受害者开牌, 这里只减少金币
            await player.coup()
        elif action == "刺杀":
            # 在外面声明受害者开牌, 这里只减少金币
            await player.stab()
        elif action == "大使":
            await self.change_two_cards(QQ_number)
        self.action_chain = ["", "", "", "", ""]

    # 处理开牌事件, 全部开牌的角色仍然存在
    async def open_card(self, qq_number, num):
        await self.players[qq_number].open_card(num)

    # 处理质疑事件
    async def doubt(self, qq_number: str, identity: list):
        player = self.players[qq_number]
        return set(player.open_identities) & set(identity)

    # 参数为是否有阻止, 操作链条
    async def doubt_event(self):
        identity = []

        if self.is_block:  # 有阻止有质疑

            if self.action_chain[1] == "援助":
                identity = ["公爵"]
            elif self.action_chain[1] == "抢夺":
                identity = ["大使", "队长"]
            elif self.action_chain[1] == "刺杀":
                identity = ["夫人"]

            if await self.doubt(self.action_chain[3], identity):  # 阻止人QQ, 身份
                # 质疑失败, 质疑者打开一张牌, 阻止者换牌, 无事发生
                # 换牌、开牌要求外界玩家声明, 在外界处理
                return [self.action_chain[4], self.action_chain[3], identity]
            else:
                # 质疑成功, 阻止者打开一张牌, 操作继续
                await self.operation_event()
                return [self.action_chain[3]]

        else:  # 只有质疑

            if self.action_chain[1] == "税收":
                identity = ["公爵"]
            elif self.action_chain[1] == "抢夺":
                identity = ["大使"]
            elif self.action_chain[1] == "刺杀":
                identity = ["刺客"]
            elif self.action_chain[1] == "大使":
                identity = ["大使"]

            if await self.doubt(self.action_chain[2], identity):  # 操作者QQ, 身份
                # 质疑失败, 质疑者打开一张牌, 操作者换牌, 操作继续
                await self.operation_event()
                return [self.action_chain[4], self.action_chain[2], identity]
            else:
                # 质疑成功, 操作者打开一张牌, 无事发生
                return [self.action_chain[2]]
