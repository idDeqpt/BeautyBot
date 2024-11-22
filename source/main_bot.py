import telebot
from telebot import types
import io
import config
import sqlite


bot = telebot.TeleBot(config.load_token())
database = sqlite.Database("beauty_database")


#Функция приветствия
@bot.message_handler(commands=["start"])
def start(message):
    database = sqlite.getConnection()
    database.addProfile(message.from_user.id)
    database.updateUsername(message.from_user.id, message.from_user.username)
    print(message.from_user.username)
    database.save()
    
    last_name = "" if (message.from_user.last_name == None) else (" " + message.from_user.last_name)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text = database.getLabel("test_name"),
                                          callback_data = "TEST"))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("catalog"),
                                          callback_data = "CATALOG"))
    
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}{last_name}\n" + database.getLabel("greeting"), reply_markup = markup)


@bot.callback_query_handler(func = lambda call: call.data == "MAIN_MENU")
def main_menu(call):
    print(call.from_user.id, call.data)
    database = sqlite.getConnection()
    database.addProfile(call.message.from_user.id)
    database.updateUsername(call.message.from_user.id, call.message.from_user.username)
    database.save()
    
    last_name = "" if (call.message.from_user.last_name == None) else (" " + call.message.from_user.last_name)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text = database.getLabel("test_name"),
                                          callback_data = "TEST"))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("catalog"),
                                          callback_data = "CATALOG"))
    
    bot.send_message(call.message.chat.id, database.getLabel("main_menu"), reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


#Блок тестирования
@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "TEST")
def test_button(call):
    print(call.from_user.id, call.data)
    database = sqlite.getConnection()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text = database.getLabel("test_button"),
                                          callback_data = "TEST_QUESTION@1@0"))
    if not (database.getTestResult(call.from_user.id) is None):
        markup.add(types.InlineKeyboardButton(text = database.getLabel("test_result_button"),
                                              callback_data = "TEST_RESULT"))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("main_menu_button"),
                                          callback_data = "MAIN_MENU"))
    
    bot.edit_message_text(database.getLabel("test_name"), call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)

@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "TEST_QUESTION")
def next_question(call):
    print(call.from_user.id, call.data)
    call_data = call.data.split("@")
    database = sqlite.getConnection()
    answers = database.getQuestionAnswers(call_data[1])
    
    result = str(database.getTestResult(call.from_user.id))
    result = result[ : int(call_data[1]) - 1] + call_data[2] + result[int(call_data[1]) : ]
    database.setTestResult(call.from_user.id, result)
    database.save()
    
    if (answers == []):
        send_test_results(call)
        return
    
    markup = types.InlineKeyboardMarkup()
    for answer in answers:
        markup.add(types.InlineKeyboardButton(text = answer[1],
                                              callback_data = "TEST_QUESTION@" + str(int(call_data[1]) + 1) + "@" + str(answer[0])))
    
    bot.edit_message_text(database.getQuestionText(call_data[1]), call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)

@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "TEST_RESULT")
def send_test_results(call):
    print(call.from_user.id, call.data)
    call_data = call.data.split("@")
    database = sqlite.getConnection()
    result = list(database.getTestResult(call.from_user.id))[1 : ]
    remedies = []
    pictures = []
    
    for i, answer in enumerate(result):
        answer_data = database.getQuestionAnswer(i + 1, int(answer))
        if not (answer_data[3] == None):
            remedies.append("Вопрос: " + database.getQuestionText(i + 1) + "\nОтвет: " + answer_data[2] + "\nРешение:\n" + answer_data[3])
        if not (answer_data[4] == None):
            pictures.append(types.InputMediaPhoto(io.BufferedReader(io.BytesIO(answer_data[4]))))
    
    pictures[0].caption = "\n\n".join(remedies)
    
    bot.send_media_group(call.message.chat.id, media = pictures)
    main_menu(call)
    bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.id)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


#Кнопка выбора категории
@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "CATALOG")
def catalog_button(call):
    print(call.from_user.id, call.data)
    database = sqlite.getConnection()
    
    markup = types.InlineKeyboardMarkup()
    for category in database.getPositionsCategories():
        markup.add(types.InlineKeyboardButton(text = category[1],
                                              callback_data = "CATEGORY@" + str(category[0])))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("main_menu_button"),
                                          callback_data = "MAIN_MENU"))
    
    bot.edit_message_text(database.getLabel("choise_category"), call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


#Кнопка выбора подкатегории
@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "CATEGORY")
def category_button(call):
    print(call.from_user.id, call.data)
    database = sqlite.getConnection()
    call_data = call.data.split("@")
    
    markup = types.InlineKeyboardMarkup()
    for subcategory in database.getPositionsSubcategories(call_data[1]):
        markup.add(types.InlineKeyboardButton(text = subcategory[1],
                                              callback_data = "SUBCATEGORY@" + str(subcategory[0])))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("back"),
                                          callback_data = "CATALOG"))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("main_menu_button"),
                                          callback_data = "MAIN_MENU"))
    
    bot.edit_message_text(database.getLabel("catalog") + ": " + database.getCategoryById(call_data[1])[1], call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


#Кнопка выбора в подкатегории
@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "SUBCATEGORY")
def subcategory_button(call):
    print(call.from_user.id, call.data)
    database = sqlite.getConnection()
    call_data = call.data.split("@")
    subcategory_data = database.getSubcategoryById(call_data[1])
    category_data = database.getCategoryById(subcategory_data[1])
    
    markup = types.InlineKeyboardMarkup()
    for i, position in enumerate(database.getPositions(call_data[1])):
        markup.add(types.InlineKeyboardButton(text = position[1],
                                              callback_data = "POSITION@" + str(position[0]) + "@" + str(i)))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("back"),
                                          callback_data = "CATEGORY@" + str(subcategory_data[1])))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("main_menu_button"),
                                          callback_data = "MAIN_MENU"))
    
    bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.id)
    bot.send_message(call.message.chat.id, database.getLabel("catalog") + ": " + category_data[1] + " -> " + subcategory_data[2], reply_markup = markup)
    #bot.edit_message_text(call_data[2], call.message.chat.id, call.message.id)
    #bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


#Кнопка вывода товара
@bot.callback_query_handler(func = lambda call: call.data.split("@")[0] == "POSITION")
def position_button(call):
    print(call.from_user.id, call.data)
    database = sqlite.getConnection()
    call_data = call.data.split("@")
    
    current_position = database.getPositionById(int(call_data[1]))
    subcategory_data = database.getSubcategoryById(current_position[1])
    category_data = database.getCategoryById(subcategory_data[1])
    
    positions = database.getPositions(current_position[1])
    position_i = int(call_data[2])
    back_i = position_i - 1
    next_i = position_i + 1
    
    caption_dict = {
        "catalog": category_data[1] + " -> " + subcategory_data[2],
        "name": current_position[2],
        "description": current_position[3] 
    }
    caption = ""
    for item in caption_dict.items():
        caption += database.getLabel(item[0]) + ": " + str(item[1]) + "\n\n"
    
    markup = types.InlineKeyboardMarkup()
    navigation_buttons = []
    if (back_i >= 0):
        navigation_buttons.append(types.InlineKeyboardButton(text = database.getLabel("back"),
                                                             callback_data = "POSITION@" + str(positions[back_i][0]) + "@" + str(back_i)))
    if (next_i < len(positions)):
        navigation_buttons.append(types.InlineKeyboardButton(text = database.getLabel("next"),
                                                             callback_data = "POSITION@" + str(positions[next_i][0]) + "@" + str(next_i)))
    markup.row(*navigation_buttons)
    markup.add(types.InlineKeyboardButton(text = database.getLabel("choise_position"),
                                          callback_data = "SUBCATEGORY@" + str(current_position[1])))
    markup.add(types.InlineKeyboardButton(text = database.getLabel("main_menu_button"),
                                          callback_data = "MAIN_MENU"))
    
    bot.edit_message_media(types.InputMediaPhoto(io.BufferedReader(io.BytesIO(current_position[-1])), caption = caption), call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = markup)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    

@bot.message_handler()
def pos(message):
    pass


if (__name__ == "__main__"):
    print("bot started")
    bot.polling(none_stop = True)
    print("bot ended")