"""
总控系统
会接收所有消息，然后对对应的输入调用对应的处理函数
"""
from random import shuffle
from player import Player


class Master:
    # 游戏是否开始、玩家数据、身份牌
    players = {}
    player_num = 0
    identities = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4

    def __init__(self, num):
        self.players.clear()
        self.player_num = num  # 确定参与人数
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
            msg = msg + qq_number + " ".join(player.open_identities) + "\n"
        return msg

    # 单独处理换牌 todo
    async def change_cards(self):
        pass

    # 检查政变和刺杀是否有足够金币
    async def check_operation(self, qq_number, action):
        player = self.players[qq_number]
        if action == "政变":
            # 在外面声明受害者开牌, 这里只减少金币
            return player.coins >= 7
        if action == "刺杀":
            # 在外面声明受害者开牌, 这里只减少金币
            return player.coins >= 3

    # 处理正常操作,参数为: 受害者QQ, 操作, 操作人QQ
    async def operation_event(self, qq_number, action, QQ_number):
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

    # 处理开牌事件, 全部开牌的角色仍然存在
    async def open_card(self, qq_number, num):
        await self.players[qq_number].open_card(num)

    # 处理质疑事件
    async def doubt(self, qq_number: str, identity: list):
        player = self.players[qq_number]
        return set(player.open_identities) & set(identity)

    # 参数为是否有阻止, 操作链条
    async def doubt_event(self, is_block: bool, action: list):
        identity = []

        if is_block:  # 有阻止有质疑

            if action[1] == "援助":
                identity = ["公爵"]
            elif action[1] == "抢夺":
                identity = ["大使", "队长"]
            elif action[1] == "刺杀":
                identity = ["夫人"]

            if await self.doubt(action[3], identity):  # 阻止人QQ, 身份
                # 质疑失败, 质疑者打开一张牌, 阻止者换牌, 无事发生
                # 换牌、开牌要求外界玩家声明, 在外界处理
                return [action[4], action[3], identity]
            else:
                # 质疑成功, 阻止者打开一张牌, 操作继续
                await self.operation_event(*action[:3])
                return [action[3]]

        else:  # 只有质疑

            if action[1] == "税收":
                identity = ["公爵"]
            elif action[1] == "抢夺":
                identity = ["大使"]
            elif action[1] == "刺杀":
                identity = ["刺客"]
            elif action[1] == "换牌":
                identity = ["大使"]

            if await self.doubt(action[2], identity):  # 操作者QQ, 身份
                # 质疑失败, 质疑者打开一张牌, 操作者换牌, 操作继续
                await self.operation_event(*action[:3])
                return [action[4], action[2], identity]
            else:
                # 质疑成功, 操作者打开一张牌, 无事发生
                return [action[2]]
