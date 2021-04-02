'''
各职位及其行为:
    公爵：拿3个币
    队长：抢劫2个币或者阻止抢劫
    刺客：3个币刺杀一个身份
    夫人：可以阻止刺杀
    大使：阻止抢劫和换身份牌
'''
from parse import parse

from nonebot.rule import to_me
from nonebot import on_command, on_endswith, on_startswith, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .player import Player

get_one_coin = on_command("收入", aliases={"拿1", "拿一"}, rule=to_me(), priority=2)
get_two_coins = on_command("援助", aliases={"拿2", "拿二"}, rule=to_me(), priority=2)
get_three_coins = on_command("公爵", aliases={"拿3", "拿三", "税收"}, rule=to_me(), priority=2)
lost_two_coins = on_startswith("抢", rule=to_me(), priority=2)


@lost_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        was_robben_qq_number = parse('[CQ:at,qq={}]', str(event.get_message()))
        print(was_robben_qq_number)
        rob_qq_number = event.get_user_id()
        print(rob_qq_number)
        # await rob_captain(players[rot_qq_number], players[was_robben_qq_number])
        await lost_two_coins.finish("")
    else:
        await lost_two_coins.finish("先开始游戏哦")


@get_one_coin.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        await players[qq_number].income()
        await get_one_coin.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_one_coin.finish("先开始游戏哦")


@get_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        await players[qq_number].help()
        await get_two_coins.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_two_coins.finish("先开始游戏哦")


# 公爵
@get_three_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        players[qq_number].wealth += 3
        # await tax_duchess(players[qq_number])
        await get_three_coins.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_three_coins.finish("先开始游戏哦")

# 队长
# async def rob_captain(rob_player: Player, was_robbed_player: Player):
#     if was_robbed_player.wealth >= 2:
#         rob_player.wealth += 2
#         was_robbed_player.wealth -= 2
#     elif was_robbed_player.wealth == 1:
#         rob_player.wealth += 1
#         was_robbed_player.wealth -= 1
#     else:
#         pass

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
