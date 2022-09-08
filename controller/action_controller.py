import json

import controller.user_controller as user_controller
import controller.reply_controller as reply_controller
import controller.sheet_controller as sheet_controller
import controller.stock_controller as stock_controller
import controller.user_follow_controller as user_follow_controller
import controller.alloc_result_controller as alloc_result_controller
import module.convert_text_to_json as convert_text_to_json
import module.allocation_calculator as allocation_calculator
import global_variable.globals as g


def action_welcome(line_bot_api, event):
    tmp_wel = reply_controller.message_welcome(line_bot_api, event.source.user_id)
    tmp_start = reply_controller.message_sheet_start()
    reply_controller.reply_message(line_bot_api, event, tmp_wel + tmp_start)


def action_sheet_answer(user_id, postback=None):
    if postback is None:
        postback = {}
    message = []
    if "question_num" in postback:
        sheet_controller.write(user_id, int(postback["question_num"][0]), int(postback["answer"][0]))

    if sheet_controller.cursor(user_id):
        num = sheet_controller.cursor(user_id)
        message += reply_controller.message_sheet_show_question(num)

    else:
        action_risk_free_rate_set(user_id)
        message += reply_controller.message_sheet_complete()
        message += reply_controller.message_risk_free_rate(user_id)
    return message


def action_sheet_skip(user_id, postback=None):
    if postback is None:
        postback = {}

    message = []
    if "option" in postback:
        user_controller.set_risk_free_rate(user_id, g.GlobalVar.DEFAULT_RISK)
        message += reply_controller.message_sheet_complete()
        message += reply_controller.message_risk_free_rate(user_id)
    else:
        skip_message = reply_controller.message_sheet_skip()
        message += skip_message
    return message


def action_calculate(line_bot_api, event):
    user_id = user_controller.user_id(event.source.user_id)
    message = []
    if not user_follow_controller.read(user_id):
        action_user_follow(line_bot_api, event, '@關注清單')
    elif user_controller.read_update_time(user_id) > alloc_result_controller.read_update_time(user_id):
        allocation_calculator.allocation_cal(user_id)
        message += reply_controller.message_allocation_result_wait()
    else:
        model_type = user_controller.read_model_type(user_id)
        message += reply_controller.message_allocation_result(user_id, model_type)
    reply_controller.reply_message(line_bot_api, event, message)


def action_user_follow(line_bot_api, event, command):
    user_id = user_controller.user_id(event.source.user_id)

    message = []
    if "@關注清單+" in command:
        stock_code = command.replace("@關注清單+", "")

        if user_follow_controller.is_stock(stock_code):
            stock_controller.create(stock_code)
        else:
            message += reply_controller.message_user_follow_set(action='error')

        stock_id = stock_controller.read_by_stock_code(stock_code)

        if not user_follow_controller.read_connection(user_id, stock_id):
            user_follow_controller.create_connection(user_id, stock_id)

        message += reply_controller.message_user_follow(user_id)
        user_controller.update_update_time(user_id)
    elif "@關注清單-" in command:
        stock_code = command.replace("@關注清單-", "")
        stock_id = stock_controller.read_by_stock_code(stock_code)
        user_follow_controller.delete_connection(user_id, stock_id)
        message += reply_controller.message_user_follow(user_id)
        user_controller.update_update_time(user_id)
    else:
        message.extend(reply_controller.message_user_follow(user_id))
        message.extend(reply_controller.message_user_follow_set())

    reply_controller.reply_message(line_bot_api, event, message)


def action_risk_free_rate_set(user_id):
    with open("text_files/sheet_question_num.json") as f:
        answer_weight = json.load(f)
    answers = sheet_controller.read(user_id)

    risk_free_rate = 0
    for k, a in enumerate(answers[1:]):
        risk_free_rate += answer_weight['q' + str(k + 1) + 'a' + str(a)]
    risk_free_rate = risk_free_rate / len(answers) / 100
    user_controller.set_risk_free_rate(user_id, risk_free_rate)


def action_model_type(line_bot_api, event, postback=None):
    if postback is None:
        postback = {}

    user_id = user_controller.user_id(event.source.user_id)
    message = []
    if "modelType" in postback:
        if postback["modelType"][0] == "0":
            message += reply_controller.message_model_type_choosen(1)
            user_controller.set_model_type(user_id, 0)
        elif postback["modelType"][0] == "1":
            message += reply_controller.message_model_type_choosen(2)
            user_controller.set_model_type(user_id, 1)
        elif postback["modelType"][0] == "2":
            message += reply_controller.message_model_type_choosen(3)
            user_controller.set_model_type(user_id, 2)
    else:
        message += reply_controller.message_model_type()
    reply_controller.reply_message(line_bot_api, event, message)


def action_illustrate(line_bot_api, event, postback=None):
    if postback is None:
        postback = {}
    message = []
    if "option" in postback:
        if postback["option"][0] == "1":
            message += reply_controller.message_illustrate_option(1)
        elif postback["option"][0] == "3":
            message += reply_controller.message_illustrate_option(3)
    else:
        message += reply_controller.message_illustrate()
    reply_controller.reply_message(line_bot_api, event, message)


def action_about_us(line_bot_api, event):
    message = []
    message += reply_controller.message_about_us()
    reply_controller.reply_message(line_bot_api, event, message)


def set_risk_and_bound(line_bot_api, event, command):
    message = []
    user_id = user_controller.user_id(event.source.user_id)
    if "-edit" in command:
        risk_and_bound = convert_text_to_json.set_risk_bound(command)
        user_controller.set_risk_bound(user_id, risk_and_bound)
        message += reply_controller.message_risk_and_bound(user_id, 'update')
    else:
        message += reply_controller.message_risk_and_bound(user_id, 'set')
    reply_controller.reply_message(line_bot_api, event, message)
