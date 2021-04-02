from .game_features import *
from .identity_cards import *
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
inquire_money = on_command("查询", rule=to_me(), priority=1)
end_game = on_command("结束", rule=to_me(), priority=1)


@help_documentation.handle()
async def _(bot: Bot, event: Event):
    text = '请先呼我名\n' \
           '创建房间命令是”开始“\n' \
           '选择人数命令是“n人”\n' \
           '加入房间的命令是“n“\n' \
           '换牌命令是”换牌第n张“\n' \
           '可以用“查询”来查询各位的币数\n' \
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


# 查询钱数
@inquire_money.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities
    if game_flag:
        message = ''
        for qq_number in players.keys():
            if len(players[qq_number].identity) != 0:
                message += MessageSegment.at(qq_number) + MessageSegment.text(" ") + f'{players[qq_number].wealth}\n'
        await inquire_money.finish(message, auto_escape=False)
    else:
        await inquire_money.finish("游戏还未开始")


# 结束游戏
@end_game.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global game_flag, players, identities, card_graveyard
    game_flag = False
    players.clear()
    identities = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4
    card_graveyard.clear()
    await end_game.finish("再来一把?")

# players_library = {}
# players_library_copy = {}
# in_progress_flag = False
# identity_library = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4
# identity_library_copy = []


# # 总控制
# @on_natural_language(keywords=('1', '2', '3', '4', '5', '6', '7', '一', '二', '两', '俩', '三', '四', '五', '六', '七'),
#                      only_to_me=False)
# async def get_number(session: NLPSession):
#     if "？" == session.ctx['raw_message'][0] or "?" == session.ctx['raw_message'][0]:
#         if '拿' in session.ctx['raw_message']:
#             return IntentCommand(90.0, 'make_money')
#         if '死亡' in session.ctx['raw_message']:
#             return IntentCommand(90.0, 'lose_identity')
#         elif '换牌' in session.ctx['raw_message'] or '换人' in session.ctx['raw_message']:
#             return IntentCommand(90.0, 'change_cards')
#         else:
#             return IntentCommand(90.0, 'create_players_library')
#     else:
#         return
#
#
# @on_command('create_players_library',
#             aliases=('1', '2', '3', '4', '5', '6', '7', '一', '二', '两', '俩', '三', '四', '五', '六', '七'),
#             only_to_me=False)
# async def create_players_library(session: CommandSession):
#     global players_library, identity_library, in_progress_flag
#
#     # 人数检测
#     check_result = await check_number(session.ctx['raw_message'])
#     if not check_result:
#         await session.send('人数错误，再想想吧')
#         return
#
#     # 发牌
#     if '人' in session.ctx['raw_message']:  # 取得人数
#         # 检查游戏是否开始
#         if in_progress_flag:
#             await session.send('还没结束呢，不要太心急哦')
#         else:
#             in_progress_flag = True
#             await shuffle_and_distribute(check_result)
#             await session.send('收到啦，正在洗牌哦')
#         return
#
#     # 取得序号
#     if check_result in players_library.keys():
#         qq_number = str(session.ctx['user_id'])
#         if qq_number not in players_library.keys():
#             players_library[qq_number] = players_library.pop(check_result)
#             await session.send(''.join(players_library[qq_number].identities), ensure_private=True)
#         else:
#             await session.send('不要太贪心了')
#     else:
#         await session.send('不对哦，再想想吧')
#     await save_data()
#
#
# # 换牌
# @on_command('change_cards', aliases=('换牌', '换人'), only_to_me=False)
# async def change_cards(session: NLPSession):
#     global players_library, identity_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     qq_number = str(session.ctx['user_id'])
#
#     if '1' in session.ctx['raw_message'] or '一' in session.ctx['raw_message']:
#         await change_identity(qq_number, 0)
#     elif '2' in session.ctx['raw_message'] or '二' in session.ctx['raw_message']:
#         await change_identity(qq_number, 1)
#     else:
#         return
#     await session.send(''.join(players_library[qq_number].identities), ensure_private=True)
#     await save_data()
#
#
# # 大使
# @on_natural_language(keywords=('大使',), only_to_me=False)
# async def ambassador(session: NLPSession):
#     if "？" == session.ctx['raw_message'][0] or "?" == session.ctx['raw_message'][0]:
#         return IntentCommand(90, 'ambassador_change')
#     else:
#         return
#
#
# @on_command('ambassador_change', aliases=('大使',), only_to_me=False)
# async def ambassador_change(session: CommandSession):
#     global players_library, identity_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     await save_data()
#
#     qq_number = str(session.ctx['user_id'])
#     if len(players_library[qq_number].identities) <= 2:
#         players_library[qq_number].identities.append(identity_library.pop(0))
#         players_library[qq_number].identities.append(identity_library.pop(0))
#     else:
#         await session.send('可以了啊，你想换几张牌', at_sender=True)
#         return
#
#     await session.send(''.join(players_library[qq_number].identities), ensure_private=True)
#
#
# # 死亡一张牌
# @on_command('lose_identity', aliases=('死亡',), only_to_me=False)
# async def lose_identity(session: NLPSession):
#     global players_library, identity_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     qq_number = str(session.ctx['user_id'])
#
#     number = check_number(session.ctx['raw_message'])
#     if number:
#         number -= 1
#     else:
#         return
#
#     try:
#         identity_library.append(players_library[qq_number].indentities.pop(number))
#     except IndexError:
#         await session.send('自己几张牌没点数吗？', at_sender=True)
#         return
#
#     if players_library[qq_number].identities:
#         await session.send(''.join(players_library[qq_number].identities), ensure_private=True)
#     else:
#         await session.send('不巧，你失去了所有身份诶', at_sender=True)
#         del players_library[qq_number]
#
#     shuffle(identity_library)
#
#     if len(players_library) == 1:
#         await session.send('胜利者是' + '[CQ:at, qq=' + str(list(players_library.keys())[0]) + ']')
#         await game_end()
#     await save_data()
#
#
# # 质疑
# @on_natural_language(keywords=('质疑',), only_to_me=False)
# async def doubt_and_check(session: NLPSession):
#     global players_library, identity_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     message = session.ctx['raw_message']
#     identity = await check_identity(message)
#     qq_number = str(session.ctx['user_id'])
#     was_qq_number = await check_player(message)
#     identities = players_library[was_qq_number].identities
#
#     if identity in ''.join(identities):
#         await session.send('质疑失败', at_sender=True)
#     else:
#         await session.send('质疑成功', at_sender=True)
#         await back_to_previous_step()
#         await session.bot.send_private_msg(user_id=was_qq_number,
#                                            message=''.join(players_library[was_qq_number].identities))
#         await session.send(''.join(players_library[qq_number].identities), ensure_private=True)
#
#
# # 钱数
# @on_command('report_money', aliases=('看币',), only_to_me=False)
# async def report_money(session: CommandSession):
#     global players_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     message = ''
#     for key, value in players_library.items():
#         message += str(value.wealth) + '个币[CQ:at, qq=' + str(key) + ']\n'
#     await session.send(message)
#
#
# # 拿钱
# @on_command('make_money', aliases=('收入', '援助', '税收'), only_to_me=False)
# async def make_money(session: CommandSession):
#     global players_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     qq_number = str(session.ctx['user_id'])
#     action = session.ctx['raw_message']
#     if '收入' in action or '1' in action or '一' in action:
#         players_library[qq_number].wealth += 1
#     elif '援助' in action or '2' in action or '二' in action or '两' in action or '俩' in action:
#         await save_data()
#         players_library[qq_number].wealth += 2
#     elif '税收' in action or '3' in action or '三' in action:
#         await save_data()
#         players_library[qq_number].wealth += 3
#     else:
#         return
#
#
# # 花钱
# @on_command('spend_money', aliases=('政变',), only_to_me=False)
# async def spend_money(session: CommandSession):
#     global players_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     qq_number = str(session.ctx['user_id'])
#     action = session.ctx['raw_message']
#
#     if '政变' in action:
#         if players_library[qq_number].wealth >= 7:
#             players_library[qq_number].wealth -= 7
#         else:
#             await session.send('这都没钱了，政变空气啊')
#     else:
#         return
#
#
# # 抢钱和刺杀
# @on_natural_language(keywords=('抢', '刺杀'), only_to_me=False)
# async def grab_money(session: CommandSession):
#     global players_library, identity_library, in_progress_flag
#
#     if not in_progress_flag:
#         return
#
#     if "？" != session.ctx['raw_message'][0] or "?" != session.ctx['raw_message'][0]:
#         return
#
#     message = session.ctx['raw_message']
#     qq_number = str(session.ctx['user_id'])
#     was_qq_number = await check_player(message)
#
#     if '刺杀' in message:
#         players_library[qq_number].wealth -= 3
#         await save_data()
#     elif '抢' in message:
#         await save_data()
#         if players_library[was_qq_number].wealth >= 2:
#             players_library[qq_number].wealth += 2
#             players_library[was_qq_number].wealth -= 2
#         elif players_library[was_qq_number].wealth == 1:
#             players_library[qq_number].wealth += 1
#             players_library[was_qq_number].wealth -= 1
#         elif players_library[was_qq_number].wealth == 0:
#             await session.send('他都没钱了，图个啥')
#         else:
#             return
#     else:
#         return
#
#
# # 结束
# @on_natural_language(keywords=('结束', '胜利'), only_to_me=False)
# async def finish(session: NLPSession):
#     global in_progress_flag
#     if in_progress_flag:
#         await session.send('结束了？要不要再来一把？^_~')
#         await game_end()
#     else:
#         return
