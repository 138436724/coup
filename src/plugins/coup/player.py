class Player:
    '''
    玩家角色信息:
        币数目
        身份牌
        身份牌数目
        玩家的技能:
            质疑
            政变
    '''
    wealth = 0
    identity = []

    async def income(self):
        self.wealth += 1

    async def help(self):
        self.wealth += 2

    async def coup(self):
        if self.wealth >= 7:
            self.wealth -= 7
        else:
            pass  # todo

    async def query(self):
        pass  # todo
