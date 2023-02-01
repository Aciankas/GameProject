init python:  
    import random
    g_client_min_level = 1
    g_client_max_level = 5
    g_client_money_mod = 20
    g_client_stat_difficulty_mod = 20
    g_client_possible_acts = ['service', 'classic', 'anal', 'fetish']
    g_client_possible_bonus_acts = ['deception', 'finesse', 'power', 'magic', 'waitress', 'dancer', 'masseuse', 'geisha']
    
    def random_prostitution_act():
        return g_client_possible_acts[random.randint(0,len(g_client_possible_acts)-1)]

    def random_bonus_prostitution_act():
        if random.randint(1,100) <= 20:
            return g_client_possible_bonus_acts[random.randint(0,len(g_client_possible_bonus_acts)-1)]
        else:
            return None

    class Prostitution_Client (store.object):
        def __init__(self, level=random.randint(g_client_min_level ,g_client_max_level), prefered_act='random', bonus_act='random'):
            self.level = level
            self.money = round(g_client_money_mod*level*random.uniform(0.85, 1.15))
            if prefered_act == 'random':
                self.prefered_act = random_prostitution_act()
            else:
                self.prefered_act = prefered_act
            if bonus_act == 'random':
                self.bonus_act = random_bonus_prostitution_act()
            else:
                self.bonus_act = bonus_act
            
    class Prostitution_Action (store.object):
        def __init__(self, girl: Personage, client: Prostitution_Client):
            self.dice = Dice(10)
            
            