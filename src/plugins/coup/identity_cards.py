'''
各职位及其行为:
    公爵：拿3个币
    队长：抢劫2个币或者阻止抢劫
    刺客：3个币刺杀一个身份
    夫人：可以阻止刺杀
    大使：阻止抢劫和换身份牌
'''
from .player import Player


# 公爵
async def tax_duchess(player: Player):
    player.wealth += 3


# 队长
async def rob_captain(rob_player: Player, was_robbed_player: Player):
    if was_robbed_player.wealth >= 2:
        rob_player.wealth += 2
        was_robbed_player.wealth -= 2
    elif was_robbed_player.wealth == 1:
        rob_player.wealth += 1
        was_robbed_player.wealth -= 1
    else:
        pass

# class Role():
#     # 刺客
#     def assassin_stab(self, wealth):
#         if wealth >= 3:
#             wealth -= 3
#         else:
#             pass  # todo
#
#     # 大使
#     def ambassador_replace(self, identities, identity_library):
#         for identity in identity_library:
#             identity_library.append(identity)
#         identities = identity_library[0: 2]
