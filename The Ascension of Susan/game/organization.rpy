init python:
    import renpy.store as store
    import renpy.exports as renpy
    from os import listdir
    from os.path import isfile, join
    import random
    import math

    colour = {
        "white": "#FFFFFF",
        "neutral":"#FFFFFF",
        "green": "#70ED3B",
        "red":"#FF4040",
        "orange":"#FF9E00",
        "basic_gold":"#FFC965",
        "reputation": "#58aaf7",
        "grey": "#919191"}
    
    def stats_text(stat, pos_value = 0, neg_value = 0, base_color = "white", pos_color = "green", neg_color = "red", colored_pre_text = ""):
        base_color = colour[base_color]
        pos_color = colour[pos_color]
        neg_color = colour[neg_color]
        result_text = "{color="
        if stat < neg_value:   result_text += neg_color
        elif stat > pos_value: result_text += pos_color
        else:                  result_text += base_color
        result_text += "}"+str(colored_pre_text)
        if stat > 0:           result_text += "+"
        result_text += str(stat)+"{/color}"
        return result_text

    class Dice(store.object):
        def __init__(self, value: int):
            critical_mod_success = {
                4: 1.1,
                6: 1.25,
                8: 1.5,
                10: 2,
                12: 2.25,
                20: 3}
            critical_mod_failure = {
                4: 0.9,
                6: 0.7,
                8: 0.4,
                10: 0.25,
                12: 0.2,
                20: 0.1}
            dice_roll_pictures = {
                4: "gui/dice/dice-d4.png",
                6: "gui/dice/dice-d6.png",
                8: "gui/dice/dice-d8.png",
                10: "gui/dice/dice-d10.png",
                12: "gui/dice/dice-d12.png",
                20: "gui/dice/dice-d20.png"}

            self.max_value = value
            self.roll = random.randint(1, value)
            self.critical_mod = 1
            self.critical = None
            self.color = colour["basic_gold"]
            self.average = (value+1)/2
            if self.roll == value: # Критический успех
                self.critical = True
                #self.color = colour["green"]
                self.critical_mod = critical_mod_success[self.roll]
            if self.roll == 1: # Критический провал
                self.critical = False
                #self.color = colour["red"]
                self.critical_mod = critical_mod_failure[value]
            self.picture = dice_roll_pictures[value]


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