init python:
    import renpy.store as store
    import renpy.exports as renpy
    import random
    import time
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

        def picture(self):
            return "images/clients/icons/thug.jpg"

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
                else:                                                                                                      self.bonus_act_mod = -1
            else:                                                                                                          self.bonus_act_mod = 0
            self._roll_base = base.prostitution_difficulty_modifier + girl.stat[client.prefered_act].act_mastery() - client.level
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
    
    g_prostitution_client_screen_ysize = 60
    g_prostitution_client_screen_xsize = g_prostitution_client_screen_ysize*2
    g_prostitution_client_screen_text_size = int(g_prostitution_client_screen_ysize/3)
    g_prostitution_client_screen_statsize = int(g_prostitution_client_screen_ysize/1.8)

    g_prostitution_girl_screen_pic_size = 90
    g_prostitution_girl_screen_text_size = int(g_prostitution_girl_screen_pic_size*1/3)
    g_prostitution_girl_screen_main_statsize = int(g_prostitution_girl_screen_pic_size*2/3)
    g_prostitution_girl_screen_main_stat_text_size = int(g_prostitution_girl_screen_main_statsize/3)
    g_prostitution_girl_screen_sec_statsize = int(g_prostitution_girl_screen_pic_size*11/24)
    g_prostitution_girl_screen_sec_stat_text_size = int(g_prostitution_girl_screen_sec_statsize/2)
    g_prostitution_girl_screen_xsize = int(g_prostitution_girl_screen_pic_size*11/3)+3
    g_prostitution_girl_screen_ysize = g_prostitution_girl_screen_pic_size+g_prostitution_girl_screen_sec_statsize+3

    g_prostitution_screen_text_font = "DejaVuSans.ttf"
    g_skill_level_pic = "gui/bar/level_icon.png"


screen prostitution_client(client, x_pos = 0, y_pos = 0):
    python:
        client_pic = client.picture()
        client_pref_stat = g_base.girls.list[0].stat[client.prefered_act].get_icon(postfix="lightgold")
        if client.bonus_act is not None:
            client_bonus_stat = g_base.girls.list[0].stat[client.bonus_act].get_icon(postfix="light")
        else:
            client_bonus_stat = False
    frame:
        style "frame_brothel_client"
        xpos x_pos
        ypos y_pos
        xsize g_prostitution_client_screen_xsize
        ysize g_prostitution_client_screen_ysize
        image Transform(client_pic, fit='contain', xysize = (g_prostitution_client_screen_ysize-6,g_prostitution_client_screen_ysize-6))
        image Transform(g_skill_level_pic, fit='contain', xysize = (g_prostitution_client_screen_text_size+4,g_prostitution_client_screen_text_size+4), 
            xpos = g_prostitution_client_screen_ysize-int(g_prostitution_client_screen_text_size*1.3), 
            ypos = g_prostitution_client_screen_ysize-int(g_prostitution_client_screen_text_size*1.25))
        text '{font=[g_prostitution_screen_text_font]}{size=[g_prostitution_client_screen_text_size]}{b}[client.level]{/b}{/size}{/font}' xpos g_prostitution_client_screen_ysize-g_prostitution_client_screen_text_size-2 ypos g_prostitution_client_screen_ysize-g_prostitution_client_screen_text_size-5
        if client_bonus_stat:
            image Transform(client_pref_stat, fit='contain', xysize = (g_prostitution_client_screen_statsize, g_prostitution_client_screen_statsize), 
                xpos = g_prostitution_client_screen_ysize-2, 
                ypos = g_prostitution_client_screen_ysize-g_prostitution_client_screen_statsize-5) 
            image Transform(client_bonus_stat, fit='contain', xysize = (g_prostitution_client_screen_statsize, g_prostitution_client_screen_statsize), 
                xpos = g_prostitution_client_screen_xsize-g_prostitution_client_screen_statsize-5)
        else:
            image Transform(client_pref_stat, fit='contain', xysize = (g_prostitution_client_screen_ysize-6, g_prostitution_client_screen_ysize-6), xpos = g_prostitution_client_screen_ysize-2) 

screen prostitution_girl(girl, x_pos = 0, y_pos = 0):
    python:
        girl_pic = girl.picture("portrait")
        main_stat_pics = list()
        for stat_name in g_client_possible_acts:
            main_stat_pics.append((girl.stat[stat_name].get_icon(postfix="lightgold"), girl.stat[stat_name].act_level()))
        secondary_stat_pics = list()
        for stat_name in g_client_possible_bonus_acts:
            secondary_stat_pics.append((girl.stat[stat_name].get_icon(postfix="light"), girl.stat[stat_name].act_level()))
    frame:
        style "frame_brothel_client"
        xpos x_pos
        ypos y_pos
        xsize g_prostitution_girl_screen_xsize
        ysize g_prostitution_girl_screen_ysize
        image Transform("gui/lap_girl_left.png", fit='contain', xysize = (g_prostitution_girl_screen_ysize,  g_prostitution_girl_screen_ysize), xpos = -3-int(g_prostitution_girl_screen_ysize*0.3), ypos = -3)
        image Transform("gui/lap_girl_right.png", fit='contain', xysize = (g_prostitution_girl_screen_ysize,  g_prostitution_girl_screen_ysize), xpos = g_prostitution_girl_screen_xsize+3-int(g_prostitution_girl_screen_ysize*0.1), ypos = -3)
        image Transform(girl_pic, fit='contain', xysize = (g_prostitution_girl_screen_pic_size-1,g_prostitution_girl_screen_pic_size-1))
        text '{size=[g_prostitution_girl_screen_text_size]}[girl.name]{/size}' xpos g_prostitution_girl_screen_pic_size+2
        for idx, stat in enumerate(main_stat_pics):
            image Transform(stat[0], fit='contain', xysize = (g_prostitution_girl_screen_main_statsize-2,g_prostitution_girl_screen_main_statsize-2), 
                xpos = g_prostitution_girl_screen_pic_size+idx*g_prostitution_girl_screen_main_statsize, 
                ypos = g_prostitution_girl_screen_text_size)
            image Transform(g_skill_level_pic, fit='contain', xysize = (g_prostitution_girl_screen_main_stat_text_size + 4, g_prostitution_girl_screen_main_stat_text_size + 4), 
                xpos = g_prostitution_girl_screen_pic_size+(idx+1)*g_prostitution_girl_screen_main_statsize-int(g_prostitution_girl_screen_main_stat_text_size*1.3), 
                ypos = g_prostitution_girl_screen_pic_size-g_prostitution_girl_screen_main_stat_text_size)
            python:
                cur_stat_lvl = stat[1]
                x_text_mover = int(g_prostitution_girl_screen_main_stat_text_size*0.25) if len(str(cur_stat_lvl)) >= 2 else 0
            text '{font=[g_prostitution_screen_text_font]}{size=[g_prostitution_girl_screen_main_stat_text_size]}[cur_stat_lvl]{/size}{/font}' xpos g_prostitution_girl_screen_pic_size+(idx+1)*g_prostitution_girl_screen_main_statsize-g_prostitution_girl_screen_main_stat_text_size-x_text_mover ypos g_prostitution_girl_screen_pic_size-g_prostitution_girl_screen_main_stat_text_size
        for idx, stat in enumerate(secondary_stat_pics):
            image Transform(stat[0], fit='contain', xysize = (g_prostitution_girl_screen_sec_statsize-1,g_prostitution_girl_screen_sec_statsize-1), 
                xpos = idx*g_prostitution_girl_screen_sec_statsize, 
                ypos = g_prostitution_girl_screen_pic_size)
            image Transform(g_skill_level_pic, fit='contain', xysize = (g_prostitution_girl_screen_sec_stat_text_size + 4, g_prostitution_girl_screen_sec_stat_text_size + 4), 
                xpos = (idx+1)*g_prostitution_girl_screen_sec_statsize-int(g_prostitution_girl_screen_sec_stat_text_size*1.3), 
                ypos = g_prostitution_girl_screen_pic_size+g_prostitution_girl_screen_sec_statsize-int(g_prostitution_girl_screen_sec_stat_text_size*1))
            python:
                cur_stat_lvl = stat[1]
                x_text_mover = int(g_prostitution_girl_screen_sec_stat_text_size*0.25) if len(str(cur_stat_lvl)) >= 2 else 0
            text '{font=[g_prostitution_screen_text_font]}{size=[g_prostitution_girl_screen_sec_stat_text_size]}[cur_stat_lvl]{/size}{/font}' xpos (idx+1)*g_prostitution_girl_screen_sec_statsize-g_prostitution_girl_screen_sec_stat_text_size-x_text_mover ypos g_prostitution_girl_screen_pic_size+g_prostitution_girl_screen_sec_statsize-g_prostitution_girl_screen_sec_stat_text_size

screen prostitution_night:
    for idx, client in enumerate(g_base.cur_prostitution_night.clients.list):
        use prostitution_client(client, 100+int(idx/11)*int(g_prostitution_client_screen_xsize*1.2), 110+int(idx%11)*int(g_prostitution_client_screen_ysize*1.3))
    use prostitution_girl(g_base.girls.list[0], 600, 200)
    use prostitution_girl(g_base.girls.list[1], 600, 350)

    imagebutton:
        xsize 1920
        ysize 1080
        idle "gui/Empty.png"
        action Return()
