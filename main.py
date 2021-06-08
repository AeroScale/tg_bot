import config
import telebot
import requests
from telebot import types
from pyowm import OWM
from covid import Covid
from pyowm.utils.config import get_default_config
from bs4 import BeautifulSoup

covid = Covid(source="worldometers")
covid.get_data()
URL = 'https://tvfeed.in/film/random/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36', 'ACCEPT': '*/*'}

owm = OWM(config.token2)
mgr = owm.weather_manager()
config_dict = get_default_config()
config_dict['language'] = 'ru'
bot = telebot.TeleBot(config.token)

response = requests.get(config.url).json()

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я могу показать тебе текущий курс валют и погоду и многое другое .\n' +
        'Чтобы узнать текущий курс, введи /ex.\n' +
        'Чтобы узнать текущую погоду /w.\n' +
        'Чтобы узнать количество новых заражений COVID-19 в Украине /cov.\n' +
        'Чтобы получить случайный фильм /film.\n' +
        'Что бы получить помощь, введи /help.'
  )

@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Написать разработчику', url='telegram.me/QuentinQuarantin0'
  )
    )
    bot.send_message(
        message.chat.id,
        '1) Чтобы узнать текущий курс валют используй /ex.\n' +
        '2) Чтобы узнать текущую погоду используй /w.\n' +
        '2) Чтобы узнать всю текущую информацию /all.\n' +
        '2) Чтобы получить случайный фильм /film.\n' +
        '3) Чтобы узнать колличество новых заражений COVID-19 в Украине используй /cov.',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['ex'])
def ex(message):
    dol_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    dol_buy = dol_r[0]['buy']
    dol_buy_f = round(float(dol_buy) * float(10000) / float(10000), 3)
    dol_sel = dol_r[0]['sale']
    dol_sel_f = round(float(dol_sel) * float(10000) / float(10000), 3)
    dol_ans = 'USD: ' + str(dol_buy_f) + ' / ' + str(dol_sel_f)

    eur_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    eur_buy = eur_r[1]['buy']
    eur_buy_f = round(float(eur_buy) * float(10000) / float(10000), 3)
    eur_sel = eur_r[1]['sale']
    eur_sel_f = round(float(eur_sel) * float(10000) / float(10000), 3)
    eur_ans = 'EUR: ' + str(eur_buy_f) + ' / ' + str(eur_sel_f)

    rur_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    rur_buy = rur_r[2]['buy']
    rur_buy_f = round(float(rur_buy) * float(10000) / float(10000), 3)
    rur_sel = rur_r[2]['sale']
    rur_sel_f = round(float(rur_sel) * float(10000) / float(10000), 3)
    rur_ans = 'RUR: ' + str(rur_buy_f) + ' / ' + str(rur_sel_f)

    btc_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    btc_buy = btc_r[3]['buy']
    btc_sel = btc_r[3]['sale']
    btc_ans = 'BTC: ' + btc_buy + ' / ' + btc_sel

    ans_ex = 'Курс валют (ПриватБанк):' + '\n\n' + dol_ans + '\n' + eur_ans + '\n' + rur_ans + '\n' + btc_ans

    bot.send_message(message.chat.id, ans_ex)

@bot.message_handler(commands=['cov'])
def cov(message):
    new_cases = covid.get_status_by_country_name('Ukraine')
    new = new_cases['new_cases']
    total = new_cases['confirmed']
    death = new_cases['new_deaths']
    tests = new_cases['total_tests']

    ans = 'COVID-19 статистика: ' + '\n\n' + 'Новых заражений сегодня: +' + str(new) + '\n' + 'Новых смертей: +' + str(death) + '\n' + "Всего подтверждено случаев: " + str(total) + '\n' + 'Всего проведено тестов: ' + str(tests)

    bot.send_message(message.chat.id, ans)

@bot.message_handler(commands=['film'])
def porn(message):
    def get_html(url, params=None):
        r = requests.get(url, headers=HEADERS, params=params)
        return r

    def get_contetnt(html):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', {'class': 'container item-info'})
        for item in items:
            cont = item.find('div', {'class': 'container tcenter'})
            name_ru = cont.find('h1', {'class': 'f32'}).text
            name_eng = cont.find('h3', {'itemprop': 'alternativeHeadline'}).text
            #country = cont.find('p', {'itemprop': 'countryOfOrigin'}).text
            genre = cont.find('a', {'itemprop': 'genre'}).text
            about = item.find('div', {'class': 'about'}).text
            mes_film = 'Название: ' + name_ru + ' / ' + name_eng + '\n\n' + 'Жанр: ' + genre + '\n\n' + 'Описание: ' + about
            bot.send_message(message.chat.id, 'Привет, вот случайный фильм для тебя: ' + '\n\n' + mes_film)
    def pars():
        html = get_html(URL)
        if html.status_code == 200:
            get_contetnt(html.text)
        else:
            print('Error')

    pars()


@bot.message_handler(commands=['all'])
def all(message):
    observation1 = mgr.weather_at_place('Kyiv, UA')
    w1 = observation1.weather
    temp_kyiv = w1.temperature('celsius')["temp"]
    temp_kyiv_r = round(temp_kyiv)
    answer1 = "В городе Киев сейчас: " + str(temp_kyiv_r) + " °C."

    observation2 = mgr.weather_at_place('Bila Tserkva, UA')
    w2 = observation2.weather
    temp_bc = w2.temperature('celsius')["temp"]
    temp_bc_r = round(temp_bc)
    answer2 = "В городе Белая Церковь сейчас: " + str(temp_bc_r) + " °C."

    observation3 = mgr.weather_at_place('Kropyvnytskyi, UA')
    w3 = observation3.weather
    temp_krop = w3.temperature('celsius')["temp"]
    temp_krop_r = round(temp_krop)
    answer3 = "В городе Кропивницкий сейчас: " + str(temp_krop_r) + " °C."

    observation4 = mgr.weather_at_place('Lutugino, UA')
    w4 = observation4.weather
    temp_lug = w4.temperature('celsius')["temp"]
    temp_lug_r = round(temp_lug)
    answer4 = "В городе Лутугино сейчас: " + str(temp_lug_r) + " °C."

    dol_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    dol_buy = dol_r[0]['buy']
    dol_buy_f = round(float(dol_buy) * float(10000) / float(10000), 3)
    dol_sel = dol_r[0]['sale']
    dol_sel_f = round(float(dol_sel) * float(10000) / float(10000), 3)
    dol_ans = 'Курс валют (ПриватБанк):' + '\n' + 'USD: ' + str(dol_buy_f) + ' / ' + str(dol_sel_f)

    eur_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    eur_buy = eur_r[1]['buy']
    eur_buy_f = round(float(eur_buy) * float(10000) / float(10000), 3)
    eur_sel = eur_r[1]['sale']
    eur_sel_f = round(float(eur_sel) * float(10000) / float(10000), 3)
    eur_ans = 'EUR: ' + str(eur_buy_f) + ' / ' + str(eur_sel_f)

    rur_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    rur_buy = rur_r[2]['buy']
    rur_buy_f = round(float(rur_buy) * float(10000) / float(10000), 3)
    rur_sel = rur_r[2]['sale']
    rur_sel_f = round(float(rur_sel) * float(10000) / float(10000), 3)
    rur_ans = 'RUR: ' + str(rur_buy_f) + ' / ' + str(rur_sel_f)

    btc_r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5').json()
    btc_buy = btc_r[3]['buy']
    btc_sel = btc_r[3]['sale']
    btc_ans = 'BTC: ' + btc_buy + ' / ' + btc_sel

    new_cases = covid.get_status_by_country_name('Ukraine')
    new = new_cases['new_cases']
    total = new_cases['confirmed']
    death = new_cases['new_deaths']
    tests = new_cases['total_tests']

    ans = 'COVID-19 статистика: ' + '\n' + 'Новых заражений сегодня: +' + str(new) + '\n' + 'Новых смертей: +' + str(death) + '\n' + "Всего подтверждено случаев: " + str(total) + '\n' + 'Всего проведено тестов: ' + str(tests)

    bot.send_message(message.chat.id, 'Погода сейчас: ' + '\n' + answer1 + '\n' + answer2 + '\n' + answer3 + '\n' + answer4 + '\n\n' + dol_ans + '\n' + eur_ans + '\n' + rur_ans + '\n' + btc_ans + '\n\n' + ans )

@bot.message_handler(commands=['w'])
def weather(message):
    bot.send_message(message.chat.id, 'Репостни мне название своего города')

@bot.message_handler(content_types=['text'])
def send_eco(message):
  try:
    observation = mgr.weather_at_place(message.text)
    w = observation.weather
    temp = w.temperature('celsius')["temp"]
    temp_r = round(temp)
    wind = w.wind()['speed']
    humidity = w.humidity
    answer = "В городе " + message.text + " сейчас - " + w.detailed_status + "." +"\n"
    answer += "Температура: " + str(temp_r) + " °C." + '\n' + 'Скорость ветра - ' + str(wind) + ' м/с.' + '\n' + 'Влажность воздуха - ' + str(humidity) + ' %.'
    bot.send_message(message.chat.id, answer)

  except:
    bot.send_message(message.chat.id, 'Ошибка! Город не найден.')

if __name__ == '__main__':
    bot.polling(none_stop=True)
