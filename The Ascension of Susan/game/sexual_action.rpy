init python:
    import renpy.store as store
    import renpy.exports as renpy
    import random
    g_client_possible_acts = ['service', 'classic', 'anal', 'fetish']
    g_client_possible_bonus_acts = ['deception', 'finesse', 'power', 'magic', 'waitress', 'dancer', 'masseuse', 'geisha']

    class Prostitution_Client(store.object):
        def __init__(self, base, level = None, prefered_act='random', bonus_act='random'):
            self.level = level or random.randint(base.client_min_level, base.client_max_level)
            self.expected_money = base.client_money_mod*self.level
            self.money = round(self.expected_money*random.uniform(0.85, 1.15))
            self.served = False
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


    class Prostitution_Client_List(store.object):
        def __init__(self, base, init_list: List[Prostitution_Client] = None, quantity: int = None):
            self.quantity = quantity or base.brothel_clients()
            self.list = init_list or list()
            while len(self.list) < self.quantity:
                self.add(Prostitution_Client(base))
        
        def add(self, value: Prostitution_Client):
            self.list.append(value)

        def remove(self, value: Prostitution_Client):
            self.list.remove(value)


    class Prostitution_Act(store.object):
        def __init__(self, base, night, girl_id: int, client_id: int):
            self.girl_id = girl_id
            self.client_id = client_id
            girl = base.girls.list[girl_id]
            client = night.clients.list[client_id]
            self.dice = Dice(10)
            # доп предпочтения
            if client.bonus_act is not None:
                if girl.stat[client.bonus_act].act_level() >= client.level - 1:     self.bonus_act_mod = 4
                elif girl.stat[client.bonus_act].act_level() == client.level - 1:   self.bonus_act_mod = 2
                else:                                                               self.bonus_act_mod = -1
            else:                                                                   self.bonus_act_mod = 0
            self._roll_base = base.prostitution_difficulty_modifier + girl.stat[client.prefered_act].act_level() - client.level
            self._roll_bonuses = self.bonus_act_mod + (girl.stat[client.prefered_act].modifier + ((girl.stat[client.prefered_act].value - client.level*20)/2 + (girl.stat[girl.stat[client.prefered_act].parent_2_name].value - client.level*20)/2)/20)
            self.profit = round((min(self._roll_base + self.dice.roll, 10) + self._roll_bonuses)/10 * client.money * self.dice.critical_mod)
            if self.profit < client.money/5:
                self.failed = True
                self.profit = client.money/5
            else:
                self.failed = False
            self.expected_profit = round((min(self._roll_base + self.dice.average, 10) + self._roll_bonuses)/10 * client.expected_money)
            self.expected_profit_per_energy = self.expected_profit/girl.action_energy(client.prefered_act)
            self.reputation = -1 if self.failed else 1
            self.reputation += 2 if self.dice.critical == True else 0
            self.reputation += -2 if self.dice.critical == False else 0


    class Prostitution_Night(store.object):
        def __init__(self, base, client_list: List[Prostitution_Client] = None, client_quantity: int = None):
            self.clients = Prostitution_Client_List(base = base, init_list = client_list, quantity = client_quantity)
            self.commited_acts = list()

        def generate_acts(self, base):
            # return: Составляет список всех возможных действий за ночь
            possible_acts_list = list()
            for girl_id, girl in enumerate(base.girls.list):
                if girl.action_flag == 'whore':
                    for client_id, client in enumerate(self.clients.list):
                        if not client.served and girl.work_energy() >= girl.action_energy(client.prefered_act):
                            cur_act = Prostitution_Act(base, self, girl_id = girl_id, client_id = client_id)
                            possible_acts_list.append(cur_act)
            return possible_acts_list
        
        @staticmethod
        def best_act(base, acts: List[Prostitution_Act]):
            # acts: Список актов
            # return: Самый выгодный акт из списка, если выгода одинакова, смотрит у кого больше энергии, если и она одинакова - случайный акт 
            best_possible_act_profit = 0
            best_possible_act_energy = 999
            acts_effect_top_list = list()
            acts_energy_top_list = list()
            best_possible_act = None
            for cur_act in acts:
                if best_possible_act_profit < cur_act.expected_profit_per_energy:
                    best_possible_act_profit = cur_act.expected_profit_per_energy
                    acts_effect_top_list = list()
                if best_possible_act_profit == cur_act.expected_profit_per_energy:
                    acts_effect_top_list.append(cur_act)
            for cur_act in acts_effect_top_list:
                girl_energy = base.girls.list[cur_act.girl_id].energy
                if best_possible_act_energy > girl_energy:
                    best_possible_act_energy = girl_energy
                    acts_energy_top_list = list()
                if best_possible_act_energy == girl_energy:
                    acts_energy_top_list.append(cur_act)
            if acts_energy_top_list:
                best_possible_act = random.choice(acts_energy_top_list)
            return best_possible_act

        def commit_act(self, base, act: Prostitution_Act):
            # return: Совершенный Акт
            girl = base.girls.list[act.girl_id]
            client = self.clients.list[act.client_id]
            girl.personality.event('sex', 'peace', 'command' if girl.action_command else 'freedom', 'public' if girl.action_public else 'private')
            girl.acted(client.prefered_act)
            client.served = True
            base.gold_change(act.profit)
            base.brothel_rep_change(act.reputation)
            return act
        
        def commit_night(self, base):
            # return: Список совершённых актов
            while True:
                cur_act = self.best_act(base, self.generate_acts(base))
                if cur_act is None:
                    break
                self.commited_acts.append(self.commit_act(base, cur_act))
            return self.commited_acts

#screen prostitution_night():


#screen prostitution_girl(girl_id = None):
