async def check_num(message: str) -> int:
    if '1' in message or '一' in message:
        return 1
    elif '2' in message or '二' in message or '两' in message or '俩' in message:
        return 2
    elif '3' in message or '三' in message:
        return 3
    elif '4' in message or '四' in message:
        return 4
    elif '5' in message or '五' in message:
        return 5
    elif '6' in message or '六' in message:
        return 6
    elif '7' in message or '七' in message:
        return 7
    else:
        return -1

# # 保存数据
# async def save_data():
#     global players_library, players_library_copy, identity_library, identity_library_copy
#     players_library_copy = players_library
#     identity_library_copy = identity_library
#
#
# # 撤销
# async def back_to_previous_step():
#     global players_library, players_library_copy, identity_library, identity_library_copy
#     players_library = players_library_copy
#     identity_library = identity_library_copy
#
#
# 发牌
# async def shuffle_and_draw(player_number: int):
#     global players_library, identity_library
#     # 洗牌
#     shuffle(identity_library)
#
#     # 发牌
#     for num in range(1, player_number + 1):
#         participants = Player()  # 创建实例
#         participants.identities = identity_library[1:3]  # 输入身份
#         del identity_library[1:3]  # 删除已输入的
#         players_library[num] = participants  # 添加字典，方便查找
#
#
# # 换牌
# async def change_identity(qq_number: str, num: int):
#     global players_library, identity_library
#     identity_library.append(players_library[qq_number].identities.pop(num))
#     shuffle(identity_library)
#     players_library[qq_number].identities.append(identity_library.pop(0))
#
#
# # 确认玩家
# async def check_player(message: str):
#     global players_library
#     for qq_number in players_library.keys():
#         if qq_number in message:
#             return qq_number  # players_library[qq_number].identities
#         else:
#             continue
#
#
# # 游戏结束
# async def game_end():
#     global players_library, identity_library, in_progress_flag
#     in_progress_flag = False
#     identity_library = ['公爵 ', '队长 ', '夫人 ', '刺客 ', '大使 '] * 4
#     players_library.clear()
#
#
# # 身份检查
# async def check_identity(message: str):
#     if '公爵' in message:
#         return '公爵'
#     elif '大使' in message:
#         return '大使'
#     elif '队长' in message:
#         return '队长'
#     elif '夫人' in message:
#         return '夫人'
#     elif '刺客' in message:
#         return '刺客'
#     else:
#         return
