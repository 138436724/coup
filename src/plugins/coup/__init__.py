from random import shuffle
from parse import parse

from nonebot.rule import to_me
from nonebot import on_command, on_endswith, on_startswith, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from .game_features import *
# from .identity_cards import *
from .player import Player

# 游戏是否开始
game_flag = False
# 玩家数据
players = {}
# 身份牌
identities = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4
# 身份牌墓地
card_graveyard = []

help_documentation = on_command("帮助", rule=to_me(), priority=0)

start_game = on_command("开始", rule=to_me(), priority=1)
draw_cards = on_endswith("人", rule=to_me(), priority=1)
give_cards = on_regex("^[1-7一二三四五六七两俩]", rule=to_me(), priority=2)
change_cards = on_startswith("换牌", rule=to_me(), priority=2)
die_cards = on_startswith("死亡", rule=to_me(), priority=2)
end_game = on_command("结束", rule=to_me(), priority=1)


@help_documentation.handle()
async def _(bot: Bot, event: Event):
    text = '请先呼我名\n' \
           '创建房间命令是”开始“\n' \
           '选择人数命令是“n人”\n' \
           '加入房间的命令是“n“\n' \
           '换牌命令是”换牌第n张“\n' \
           '死亡命令是”死亡第n张“\n' \
           '支持命令”结束“快速结束\n' \
           '详情规则参考http://www.yihubg.com/rule-details/7f81295f-7160-4261-b436-d385395b9b22'
    await help_documentation.finish(text)


@start_game.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    game_flag = True
    players.clear()
    shuffle(identities)
    await start_game.finish("开始你们的表演")


# 准备身份牌
@draw_cards.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        if len(players) != 0:
            await draw_cards.finish("嗯?")
        num = await check_num(str(event.get_message()))
        if num != -1:
            for i in range(num):
                participant = Player()
                participant.identity = identities[0:2]
                del identities[0:2]
                players[i] = participant
        else:
            await draw_cards.finish("序号错误")
    else:
        await draw_cards.finish("先开始游戏哦")


# 分发身份牌
@give_cards.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        num = await check_num(str(event.get_message()))
        if num != -1:
            qq_number = event.get_user_id()
            # print(qq_number)
            if num - 1 in players.keys() and qq_number not in players.keys():
                players[qq_number] = players.pop(num - 1)
                await give_cards.finish(user_id=int(qq_number), message=" ".join(players[qq_number].identity),
                                        message_type="private")
            else:
                await give_cards.finish("有人选了哦")
        else:
            await give_cards.finish("序号错误")
    else:
        await give_cards.finish("请先开始游戏")
        # await give_cards.finish("")
        # print(players)


# 换牌
@change_cards.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        num = await check_num(str(event.get_message()))
        qq_number = event.get_user_id()
        if num != -1:
            if len(players[qq_number].identity) != 0:
                identities.append(players[qq_number].identity.pop(num - 1))
                players[qq_number].identity.append(identities.pop())
                shuffle(identities)
                await change_cards.finish(user_id=int(qq_number), message=" ".join(players[qq_number].identity),
                                          message_type="private")
            else:
                await change_cards.finish("你已经没有手牌了诶")
        else:
            await change_cards.finish("序号错误")
    else:
        await change_cards.finish("请先开始游戏")


# 死亡身份牌
@die_cards.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        num = await check_num(str(event.get_message()))
        qq_number = event.get_user_id()
        if num != -1:
            if len(players[qq_number].identity) == 2:
                card_graveyard.append(players[qq_number].identity.pop(num - 1))
                # identities.append(players[qq_number].identity.pop(num - 1))
                await die_cards.finish(user_id=int(qq_number), message=" ".join(players[qq_number].identity),
                                       message_type="private")
            elif len(players[qq_number].identity) == 1:
                card_graveyard.append(players[qq_number].identity.pop())
                # identities.append(players[qq_number].identity.pop())
                await die_cards.finish("你没了啊", at_sender=True)
            else:
                await die_cards.finish("你已经没有身份牌了诶")
        else:
            await die_cards.finish("序号错误")
    else:
        await die_cards.finish("请先开始游戏哦")
