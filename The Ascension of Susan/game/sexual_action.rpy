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
            self.girl_id = None
            self.commited_act_number = None
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

        def clients_by_girl_id(self, girl_id):
            result = list()
            for idx, client in enumerate(self.list):
                if client.girl_id == girl_id:
                    result.append(client)
                    result.sort(key=lambda x: x.commited_act_number)
            return result


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
            self._roll_effect = min(self._roll_base + self.dice.roll, 10)
            self.profit = round((self._roll_effect + self._roll_bonuses)/10 * client.money * self.dice.critical_mod)
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
            self.commited_act_number = 0

        def generate_acts(self, base):
            # return: Составляет список всех возможных действий за ночь
            possible_acts_list = list()
            self.whored_girls_id = list()
            for girl_id, girl in enumerate(base.girls.list):
                if girl.action_flag == 'whore':
                    self.whored_girls_id.append(girl_id)
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
            act.stat_changes = girl.acted(client.prefered_act)
            client.served = True
            # Для анимирования Ночи:
            client.girl_id = act.girl_id
            client.commited_act_number = base.cur_prostitution_night.commited_act_number
            base.cur_prostitution_night.commited_act_number += 1
            # Эффект на ресурсы:
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
                self.commited_acts.sort(key=lambda x: x.girl_id)
            return self.commited_acts
        
        def first_commited_act(self):
            if len(self.commited_acts) == 0: return None
            else: return self.commited_acts[0]
        
        def next_commited_act(self, act):
            if len(self.commited_acts) == 0: return None
            for idx, cur_act in enumerate(self.commited_acts):
                if cur_act.girl_id == act.girl_id and cur_act.client_id == act.client_id:
                    if idx + 1 == len(self.commited_acts): return None
                    else: return self.commited_acts[idx + 1]

    
    g_screens_x_gap = 100
    g_screens_y_gap = 110

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
    g_prostitution_girl_screen_left_right_gaps = int(g_prostitution_girl_screen_xsize*0.12)

    g_prostitution_screen_text_font = g_num_font_bold #"DejaVuSans.ttf"
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

screen framecrop_revealer(framefile, bckgrnd, x_pos = 0, y_pos = 0, x_size = 1, y_size = 1, pauser = 0.0, re_pauser = None):
    if re_pauser is None:
        image crop_revealer(bckgrnd,
            x_pos,
            y_pos,
            x_size,
            y_size,
            pauser)
        image revealer(Transform(framefile,
                xpos = x_pos,
                ypos = y_pos,
                xsize = x_size,
                ysize = y_size),
            pauser)
    else:
        image re_crop_revealer(bckgrnd,
            x_pos,
            y_pos,
            x_size,
            y_size,
            pauser,
            re_pauser)
        image re_revealer(Transform(framefile,
                xpos = x_pos,
                ypos = y_pos,
                xsize = x_size,
                ysize = y_size),
            pauser,
            re_pauser,
            "nothing_bg")

screen prostitution_night:
    python:
        l_client_quantity = len(g_base.cur_prostitution_night.clients.list)
        l_client_start_x = g_screens_x_gap
        l_client_start_y = g_screens_y_gap
        l_client_max_row_length = 11
        l_client_max_rows = 4
        l_client_border_px = 7
        l_client_x_gap = int(g_prostitution_client_screen_xsize*1.2)
        l_client_y_gap = int(g_prostitution_client_screen_ysize*1.3)
        l_client_showed = l_client_quantity if l_client_quantity<l_client_max_rows*l_client_max_row_length else l_client_max_rows*l_client_max_row_length
        l_client_actual_rows = 1 + (l_client_showed - 1)//l_client_max_row_length
        l_client_actual_row_length = l_client_quantity if l_client_quantity<l_client_max_row_length else l_client_max_row_length
        l_frame_client_xpos = l_client_start_x - l_client_border_px
        l_frame_client_ypos = l_client_start_y - l_client_border_px
        l_frame_client_xsize = l_client_x_gap*(l_client_max_rows - 1) + g_prostitution_client_screen_xsize + l_client_border_px*2
        l_frame_client_ysize = l_client_y_gap*(l_client_max_row_length - 1) + g_prostitution_client_screen_ysize + l_client_border_px*2
        # Timers
        l_client_full_time = 4
        l_client_time = l_client_full_time/l_client_showed if l_client_full_time/l_client_showed < 0.3 else 0.3
        l_client_full_time = l_client_time*l_client_showed
        l_client_commited_full_time = 4
        l_client_commited_time = g_base.cur_prostitution_night.commited_act_number/l_client_commited_full_time if g_base.cur_prostitution_night.commited_act_number/l_client_commited_full_time < 0.3 else 0.3
        l_client_commited_full_time = l_client_commited_time*g_base.cur_prostitution_night.commited_act_number

    image Frame("gui/no_frame_high_transparent.png", l_client_border_px, l_client_border_px,
        xpos = l_frame_client_xpos, 
        ypos = l_frame_client_ypos, 
        xsize = l_frame_client_xsize, 
        ysize = l_frame_client_ysize
        )
    for idx, client in enumerate(g_base.cur_prostitution_night.clients.list):
        if idx < l_client_showed:
            python:
                cur_client_xpos = l_client_start_x+(idx//l_client_max_row_length)*l_client_x_gap
                cur_client_ypos = l_client_start_y+(idx%l_client_max_row_length)*l_client_y_gap
            use prostitution_client(client, 
                cur_client_xpos, 
                cur_client_ypos)
            use framecrop_revealer(
                "gui/no_frame_high_transparent.png",
                "red_light_night_bg",
                cur_client_xpos,
                cur_client_ypos,
                g_prostitution_client_screen_xsize,
                g_prostitution_client_screen_ysize+4,
                l_client_time*idx,
                None if client.girl_id is None else l_client_full_time + l_client_commited_time*client.commited_act_number
            )
    # Девочки (Необходимо сделать распределение, если их больше 5, 10, 15):
    python:
        l_frame_girl_xpos = l_frame_client_xpos + l_frame_client_xsize + 30
        l_frame_girl_start_ypos = l_frame_client_ypos
        l_frame_girl_xsize = 1920 - l_frame_girl_xpos - l_client_start_x
        l_frame_girl_ysize = int(g_prostitution_girl_screen_ysize*1.2)
        l_frame_girl_y_gap = int(l_frame_girl_ysize*1.1)
        l_girl_screen_xpos = l_frame_girl_xpos + g_prostitution_girl_screen_left_right_gaps
        l_girl_client_start_x_gap = g_prostitution_girl_screen_xsize + g_prostitution_girl_screen_left_right_gaps*2
        l_girl_client_max_row_length = int((l_frame_girl_xsize - g_prostitution_girl_screen_xsize - 2*g_prostitution_girl_screen_left_right_gaps)/g_prostitution_client_screen_xsize)
        l_girl_client_x_gap = int((l_frame_girl_xsize - g_prostitution_girl_screen_xsize - 2*g_prostitution_girl_screen_left_right_gaps)/l_girl_client_max_row_length)
        l_girl_client_max_rows = int(l_frame_girl_ysize/g_prostitution_client_screen_ysize)
        l_girl_client_start_y_gap = int((l_frame_girl_ysize/l_girl_client_max_rows - g_prostitution_client_screen_ysize)/2)
        l_girl_client_y_gap = g_prostitution_client_screen_ysize + l_girl_client_start_y_gap*2

        # Timers
        l_girl_full_time = l_client_full_time
        l_each_girl_time = l_girl_full_time/(len(g_base.cur_prostitution_night.whored_girls_id) + 1) # Для дополнительного промежутка, когда появляется девочка и затем фон

    for girl_idx, girl_id in enumerate(g_base.cur_prostitution_night.whored_girls_id):
        python:
            girl = g_base.girls.list[girl_id]
            cur_frame_ypos = l_frame_girl_start_ypos + girl_idx*l_frame_girl_y_gap
            cur_girl_screen_ypos = cur_frame_ypos + int((l_frame_girl_ysize-g_prostitution_girl_screen_ysize)/2)
            cur_girl_clients = g_base.cur_prostitution_night.clients.clients_by_girl_id(girl_id)
        image frame_revealer(
            "nothing_bg",
            l_client_border_px,
            l_client_border_px,
            l_frame_girl_xpos,
            cur_frame_ypos,
            l_frame_girl_xsize,
            l_frame_girl_ysize,
            l_each_girl_time*(girl_idx),
            "gui/no_frame_high_transparent.png",
            0.0
        )
        use prostitution_girl(girl, l_girl_screen_xpos, cur_girl_screen_ypos)
        # Мальчики для девочек:
        for client_idx, client in enumerate(cur_girl_clients):
            python:
                cur_girl_client_xpos = l_frame_girl_xpos + l_girl_client_start_x_gap + (client_idx%l_girl_client_max_row_length)*l_girl_client_x_gap
                cur_girl_client_ypos = cur_frame_ypos + l_girl_client_start_y_gap + (client_idx//l_girl_client_max_row_length)*l_girl_client_y_gap
            if client_idx//l_girl_client_max_row_length < l_girl_client_max_rows:
                use prostitution_client(client, 
                    cur_girl_client_xpos,
                    cur_girl_client_ypos)
                use framecrop_revealer(
                    "gui/no_frame_high_transparent.png",
                    "red_light_night_bg",
                    cur_girl_client_xpos,
                    cur_girl_client_ypos,
                    g_prostitution_client_screen_xsize,
                    g_prostitution_client_screen_ysize+4,
                    l_client_full_time + l_client_commited_time*client.commited_act_number
                )
        image crop_revealer(
            "red_light_night_bg",
            l_frame_girl_xpos,
            cur_frame_ypos,
            l_frame_girl_xsize,
            l_frame_girl_ysize,
            l_each_girl_time*girl_idx
        )

    use skip_screen

screen prostitution_night_act(act):
    python:
        girl = g_base.girls.list[act.girl_id]
        client = g_base.cur_prostitution_night.clients.list[act.client_id]

        l_girl_screen_xpos = g_prostitution_girl_screen_left_right_gaps + g_screens_x_gap
        l_girl_screen_ypos = 1080 - g_prostitution_girl_screen_ysize - g_screens_y_gap
        l_after_girl_xpos = g_prostitution_girl_screen_xsize + g_prostitution_girl_screen_left_right_gaps*2
        l_second_row_size = g_prostitution_client_screen_ysize
        l_second_yrow = int(g_prostitution_girl_screen_ysize-l_second_row_size)
        
        l_font = g_num_font_bold
        l_font_stat_size = int(g_prostitution_girl_screen_ysize/5)
        l_font_stat_min_size = int(l_font_stat_size/2)
        
    image Frame("gui/no_frame_low_transparent.png", 0, 0,
        xpos = 0, 
        ypos = l_girl_screen_ypos-g_prostitution_girl_screen_ysize//5, 
        xsize = 1920, 
        ysize = 1080-(l_girl_screen_ypos-g_prostitution_girl_screen_ysize//5)
        )
    frame:
        style "frame_empty"
        xpos l_girl_screen_xpos
        ypos l_girl_screen_ypos
        xsize 1920-l_girl_screen_xpos-g_screens_x_gap
        ysize 1080 - l_girl_screen_ypos
        use prostitution_girl(girl, 0, 0)
        use prostitution_client(client, l_after_girl_xpos, 0)
        use dice_screen(p_dice = act.dice, p_xpos = l_after_girl_xpos, p_ypos = l_second_yrow, p_size = l_second_row_size)
        hbox:
            xpos l_after_girl_xpos + g_prostitution_client_screen_xsize + int(g_prostitution_client_screen_xsize/5)
            ysize g_prostitution_girl_screen_ysize
            vbox:
                python:
                    l_bonus_act = stats_text(act.bonus_act_mod, colored_pre_text = '')
                    l_roll_effect = stats_text(act._roll_effect, neg_value = g_base.prostitution_difficulty_modifier+1, pos_value = 9, colored_pre_text = '')
                    l_reputation = stats_text(act.reputation)
                    l_profit = int(act.profit)
                    l_expected_profit = act.expected_profit
                text "{font=[l_font]}{size=[l_font_stat_size]}Бонус кубика: [l_roll_effect]{/size}{/font}"
                text "{font=[l_font]}{size=[l_font_stat_size]}Бонус акт: [l_bonus_act]{/size}{/font}"
                text "{font=[l_font]}{size=[l_font_stat_size]}{color=" + colour['reputation'] + "}Репутация: {/color}[l_reputation]{/size}{/font}"
                text "{font=[l_font]}{size=[l_font_stat_size]}{color=" + colour['basic_gold'] + "}Заработок: [l_profit]{/color}{/size}{/font}"
                text "{font=[l_font]}{size=[l_font_stat_min_size]}{color=" + colour['grey'] + "}(Ожидаемый: {/color}{color=" + colour['basic_gold'] + "}[l_expected_profit]{/color}{color=" + colour['grey'] + "}){/color}{/size}{/font}"
            vbox:
                xsize int(g_prostitution_client_screen_xsize/5)
            vbox:
                for chg in act.stat_changes:
                    text "{font=[l_font]}{size=[l_font_stat_size]}[chg]{/size}{/font}"


    use skip_screen