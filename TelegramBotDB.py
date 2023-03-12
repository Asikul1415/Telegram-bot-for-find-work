import telebot
from telebot import types
import sqlite3
from datetime import*


	
bot = telebot.TeleBot("TOKEN")

db = sqlite3.connect("DB.db",check_same_thread=False)
sql = db.cursor()


type_of_work_default = ""
city_default = "" 
specialization_default = ""
desired_salary_default = 0
knowlege_of_english_default = 0
auto_mailing_default = 1 #automatic
message_frequensy_default = 1 #per day
number_of_orders_default = 3 # per message
subcription_status_default = 0
subcription_until_status_default = 0
trial_subcription_activation_default = 0








#START
@bot.message_handler(commands=["start"])
def send_welcome(message):
	bot.send_message(message.chat.id, f"""Привет, {message.from_user.first_name}. 
	Я бот который позволяет программистам экономить время на поиске доступных вакансий и заказов
	\nУчти я работаю не за бесплатно, а за небольшую плату. 
	Конечно я дам тебе сначала бесплатно воспользоваться мной, 
	а дальше сам решай что будешь делать, платить или нет.""")

	#id, user_id, subcription_status, subcription_until, auto_mailing_status, message_frequensy, number_of_orders
	#type_of_work, city, specialization, desired_salary, knowlege_of_english
	sql.execute("SELECT * FROM users WHERE user_id = ?",(message.chat.id,))
	if sql.fetchone() == None:
		sql.execute("INSERT INTO users VALUES (NULL, ?,?,?,?,?,?,?,?,?,?,?,?)",(message.chat.id,subcription_status_default,
		subcription_until_status_default,auto_mailing_default,message_frequensy_default,number_of_orders_default,
		type_of_work_default,city_default,specialization_default,desired_salary_default,knowlege_of_english_default,trial_subcription_activation_default))
		db.commit()
	main_menu(message)

def set_subcription_when_paying(operation_status,message):
	if operation_status == 'success':
		today = date.today()
		sql.execute("UPDATE users SET subcription_until == ? WHERE user_id = ?",((today+timedelta(days=30)).strftime("%d%m%Y"),message.chat.id))
		sql.execute("UPDATE users SET subcription_status == ? WHERE user_id = ?",(1,message.chat.id))
		db.commit()
		until = str(sql.execute('SELECT * FROM users WHERE user_id = ?',(message.chat.id,)).fetchone()[3])
		until_text = date(day = int(until[0:2]),month = int(until[2:4]),year=int(until[4:8])).strftime("%d-%m-%Y")
		bot.send_message(message.chat.id,'Подписка успешно активирована до ' + str(until_text))

def subscription_expiration(message):
	today = int(date.today())
	if today < sql.execute("SELECT * FROM users WHERE user_id = ?",(message.chat.id,)).fetchone()[3]:
		pass
	else:
		sql.execute("UPDATE users SET subcription_until = ? WHERE user_id = ?",(0,message.chat.id))
		sql.execute("UPDATE users SET subcription_status = ? WHERE user_id = ?",(0,message.chat.id))
		db.commit()
		
def check_subcription_status(call):
	if sql.execute("SELECT * FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[2] == 1:
		return True
	else:
		return False

def find_orders():
	pass


#MAIN MENU
@bot.message_handler(commands=["menu"])
def main_menu(message):
	markup = types.InlineKeyboardMarkup()
	
	markup.add(types.InlineKeyboardButton("Профиль 💻",callback_data="profile_button" ))
	markup.add(types.InlineKeyboardButton("Поиск закзов/вакансий",callback_data="find_orders_button"))
	markup.add(types.InlineKeyboardButton("Настройки бота 🛠️",callback_data="bot_settings_button" ))
	markup.add(types.InlineKeyboardButton("F.A.Q ❓",callback_data="faq_button" ))
	
	bot.send_message(message.chat.id, "Чего вы желаете?", reply_markup = markup)


#PROFILE
@bot.callback_query_handler(func=lambda c: c.data == "profile_button")
def profile(call):
		markup = types.InlineKeyboardMarkup()
		
		markup.add(types.InlineKeyboardButton("Показать профиль 👤",callback_data="show_profile_button" ))
		markup.add(types.InlineKeyboardButton("Тип работы(Фриланс, постоянная работа)",callback_data="type_of_work_button"))
		markup.add(types.InlineKeyboardButton("Город/Регион 🏙️",callback_data="city_button"))
		markup.add(types.InlineKeyboardButton("Специализация 🖥️",callback_data="specialization_button"))
		markup.add(types.InlineKeyboardButton("Желаемая зарплата 💶",callback_data="desired_salary_button"))
		markup.add(types.InlineKeyboardButton("Знание английского",callback_data="knowlege_of_english_button"))
		markup.add(types.InlineKeyboardButton("Вернуться в главное меню ⏮️",callback_data="back_to_main_menu_button"))
		
		bot.send_message(call.message.chat.id,"Выберите категорию:", reply_markup=markup)




#PROFILE Type of work
@bot.callback_query_handler(func=lambda c: c.data == "type_of_work_button")
def type_of_work_button(call):
	markup = types.InlineKeyboardMarkup(row_width=2)
	
	freelance_button = types.InlineKeyboardButton("Фриланс",callback_data = "freelance_button")
	full_time_job_button = types.InlineKeyboardButton("Постоянная работа",callback_data="full_time_job_button")
	markup.row(freelance_button,full_time_job_button)
	markup.add(types.InlineKeyboardButton("И то и то",callback_data = "freelance_and_full_time_job_button"))
	
	bot.send_message(call.message.chat.id,"Выберите подходящий вам тип работы:",reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "freelance_button")
def type_of_work_function(call):
	sql.execute("UPDATE users SET type_of_work == ? WHERE user_id = ?",('Фриланс',call.message.chat.id,))
	db.commit()
	bot.send_message(call.message.chat.id,"Сохранено.")
	profile(call)
@bot.callback_query_handler(func=lambda c: c.data == "full_time_job_button")
def type_of_work_function(call):
	sql.execute("UPDATE users SET type_of_work == ? WHERE user_id = ?",('Постоянная работа',call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,"Сохранено.")
	profile(call)
@bot.callback_query_handler(func=lambda c: c.data == "freelance_and_full_time_job_button")
def type_of_work_function(call):
	sql.execute("UPDATE users SET type_of_work == ? WHERE user_id = ?",('Не важно',call.message.chat.id,))
	db.commit()
	bot.send_message(call.message.chat.id,"Сохранено.")
	profile(call)


#PROFILE City or region
@bot.callback_query_handler(func=lambda c: c.data == "city_button")
def city_button(call):
	sent = bot.send_message(call.message.chat.id,"Укажите свой город/регион\n(Пример:Саратов)")
	bot.register_next_step_handler(sent,save_city)
def save_city(message):
	sql.execute("UPDATE users SET city == ? WHERE user_id = ?",(message.text,message.chat.id,))
	db.commit()
	bot.send_message(message.chat.id,f"Сохранено.")
	

#PROFILE Specialization
@bot.callback_query_handler(func=lambda c: c.data == "specialization_button")
def specialization_button(call):
	sent = bot.send_message(call.message.chat.id,"Введите свою специализацию.\n(Пример: Java junior)")
	bot.register_next_step_handler(sent,save_specialization)
def save_specialization(message):
	sql.execute("UPDATE users SET specialization == ? WHERE user_id = ?",(message.text,message.chat.id,))
	db.commit()
	bot.send_message(message.chat.id,f"Сохранено.")


#PROFILE Desired salary
@bot.callback_query_handler(func=lambda c: c.data == "desired_salary_button")
def desired_salary_button(call):
	sent = bot.send_message(call.message.chat.id,"Напишите от скольки начинается ваша желаемая зарплата/цена за ваши услуги 💶.\n(Укажите в цифрах и рублях, без точек, запятых или пробелов)")
	bot.register_next_step_handler(sent,save_desired_salary)
def save_desired_salary(message):
	sql.execute("UPDATE users SET desired_salary == ? WHERE user_id = ?",(message.text,message.chat.id,))
	db.commit()
	bot.send_message(message.chat.id,f"Сохранено.")
	

#PROFILE Knowlege of Enlish
@bot.callback_query_handler(func=lambda c: c.data == "knowlege_of_english_button")
def knowlege_of_english_button(call):
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton("Да",callback_data="knowlege_of_enlish_answer_yes"))
	markup.add(types.InlineKeyboardButton("Нет",callback_data="knowlege_of_enlish_answer_no"))
	bot.send_message(call.message.chat.id,"Знаете ли вы английский?",reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "knowlege_of_enlish_answer_yes")
def knowlege_of_english_function(call):
	sql.execute("UPDATE users SET knowlege_of_english == ? WHERE user_id = ?",('Есть',call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	profile(call)

@bot.callback_query_handler(func=lambda c: c.data == "knowlege_of_enlish_answer_no")
def knowlege_of_english_function(call):
	sql.execute("UPDATE users SET knowlege_of_english == ? WHERE user_id = ?",('Нету',call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	profile(call)


#PROFILE Back to main menu
@bot.callback_query_handler(func=lambda c: c.data == "back_to_main_menu_button" )
def back_to_main_menu(call):
	main_menu(call.message)

#PROFILE Show profile
@bot.callback_query_handler(func= lambda c: c.data == "show_profile_button")
def show_profile(call):
	bot.send_message(call.message.chat.id,f"""Ваш профиль выглядит так: 
	Тип работы: {sql.execute("SELECT * FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[7]}
	Город: {sql.execute("SELECT * FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[8]}
	Специализация: {sql.execute("SELECT * FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[9]}
	Желаемая зарплата: {sql.execute("SELECT *  FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[10]}
	Знание английского: {sql.execute("SELECT * FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[11]} 
	""")
	profile(call)


#FIND ORDERS
@bot.callback_query_handler(func=lambda c: c.data == "find_orders_button")
def find_orders_button(call):
	if check_subcription_status(call):
		find_orders()
		bot.send_message(call.message.chat.id,"Successful")
	else:
		bot.send_message(call.message.chat.id,"У вас неактивирована подписка! Пожалуйста приобретите её для использования!")




#BOT SETTINGS
@bot.callback_query_handler(func = lambda c: c.data == "bot_settings_button")
def bot_settings(call):
	markup = types.InlineKeyboardMarkup()

	markup.add(types.InlineKeyboardButton("Рассылка вакансий/заказов автоматически 🤖",callback_data="auto_mailing_status_button" ))
	markup.add(types.InlineKeyboardButton("Частота сообщений ✉️",callback_data="message_frequensy_per_day_button"))
	markup.add(types.InlineKeyboardButton("Кол-во вакансий/заказов за сообщение 🔢",callback_data="number_of_orders_per_message_button"))
	markup.add(types.InlineKeyboardButton("Подписка 💸",callback_data="subcription_status_button"))
	markup.add(types.InlineKeyboardButton("Вернуться в главное меню ⏮️",callback_data="back_to_main_menu_button"))
	
	bot.send_message(call.message.chat.id,"Выберите настройку: ",reply_markup=markup)


#BOT SETTINGS auto_mailing_status
@bot.callback_query_handler(func=lambda c: c.data == "auto_mailing_status_button")
def auto_mailing_status_button(call):
	markup = types.InlineKeyboardMarkup()

	markup.add(types.InlineKeyboardButton("Автоматически",callback_data="auto_mailing_status_true"))
	markup.add(types.InlineKeyboardButton("По запросу пользователя",callback_data="auto_mailing_status_false"))

	bot.send_message(call.message.chat.id,"Выберите статус рассылки: ",reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "auto_mailing_status_true")
def auto_mailing_status(call):
	sql.execute("UPDATE users SET auto_mailing_status == ? WHERE user_id = ?",(1,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)

@bot.callback_query_handler(func=lambda c: c.data == "auto_mailing_status_false")
def auto_mailing_status(call):
	sql.execute("UPDATE users SET auto_mailing_status == ? WHERE user_id = ?",(0,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)


#BOT SETTINGS message_frequensy
@bot.callback_query_handler(func=lambda c: c.data == "message_frequensy_per_day_button")
def message_frequensy_button(call):
	markup = types.InlineKeyboardMarkup()

	markup.add(types.InlineKeyboardButton("1 раз в день(в 12 по МСК)",callback_data="message_frequensy_1_per_day"))
	markup.add(types.InlineKeyboardButton("3 раза в день(6,12,18 по МСК)",callback_data="message_frequensy_3_per_day"))

	bot.send_message(call.message.chat.id,"Выберите число: ",reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "message_frequensy_1_per_day")
def auto_mailing_status(call):
	sql.execute("UPDATE users SET message_frequensy == ? WHERE user_id = ?",(1,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)

@bot.callback_query_handler(func=lambda c: c.data == "message_frequensy_3_per_day")
def auto_mailing_status(call):
	sql.execute("UPDATE users SET message_frequensy == ? WHERE user_id = ?",(3,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)


#BOT SETTINGS number of orders per message number_of_orders_per_message
@bot.callback_query_handler(func=lambda c: c.data == "number_of_orders_per_message_button")
def number_of_orders_per_message_button(call):
	markup = types.InlineKeyboardMarkup()

	one_order_per_message_button = types.InlineKeyboardButton("1 вакансия/заказ)",callback_data="number_of_orders_per_message_is_one")
	three_orders_per_message_button = types.InlineKeyboardButton("3 вакансий/заказов)",callback_data="number_of_orders_per_message_is_three")
	six_orders_per_message_button = types.InlineKeyboardButton("6 вакансий/заказов)",callback_data="number_of_orders_per_message_is_six")
	ten_orders_per_message_button = types.InlineKeyboardButton("10 вакансий/заказов)",callback_data="number_of_orders_per_message_is_ten")

	markup.row(one_order_per_message_button,three_orders_per_message_button)
	markup.row(six_orders_per_message_button,ten_orders_per_message_button)

	bot.send_message(call.message.chat.id,"Выберите число: ",reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "number_of_orders_per_message_is_one")
def number_of_message_per_message(call):
	sql.execute("UPDATE users SET number_of_orders == ? WHERE user_id = ?",(1,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)

@bot.callback_query_handler(func=lambda c: c.data == "number_of_orders_per_message_is_three")
def number_of_message_per_message(call):
	sql.execute("UPDATE users SET number_of_orders == ? WHERE user_id = ?",(3,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)

@bot.callback_query_handler(func=lambda c: c.data == "number_of_orders_per_message_is_six")
def number_of_message_per_message(call):
	sql.execute("UPDATE users SET number_of_orders == ? WHERE user_id = ?",(6,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)

@bot.callback_query_handler(func=lambda c: c.data == "number_of_orders_per_message_is_ten")
def number_of_message_per_message(call):
	sql.execute("UPDATE users SET number_of_orders == ? WHERE user_id = ?",(10,call.message.chat.id,))
	db.commit()	
	bot.send_message(call.message.chat.id,f"Сохранено.")
	bot_settings(call)

#BOT SETTINGS subcription status
@bot.callback_query_handler(func=lambda c: c.data == "subcription_status_button")
def subcription_status_button(call):
	if sql.execute("SELECT * FROM users WHERE user_id = ?",(call.message.chat.id,)).fetchone()[2] == 0:
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton("Оплатить",callback_data="payment_button"))
		bot.send_message(call.message.chat.id,'Подписка неактивна',reply_markup=markup)
		if check_subcription_status(call) == False:
			markup = types.InlineKeyboardMarkup()
			markup.add(types.InlineKeyboardButton("Активировать",callback_data="trial_subcription_button_yes")) 
			bot.send_message(call.message.chat.id,'Активировать пробную подписку?',reply_markup=markup)
		bot_settings(call)
	else:
		until = str(sql.execute('SELECT * FROM users WHERE user_id = ?',(call.message.chat.id,)).fetchone()[3])
		until_text = date(day = int(until[0:2]),month = int(until[2:4]),year=int(until[4:8])).strftime("%d-%m-%Y")
		bot.send_message(call.message.chat.id,'Подписка активна до ' + str(until_text))
		bot_settings(call)

#BOT SETTING trial subcription
@bot.callback_query_handler(func=lambda c: c.data == "trial_subcription_button_yes")
def trial_subcription(call):
	today = date.today()
	sql.execute("UPDATE users SET subcription_until == ? WHERE user_id = ?",((today+timedelta(days=7)).strftime("%d%m%Y"),call.message.chat.id))
	sql.execute("UPDATE users SET subcription_status == ? WHERE user_id = ?",(1,call.message.chat.id))
	sql.execute("UPDATE users SET trial_subscription_activation == ? WHERE user_id = ?",(1,call.message.chat.id))
	db.commit()
	until = str(sql.execute('SELECT * FROM users WHERE user_id = ?',(call.message.chat.id,)).fetchone()[3])
	until_text = date(day = int(until[0:2]),month = int(until[2:4]),year=int(until[4:8])).strftime("%d-%m-%Y")
	bot.send_message(call.message.chat.id,"Подписка успешно активирована и действует до " + str(until_text))
	bot_settings(call)



#F.A.Q
@bot.callback_query_handler(func=lambda c: c.data == "faq_button")
def faq(call):
	bot.send_message(call.message.chat.id,"""
	Q: Сколько длиться пробная подписка?
	A: 1 неделю 

	Q:Сколько стоит обычная подписка?
	A: 50 рублей
	
	Q:Сколько длится подписка?
	A:Пока что 1 месяц. В будущем планируется расширить варианты 
	до 3 месяцев,6 месяцев и года.                                                                 
	
	Q:Если бот скинул ссылку на скам-объявление?
	A:Этот бот не проверяет содержимое самих объявлений, его задача состоит в том чтобы просто скинуть вам 
	подходящие объявления. Так что если что-то вдруг не дай Бог случилось, то обращайтесь к администрации сайта.                        
	
	Q: Как связаться с создателем бота?
	A:Просто напишите отзыв об улучшении, или ошибке.
	
	Q:Проблемы с оплатой/или ещё чем-либо
	A: Оставьте отзыв об ошибке.""")
	
	operation_status = 'success'
	#set_subcription_when_paying(operation_status,call.message)
	subscription_expiration(call.message)
	main_menu(call.message)







	









































bot.infinity_polling()
