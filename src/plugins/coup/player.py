class Player:
    '''
    玩家角色信息:
        币数目
        身份牌
        身份牌数目
        玩家的技能:本身技能和身份技能
            本身技能:
                收入
                援助
                质疑
                政变
            角色技能:
                公爵
                队长
                刺客
    '''
    wealth = 0
    identity = []

    async def get_one_coin(self):
        self.wealth += 1

    async def get_two_coins(self):
        self.wealth += 2

    async def get_three_coins(self):
        self.wealth += 2

    async def rob_two_coins(self, flag: bool):
        if flag:
            self.wealth += 2
        else:
            self.wealth += 1

    async def was_robben(self):
        self.wealth -= 2
        if self.wealth < 0:
            self.wealth = 0

    # 是否有币由其他程序判断
    async def coup(self):
        self.wealth -= 7

    async def stab(self):
        self.wealth -= 3
