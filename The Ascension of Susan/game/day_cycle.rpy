init python:
    import renpy.store as store
    import renpy.exports as renpy
    from os import listdir
    from os.path import isfile, join
    import random
    import math

    dict_ru_daytime = {
        'morning': 'утро',
        'day':  'день',
        'evening': 'вечер',
        'night': 'ночь'
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
            dict_daytime_cycle = {
                'morning': 'day',
                'day':  'evening',
                'evening': 'night',
                'night': 'morning'
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
            renpy.checkpoint()
            renpy.retain_after_load()
            self.time = dict_daytime_cycle[self.time]
            if self.time == 'morning':
                self.weekday = dict_weekday_cycle[self.weekday] 
            self.events.execute_events(self.time, self.weekday)
        
        def button_picture(self):
            dict_daytime_picture = {
                'morning': "gui/day_cycle/morning.png",
                'day':  "gui/day_cycle/day.png",
                'evening': "gui/day_cycle/evening.png",
                'night': "gui/day_cycle/night.png"
            }
            return dict_daytime_picture[self.time]
        
        def add_event(self, time: str, weekday: str, exec_code: str, repeatable = False):
            self.events.add(Event(time, weekday, exec_code, repeatable))

        def night_routine(self, base):
            base.commit_prostitution_night()
            self.night_rest(base)
            base.girls.drop_static_pictires()
            renpy.jump("night_action_label")
            
        def night_rest(self, base):
            base.girls.night_rest()

label night_action_label:
    python:
        hide_screens()
    # Ночь борделя
    $ quick_menu = False
    scene red_light_night_bg with dissolve
    $ g_current_night_act = g_base.cur_prostitution_night.first_commited_act()
    if g_current_night_act is not None:
        jump prostitution_night_label
    else:
        jump prostitution_night_label_end

label prostitution_night_label:
    if not renpy.is_skipping(): 
        call screen prostitution_night
    jump prostitution_night_label_act

label prostitution_night_label_act:
    if not renpy.is_skipping(): 
        call screen prostitution_night_act(g_current_night_act)
    $ g_current_night_act = g_base.cur_prostitution_night.next_commited_act(g_current_night_act)
    if g_current_night_act is not None:
        jump prostitution_night_label_act
    else:
        jump prostitution_night_label_end

label prostitution_night_label_end:
    jump night_action_label_end

label night_action_label_end:
    $ g_time.next()
    $ quick_menu = True
    jump main_hub_label
