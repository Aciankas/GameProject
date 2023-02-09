init python:
    import renpy.store as store
    import renpy.exports as renpy
    from os import listdir
    from os.path import isfile, join
    import random
    import math

    dict_daytime_cycle = {
        'morning': 'day',
        'day':  'evening',
        'evening': 'night',
        'night': 'morning'
    }

    dict_ru_daytime = {
        'morning': 'утро',
        'day':  'день',
        'evening': 'вечер',
        'night': 'ночь'
    }

    dict_weekday_cycle = {
        'monday': 'tuesday',
        'tuesday': 'wednesday',
        'wednesday': 'thursday',
        'thursday': 'friday',
        'friday': 'saturday',
        'saturday': 'sunday',
        'sunday': 'monday'
    }

    dict_ru_weekday = {
        'monday': 'понедельник',
        'tuesday': 'вторник',
        'wednesday': 'среда',
        'thursday': 'четверг',
        'friday': 'пятница',
        'saturday': 'суббота',
        'sunday': 'воскресенье'
    }

    class Time_Event(store.object):
        def __init__(self, time: str, weekday: str, exec_code: str):
            self.time = time
            self.weekday = weekday
            self.exec_code = exec_code
        
        def execute(self, time: str, weekday: str):
            if self.time in (time, 'any') and self.weekday in (weekday, 'any'):
                exec(self.exec_code)


    g_time_events = [
        Time_Event('night', 'any', 'g_time.night_routine()')
    ]


    class Day_Cycle(store.object):
        def __init__(self):
            self.time = 'morning'
            self.weekday = 'monday'
        
        def next(self):
            self.time = dict_daytime_cycle[self.time]
            if self.time == 'morning':
                self.weekday = dict_weekday_cycle[self.weekday] 
            self.execute_time_events()

        def execute_time_events(self):
            for event in g_time_events:
                event.execute(self.time, self.weekday)
        
        def night_routine(self):
            global g_cur_prostitution_night
            g_cur_prostitution_night = Prostitution_Night()
            g_cur_prostitution_night.commit_night()
            self.next()


    g_time = Day_Cycle()
    
