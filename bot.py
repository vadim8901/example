#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import config
import datetime
from telebot import apihelper, types
from telebot.types import CallbackQuery, ReplyKeyboardRemove
import telebot_calendar

key_Button = []
dateUsers = dict()
text_Massiv = dict()
messageUsers = dict()
bot = telebot.TeleBot(config.TOKEN)

calendar = telebot_calendar.CallbackData("calendar", "action", "year", "month", "day")


def mainmenu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("дата.время.человек")
    markup.add(button1)
    return markup


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("дата.время.человек")
    markup.add(button1)
    bot.send_message(message.chat.id, 'Привет' , reply_markup=markup)



@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.chat.type == 'private':
        if message.text == 'дата.время.человек':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            main_menu1 = types.KeyboardButton("В главное меню")
            keyboard.add(main_menu1)
            now = datetime.datetime.now()
            date_message = bot.send_message(message.chat.id, "Дата",
                                            reply_markup=telebot_calendar.create_calendar(name=calendar.prefix,
                                                                                          year=now.year,
                                                                                          month=now.month))
            messageUsers[message.from_user.id] = date_message.message_id
            bot.send_message(message.chat.id, 'Выберите нужную дату.', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar.prefix))
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    keyboard_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu = types.KeyboardButton("В главное меню")
    keyboard_main_menu.add(main_menu)
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        if telebot_calendar.check_date(date):
            dateUsers[call.from_user.id] = f"{date.strftime('%d.%m.%Y')}"
            print(dateUsers[call.from_user.id])
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Вы выбрали: {date.strftime('%d.%m.%Y')}",
                reply_markup=ReplyKeyboardRemove(),
            )
            key = types.InlineKeyboardMarkup(row_width=3)
            for i in range(0, 18, 1):
                key_Button.append(types.InlineKeyboardButton(text=str(15 + i % 18 // 2) + ':' + str(i % 2 * 3) + '0',
                                                             callback_data=str(15 + i % 18 // 2) + ':' + str(
                                                                 i % 2 * 3) + '0'))
            key_Button.append(types.InlineKeyboardButton(text="00:00", callback_data="00:00"))
            key_Button.append(types.InlineKeyboardButton(text="00:30", callback_data="00:30"))
            key_Button.append(types.InlineKeyboardButton(text="01:00", callback_data="01:00"))
            key_Button.reverse()
            for j in range(0, 7, 1):
                key.row(key_Button.pop(), key_Button.pop(), key_Button.pop())
            first = bot.send_message(call.from_user.id, "Выберите время", reply_markup=key)
            messageUsers[call.from_user.id] = first.message_id
            bot.send_message(call.message.chat.id, 'Выберите нужное время.', reply_markup=keyboard_main_menu)

        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Вы не можете выбрать дату из прошлого",
                                      show_alert=True)
        print(f"{calendar}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="отмена",
            reply_markup=ReplyKeyboardRemove(),
        )
        bot.send_message(call.message.chat.id, 'Вы в главном меню', reply_markup=mainmenu())
        print(f"{calendar}: Cancellation")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: CallbackQuery):
    main_menu = types.KeyboardButton("В главное меню")
    markup_request = types.ReplyKeyboardMarkup(resize_keyboard=1)
    item_request = types.KeyboardButton("Отправить свой контакт ☎️", request_contact=True)
    markup_request.add(item_request, main_menu)
    if call.message:
        for i in range(0, 48, 1):
            if i < 20:
                s = '0'
            else:
                s = ''
            s = s + str(i // 2) + ":" + str(3 * (i % 2)) + "0"
            if call.data == s:
                bot.send_message(
                    chat_id=call.from_user.id,
                    text="Вы выбрали: " + s,
                    reply_markup=ReplyKeyboardRemove(),
                )
                bot.delete_message(
                    chat_id=call.message.chat.id, message_id=call.message.message_id
                )
                bot.send_message(call.message.chat.id,
                                 "Пришлите нам свои контакты, нажмите на кнопку <b>Отправить "
                                 "свой контакт ☎️</b>", parse_mode='html',
                                 reply_markup=markup_request)
                text_Massiv[call.from_user.id] = (
                        "Пользователь ID: " + str(call.from_user.id) + "\nДата: "
                        + dateUsers[call.from_user.id] + "\nВремя: " + s)
                dateUsers.pop(call.from_user.id, None)


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    telega_markup = types.InlineKeyboardMarkup(row_width=1)
    telega = types.InlineKeyboardButton(text='Телеграм канал', url='https://t.me/pewpewpew3')
    telega_markup.add(telega)
    text1 = text_Massiv[message.from_user.id]
    text = message.contact.phone_number
    bot.send_message(message.chat.id, "Спасибо, скоро мы с вами свяжемся!", reply_markup=mainmenu())
    bot.send_message(message.chat.id, "Подписывайтесь на наш телеграм канал", reply_markup=telega_markup)
    bot.send_message('-1001479834434', text1 + "\nНомер: " + text + "\nИмя: " + message.from_user.first_name)
    text_Massiv.pop(message.from_user.id, None)


bot.polling(none_stop=True)

