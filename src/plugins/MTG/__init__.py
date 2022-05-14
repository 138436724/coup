import httpx
from nonebot import on_command
# from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment

draw_cards = on_command("抽卡", aliases={'抽牌', '抽卡', 'random'}, priority=9)


# headers = {
#     'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36 Edg/84.0.522.44'
# }


@draw_cards.handle()
async def random_card(bot: Bot, event: Event, state: T_State):
    # global headers
    url = r"https://api.scryfall.com/cards/random"

    response = httpx.get(url=url)  # , headers=headers)
    response_text = response.json()
    card_name = response_text["scryfall_uri"]
    # print(type(card_name))
    await draw_cards.finish(card_name)
