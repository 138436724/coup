"""
这里接收所有与政变有关的命令, 具体事务由master处理
"""

from nonebot.rule import to_me
from nonebot import on_command, on_endswith, on_startswith, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from .game_features import check_num

from master import Master

masters = {}  # 存储所有房间, 存储方式为 {房间号: 对应房间}
all_player = {}  # 存储所有的玩家, 存储方式为 {玩家QQ号: 对应房间号}
# [受害者QQ, 操作, 操作人QQ, 阻止人QQ, 质疑人QQ(""代表无人)]
action_chain = ["", "", "", "", ""]
is_block = False  # 是否阻止
identity_card = ""  # 需要换掉的身份

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
    global masters, all_player, action_chain, is_block, identity_card
    # 获取房间号
    qq_number = event.get_user_id()
    room_number = all_player.get(qq_number, "")

    # 添加质疑人进入操作链
    action_chain[-1] = qq_number

    # 处理质疑
    result = await masters[room_number].doubt_event(is_block, action_chain)
    is_block = False
    # action_chain = ["", "", "", "", ""]
    if len(result) == 3:
        await doubt.finish(f"{result[0]}质疑失败，选择开牌; {result[1]}选择换牌")
        identity_card = result[-1]
    else:
        await doubt.finish(f"质疑成功, {result[0]}选择开牌")
        identity_card = ""

# 所有操作先加入操作链, 时刻注意is_block和identity_card, 涉及刺杀和政变先检查金币数量

change_cards = on_startswith("换牌", rule=to_me(), priority=2)
die_cards = on_startswith("死亡", rule=to_me(), priority=2)
get_one_coin = on_command("收入", aliases={"拿1", "拿一"}, rule=to_me(), priority=2)
get_two_coins = on_command("援助", aliases={"拿2", "拿二"}, rule=to_me(), priority=2)
get_three_coins = on_command("公爵", aliases={"拿3", "拿三", "税收"}, rule=to_me(), priority=2)
lost_two_coins = on_startswith("抢", rule=to_me(), priority=2)
lost_three_coins = on_startswith("刺杀", rule=to_me(), priority=2)
lost_seven_coins = on_startswith("政变", rule=to_me(), priority=2)


# 换牌
@change_cards.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_start, players, identities
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
    global game_start, players, identities
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


@get_one_coin.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_start, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        await players[qq_number].get_one_coin()
        await get_one_coin.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_one_coin.finish("先开始游戏哦")


@get_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_start, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        await players[qq_number].get_two_coins()
        await get_two_coins.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_two_coins.finish("先开始游戏哦")


# 公爵
@get_three_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_start, players, identities
    if game_flag:
        qq_number = event.get_user_id()
        players[qq_number].get_three_coins()
        await get_three_coins.finish(f"你现在有{players[qq_number].wealth}个币了", at_sender=True)
    else:
        await get_three_coins.finish("先开始游戏哦")


# 队长
@lost_two_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_start, players, identities
    if game_flag:
        was_robben_qq_number = parse("抢[CQ:at,qq={}]", str(event.get_message()))[0]  # todo
        print(int(was_robben_qq_number))
        qq_number = event.get_user_id()
        if players[was_robben_qq_number].wealth >= 2:
            players[qq_number].rob_two_coins(True)
        players[was_robben_qq_number].was_robben()
        await lost_two_coins.finish("")
    else:
        await lost_two_coins.finish("先开始游戏哦")


# 刺客
@lost_three_coins.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_start, players, identities
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
    global game_start, players, identities
    if game_flag:
        coup_qq_number = parse('[CQ:at,qq={}]', str(event.get_message()))  # todo
        qq_number = event.get_user_id()
        if players[qq_number].wealth >= 7:
            players[qq_number].coup()
        else:
            await lost_seven_coins.finish("没钱了诶")
    else:
        await lost_seven_coins.finish("先开始游戏哦")
