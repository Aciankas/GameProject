﻿# Вы можете расположить сценарий своей игры в этом файле.

# Вместо использования оператора image можете просто
# складывать все ваши файлы изображений в папку images.
# Например, сцену bg room можно вызвать файлом "bg room.png",
# а eileen happy — "eileen happy.webp", и тогда они появятся в игре.

# Игра начинается здесь:
label start:
    python:
        g_base = Organization(gold = 250, girls = [Personage('Angelise', pic_directory = 'Angelise'), Personage('Empty', pic_directory = 'Empty')])
        g_time = Day_Cycle(event_list = Event_List(
            init_list = [
                Event('night', 'any', 'g_time.night_routine(g_base)', True)
            ]))
    jump main_hub_label
    return
