init python:  
    import random
    g_client_min_level = 1
    g_client_max_level = 5
    g_client_money_mod = 20
    g_client_stat_difficulty_mod = 20
    g_client_possible_bonus_acts = [
        ('service', ),
        ('classic', ),
        ('anal', ),
        ('fetish', ),
        ('', ),
        ('', ),
    ]

    class Prostitution_Client (store.object):
        def __init__(self, level=random.randint(g_client_min_level ,g_client_max_level), prefered_act='random'):
            self.level = level
            self.money = round(g_client_money_mod*level*random.uniform(0.85, 1.15))
            if prefered_act == 'random':
                pass
            else:
                self.prefered_act = prefered_act
            

    class Prostitution_Action (store.object):
        def __init__(self, girl, client):
            pass
            