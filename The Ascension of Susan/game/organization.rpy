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
            self.client_min_level = 1
            self.client_max_level = 1
            self.client_money_mod = 20
            self.prostitution_difficulty_modifier = 3
        
        def gold_change(self, value: int):
            self.gold += value