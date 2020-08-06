import json
import ssd1306
import urequests
from machine import Pin, I2C
from time import localtime, mktime, sleep

CONTENTS = ['confirmed', 'cases', 'recovered', 'deaths']
last_values = []

i2c = I2C(-1, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text('github.com/', 20, 20)
oled.text('nilson-santos', 13, 35)        
oled.show()


def get_api():
    return eval(urequests.get('https://covid19-brazil-api.now.sh/api/report/v1/brazil/').text)


def counters_sanitizer(content):
    content = str("{:,}".format(int(api['data'][content]))).replace(',', '.')
    return content


def change_to_string(valor):
    if valor < 10:
        valor = '0' + str(valor)
    else:
        valor = str(valor)
    return valor


def datatime_sanitizer():
    update_at = api['data']['updated_at']
    Y = int(update_at[:4])
    m = int(update_at[5:7])
    d = int(update_at[8:10])
    H = int(update_at[11:13])
    M = int(update_at[14:16])
    S = int(update_at[17:19])

    t = mktime((Y, m, d, H, M, S, 0, 0, 0))
    t -= 3*3600  # convert to local time UTC -3
    t = localtime(t)
    
    t_list = [change_to_string(valor) for valor in t]

    data = t_list[2] + '-' + t_list[1] + '-' + t_list[0]
    time = t_list[3] + ':' + t_list[4] + ':' + t_list[5]

    return [data, time]


def oled_show(title, title_h_start, title_v_start, value,
            value_h_start, value_v_start,
            value2='', value2_h_start=0, value2_v_start=0
            ):
    oled.fill(0)
    oled.text('CORONAVIRUS', 20, 0)
    oled.text(title, title_h_start, title_v_start)
    oled.text(value, value_h_start, value_v_start)
    oled.text(value2, value2_h_start, value2_v_start)
    oled.show()
    sleep(5)


while True:
    api = get_api()
    values = [counters_sanitizer(value) for value in CONTENTS]
    date, time = datatime_sanitizer()

    for _ in range(10):

        oled_show('Confirmados', 20, 22, values[0], 27, 40)
        
        oled_show('Ativos', 40, 22, values[1], 36, 40)
        
        oled_show('Recuperados', 20, 22, values[2], 27, 40)
        
        oled_show('Mortos', 40, 22, values[3], 39, 40)
        
        oled_show('Atualizado', 24, 22, date, 24, 40, time, 32, 50)
