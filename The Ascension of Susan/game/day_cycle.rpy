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

    class Event(store.object):
        def __init__(self, time: str, weekday: str, exec_code: str, repeatable = False):
            self.time = time
            self.weekday = weekday
            self.exec_code = exec_code
            self.repeatable = repeatable
        
        def execute(self, time: str, weekday: str):
            if self.time in (time, 'any') and self.weekday in (weekday, 'any'):
                exec(self.exec_code)


    class Event_List(store.object):
        def __init__(self, init_list: List[Event] = None):
            self.list = init_list or list()
        
        def add(self, value: Event):
            self.list.append(value)

        def remove(self, value: Event):
            self.list.remove(value)
        
        def execute_events(self, time: str, weekday: str):
            for event in self.list:
                event.execute(time, weekday)
                if not event.repeatable:
                    self.remove(event)


    class Day_Cycle(store.object):
        def __init__(self, event_list: Event_List):
            self.time = 'morning'
            self.weekday = 'monday'
            self.events = event_list
        
        def next(self):
            self.time = dict_daytime_cycle[self.time]
            if self.time == 'morning':
                self.weekday = dict_weekday_cycle[self.weekday] 
            self.events.execute_events(self.time, self.weekday)
        
        def add_event(self, time: str, weekday: str, exec_code: str, repeatable = False):
            self.events.add(Event(time, weekday, exec_code, repeatable))

        def night_routine(self, base):
            base.cur_prostitution_night = Prostitution_Night()
            base.cur_prostitution_night.commit_night()
            self.night_rest(base)
            self.next()

        def night_rest(self, base):
            base.girls.night_rest()

    g_time = Day_Cycle(event_list = Event_List(
        init_list = [
            Event('night', 'any', 'g_time.night_routine(g_base)', True)
        ]))

