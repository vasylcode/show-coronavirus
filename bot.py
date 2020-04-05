import telebot

from bs4 import BeautifulSoup
from requests import get

headers = ({'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
sapo = "https://www.worldometers.info/coronavirus/"

bot = telebot.TeleBot('token') ## showcovidbot


usa = '🇺🇸'
russia = '🇷🇺'
looking = '🔍'
warning = '⚠'

##startText1 = usa +': Hi, I`m COVID-2019 bot.\nWrite me the name of the country to show the statistics of the coronavirus there.\n\n' + russia + ': Привет, я COVID-2019 бот.\nНапиши мне название страны чтобы узнать статистику коронавируса в ней.'

startText = usa + ' Hi, I`m COVID-2019 bot.\nWrite me the name of the country to show the statistics of the coronavirus there.'
onceMoreText = usa + ' Country was not found.\n\nWrite me the name of the country to show the statistics of the coronavirus there.'

startMarkup = telebot.types.InlineKeyboardMarkup()
""" startMarkup.add(telebot.types.InlineKeyboardButton(text='United States', callback_data='usa')) ## это чтобы выслать кажду кнопку по отдельности в столбик
startMarkup.add(telebot.types.InlineKeyboardButton(text='Italy', callback_data='it'))
startMarkup.add(telebot.types.InlineKeyboardButton(text='Ukraine', callback_data='uk')) """

button1 = telebot.types.InlineKeyboardButton(text='USA', callback_data='USA')
button2 = telebot.types.InlineKeyboardButton(text='Italy', callback_data='Italy')
button3 = telebot.types.InlineKeyboardButton(text='Ukraine', callback_data='Ukraine')

startMarkup.add(button1, button2, button3) ## а это высылыает три кнопки в столбик

def delSpaces(a): ## функция для удаления пробелов из строки
    return ''.join(a.split())

def getCountry(name): ## функция для извлечения информации о стране из HTML кода
    response = get(sapo, headers=headers)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    allTr = html_soup.find_all('tr')
    for i in range(1, 187):
        country = allTr[i].find_all('td')[0].text
        totalCases = allTr[i].find_all('td')[1].text
        death = allTr[i].find_all('td')[3].text
        recovered = allTr[i].find_all('td')[5].text

        if country.lower() == name.lower():
            boolState = True
            break
        else:
            boolState = False
    return boolState, country, delSpaces(totalCases), delSpaces(death), delSpaces(recovered)

@bot.message_handler(commands=['start']) ## срабатывание на команду /start
def start_message(message):
    bot.send_message(message.chat.id, startText, reply_markup=startMarkup)

@bot.message_handler(content_types=['text']) ## срабатывания на текст
def send_text(message):
    if message.text:
        bot.send_message(message.chat.id, looking + "Looking for a country...")
        boolState, country, totalCases, death, recovered = getCountry(message.text)
        if boolState:
            bot.send_message(message.chat.id, warning + ' ' + country + " / Cases: " + totalCases + " / Death: " + death + " / Recovered: " + recovered)
        else: ## если юзер написал непонятный нам текст
            bot.send_message(message.chat.id, onceMoreText, reply_markup=startMarkup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call): ## обработка результатов нажатий на кнопки
    bot.answer_callback_query(callback_query_id=call.id, text='processing...')
    if call.data:
        boolState, country, totalCases, death, recovered = getCountry(call.data)
        if boolState:
            bot.send_message(call.message.chat.id, warning + ' ' + country + " / Cases: " + totalCases + " / Death: " + death  + " / Recovered: " + recovered) ## отправка ответа

    ##bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id) ## убираем inline клавиатуру с сообщения


bot.polling()