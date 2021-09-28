"""
这里接收所有与政变有关的命令, 具体事务由master处理
"""
from parse import parse
from nonebot.rule import to_me
from nonebot import on_command, on_endswith, on_startswith, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from .game_features import check_num

from master import Master

masters = {}  # 存储所有房间, 存储方式为 {房间号: 对应房间}
all_player = {}  # 存储所有的玩家, 存储方式为 {玩家QQ号: 对应房间号}

# ======================基础元素====================== #
# 帮助文档
Docs = on_command("帮助", rule=to_me(), aliases={"帮助文档", }, priority=0)


@Docs.handle()
async def _(bot: Bot):
    text = '创建房间命令是”开始“\n' \
           '选择人数命令是“n人”\n' \
           '加入房间的命令是“n“\n' \
           '换牌命令是”换牌第n张“\n' \
           '可以用“查询”来查询各位的币数\n' \
           '死亡命令是”死亡第n张“\n' \
           '支持命令”结束“快速结束\n' \
           '详情规则参考http://www.yihubg.com/rule-details/7f81295f-7160-4261-b436-d385395b9b22'
    await Docs.finish(text)


# 玩家人数
players_num = on_endswith("人", rule=to_me(), priority=1)


@players_num.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global masters, all_player
    qq_number = event.get_user_id()
    if all_player.get(qq_number, ""):

        num = await check_num(str(event.get_message()))
        if 2 <= num <= 7:
            # 为房主分发身份牌
            master_ = Master(num)
            cards = await master_.draw_cards(qq_number)

            if cards:
                # 私聊发送身份牌
                await bot.send_private_msg(user_id=int(qq_number), message="".join(cards))
                # 将房主纳入参与者名单
                all_player[qq_number] = qq_number
                # 用房主QQ表作为房间号
                masters[qq_number] = master_
                await players_num.finish(f"创建的房间号为{qq_number}")
            else:
                await players_num.finish("人数已满!")

        else:
            await players_num.finish("人数错误!")

    else:
        await players_num.finish(f"你已经在{all_player[qq_number]}房间里面了哦")


# 加入房间自动分配顺序
join_in_room = on_startswith("进", rule=to_me(), priority=1)


# 玩家是否已经在某个房间里面了，房间是否存在，房间是否满员
@join_in_room.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    qq_number = event.get_user_id()
    # 是否已经加入房间
    if all_player.get(qq_number, ""):
        # 从命令中取得房号
        room_number = str(event.get_message())[1:]
        room = await masters.get(room_number, None)

        if room:
            # 分发身份牌
            cards = room.draw_cards(qq_number)

            if cards:
                # 纳入参与者名单
                all_player[qq_number] = room_number
                # 私聊发送身份牌
                await players_num.finish(user_id=int(qq_number), message=" ".join(cards), message_type="private")

            else:
                await join_in_room.finish("房间已满，换一个吧")

        else:
            await join_in_room.finish("房间号错误!")

    else:
        await players_num.finish(f"你已经在{all_player[qq_number]}房间里面了哦")


# 查询现在在场玩家的打开身份牌和钱币
inquire_info = on_command("查询", priority=1)


@inquire_info.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取这个玩家所在的房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    if room_number and await masters[room_number].is_full_people():
        # 获取这个房间里面所有玩家的信息
        msg = await masters[room_number].players_info()
        await inquire_info.finish(msg)
    else:
        await inquire_info.finish("你是来找茬的是不是?")


end_game = on_command("结束", rule=to_me(), priority=1)


# 用于玩家自己结束游戏
@end_game.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    if room_number:
        # 销毁该对象
        del masters[room_number]
        await end_game.finish("再来一把?")
    else:
        await inquire_info.finish("你是来找茬的是不是?")


# ======================游戏逻辑====================== #
# 质疑的处理
doubt = on_command("质疑", priority=1)


@doubt.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    # 添加质疑人进入操作链
    masters[room_number].action_chain[-1] = qq_number

    # 处理质疑
    result = await masters[room_number].doubt_event()
    masters[room_number].is_block = False
    # action_chain = ["", "", "", "", ""]
    if len(result) == 3:
        await doubt.finish(f"{result[0]}质疑失败，选择开牌; {result[1]}选择换牌")
        masters[room_number].identity_card = result[-1]
    else:
        await doubt.finish(f"质疑成功, {result[0]}选择开牌")
        masters[room_number].identity_card = ""


# 强制结算
go_pass = on_command("过", priority=1)


@go_pass.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    # 判断是否有阻止, 有:无事发生, 无: 判断操作
    if masters[room_number].is_block:
        masters[room_number].is_block = False
    else:
        await masters[room_number].operation_event()
    # action_chain = ["", "", "", "", ""]


# 开牌
open_card = on_startswith("开", priority=1)


@open_card.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    num = await check_num(str(event.get_message()))
    await masters[room_number].open_card(num)


# 政变
lost_seven_coins = on_startswith("政变", priority=1)


@lost_seven_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    # 检查金币数量
    if masters[room_number].check_coins(qq_number, "政变"):
        QQ_number = parse("政变[CQ:at,qq={}]", str(event.get_message()))[0]
        masters[room_number].action_chain[:3] = [QQ_number, "政变", qq_number]
        await masters[room_number].operation_event()
        await lost_seven_coins.finish(f"{QQ_number}开一张牌吧")
    else:
        await lost_seven_coins.finish("没钱!没钱!")


# 刺杀
lost_three_coins = on_startswith("刺杀", priority=1)


@lost_three_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    # 检查金币数量
    if masters[room_number].check_coins(qq_number, "刺杀"):
        QQ_number = parse("刺杀[CQ:at,qq={}]", str(event.get_message()))[0]
        # await masters[room_number].operation_event(qq_number, "刺杀", QQ_number)
        # 写入操作链, [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ)]
        masters[room_number].action_chain[:3] = [QQ_number, "刺杀", qq_number]
    else:
        await lost_seven_coins.finish("没钱!没钱!")


# 阻止
block_operation = on_command("阻止", priority=1)


@block_operation.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    masters[room_number].is_block = True
    # 阻止人写入操作链
    masters[room_number].action_chain[3] = qq_number


# 收入
get_one_coin = on_command("收入", aliases={"拿1", "拿一"}, priority=1)


@get_one_coin.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    masters[room_number].action_chain[:3] = ["", "收入", qq_number]
    await masters[room_number].operation_event()


# 援助
get_two_coins = on_command("援助", aliases={"拿2", "拿二"}, priority=1)


@get_two_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    masters[room_number].action_chain[:3] = ["", "援助", qq_number]


get_three_coins = on_command("公爵", aliases={"拿3", "拿三", "税收"}, priority=1)


# 公爵
@get_three_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    masters[room_number].action_chain[:3] = ["", "税收", qq_number]


lost_two_coins = on_startswith("抢", priority=2)


# 队长
@lost_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    QQ_number = parse("抢[CQ:at,qq={}]", str(event.get_message()))[0]
    # await masters[room_number].operation_event(qq_number, "刺杀", QQ_number)
    # 写入操作链, [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ)]
    masters[room_number].action_chain[:3] = [QQ_number, "刺杀", qq_number]

# 如果identity_card有值, 就是要换掉对应的牌
# 所有操作先加入操作链, 时刻注意is_block和identity_card, 涉及刺杀和政变先检查金币数量
# 如何at别人message += MessageSegment.at(qq_number) + MessageSegment.text(" ") + f'{players[qq_number].wealth}\n'


# change_cards = on_startswith("换牌", rule=to_me(), priority=2)
#
#
# # 换牌
# @change_cards.handle()
# async def _(bot: Bot, event: Event, state: T_State):
#     global game_start, players, identities
#     if game_flag:
#         num = await check_num(str(event.get_message()))
#         qq_number = event.get_user_id()
#         if num != -1:
#             if len(players[qq_number].identity) != 0:
#                 identities.append(players[qq_number].identity.pop(num - 1))
#                 players[qq_number].identity.append(identities.pop())
#                 shuffle(identities)
#                 await change_cards.finish(user_id=int(qq_number), message=" ".join(players[qq_number].identity),
#                                           message_type="private")
#             else:
#                 await change_cards.finish("你已经没有手牌了诶")
#         else:
#             await change_cards.finish("序号错误")
#     else:
#         await change_cards.finish("请先开始游戏")
