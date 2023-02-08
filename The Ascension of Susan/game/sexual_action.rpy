init python:
    import renpy.store as store
    import renpy.exports as renpy
    import random
    g_client_min_level = 1
    g_client_max_level = 5
    g_client_money_mod = 20
    g_prostitution_difficulty_modifier = 3 # normal diff
    g_client_possible_acts = ['service', 'classic', 'anal', 'fetish']
    g_client_possible_bonus_acts = ['deception', 'finesse', 'power', 'magic', 'waitress', 'dancer', 'masseuse', 'geisha']


    class Prostitution_Client (store.object):
        def __init__(self, level=random.randint(g_client_min_level ,g_client_max_level), prefered_act='random', bonus_act='random'):
            self.level = level
            self.expected_money = g_client_money_mod*level
            self.money = round(self.expected_money*random.uniform(0.85, 1.15))
            if prefered_act == 'random':   self.prefered_act = self.random_prostitution_act()
            else:                          self.prefered_act = prefered_act
            if bonus_act == 'random':   self.bonus_act = self.random_bonus_prostitution_act()
            else:                       self.bonus_act = bonus_act
    
        @staticmethod
        def random_prostitution_act():
            return g_client_possible_acts[random.randint(0,len(g_client_possible_acts)-1)]
        
        @staticmethod
        def random_bonus_prostitution_act():
            if random.randint(1,100) <= 20: return g_client_possible_bonus_acts[random.randint(0,len(g_client_possible_bonus_acts)-1)]
            return None

    class Prostitution_Client_List (store.object):
        def __init__(self, init_list: List[Prostitution_Client] = None, quantity: int = 1):
            self.list = init_list or list()
            while len(self.list) < quantity:
                self.add(Prostitution_Client())
        
        def add(self, value: Prostitution_Client):
            self.list.append(value)

        def remove(self, value: Prostitution_Client):
            self.list.remove(value)


    class Prostitution_Act (store.object):
        def __init__(self, girl: Personage, client: Prostitution_Client, girl_id: int, client_id: int):
            self.girl_id = girl_id
            self.client_id = client_id
            self.dice = Dice(10)
            # доп предпочтения
            if client.bonus_act is not None:
                if girl.stat[client.bonus_act].act_level() >= client.level - 1:     self.bonus_act_mod = 4
                elif girl.stat[client.bonus_act].act_level() == client.level - 1:   self.bonus_act_mod = 2
                else:                                                               self.bonus_act_mod = -1
            else:                                                                   self.bonus_act_mod = 0
            self._roll_base = g_prostitution_difficulty_modifier + girl.stat[client.prefered_act].act_level() - client.level
            self._roll_bonuses = self.bonus_act_mod + (girl.stat[client.prefered_act].modifier + ((girl.stat[client.prefered_act].value - client.level*20)/2 + (girl.stat[girl.stat[client.prefered_act].parent_2_name].value - client.level*20)/2)/20)
            self.profit = round((min(self._roll_base + self.dice.roll, 10) + self._roll_bonuses)/10 * client.money * self.dice.critical_mod)
            self.expected_profit = round((min(self._roll_base + self.dice.average, 10) + self._roll_bonuses)/10 * client.expected_money)
            self.expected_profit_per_energy = self.expected_profit/girl.action_energy(client.prefered_act)


    class Prostitution_Night (store.object):
        def __init__(self, client_list: List[Prostitution_Client] = None, client_quantity: int = None):
            global g_companions
            self.clients = Prostitution_Client_List(init_list = client_list, quantity = client_quantity)

        def generate_night_act(self):
            # Составляет список всех возможных действий за ночь и выбирает лучший
            # self.possible_acts_list = list()
            self.__best_possible_act_profit = 0
            for girl_id, girl in enumerate(g_companions.list):
                if girl.action_flag == 'whore':
                    for client_id, client in enumerate(self.clients.list):
                        if girl.work_energy() >= girl.action_energy(client.prefered_act):
                            self.__cur_act = Prostitution_Act(girl = girl, client = client, girl_id = girl_id, client_id = client_id)
                            # self.possible_acts_list.append(self.__cur_act)
                            if self.__cur_act.expected_profit_per_energy > self.__best_possible_act_profit:
                                self.__best_possible_act_profit = self.__cur_act.expected_profit_per_energy
                                self.best_possible_act = self.__cur_act

        def commit_act(self):
            girl.personality.event('sex', 'peace', 'command' if command else 'freedom', 'public' if public else 'private')
            girl.change_exp(client.prefered_act)
            resourses.gold_change(self.profit)
