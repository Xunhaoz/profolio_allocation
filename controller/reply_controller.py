from linebot.models import (
    TextSendMessage, TemplateSendMessage, StickerSendMessage,
    CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn, ConfirmTemplate, QuickReplyButton,
    QuickReply,
    PostbackTemplateAction, PostbackAction, URITemplateAction
)
import controller.user_controller as user_controller
import global_variable.globals as g
import controller.user_follow_controller as user_follow_controller
import controller.stock_controller as stock_controller
import controller.alloc_result_controller as alloc_result_controller
import json


def reply_message(line_bot_api, event, message):
    if len(message) != 0:
        try:
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def load_json_file(json_file_path):
    with open(json_file_path, 'r', encoding="utf-8") as json_file:
        dic_file = json.load(json_file)
    return dic_file


def message_welcome(line_bot_api, line_id):
    dic_text = load_json_file("text_files/text_welcome.json")
    display_name = line_bot_api.get_profile(line_id).display_name
    message = [
        TextSendMessage(
            text=display_name + '\n'.join(dic_text['welcome_text'])
        )
    ]
    return message


def message_sheet_start():
    dic_text = load_json_file("text_files/text_sheet.json")
    message = [
        TemplateSendMessage(
            alt_text=''.join(dic_text["0"]),
            template=ConfirmTemplate(
                text='\n'.join(dic_text["1"]),
                actions=[
                    PostbackAction(
                        label=''.join(dic_text["0"]),
                        data='action=sheet&option=continue'
                    ),
                    PostbackAction(
                        label=''.join(dic_text["2"]),
                        data='action=sheet'
                    ),
                ]
            )
        )
    ]
    return message


def message_sheet_show_question(num):
    dic_text = load_json_file('text_files/text_sheet_content.json')

    question = [f"Q{str(num)}.", ]
    question.extend(dic_text['Q' + str(num)]['question'])
    items = []

    for k, ans in enumerate(dic_text["Q" + str(num)]['answer']):
        code = f"({chr(65 + k)})"
        question.append('\n' + code + ans)
        items.append(
            QuickReplyButton(
                action=PostbackAction(
                    text=code + ans,
                    label=code,
                    data="action=sheet&option=continue&question_num=" + str(num) + "&answer=" + str(k)),
            )
        )

    message = [
        TextSendMessage(
            text='\n'.join(question),
            quick_reply=QuickReply(
                items=items
            )
        )
    ]
    return message


def message_sheet_skip():
    dic_text = load_json_file('text_files/text_sheet.json')
    message = [
        TemplateSendMessage(
            alt_text=''.join(dic_text["3"]),
            template=ConfirmTemplate(
                text=''.join(dic_text["4"]) + str(g.GlobalVar.DEFAULT_RISK),
                actions=[
                    PostbackTemplateAction(
                        label=''.join(dic_text["7"]),
                        data='action=sheet&option=continue'
                    ),
                    PostbackTemplateAction(
                        label=''.join(dic_text["6"]),
                        data='action=sheet&option=skip'
                    )

                ]
            )
        )
    ]
    return message


def message_sheet_complete():
    dic_text = load_json_file('text_files/text_sheet.json')
    message = [
        StickerSendMessage(
            package_id='8522',
            sticker_id='16581267'
        ),
        TextSendMessage(
            text=''.join(dic_text["8"])
        ),
    ]
    return message


def message_sheet_undone():
    dic_text = load_json_file("text_files/text_sheet.json")
    message = [
        TextSendMessage(
            text=''.join(dic_text["5"])
        ),
    ]
    return message


def message_user_follow(user_id):
    dic_text = load_json_file('text_files/text_user_follow.json')
    if user_follow_controller.read(user_id):
        stock_list = []
        for connection in user_follow_controller.read(user_id):
            stock_list.append(stock_controller.read_by_stock_id(connection[2]))

        message = [
            TextSendMessage(
                text=''.join(dic_text["0"]) + '\n'.join(stock_list)
            ),
        ]
    else:
        message = [
            TextSendMessage(
                text=''.join(dic_text["3"])
            ),
        ]
    return message


def message_user_follow_set(action='method'):
    dic_text = load_json_file('text_files/text_user_follow.json')
    dic_key = {'method': "1", 'error': '2'}
    message = [
        TextSendMessage(
            text='\n'.join(dic_text[dic_key[action]])
        ),
    ]
    if action == 'method':
        message += [
            TextSendMessage(
                text='\n'.join(dic_text['4'])
            ),
        ]
        message += [
            TextSendMessage(
                text='\n'.join(dic_text['5'])
            ),
        ]
    return message


def message_risk_free_rate(user_id):
    dic_text = load_json_file('text_files/text_risk_free_rate.json')
    risk_free = user_controller.read_risk_free_rate(user_id)
    message = [
        TextSendMessage(
            text=''.join(dic_text["0"]) + str(risk_free)
        ),
    ]
    return message


def message_model_type():
    dic_text = load_json_file('text_files/text_model_type.json')
    message = [
        TemplateSendMessage(
            alt_text=''.join(dic_text["1"]),
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=g.GlobalVar.BASE_URL + ''.join(dic_text["3"]).rstrip(),
                        title=''.join(dic_text["4"]),
                        text=''.join(dic_text["5"]),
                        actions=[
                            PostbackTemplateAction(
                                label=''.join(dic_text["2"]),
                                data='action=model&modelType=0'
                            ),
                        ]
                    ),
                    # CarouselColumn(
                    #     thumbnail_image_url=g.GlobalVar.BASE_URL + ''.join(dic_text["6"]).rstrip(),
                    #     title=''.join(dic_text["7"]),
                    #     text=''.join(dic_text["8"]),
                    #     actions=[
                    #         PostbackTemplateAction(
                    #             label=''.join(dic_text["2"]),
                    #             data='action=model&modelType=1'
                    #         ),
                    #     ]
                    # ),
                    CarouselColumn(
                        thumbnail_image_url=g.GlobalVar.BASE_URL + ''.join(dic_text["9"]).rstrip(),
                        title=''.join(dic_text["10"]),
                        text=''.join(dic_text["11"]),
                        actions=[
                            PostbackTemplateAction(
                                label=''.join(dic_text["2"]),
                                data='action=model&modelType=2'
                            ),
                        ]
                    ),
                ]
            )
        )
    ]
    return message


def message_model_type_choosen(type):
    dic_text = load_json_file('text_files/text_model_type.json')
    model_type = ["-1", "4", "7", "10"]
    message = [
        TextSendMessage(  # 傳送文字
            text=''.join(dic_text["0"]) + ''.join(dic_text[model_type[type]])
        ),
    ]
    return message


def message_illustrate():
    dic_text = load_json_file('text_files/text_illustrate.json')
    message = [
        TemplateSendMessage(
            alt_text=''.join(dic_text["0"]),
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url=g.GlobalVar.BASE_URL + ''.join(dic_text["1"]).rstrip(),
                        action=PostbackTemplateAction(
                            label=''.join(dic_text["2"]),
                            data='action=illustrate&option=1'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url=g.GlobalVar.BASE_URL + ''.join(dic_text["4"]).rstrip(),
                        action=URITemplateAction(
                            label=''.join(dic_text["5"]),
                            uri=''.join(dic_text["6"]).rstrip()
                        )
                    ),
                    ImageCarouselColumn(
                        image_url=g.GlobalVar.BASE_URL + ''.join(dic_text["7"]).rstrip(),
                        action=PostbackTemplateAction(
                            label=''.join(dic_text["8"]),
                            data='action=illustrate&option=3'
                        )
                    )
                ]
            )
        ),
    ]
    return message


def message_illustrate_option(option):
    illustration = ["-1", "3", "6", "9"]
    dic_text = load_json_file('text_files/text_illustrate.json')
    message = [
        TextSendMessage(
            text='\n'.join(dic_text[illustration[int(option)]])
        )
    ]
    return message


def message_about_us():
    dic_text = load_json_file('text_files/text_about_us.json')
    message = [
        TextSendMessage(
            text=''.join(dic_text["0"])
        ),
    ]
    return message


def message_risk_and_bound(user_id, command):
    dic_text = load_json_file('text_files/text_calculate.json')
    risk_free = user_controller.read_risk_free_rate(user_id)
    stocks = user_follow_controller.read(user_id)

    text = []
    if command == 'update':
        text.append('\n'.join(dic_text["9"]))
    elif command == 'set':
        text.append('\n'.join(dic_text["10"]))
        text.append('\n'.join(dic_text["1"]))

    text.append('\n')
    text.append(''.join(dic_text["5"]) + str(risk_free))

    text.append('\n')
    text.append(''.join(dic_text["6"]) + "否")

    text.append('\n')
    text.append(''.join(dic_text["7"]) + "0.0")
    text.append(''.join(dic_text["8"]))

    text.append('\n')
    text.append(''.join(dic_text["3"]) + "1.0")
    text.append(''.join(dic_text["4"]) + "0.0")

    message = [
        TextSendMessage(
            text='\n'.join(text)
        ),
    ]
    return message


def message_allocation_result(user_id, model):
    alloc_result = alloc_result_controller.read_allocate_result(user_id, model)
    alloc_result = json.loads(alloc_result)
    risk_free = user_controller.read_risk_free_rate(user_id)
    risk_not_free = 1 - risk_free

    text = ""
    text += f"現金應該配置 {risk_free * 100}%\n"
    for stock_code, rate in alloc_result['clean_weight'].items():
        text += f"{stock_code} 應該配置 {rate * 100 * risk_not_free}%\n"

    text += f"\n年化報酬率為\n\t{alloc_result['performance']['expected_annual_return']}\n"
    text += f"年化波動率為\n\t{alloc_result['performance']['annual_volatility']}\n"
    text += f"夏普指數\n\t{alloc_result['performance']['sharpe_ratio']}"
    message = [
        TextSendMessage(
            text=text
        ),
    ]
    return message


def message_allocation_result_wait():
    message = [
        TextSendMessage(
            text="程式計算中，請稍後..."
        ),
    ]
    return message
