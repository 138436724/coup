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
lost_three_coins = on_startswith("刺杀", rule=to_me(), priority=2)
lost_seven_coins = on_startswith("政变", rule=to_me(), priority=2)


@get_one_coin.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        await players[qq_number].get_one_coin()
        await get_one_coin.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_one_coin.finish("先开始游戏哦")


@get_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        await players[qq_number].get_two_coins()
        await get_two_coins.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_two_coins.finish("先开始游戏哦")


# 公爵
@get_three_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        players[qq_number].get_three_coins()
        await get_three_coins.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_three_coins.finish("先开始游戏哦")


# 队长
@lost_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        print("1------"+str(event.get_message()))
        was_robben_qq_number = parse("抢[CQ:at,qq={}]", str(event.get_message()))  # todo
        print("2-----"+str(was_robben_qq_number))
        qq_number = event.get_user_id()
        print("3-----"+str(qq_number))
        if players[was_robben_qq_number].wealth >= 2:
            players[qq_number].rob_two_coins(True)
        players[was_robben_qq_number].was_robben()
        await lost_two_coins.finish("")
    else:
        await lost_two_coins.finish("先开始游戏哦")


# 刺客
@lost_three_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        if players[qq_number].wealth >= 3:
            players[qq_number].stab()
        else:
            await lost_three_coins.finish("没钱了诶")
    else:
        await lost_three_coins.finish("先开始游戏哦")


# 政变
@lost_seven_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        coup_qq_number = parse('[CQ:at,qq={}]', str(event.get_message()))  # todo
        qq_number = event.get_user_id()
        if players[qq_number].wealth >= 7:
            players[qq_number].coup()
        else:
            await lost_seven_coins.finish("没钱了诶")
    else:
        await lost_seven_coins.finish("先开始游戏哦")
