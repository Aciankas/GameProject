init python:  
    import random
    g_client_min_level = 1
    g_client_max_level = 5
    g_client_money_mod = 20
    g_prostitution_difficulty_modifier = 3 # normal diff
    g_client_possible_acts = ['Service', 'Classic', 'Anal', 'Fetish']
    g_client_possible_bonus_acts = ['Deception', 'Finesse', 'Power', 'Magic', 'Waitress', 'Dancer', 'Masseuse', 'Geisha']
    
    def random_prostitution_act():
        return g_client_possible_acts[random.randint(0,len(g_client_possible_acts)-1)]

    def random_bonus_prostitution_act():
        if random.randint(1,100) <= 20: return g_client_possible_bonus_acts[random.randint(0,len(g_client_possible_bonus_acts)-1)]
        return None

    class Prostitution_Client (store.object):
        def __init__(self, level=random.randint(g_client_min_level ,g_client_max_level), prefered_act='Random', bonus_act='Random'):
            self.level = level
            self.money = round(g_client_money_mod*level*random.uniform(0.85, 1.15))
            if prefered_act == 'Random':   self.prefered_act = random_prostitution_act()
            else:                          self.prefered_act = prefered_act
            if bonus_act == 'Random':   self.bonus_act = random_bonus_prostitution_act()
            else:                       self.bonus_act = bonus_act
            
    class Prostitution_Action (store.object):
        def __init__(self, girl: Personage, client: Prostitution_Client):
            self.dice = Dice(10)
            # доп предпочтения
            if client.bonus_act is not None:
                if girl.stat[client.bonus_act].act_level() >= client.level - 1:     self.bonus_act_mod = 4
                elif girl.stat[client.bonus_act].act_level() == client.level - 1:   self.bonus_act_mod = 2
                else:                                                               self.bonus_act_mod = -1
            else:                                                                   self.bonus_act_mod = 0
            self.modifiers = girl.stat[client.prefered_act].modifier + ((girl.stat[client.prefered_act].value - client.level*20)/2 + (girl.stat[girl.stat[client.prefered_act].parent_2_name].value - client.level*20)/2)/20
            self.final_result = min(g_prostitution_difficulty_modifier + girl.stat[client.prefered_act].act_level() - client.level + self.dice.roll, 10) + self.bonus_act_mod + self.modifiers
            self.profit = round(self.final_result/10 * client.money * self.dice.critical_mod)