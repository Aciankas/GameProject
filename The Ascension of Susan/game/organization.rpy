init python:
    import renpy.store as store
    import renpy.exports as renpy
    from os import listdir
    from os.path import isfile, join
    import random
    import math

    class Organization(store.object):
        def __init__(self, location = None, gold = None, mc = None, girls = None):
            self.location = location or 'start' 
            self.gold = gold or 250
            self.mc = mc
            self.girls = Personage_List([Personage('Susan', pic_directory = 'Susan', lore_flag = True)])
            if girls is not None:
                for girl in girls:
                    self.girls.add(girl)
            self.brothel_rep = 0
            self.max_brotlel_rep = 10
            self.client_min_level = 1
            self.client_max_level = 1
            self.client_money_mod = 20
            self.prostitution_difficulty_modifier = 3
            self.max_girl_capacity = 4
        
        def gold_change(self, value: int):
            self.gold += value
            if self.gold < 0:
                self.gold = 0

        def brothel_rep_change(self, value: int):
            self.brothel_rep += value
            if self.brothel_rep < 0:
                self.brothel_rep = 0
            if self.brothel_rep > self.max_brotlel_rep:
                self.brothel_rep = self.max_brotlel_rep

        def brothel_clients(self):
            dict_client_rep = { #Репутация: количество клиентов 1 уровн
                0: 14,
                1: 24,
                3: 34,
                5: 44,
                8: 44,
                # 2 уровень:
                13: 44,
                21: 7,
                34: 8,
                55: 9,
                89: 10,
                144: 11,
                # 3 уровень:
                233: 12,
                377: 13,
                610: 14,
                987: 15,
                1597: 16,
                # 4 уровень:
                2584: 17,
                4181: 18,
                6765: 19,
                10946: 20,
                17711: 21
            }
            for dict_value, dict_clients in dict_client_rep.items():
                if self.brothel_rep <= dict_value:
                    return dict_clients

        def commit_prostitution_night(self):
            self.cur_prostitution_night = Prostitution_Night(self, client_quantity = self.brothel_clients())
            self.cur_prostitution_night.commit_night(self)

label lock_label(to_label):
    $ renpy.checkpoint()
    $ renpy.jump(to_label)