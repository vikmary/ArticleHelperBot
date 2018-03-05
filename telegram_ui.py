#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import argparse
import telebot
import logging

from glavred_api import GlavRed


class UserState:

    def __init__(self):
        self.score_type = 'red'
        self.score_type_str = 'по словам'
        self.text = ""

    def set_score_type(self, score_type):
        print("Handling score_type=`{}`".format(score_type))
        self.score_type = score_type
        if score_type == 'blue':
            self.score_type_str = "но синтаксису"
        elif score_type == 'red':
            self.score_type_str = "по словам"
        else:
            print("strange score_type=`{}`".format(score_type))
        print("score_type =", self.score_type)


def init_bot(token, glvred, name='GlavRed'):
    bot = telebot.TeleBot(token)

    # Outputs debug messages to console.
    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)

    state = UserState()

    @bot.message_handler(commands=['score'])
    def send_start_message(message):
        chat_id = message.chat.id

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Слова",
                                       callback_data="score_type=red"),
            telebot.types.InlineKeyboardButton(text="Синтаксис",
                                       callback_data="score_type=blue")
        )
        out_message = "Выбирите тип шкалы:"
        bot.send_message(message.chat.id,
                         out_message,
                         reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def score_type_entry_callback(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if call.message:
            score_type_new = call.data.split('=', 1)[1]
            score_type_changed = bool(score_type_new != state.score_type)
            state.set_score_type(score_type_new)

            out_message = "Новый тип разбалловки: {}."\
                    .format(state.score_type_str)

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=out_message)

            print("score_type_changed=", score_type_changed)
            print("state.text =", state.text)
            if score_type_changed and state.text:
                out_message = "Пересчиваю баллы {} для последнего"\
                        " введенного текста.".format(state.score_type_str)
                bot.send_message(chat_id, out_message)
                reply_score(chat_id)

    @bot.message_handler(commands=['help'])
    def send_help_message(message):
        chat_id = message.chat.id
        out_message = "/score Выбрать тип шкалы" 
        bot.send_message(chat_id, out_message)

    @bot.message_handler()
    def handle_inference(message):
        chat_id = message.chat.id
        context = message.text
        state.text = copy.deepcopy(context)

        out_message = "Считаю баллы {} для последнего введенного текста."\
                .format(state.score_type_str)
        bot.send_message(chat_id, out_message)

        reply_score(chat_id)

    def reply_score(chat_id):
        score = glvred.get_score(state.text, state.score_type)
        print_text = state.text[:15]
        if len(state.text) > 15:
            print_text += ' <..>' 
        out_message = "{} баллов {} для \"{}\"."\
                .format(str(score), state.score_type_str, print_text)
        bot.send_message(chat_id, out_message)

    bot.polling(none_stop=True, interval=1, timeout=20)


def interact_glavred_by_telegram(token):
    with GlavRed() as glvred:
        init_bot(token, glvred)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token",  help="telegram bot token")
    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_args()
    interact_glavred_by_telegram(opts.token)

