"""
这里接收所有与政变有关的命令, 具体事务由master处理
"""
#from parse import parse
from nonebot.rule import to_me
from nonebot import on_command, on_endswith, on_startswith
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent
from .game_features import check_num

from .master import Master

masters = {}  # 存储所有房间, 存储方式为 {房间号: 对应房间}
all_player = {}  # 存储所有的玩家, 存储方式为 {玩家QQ号: 对应房间号}

# ======================基础元素====================== #
# 帮助文档
Docs = on_command("帮助", rule=to_me(), aliases={"帮助文档", }, priority=0)


@Docs.handle()
async def _(bot: Bot):
    text = '创建房间需要先@机器人再声明“n人”\n' \
           '加入房间的命令是“进XX“\n' \
           '查询已经打开的牌和玩家金币使用”查询“\n' \
           '支持强制结束”结束“' \
           '换牌分两种:\n' \
           '    一是被质疑的换牌命令”换n“\n' \
           '    二是大使的换牌, 命令是”大使“, 此时去掉多余的牌使用”删mn“\n' \
           '质疑使用”质疑“\n' \
           '由于对质疑的支持, 凡是不涉及质疑的操作需要使用”过“强制结算\n' \
           '翻牌使用”开n“\n' \
           '政变需要使用”@xx政变“\n' \
           '刺杀需要使用”@xx刺杀“\n' \
           '阻止、收入、援助、公爵 使用对应名称作为命令\n' \
           '抢夺也是”@xx抢“\n' \
           '!!! 注意:当前阶段必须严格按照命令格式, 否则不会响应\n' \
           '详情规则参考http://www.yihubg.com/rule-details/7f81295f-7160-4261-b436-d385395b9b22'
    await Docs.finish(text)


# 玩家人数
players_num = on_endswith("人", rule=to_me(), priority=1)


@players_num.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    qq_number = event.get_user_id()
    if not all_player.get(qq_number, ""):

        num = await check_num(str(event.get_message()))
        if 2 <= num <= 7:
            # 为房主分发身份牌
            room = Master(num)
            cards = await room.draw_cards(qq_number)

            if cards:
                # 私聊发送身份牌
                await players_num.send(user_id=int(qq_number), message=" ".join(cards), message_type="private")
                # await bot.send_private_msg(user_id=int(qq_number), message="".join(cards))
                # 将房主纳入参与者名单
                masters[qq_number] = room
                all_player[qq_number] = qq_number
                # 用房主QQ表作为房间号
                await players_num.finish(f"创建的房间号为{qq_number}")
            else:
                await players_num.finish("人数已满!")

        else:
            await players_num.finish()

    else:
        await players_num.finish(f"你已经在{all_player[qq_number]}房间里面了哦")


# 加入房间自动分配顺序
join_in_room = on_startswith("进", priority=1)


# 玩家是否已经在某个房间里面了，房间是否存在，房间是否满员
@join_in_room.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    qq_number = event.get_user_id()
    # 是否已经加入房间
    if not all_player.get(qq_number, ""):
        # 从命令中取得房号
        room_number = str(event.get_message())[1:]
        room = masters.get(room_number, None)

        if room:
            # 分发身份牌
            cards = await room.draw_cards(qq_number)

            if cards:
                # 纳入参与者名单
                all_player[qq_number] = room_number
                # 私聊发送身份牌
                await join_in_room.finish(user_id=int(qq_number), message=" ".join(cards), message_type="private")

            else:
                await join_in_room.finish("房间已满，换一个吧")

        else:
            await join_in_room.finish()

    else:
        await join_in_room.finish(f"你已经在{all_player[qq_number]}房间里面了哦")


# 查询现在在场玩家的打开身份牌和钱币
inquire_info = on_command("查询", priority=1)


@inquire_info.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取这个玩家所在的房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    if room_number:
        if await masters[room_number].is_full_people():
            # 获取这个房间里面所有玩家的信息
            msg = await masters[room_number].players_info()
            await inquire_info.finish(msg)
        else:
            await inquire_info.finish("人还没齐哦")
    else:
        await inquire_info.finish()


end_game = on_command("结束", priority=1)


# 用于玩家自己结束游戏
@end_game.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    if room_number:
        # 销毁该对象、在参与者名单里面剔除所有玩家
        room = masters[room_number]
        await room.delete_player(all_player)
        del masters[room_number]
        await end_game.finish("再来一把?")
    else:
        await end_game.finish()


# ======================游戏逻辑====================== #
# 关于被质疑者的换牌
change_one_cards = on_startswith("换", priority=1)


# 换牌
@change_one_cards.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        card_num = await check_num(str(event.get_message()))
        cards = await masters[room_number].change_one_card(qq_number, card_num)
        await change_one_cards.finish(user_id=int(qq_number), message=" ".join(cards), message_type="private")
    else:
        await change_one_cards.finish()


# 质疑的处理
doubt = on_command("质疑", priority=1)


@doubt.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:  # and masters[room_number].action_chain[2] != qq_number:

        # 添加质疑人进入操作链
        masters[room_number].action_chain[4] = qq_number

        # 处理质疑
        result = await masters[room_number].doubt_event()
        if result:
            masters[room_number].is_block = False
            masters[room_number].action_chain = ["", "", "", "", ""]
            # action_chain = ["", "", "", "", ""]

            # 判断大使换牌
            if masters[room_number].ambassador_cards:
                QQ_number, cards = masters[room_number].ambassador_cards
                masters[room_number].ambassador_cards = []
                await doubt.send(user_id=int(QQ_number), message=" ".join(cards), message_type="private")

            if len(result) == 3:
                masters[room_number].identity_card = result[-1]
                await doubt.finish(f"{result[0]}质疑失败，选择开牌; {result[1]}选择换牌")
            else:
                masters[room_number].identity_card = ""
                await doubt.finish(f"质疑成功, {result[0]}选择开牌")
        else:
            await doubt.finish("嗯?")
    else:
        await doubt.finish()


# 强制结算
go_pass = on_command("过", priority=1)


@go_pass.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    if room_number:
        # 判断是否是操作者过
        if masters[room_number].action_chain[2] != qq_number:

            # 判断是否有阻止, 有:无事发生, 无: 判断操作
            if not masters[room_number].is_block:
                await masters[room_number].operation_event()
            masters[room_number].is_block = False
            masters[room_number].action_chain = ["", "", "", "", ""]
            # 判断大使身份
            if masters[room_number].ambassador_cards:
                QQ_number, cards = masters[room_number].ambassador_cards
                masters[room_number].ambassador_cards = []
                await go_pass.finish(user_id=int(QQ_number), message=" ".join(cards), message_type="private")
            await go_pass.finish()
        else:
            await go_pass.finish("我谴责你这种行为!")
    else:
        await go_pass.finish()


# 开牌
open_card = on_startswith("开", priority=1)


@open_card.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        num = await check_num(str(event.get_message()))
        if num != -1:
            cards = await masters[room_number].open_card(qq_number, num)
            await open_card.send(user_id=int(qq_number), message=" ".join(cards), message_type="private")
        QQ_number = await masters[room_number].winner()
        if QQ_number:
            # 结束游戏，销毁该对象、在参与者名单里面剔除所有玩家
            room = masters[room_number]
            await room.delete_player(all_player)
            del masters[room_number]
            await open_card.finish(f"获胜者是{QQ_number}")
    await open_card.finish()


# 政变
lost_seven_coins = on_endswith("政变", priority=1)


@lost_seven_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        # 检查金币数量
        if await masters[room_number].check_coins(qq_number, "政变"):
            QQ_number = event.message[0].data['qq']
            masters[room_number].action_chain[:3] = [QQ_number, "政变", qq_number]
            await masters[room_number].operation_event()
            masters[room_number].is_block = False
            masters[room_number].action_chain = ["", "", "", "", ""]
            await lost_seven_coins.finish(f"{QQ_number}开一张牌吧")
        else:
            await lost_seven_coins.finish("没钱!没钱!")
    await lost_seven_coins.finish()


# 刺杀
lost_three_coins = on_endswith("刺杀", priority=1)


@lost_three_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        # 检查金币数量
        if await masters[room_number].check_coins(qq_number, "刺杀"):
            QQ_number = event.message[0].data['qq']
            # await masters[room_number].operation_event(qq_number, "刺杀", QQ_number)
            # 写入操作链, [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ)]
            masters[room_number].action_chain[:3] = [QQ_number, "刺杀", qq_number]
        else:
            await lost_seven_coins.finish("没钱!没钱!")
    await lost_three_coins.finish()


# 阻止
block_operation = on_command("阻止", priority=1)


@block_operation.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number and masters[room_number].action_chain[2] != qq_number:
        masters[room_number].is_block = True
        # 阻止人写入操作链
        masters[room_number].action_chain[3] = qq_number
    await block_operation.finish()


# 收入
get_one_coin = on_command("收入", aliases={"拿1", "拿一"}, priority=1)


@get_one_coin.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        masters[room_number].action_chain[:3] = ["", "收入", qq_number]
        await masters[room_number].operation_event()
        masters[room_number].is_block = False
        masters[room_number].action_chain = ["", "", "", "", ""]
    await get_one_coin.finish()


# 援助
get_two_coins = on_command("援助", aliases={"拿2", "拿二"}, priority=1)


@get_two_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        masters[room_number].action_chain[:3] = ["", "援助", qq_number]
    await get_two_coins.finish()


get_three_coins = on_command("公爵", aliases={"拿3", "拿三", "税收"}, priority=1)


# 公爵
@get_three_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        masters[room_number].action_chain[:3] = ["", "税收", qq_number]
    await get_three_coins.finish()


lost_two_coins = on_endswith("抢", priority=1)


# 队长
@lost_two_coins.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        QQ_number = event.message[0].data['qq']
        # QQ_number = parse("[CQ: at, qq = {}}] 抢", str(event.get_message()))[0]
        # await masters[room_number].operation_event(qq_number, "刺杀", QQ_number)
        # 写入操作链, [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ)]
        masters[room_number].action_chain[:3] = [QQ_number, "抢夺", qq_number]
    await lost_two_coins.finish()


# 如果identity_card有值, 就是要换掉对应的牌
# 所有操作先加入操作链, 时刻注意is_block和identity_card, 涉及刺杀和政变先检查金币数量
# 如何at别人message += MessageSegment.at(qq_number) + MessageSegment.text(" ") + f'{players[qq_number].wealth}\n'


# 关于大使的换牌
change_two_cards = on_command("大使", priority=1)


@change_two_cards.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        # 写入操作链, [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ)]
        masters[room_number].action_chain[:3] = ["", "大使", qq_number]
    await change_two_cards.finish()


delete_cards = on_startswith("删", priority=1)


@delete_cards.handle()
async def _(bot: Bot, event: Event):
    global masters, all_player
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")
    if room_number:
        card_num = [int(x) for x in list(str(event.get_message())[1:])]
        cards = await masters[room_number].delete_cards(qq_number, card_num)
        if cards:
            await delete_cards.finish(user_id=int(qq_number), message=" ".join(cards), message_type="private")
        else:
            await delete_cards.finish("嘿嘿嘿，想搞事是吧")
    else:
        await delete_cards.finish()
