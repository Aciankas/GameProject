init python:
    import renpy.store as store
    import renpy.exports as renpy
    from os import listdir
    from os.path import isfile, join
    import random
    import math

    class Dice(store.object):
        def __init__(self, value: int):
            self.roll = random.randint(1, value)
            self.critical_mod = 1
            self.critical = None
            self.average = (value+1)/2

            if self.roll == value: # Критический успех
                self.critical = True
                if value == 6:
                    self.critical_mod = 1.25
                elif value == 8:
                    self.critical_mod = 1.5
                elif value == 10:
                    self.critical_mod = 2
                elif value == 12:
                    self.critical_mod = 2.25
                elif value == 20:
                    self.critical_mod = 3
            if self.roll == 1: # Критический провал
                self.critical = False
                if value == 6:
                    self.critical_mod = 0.7
                elif value == 8:
                    self.critical_mod = 0.4
                elif value == 10:
                    self.critical_mod = 0.25
                elif value == 12:
                    self.critical_mod = 0.2
                elif value == 20:
                    self.critical_mod = 0.1

    stat_ru_name = {
        "sex": "секс",
        "combat": "бой",
        "job": "услуги",
        "charm": "очарование",
        "grace": "грация",
        "strength": "сила",
        "erudition": "эрудиция",
        "service": "ласки",
        "classic": "классика",
        "anal": "анал",
        "fetish": "фетиш",
        "deception": "уловки",
        "finesse": "искусность",
        "power": "мощь",
        "magic": "магия",
        "waitress": "официантка",
        "dancer": "танцовщица",
        "masseuse": "массажистка",
        "geisha": "гейша"
    }

    stat_system_name = {
        "секс": "sex",
        "бой": "combat",
        "услуги": "job",
        "очарование": "charm",
        "грация": "grace",
        "сила": "strength",
        "эрудиция": "erudition",
        "ласки": "service",
        "классика": "classic",
        "анал": "anal",
        "фетиш": "fetish",
        "уловки": "deception",
        "искусность": "finesse",
        "мощь": "power",
        "магия": "magic",
        "официантка": "waitress",
        "танцовщица": "dancer",
        "массажистка": "masseuse",
        "гейша": "geisha"
    }

    colour = {
        "green": "#70ED3B",
        "red":"#FF4040",
        "orange":"#FF9E00",
        "neutral":"#FFFFFF"}

    personality_traits = [
        ('Дисциплина','Свобода'),
        ('Миролюбие','Кровожадность'),
        ('Раскованность','Скромность'),
        ('Интроверсия','Экстраверсия'),
        ('Аскетизм','Гедонизм'),
        ('Эгоистичность','Альтруистичность')
    ]

    class Personality(store.object):
        def __init__(self, traits=None):
            self.loyalty = 20
            self.discipline = 20
            self.affection_flag = 'loyalty'
            self.affection = 20 #Текущая стата привязки
            self.mood = 50
            self.loyalty_min = 0
            self.loyalty_max = 100
            self.discipline_min = 0
            self.discipline_max = 100
            self.mood_min = 0
            self.mood_max = 100
            self.naughtiness_min = -100
            self.naughtiness_max = 100
            if traits is None:
                self.traits = self.random_traits()
            else:
                self.traits = traits
            if self.has_trait('Раскованность'):
                self.naughtiness = random.randint(0,80)
            elif self.has_trait('Скромность'):
                self.naughtiness = random.randint(-40,-20)
            else:
                self.naughtiness = random.randint(-20,20)

        def change(self, name, value):
            name = name.lower()
            if name in ('loyalty', 'лояльность'):
                self.loyalty += value
                if self.loyalty > self.loyalty_max: self.loyalty = self.loyalty_max
                if self.loyalty < self.loyalty_min: self.loyalty = self.loyalty_min
                if (self.loyalty >= self.discipline + 30) and (self.affection_flag != 'loyalty'):
                    self.affection_flag = 'loyalty'
                if self.affection_flag == 'loyalty':
                    self.affection = self.loyalty
            if name in ('discipline', 'дисциплина'):
                self.discipline += value
                if self.discipline > self.discipline_max: self.discipline = self.discipline_max
                if self.discipline < self.discipline_min: self.discipline = self.discipline_min
                if (self.discipline >= self.loyalty + 30) and (self.affection_flag != 'discipline'):
                    self.affection_flag = 'discipline'
                if self.affection_flag == 'discipline':
                    self.affection = self.discipline
            if name in ('affection','привязанность'):
                if self.affection_flag == 'loyalty':
                    self.change('loyalty', value)
                elif self.affection_flag == 'discipline':
                    self.change('discipline', value)
            if name in ('naughtiness', 'похоть', 'сексуальность'):
                self.naughtiness += value
                if self.naughtiness > self.naughtiness_max: self.naughtiness = self.naughtiness_max
                if self.naughtiness < self.naughtiness_min: self.naughtiness = self.naughtiness_min
            if name in ('mood', 'настроение'):
                self.mood += value
                if self.mood > self.mood_max: self.mood = self.mood_max
                if self.mood < self.mood_min: self.mood = self.mood_min

        def has_trait(self, name):
            #Наличие черты у личности
            for trait in self.traits:
                if trait == name:
                    return True
            return False

        def can_do(self, option):
            #Может ли персонаж выполнить какое либо действие
            option = option.lower()
            return ((option in ('service', 'ласки') and self.naughtiness >= 20)
                or (option in ('sex', 'classic', 'секс', 'классика') and self.naughtiness >= 40)
                or (option in ('anal', 'анал') and self.naughtiness >= 60)
                or (option in ('fetish', 'bdsm', 'фетиш', 'бдсм') and self.naughtiness >= 80))

        def event(self, *events, value=1, param='all'):
            #param: изменяемый параметр личности
            #value: коэффициент изменения
            #events: событие/модификаторы характера воздействия
            multiplier_mod  = 1
            loyalty_mod     = 0
            discipline_mod  = 0
            mood_mod        = 0
            naughtiness_mod = 0
            for subevent in events:
                subevent = subevent.lower() if type(subevent) is str else ''
                if subevent in ('battle', 'бой'): #Миролюбие-Кровожадность
                    if self.has_trait('Кровожадность'):
                        mood_mod += 0.5
                        if self.affection_flag == 'discipline':
                            discipline_mod += 0.5
                    elif self.has_trait('Миролюбие'):
                        mood_mod += -0.5
                        if self.affection_flag == 'loyalty':
                            loyalty_mod += -0.5
                elif subevent in ('peace', 'мир'): #Миролюбие-Кровожадность
                    if self.has_trait('Кровожадность'):
                        mood_mod += -0.5
                        if self.affection_flag == 'discipline':
                            discipline_mod += -0.5
                    elif self.has_trait('Миролюбие'):
                        mood_mod += 0.5
                        if self.affection_flag == 'loyalty':
                            loyalty_mod += 0.5
                elif subevent in ('punishment', 'punish', 'discipline', 'order', 'command', 'наказание', 'муштра', 'приказ'): #Дисциплина-Свобода
                    if self.has_trait('Дисциплина'):
                        mood_mod       += 1
                        discipline_mod += 0.5
                    elif self.has_trait('Свобода'):
                        mood_mod    += -1
                        loyalty_mod += -0.5
                    # Основной расчёт при наказании
                    discipline_mod += 1 #Дисциплина набирается быстрее с штрафом на настроение, относительно лояльности
                    loyalty_mod    += -0.5
                    if self.affection_flag == 'discipline':
                        if self.affection >= 80:
                            mood_mod       += 0.5
                            discipline_mod += 0
                        elif self.affection >= 60:
                            mood_mod       += 0.25
                            discipline_mod += 0.25
                        elif self.affection >= 40:
                            mood_mod       += 0
                            discipline_mod += 0.25
                        elif self.affection >= 20:
                            mood_mod       += -0.5
                            discipline_mod += 0.5
                        else:
                            mood_mod       += -1
                            discipline_mod += 0.5
                    elif self.affection_flag == 'loyalty':
                        if self.affection >= 80:
                            mood_mod += -1.5
                        elif self.affection >= 60:
                            mood_mod += -1
                        elif self.affection >= 40:
                            mood_mod += -0.5
                        elif self.affection >= 20:
                            mood_mod += 0
                        else:
                            mood_mod += 0
                elif subevent in ('reward', 'freedom', 'поощрение', 'награда', 'похвала', 'свобода'): #Дисциплина-Свобода
                    if self.has_trait('Дисциплина'):
                        mood_mod       += -1
                        discipline_mod += -0.5
                    elif self.has_trait('Свобода'):
                        mood_mod    += 1
                        loyalty_mod += 0.5
                    # Основной расчёт при поощрении
                    loyalty_mod    += 0.5
                    discipline_mod += -0.25
                    if self.affection_flag == 'discipline':
                        if self.affection >= 80:
                            mood_mod += -0.5
                        elif self.affection >= 60:
                            mood_mod += -0.25
                        elif self.affection >= 40:
                            mood_mod += 0
                        elif self.affection >= 20:
                            mood_mod += 0.25
                        else:
                            mood_mod += 0.25
                    elif self.affection_flag == 'loyalty':
                        if self.affection >= 80:
                            mood_mod    += 0.5
                            loyalty_mod += 0
                        elif self.affection >= 60:
                            mood_mod    += 0.75
                            loyalty_mod += 0.25
                        elif self.affection >= 40:
                            mood_mod    += 1
                            loyalty_mod += 0.25
                        elif self.affection >= 20:
                            mood_mod    += 1.25
                            loyalty_mod += 0.5
                        else:
                            mood_mod    += 1.5
                            loyalty_mod += 0.5
                elif subevent in ('public', 'публичное', 'публичная', 'публичный'): #Интроверсия-Экстраверсия
                    if self.has_trait('Интроверсия'):
                        mood_mod       +=-0.25
                        multiplier_mod +=-0.25
                    elif self.has_trait('Экстраверсия'):
                        mood_mod       += 0.25
                        multiplier_mod += 0.25
                elif subevent in ('personal', 'private', 'личное', 'личная', 'личный'): #Интроверсия-Экстраверсия
                    if self.has_trait('Интроверсия'):
                        mood_mod       += 0.25
                        multiplier_mod += 0.25
                    elif self.has_trait('Экстраверсия'):
                        mood_mod       +=-0.25
                        multiplier_mod +=-0.25
                elif subevent in ('lust', 'sex', 'секс', 'похоть'): #Раскованность-Скромность
                    if self.has_trait('Раскованность'):
                        mood_mod += 0.5
                        if self.naughtiness >= 80:
                            naughtiness_mod += 1
                        elif self.naughtiness >= 60:
                            naughtiness_mod += 1.25
                        elif self.naughtiness >= 40:
                            naughtiness_mod += 1.5
                        elif self.naughtiness >= 20:
                            naughtiness_mod += 1.75
                        elif self.naughtiness >= 0:
                            naughtiness_mod += 2
                        else:
                            naughtiness_mod += 2.5
                    elif self.has_trait('Скромность'):
                        mood_mod += -0.5
                        if self.naughtiness >= 80:
                            naughtiness_mod += 1
                        elif self.naughtiness >= 60:
                            naughtiness_mod += 0.75
                        elif self.naughtiness >= 40:
                            naughtiness_mod += 0.5
                        elif self.naughtiness >= 20:
                            naughtiness_mod += 0.25
                        elif self.naughtiness >= 0:
                            naughtiness_mod += 0
                        else:
                            naughtiness_mod += -0.25
                    else:
                        if self.naughtiness >= 80:
                            naughtiness_mod += 0.75
                        elif self.naughtiness >= 60:
                            naughtiness_mod += 1
                        elif self.naughtiness >= 40:
                            naughtiness_mod += 1
                        elif self.naughtiness >= 20:
                            naughtiness_mod += 1.25
                        elif self.naughtiness >= 0:
                            naughtiness_mod += 1.25
                        else:
                            naughtiness_mod += 1.5
                elif subevent in ('shy', 'modest', 'modesty', 'скромность', 'забота', 'любовь'): #Раскованность-Скромность
                    if self.has_trait('Раскованность'):
                        mood_mod += -0.5
                        if self.naughtiness >= 80:
                            naughtiness_mod += -1
                        elif self.naughtiness >= 60:
                            naughtiness_mod += -1
                        elif self.naughtiness >= 40:
                            naughtiness_mod += -0.75
                        elif self.naughtiness >= 20:
                            naughtiness_mod += -0.75
                        elif self.naughtiness >= 0:
                            naughtiness_mod += -0.5
                        else:
                            naughtiness_mod += -0.5
                    elif self.has_trait('Скромность'):
                        mood_mod += 0.5
                        if self.naughtiness >= 80:
                            naughtiness_mod += 0
                        elif self.naughtiness >= 60:
                            naughtiness_mod += 0
                        elif self.naughtiness >= 40:
                            naughtiness_mod += 0
                        elif self.naughtiness >= 20:
                            naughtiness_mod += 0.5
                        elif self.naughtiness >= 0:
                            naughtiness_mod += 0.75
                        else:
                            naughtiness_mod += 1
                    else:
                        if self.naughtiness >= 80:
                            naughtiness_mod += -0.5
                        elif self.naughtiness >= 60:
                            naughtiness_mod += -0.5
                        elif self.naughtiness >= 40:
                            naughtiness_mod += -0.25
                        elif self.naughtiness >= 20:
                            naughtiness_mod += -0.25
                        elif self.naughtiness >= 0:
                            naughtiness_mod += 0
                        else:
                            naughtiness_mod += 0
                elif subevent in ('asceticism', 'аскетизм', 'духовность'): #Аскетизм-Гедонизм
                    if self.has_trait('Аскетизм'):
                        mood_mod       += 0.25
                        multiplier_mod += 0.25
                    elif self.has_trait('Гедонизм'):
                        mood_mod       +=-0.25
                        multiplier_mod +=-0.25
                elif subevent in ('hedonism', 'гедонизм', 'жадность', 'меркантильность'): #Аскетизм-Гедонизм
                    if self.has_trait('Аскетизм'):
                        multiplier_mod +=-0.25
                        mood_mod       +=-0.25
                    elif self.has_trait('Гедонизм'):
                        multiplier_mod += 0.25
                        mood_mod       += 0.25
                elif subevent in ('selfishness', 'selfish', 'эгоистичность', 'эгоистичный', 'эгоизм'): #Эгоистичность-Альтруистичность
                    if self.has_trait('Эгоистичность'):
                        multiplier_mod += 0.25
                        mood_mod       += 0.25
                    elif self.has_trait('Альтруистичность'):
                        multiplier_mod +=-0.25
                        mood_mod       +=-0.25
                elif subevent in ('altruism', 'altruistic', 'альтруистичность', 'альтруистичный', 'альтруизм'): #Эгоистичность-Альтруистичность
                    if self.has_trait('Эгоистичность'):
                        multiplier_mod +=-0.25
                        mood_mod       +=-0.25
                    elif self.has_trait('Альтруистичность'):
                        multiplier_mod += 0.25
                        mood_mod       += 0.25
                else:
                    pass

            param = param.lower()
            if param in ('loyalty', 'лояльность'):
                self.change('loyalty',         loyalty_mod*value*multiplier_mod)
            elif param in ('discipline', 'дисциплина'):
                self.change('discipline',   discipline_mod*value*multiplier_mod)
            elif param in ('mood', 'настроение'):
                self.change('mood',               mood_mod*value*multiplier_mod)
            elif param in ('naughtiness', 'похоть', 'сексуальность'):
                self.change('naughtiness', naughtiness_mod*value*multiplier_mod)
            else:
                self.change('loyalty',         loyalty_mod*value*multiplier_mod)
                self.change('discipline',   discipline_mod*value*multiplier_mod)
                self.change('mood',               mood_mod*value*multiplier_mod)
                self.change('naughtiness', naughtiness_mod*value*multiplier_mod)

        def random_traits(self, quantity_min=3, quantity_max=5):
            #Функция для формирования случайного списка черт характера персонажа
            #quantity_min: минимальное количество черт для генерации
            #quantity_max: максимальное количество черт для генерации
            #return: список черт персонажа
            quantity = random.randint(quantity_min, quantity_max)
            traits_not_in_list = []
            for trait in personality_traits:
                traits_not_in_list += [trait]
            trait_list = []
            for counter in range(0, quantity):
                picked_trait = random.randint(0,len(traits_not_in_list)-1)
                #print('picked_trait: '+str(picked_trait)+'; len(traits_not_in_list): '+str(len(traits_not_in_list))) #logging
                picked_orientation = random.randint(0,1)
                trait_list += [traits_not_in_list[picked_trait][picked_orientation]]
                traits_not_in_list.remove(traits_not_in_list[picked_trait])
            return trait_list

        def show(self):
            print(f"""
            Personality stats:
                traits: {self.traits}
                affection: {self.affection}
                affection flag: {self.affection_flag}
                    loyalty: {self.loyalty}
                    discipline: {self.discipline}
                mood: {self.mood}
                naughtiness: {self.naughtiness}
            """)

    class Trait(store.object):
        def __init__(self, name, eng_name, effects, orientation='positive'):
            self.name = name
            self.eng_name = eng_name
            self.effects = effects
            self.orientation = orientation

        def get_trait_info(self):
            result = '{size=30}{u}' + self.name + '{/u}{/size}' #Заголовок инфоокна
            result += '{size=26}' #Размер текста
            for name, effect in self.effects.iteritems():
                result += '\n' + stat_ru_name[name].title() + ' '
                if effect[1] > 0:
                    number_text = '{color=' + colour["green"] + '}+' + str(effect[1]) + ''
                else:
                    number_text = '{color=' + colour["red"] + '}' + str(effect[1]) + ''
                if effect[0] == 'exp_rate':
                    result += number_text + '%{/color} опыта'
                elif effect[0] == 'max_value':
                    result += number_text + '{/color} макс лимит'
                elif effect[0] == 'modifier':
                    result += number_text + '{/color} эффективность'
            result += '{/size}'
            return result

    all_traits = [
                Trait("Нимфоманка",           "", {"sex": ("exp_rate", 30)},                                   "positive"),
                Trait("Грамотные тренировки", "", {"combat": ("exp_rate", 30)},                                "positive"),
                Trait("Гениальная служанка",  "", {"job": ("exp_rate", 30)},                                   "positive"),
                Trait("Чуткая",               "", {"charm": ("exp_rate", 35)},                                 "positive"),
                Trait("Природная гибкость",   "", {"grace": ("exp_rate", 35)},                                 "positive"),
                Trait("Растущая мощь",        "", {"strength": ("exp_rate", 35)},                              "positive"),
                Trait("Осознанная",           "", {"erudition": ("exp_rate", 35)},                             "positive"),
                Trait("Чувствительная грудь", "", {"charm": ("exp_rate", 18), "sex": ("exp_rate", 18)},        "positive"),
                Trait("Карманница",           "", {"charm": ("exp_rate", 18), "combat": ("exp_rate", 18)},     "positive"),
                Trait("Быстрое обслуживание", "", {"charm": ("exp_rate", 18), "job": ("exp_rate", 18)},        "positive"),
                Trait("Податливая",           "", {"grace": ("exp_rate", 18), "sex": ("exp_rate", 18)},        "positive"),
                Trait("Уроки охоты",          "", {"grace": ("exp_rate", 18), "combat": ("exp_rate", 18)},     "positive"),
                Trait("Чувство ритма",        "", {"grace": ("exp_rate", 18), "job": ("exp_rate", 18)},        "positive"),
                Trait("Пышные формы",         "", {"strength": ("exp_rate", 18), "sex": ("exp_rate", 18)},     "positive"),
                Trait("Развитые мышцы",       "", {"strength": ("exp_rate", 18), "combat": ("exp_rate", 18)},  "positive"),
                Trait("Знание анатомии",      "", {"strength": ("exp_rate", 18), "job": ("exp_rate", 18)},     "positive"),
                Trait("Любительница нового",  "", {"erudition": ("exp_rate", 18), "sex": ("exp_rate", 18)},    "positive"),
                Trait("Тайны магии",          "", {"erudition": ("exp_rate", 18), "combat": ("exp_rate", 18)}, "positive"),
                Trait("Умелый собеседник",    "", {"erudition": ("exp_rate", 18), "job": ("exp_rate", 18)},    "positive"),

                Trait("Ночь напролёт",       "", {"sex": ("max_value", 20), "service": ("max_value", 20), "classic": ("max_value", 20), "anal": ("max_value", 20), "fetish": ("max_value", 20)},      "positive"),
                Trait("Боевой раж",          "", {"combat": ("max_value", 20), "deception": ("max_value", 20), "finesse": ("max_value", 20), "power": ("max_value", 20), "magic": ("max_value", 20)}, "positive"),
                Trait("Семейное дело",       "", {"job": ("max_value", 20), "waitress": ("max_value", 20), "dancer": ("max_value", 20), "masseuse": ("max_value", 20), "geisha": ("max_value", 20)},  "positive"),
                Trait("Живая мимика",        "", {"charm": ("max_value", 30), "service": ("max_value", 30), "deception": ("max_value", 30), "waitress": ("max_value", 30)},                           "positive"),
                Trait("Идеальная фигура",    "", {"grace": ("max_value", 30), "classic": ("max_value", 30), "finesse": ("max_value", 30), "dancer": ("max_value", 30)},                               "positive"),
                Trait("Природная мощь",      "", {"strength": ("max_value", 30), "anal": ("max_value", 30), "power": ("max_value", 30), "masseuse": ("max_value", 30)},                               "positive"),
                Trait("Пытливый ум",         "", {"erudition": ("max_value", 30), "fetish": ("max_value", 30), "magic": ("max_value", 30), "geisha": ("max_value", 30)},                              "positive"),
                Trait("Глубокий поцелуй",    "", {"service": ("max_value", 70)},   "positive"),
                Trait("Невидимка",           "", {"deception": ("max_value", 70)}, "positive"),
                Trait("Марафонец",           "", {"waitress": ("max_value", 70)},  "positive"),
                Trait("Возбуждающие изгибы", "", {"classic": ("max_value", 70)},   "positive"),
                Trait("Зоркий глаз",         "", {"finesse": ("max_value", 70)},   "positive"),
                Trait("Танцевальный азарт",  "", {"dancer": ("max_value", 70)},    "positive"),
                Trait("Крепкий орешек",      "", {"anal": ("max_value", 70)},      "positive"),
                Trait("Безграничная сила",   "", {"power": ("max_value", 70)},     "positive"),
                Trait("Сильные руки",        "", {"masseuse": ("max_value", 70)},  "positive"),
                Trait("Богатая фантазия",    "", {"fetish": ("max_value", 70)},    "positive"),
                Trait("Духовная стойкость",  "", {"magic": ("max_value", 70)},     "positive"),
                Trait("Эрудиция",            "", {"geisha": ("max_value", 70)},    "positive"),

                Trait("Развратница",          "", {"service": ("modifier", 1), "classic": ("modifier", 1), "anal": ("modifier", 1), "fetish": ("modifier", 1)},     "positive"),
                Trait("Прирождённый боец",    "", {"deception": ("modifier", 1), "finesse": ("modifier", 1), "power": ("modifier", 1), "magic": ("modifier", 1)},   "positive"),
                Trait("Лояльная",             "", {"waitress": ("modifier", 1), "dancer": ("modifier", 1), "masseuse": ("modifier", 1), "geisha": ("modifier", 1)}, "positive"),
                Trait("Обольстительница",     "", {"service": ("modifier", 2), "deception": ("modifier", 2), "waitress": ("modifier", 2)},                          "positive"),
                Trait("Изящество",            "", {"classic": ("modifier", 2), "finesse": ("modifier", 2), "dancer": ("modifier", 2)},                              "positive"),
                Trait("Подавляющая",          "", {"anal": ("modifier", 2), "power": ("modifier", 2), "masseuse": ("modifier", 2)},                                 "positive"),
                Trait("Гуру",                 "", {"fetish": ("modifier", 2), "magic": ("modifier", 2), "geisha": ("modifier", 2)},                                 "positive"),
                Trait("Мягкие губы",          "", {"service": ("modifier", 3)},   "positive"),
                Trait("Амбидекстр",           "", {"deception": ("modifier", 3)}, "positive"),
                Trait("Боковое зрение",       "", {"waitress": ("modifier", 3)},  "positive"),
                Trait("Влажные губы",         "", {"classic": ("modifier", 3)},   "positive"),
                Trait("Следопыт",             "", {"finesse": ("modifier", 3)},   "positive"),
                Trait("Кураж",                "", {"dancer": ("modifier", 3)},    "positive"),
                Trait("Притягательные бёдра", "", {"anal": ("modifier", 3)},      "positive"),
                Trait("Берсерк",              "", {"power": ("modifier", 3)},     "positive"),
                Trait("Расслабляющие обряды", "", {"masseuse": ("modifier", 3)},  "positive"),
                Trait("Раскрепощенная",       "", {"fetish": ("modifier", 3)},    "positive"),
                Trait("Гибкая энергия",       "", {"magic": ("modifier", 3)},     "positive"),
                Trait("Мечтательница",        "", {"geisha": ("modifier", 3)},    "positive"),


                Trait("Фригидная",        "", {"sex": ("exp_rate", -30)},       "negative"),
                Trait("Растерянность",    "", {"combat": ("exp_rate", -30)},    "negative"),
                Trait("Ленивая",          "", {"job": ("exp_rate", -30)},       "negative"),
                Trait("Чёрствая",         "", {"charm": ("exp_rate", -35)},     "negative"),
                Trait("Деревянная",       "", {"grace": ("exp_rate", -35)},     "negative"),
                Trait("Болезненная",      "", {"strength": ("exp_rate", -35)},  "negative"),
                Trait("Забывчивая",       "", {"erudition": ("exp_rate", -35)}, "negative"),
                Trait("Консерватор",      "", {"charm": ("exp_rate", -18), "sex": ("exp_rate", -18)},       "negative"),
                Trait("TEMPORARY_2_2_3",  "", {"charm": ("exp_rate", -18), "combat": ("exp_rate", -18)},    "negative"),
                Trait("Халатность",       "", {"charm": ("exp_rate", -18), "job": ("exp_rate", -18)},       "negative"),
                Trait("Бревно",           "", {"grace": ("exp_rate", -18), "sex": ("exp_rate", -18)},       "negative"),
                Trait("Неустойчивость",   "", {"grace": ("exp_rate", -18), "combat": ("exp_rate", -18)},    "negative"),
                Trait("Замкнутая",        "", {"grace": ("exp_rate", -18), "job": ("exp_rate", -18)},       "negative"),
                Trait("Неприступная",     "", {"strength": ("exp_rate", -18), "sex": ("exp_rate", -18)},    "negative"),
                Trait("TEMPORARY_2_4_3",  "", {"strength": ("exp_rate", -18), "combat": ("exp_rate", -18)}, "negative"),
                Trait("TEMPORARY_2_4_4",  "", {"strength": ("exp_rate", -18), "job": ("exp_rate", -18)},    "negative"),
                Trait("Ханжа",            "", {"erudition": ("exp_rate", -18), "sex": ("exp_rate", -18)},   "negative"),
                Trait("Неуравновешенная", "", {"erudition": ("exp_rate", -18), "combat": ("exp_rate", -18)},"negative"),
                Trait("Тугодум",          "", {"erudition": ("exp_rate", -18), "job": ("exp_rate", -18)},   "negative"),

                Trait("Аногразмия",              "", {"sex": ("max_value", -20), "service": ("max_value", -20), "classic": ("max_value", -20), "anal": ("max_value", -20), "fetish": ("max_value", -20)},      "negative"),
                Trait("Трусость",                "", {"combat": ("max_value", -20), "deception": ("max_value", -20), "finesse": ("max_value", -20), "power": ("max_value", -20), "magic": ("max_value", -20)}, "negative"),
                Trait("Растяпа",                 "", {"job": ("max_value", -20), "waitress": ("max_value", -20), "dancer": ("max_value", -20), "masseuse": ("max_value", -20), "geisha": ("max_value", -20)},  "negative"),
                Trait("Грубая",                  "", {"charm": ("max_value", -30), "service": ("max_value", -30), "deception": ("max_value", -30), "waitress": ("max_value", -30)}, "negative"),
                Trait("Неуклюжая",               "", {"grace": ("max_value", -30), "classic": ("max_value", -30), "finesse": ("max_value", -30), "dancer": ("max_value", -30)},     "negative"),
                Trait("Немощная",                "", {"strength": ("max_value", -30), "anal": ("max_value", -30), "power": ("max_value", -30), "masseuse": ("max_value", -30)},     "negative"),
                Trait("Легкомысленная",          "", {"erudition": ("max_value", -30), "fetish": ("max_value", -30), "magic": ("max_value", -30), "geisha": ("max_value", -30)},    "negative"),
                Trait("Слабая чувствительность", "", {"service": ("max_value", -70)},   "negative"),
                Trait("TEMPORARY_4_2_3",         "", {"deception": ("max_value", -70)}, "negative"),
                Trait("TEMPORARY_4_2_4",         "", {"waitress": ("max_value", -70)},  "negative"),
                Trait("Мимолетное возбуждение",  "", {"classic": ("max_value", -70)},   "negative"),
                Trait("Хромая",                  "", {"finesse": ("max_value", -70)},   "negative"),
                Trait("TEMPORARY_4_3_4",         "", {"dancer": ("max_value", -70)},    "negative"),
                Trait("TEMPORARY_4_4_2",         "", {"anal": ("max_value", -70)},      "negative"),
                Trait("Хилая",                   "", {"power": ("max_value", -70)},     "negative"),
                Trait("TEMPORARY_4_4_4",         "", {"masseuse": ("max_value", -70)},  "negative"),
                Trait("TEMPORARY_4_5_2",         "", {"fetish": ("max_value", -70)},    "negative"),
                Trait("Рассеяная",               "", {"magic": ("max_value", -70)},     "negative"),
                Trait("Сонный голос",            "", {"geisha": ("max_value", -70)},    "negative"),

                Trait("Стеснительная",       "", {"service": ("modifier", -1), "classic": ("modifier", -1), "anal": ("modifier", -1), "fetish": ("modifier", -1)},     "negative"),
                Trait("Пацифист",            "", {"deception": ("modifier", -1), "finesse": ("modifier", -1), "power": ("modifier", -1), "magic": ("modifier", -1)},   "negative"),
                Trait("Неряха",              "", {"waitress": ("modifier", -1), "dancer": ("modifier", -1), "masseuse": ("modifier", -1), "geisha": ("modifier", -1)}, "negative"),
                Trait("Медлительная",        "", {"service": ("modifier", -2), "deception": ("modifier", -2), "waitress": ("modifier", -2)},                           "negative"),
                Trait("Нелепая",             "", {"classic": ("modifier", -2), "finesse": ("modifier", -2), "dancer": ("modifier", -2)},                               "negative"),
                Trait("Слабая",              "", {"anal": ("modifier", -2), "power": ("modifier", -2), "masseuse": ("modifier", -2)},                                  "negative"),
                Trait("Простачка",           "", {"fetish": ("modifier", -2), "magic": ("modifier", -2), "geisha": ("modifier", -2)},                                  "negative"),
                Trait("TEMPORARY_6_2_2",     "", {"service": ("modifier", -3)},   "negative"),
                Trait("TEMPORARY_6_2_3",     "", {"deception": ("modifier", -3)}, "negative"),
                Trait("TEMPORARY_6_2_4",     "", {"waitress": ("modifier", -3)},  "negative"),
                Trait("TEMPORARY_6_3_2",     "", {"classic": ("modifier", -3)},   "negative"),
                Trait("Одноглазая",          "", {"finesse": ("modifier", -3)},   "negative"),
                Trait("TEMPORARY_6_3_4",     "", {"dancer": ("modifier", -3)},    "negative"),
                Trait("TEMPORARY_6_4_2",     "", {"anal": ("modifier", -3)},      "negative"),
                Trait("TEMPORARY_6_4_3",     "", {"power": ("modifier", -3)},     "negative"),
                Trait("TEMPORARY_6_4_4",     "", {"masseuse": ("modifier", -3)},  "negative"),
                Trait("Скованная",           "", {"fetish": ("modifier", -3)},    "negative"),
                Trait("Безумная",            "", {"magic": ("modifier", -3)},     "negative"),
                Trait("Плохая дикция",       "", {"geisha": ("modifier", -3)},    "negative")
                ]

    def get_trait_from_all_traits(input_value, not_traits=[]):
        #input_value: либо название черты, либо "positive"/"negative"/"special" для случайной
        #not_traits: массив черт, эффектов которых необходимо избегать при поиске новой черты
        #return: черту, если та существует, если нет - None
        if input_value in ("positive", "negative", "special"):
            possible_traits = []
            if len(not_traits) == 0:
                for trait in all_traits:
                    if trait.orientation == input_value:
                        possible_traits += [trait]
            else:
                for trait in all_traits:
                    if trait.orientation == input_value:
                        valid = True
                        for trait_effect_name, trait_effect in trait.effects.iteritems():
                            for forbidden_trait in not_traits:
                                for forbidden_effect_name, forbidden_effect in forbidden_trait.effects.iteritems():
                                    if trait_effect_name == forbidden_effect_name and trait_effect[0] == forbidden_effect[0]:
                                        valid = False
                        if valid:
                            possible_traits += [trait]
            return possible_traits[random.randint(0,len(possible_traits)-1)]
        else:
            for trait in all_traits:
                if trait.name == input_value:
                    return trait

    class Stat(store.object):
        def __init__(self, name, eng_name, value, max_value, modifier, exp, exp_rate, parent_1_name, parent_2_name, bar_texture, icon):
            self.name = name
            self.eng_name = eng_name
            self.title = name.title()
            self.value = value
            self.max_value = max_value
            self.modifier = modifier
            self.exp = exp
            self.exp_rate = exp_rate
            self.parent_1_name = parent_1_name
            self.parent_2_name = parent_2_name
            self.bar_texture = bar_texture
            self.icon = icon

        # динамический бар статы
        def get_bar_texture(self):
            if self.bar_texture == "dynamic":
                if self.value < 25:
                    texture = "common"
                elif self.value < 50:
                    texture = "uncommon"
                elif self.value < 75:
                    texture = "rare"
                elif self.value < 100:
                    texture = "epic"
                elif self.value < 130:
                    texture = "legendary"
                elif self.value < 170:
                    texture = "artifact"
                else:
                    texture = "maximum"
            else:
                texture = self.bar_texture
            return "gui/bar/left_" + texture + ".png"

        # иконка характеристики
        def get_icon(self, icon_name="default", postfix="", x = False, y = False):
            #default
            if not x:
                if icon_name == "plus":
                    x = 25
                else:
                    x = 40
            if not y:
                if icon_name == "plus":
                    y = 25
                else:
                    y = 40
            # -----------
            if self.icon == "" or icon_name == "plus":
                icon = "plus"
            else:
                icon = self.icon

            if postfix in ("light", "gold", "lightgold"):
                cur_stat_icon = "images/icons/stats/" + icon + "_" + postfix + ".png"
            else:
                cur_stat_icon = "images/icons/stats/" + icon + ".png"
            return Transform(cur_stat_icon, fit='contain', xysize = (x,y))

        # уровень акта (владение характеристикой через таланты)
        def act_level(self):
            return self.value//20 # Пока нет перков прокачки стат
        
        def upcost(self):
            dict_upcost = {
                140: 250,
                120: 200,
                100: 150,
                80: 100,
                60: 70,
                40: 40,
                20: 20,
                0: 10
            }
            for dict_value, dict_upcost in dict_upcost.items():
                if self.value >= dict_value:
                    return dict_upcost

    class Personage(store.object):
        def __init__(self, name='default', energy=100, max_energy = 100, health=100, max_health = 100, pic_directory = 'default', traits=[],
        base_sex=0,          base_combat=0,     base_job=0,      base_charm=0,         base_grace=0,         base_strength=0,         base_erudition=0,
        sec_service=0,       sec_classic=0,     sec_anal=0,      sec_fetish=0,
        sec_deception=0,     sec_finesse=0,     sec_power=0,     sec_magic=0,
        sec_waitress=0,      sec_dancer=0,      sec_masseuse=0,  sec_geisha=0,
        base_sex_exp=0,      base_combat_exp=0, base_job_exp=0,  base_charm_exp=0,     base_grace_exp=0,     base_strength_exp=0,     base_erudition_exp=0, 
        lore_flag = False
        ):
            self.name = name
            self.energy = energy
            self.max_energy = max_energy
            self.health = health
            self.max_health = max_health
            self.pic_directory = pic_directory
            self.profile_image = self.picture('profile')
            self.init_stats(base_sex, base_combat, base_job, base_charm, base_grace, base_strength, base_erudition, sec_service, sec_classic, sec_anal, sec_fetish, sec_deception, sec_finesse, sec_power, sec_magic, sec_waitress, sec_dancer, sec_masseuse, sec_geisha, base_sex_exp, base_combat_exp, base_job_exp, base_charm_exp, base_grace_exp, base_strength_exp, base_erudition_exp)
            self.init_traits(traits)
            self.personality = Personality()
            # Флаги деятельности
            self.action_flag = 'whore' # 'work'/'whore'/'arena'/'rest'/'training'/'event'
            self.action_command = False
            self.action_public = False
            self.rest_flag = None
            self.lore_flag = lore_flag # Является ли персонаж сюжетным

        def show(self):
            print(f"""
            {self.name}
            energy: {self.energy}
            health: {self.health}/{self.max_health}
            Stats:
            """)
            stats = ''
            for key, stat in self.stat.items():
                print(f' -{stat.name}: {stat.value}/{stat.max_value}, exp: {stat.exp}, exp_rate: {stat.exp_rate}, mod: {stat.modifier}')
            print('Traits:')
            for trait in self.traits:
                print(f'-{trait.name}')
            self.personality.show()

        # Блок инициализации
        def init_stats(self,
        base_sex,        base_combat,      base_job,      base_charm,      base_grace,      base_strength,      base_erudition,
        sec_service,     sec_classic,      sec_anal,      sec_fetish,
        sec_deception,   sec_finesse,      sec_power,     sec_magic,
        sec_waitress,    sec_dancer,       sec_masseuse,  sec_geisha,
        base_sex_exp,    base_combat_exp,  base_job_exp,  base_charm_exp,  base_grace_exp,  base_strength_exp,  base_erudition_exp):
            self.stat = {
                "sex"       : Stat(name="секс",        eng_name="sex"       ,value=base_sex,       max_value=100, modifier=None, exp=base_sex_exp,      exp_rate=1,    parent_1_name="sex",       parent_2_name=None,     bar_texture="dynamic", icon=""),
                "combat"    : Stat(name="бой",         eng_name="combat"    ,value=base_combat,    max_value=100, modifier=None, exp=base_combat_exp,   exp_rate=1,    parent_1_name="combat",    parent_2_name=None,     bar_texture="dynamic", icon=""),
                "job"       : Stat(name="услуги",      eng_name="job"       ,value=base_job,       max_value=100, modifier=None, exp=base_job_exp,      exp_rate=1,    parent_1_name="job",       parent_2_name=None,     bar_texture="dynamic", icon=""),
                "charm"     : Stat(name="очарование",  eng_name="charm"     ,value=base_charm,     max_value=100, modifier=None, exp=base_charm_exp,    exp_rate=1,    parent_1_name="charm",     parent_2_name=None,     bar_texture="dynamic", icon=""),
                "grace"     : Stat(name="грация",      eng_name="grace"     ,value=base_grace,     max_value=100, modifier=None, exp=base_grace_exp,    exp_rate=1,    parent_1_name="grace",     parent_2_name=None,     bar_texture="dynamic", icon=""),
                "strength"  : Stat(name="сила",        eng_name="strength"  ,value=base_strength,  max_value=100, modifier=None, exp=base_strength_exp, exp_rate=1,    parent_1_name="strength",  parent_2_name=None,     bar_texture="dynamic", icon=""),
                "erudition" : Stat(name="эрудиция",    eng_name="erudition" ,value=base_erudition, max_value=100, modifier=None, exp=base_erudition_exp,exp_rate=1,    parent_1_name="erudition", parent_2_name=None,     bar_texture="dynamic", icon=""),
                "service"   : Stat(name="ласки",       eng_name="service"   ,value=sec_service,    max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="charm",     parent_2_name="sex",    bar_texture="dynamic", icon="service"),
                "deception" : Stat(name="уловки",      eng_name="deception" ,value=sec_deception,  max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="charm",     parent_2_name="combat", bar_texture="dynamic", icon="rogue"),
                "waitress"  : Stat(name="официантка",  eng_name="waitress"  ,value=sec_waitress,   max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="charm",     parent_2_name="job",    bar_texture="dynamic", icon="waitress"),
                "classic"   : Stat(name="классика",    eng_name="classic"   ,value=sec_classic,    max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="grace",     parent_2_name="sex",    bar_texture="dynamic", icon="sex"),
                "finesse"   : Stat(name="искусность",  eng_name="finesse"   ,value=sec_finesse,    max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="grace",     parent_2_name="combat", bar_texture="dynamic", icon="archer"),
                "dancer"    : Stat(name="танцовщица",  eng_name="dancer"    ,value=sec_dancer,     max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="grace",     parent_2_name="job",    bar_texture="dynamic", icon="dancer"),
                "anal"      : Stat(name="анал",        eng_name="anal"      ,value=sec_anal,       max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="strength",  parent_2_name="sex",    bar_texture="dynamic", icon="anal"),
                "power"     : Stat(name="мощь",        eng_name="power"     ,value=sec_power,      max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="strength",  parent_2_name="combat", bar_texture="dynamic", icon="warrior"),
                "masseuse"  : Stat(name="массажистка", eng_name="masseuse"  ,value=sec_masseuse,   max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="strength",  parent_2_name="job",    bar_texture="dynamic", icon="masseuse"),
                "fetish"    : Stat(name="фетиш",       eng_name="fetish"    ,value=sec_fetish,     max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="erudition", parent_2_name="sex",    bar_texture="dynamic", icon="fetish"),
                "magic"     : Stat(name="магия",       eng_name="magic"     ,value=sec_magic,      max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="erudition", parent_2_name="combat", bar_texture="dynamic", icon="mage"),
                "geisha"    : Stat(name="гейша",       eng_name="geisha"    ,value=sec_geisha,     max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="erudition", parent_2_name="job",    bar_texture="dynamic", icon="geisha")
            }

        def init_traits(self, traits):
            # Заполнение черт
            positive_traits_count = 0
            negative_traits_count = 0
            self.traits = []
            for trait_name in traits:
                if trait_name in ("positive", "negative", "special"):
                    self.add_trait(trait_name)
                else:
                    trait = get_trait_from_all_traits(trait_name)
                    if trait is not None:
                        if trait.orientation == 'negative':
                            negative_traits_count += 1
                        else:
                            positive_traits_count += 1
                        self.traits += trait
            while positive_traits_count < 2:
                self.add_trait("positive")
                positive_traits_count += 1
            while negative_traits_count < 1:
                self.add_trait("negative")
                negative_traits_count += 1

        def night_rest(self):
            self.energy = self.max_energy

        def work_energy(self):
            #return: Количество энергии, доступное для работы в этот день
            return self.energy

        def action_energy(self, action: str = 'default'):
            # action: тип действия персонажа, для которого необходимо расчитать его цену, учитывая перки
            # return: количество энергии, затрачиваемое на этот тип действия
            return 25
        
        def acted(self, action: str = 'default', exp_value: float = 1):
            # action: тип действия персонажа, для которого необходимо выполнить изменения, связанные с персонажем
            self.energy -= self.action_energy(action)
            self.change_exp(action, exp_value)
        
        # Блок черт персонажа
        def add_trait(self, trait_name):
            # Простая запись для добавления черты и пересчет параметров
            # trait_name - "positive", "negative", "special" или имя черты на русском
            self.traits.append(get_trait_from_all_traits(trait_name, self.traits))
            self.recalculate_traits()

        def remove_trait(self, trait_name):
            # trait_name - "all" или имя черты на русском
            for trait in reversed(self.traits):
                if trait_name == trait.name or trait_name == "all":
                    self.traits.remove(trait)

        def get_stat_color(self, input_stat):
            positive = False
            negative = False
            for trait in self.traits:
                for stat, effect in trait.effects.iteritems():
                    if (effect[0] == "exp_rate" and (input_stat.parent_1_name == stat or input_stat.parent_2_name == stat)) or (stat == input_stat.eng_name):
                    #Если модификатор на экспу и кто-то из родителей проверяемой статы есть в эффекте, либо в эффекте сама стата, то мы учитываем этот эффект в подсветке
                        if effect[1] > 0:
                            positive = True
                        elif effect[1] < 0:
                            negative = True
            if positive and negative:
                result = colour["orange"]
            elif positive:
                result = colour["green"]
            elif negative:
                result = colour["red"]
            else:
                result = colour["neutral"]
            return result

        def recalculate_traits(self):
            for i, stat in self.stat.iteritems():
                stat.max_value = 100
                if stat.modifier is not None:
                    stat.modifier = 0
                if stat.exp_rate is not None:
                    stat.exp_rate = 1
            for trait in self.traits:
                for stat_name, effect in trait.effects.iteritems():
                    if effect[0] == "exp_rate":
                        self.stat[stat_name].exp_rate += 0.01 * effect[1]
                    elif effect[0] == "max_value":
                        self.stat[stat_name].max_value += effect[1]
                    elif effect[0] == "modifier":
                        self.stat[stat_name].modifier += effect[1]

        # Блок основных характеристик персонажа
        def is_secondary_stat_group_upgradable(self, stat): # Можно ли улучшить вторичную характеристику или первичные, от которых она зависит
            if self.is_stat_upgradable(stat) or self.is_stat_upgradable(self.stat[stat.parent_1_name]) or self.is_stat_upgradable(self.stat[stat.parent_2_name]):
                return True
            else:
                return False

        def is_stat_upgradable(self, stat: Stat): #Можно ли улучшить конкретную характеристику
            main_stat_higher_flag = True #Выше ли доп статы основная?
            if stat.parent_2_name is None:
                cur_exp = stat.exp
            else:
                parent_stat_1 = self.stat[stat.parent_1_name]
                parent_stat_2 = self.stat[stat.parent_2_name]
                cur_exp = parent_stat_1.exp + parent_stat_2.exp
                if (float(stat.value)/float(stat.max_value) >= float(parent_stat_1.value)/float(parent_stat_1.max_value)) or (float(stat.value)/float(stat.max_value) >= float(parent_stat_2.value)/float(parent_stat_2.max_value)): #Процентно ниже ли доп стата основных, от которых зависит?
                    main_stat_higher_flag = False
            if (stat.value < stat.max_value) and (cur_exp >= stat.upcost()) and main_stat_higher_flag:
                return True
            else:
                return False

        def change_exp(self, stat, value=1):
            if type(stat) is str:
                cur_stat = self.stat[stat]
            elif type(stat) is Stat:
                cur_stat = stat
            else:
                print('return None')
                return None
            if cur_stat.parent_2_name is None:
                cur_stat.exp += value*(cur_stat.exp_rate if value > 0 else 1)
            else:
                self.change_exp(cur_stat.parent_1_name, value)
                self.change_exp(cur_stat.parent_2_name, value)

        def stat_upgrade(self, stat, mode=0): #mode - какую характеристику использовать первой при апгрейде. 0 - очарование, грация, сила, эрудиция; Другое - секс, бой, услуги
            if self.is_stat_upgradable(stat):
                # Расчёт расхода экспы
                expense_exp = stat.upcost()
                if stat.parent_2_name is not None:
                    if mode == 0:
                        expense_exp_1 = self.stat[stat.parent_1_name].exp
                        if expense_exp_1 >= expense_exp:
                            expense_exp_1 = expense_exp
                            expense_exp_2 = 0
                        else:
                            expense_exp_2 = expense_exp - expense_exp_1
                    else:
                        expense_exp_2 = self.stat[stat.parent_2_name].exp
                        if expense_exp_2 >= expense_exp:
                            expense_exp_2 = expense_exp
                            expense_exp_1 = 0
                        else:
                            expense_exp_1 = expense_exp - expense_exp_2
                    self.change_exp(stat.parent_1_name, -expense_exp_1)
                    self.change_exp(stat.parent_2_name, -expense_exp_2)
                else:
                    self.change_exp(stat, -expense_exp)
                # Прибавка к характеристике
                stat.value += 1

        # Блок подбора картинок по тэгу
        def picture(self, *titles):
            if os.path.isdir('game'):
                path = "game/images/Girls/" + self.pic_directory
            else:
                path = "../GameProject/The Ascension of Susan/game/images/Girls/" + self.pic_directory
            pic_list = os.listdir(path)
            result_list = []
            for title in titles:
                for pic in pic_list:
                    if title in pic:
                        result_list.append(pic)
                if len(result_list) != 0:
                    break
            result = "images/Girls/" + self.pic_directory + "/" + str(result_list[random.randint(0, len(result_list)-1)])
            return result

        def make_profile_image(self):
            self.profile_image = self.picture('profile')

    class Personage_List (store.object):
        def __init__(self, init_list: List[Personage] = None):
            self.list = init_list or list()

        def add(self, value: Personage):
            self.list.append(value)

        def remove(self, value: Personage):
            self.list.remove(value)

        def make_profile_image(self):
            for girl in self.list:
                girl.make_profile_image()

        def night_rest(self):
            for girl in self.list:
                girl.night_rest()


screen personage_screen:
    frame:
        background Frame(im.MatrixColor("gui/frame.png", im.matrix.brightness(-1) * im.matrix.opacity(0.65)))
        xpos 1290
        ypos 65
        padding (3, 3, 3, 3)
        vbox:
            xsize 620
            ysize 1000
            for girl_iterator in range(0,len(g_base.girls.list)):
                hbox:
                    $ displayed_name = g_base.girls.list[girl_iterator].name
                    textbutton "[displayed_name]" action Show("personage_stats", None, girl_iterator)
            textbutton "Вернуться" action [Hide("personage_screen"), Hide("personage_stats"), Hide("increment_stat")]

label personage_screen_label:
    $ g_base.girls.make_profile_image()
    call screen personage_screen
    return

style textstat:
    color colour['neutral']

# Отображение блока характеристики
screen stat_block(cur_stat, current_companion, button_display='observe'):
    python:
        bar_xsize = 200
        bar_ysize = 20
        text_size = 24
        bar_text_size = bar_ysize-3
        cur_stat_colour = current_companion.get_stat_color(cur_stat)
        cur_bar_texture = cur_stat.get_bar_texture()
    fixed:
        xmaximum bar_xsize+10
        ymaximum bar_ysize+text_size+5
        text "{color=[cur_stat_colour]}{size=[text_size]}[cur_stat.title]{/size}{/color}" xalign 0.5
        bar value AnimatedValue(cur_stat.value, cur_stat.max_value, 0.5):
            left_bar Frame(cur_bar_texture)
            right_bar Frame("gui/bar/empty.png")
            xsize bar_xsize
            ysize bar_ysize
            ypos text_size+3
            xalign 0.5
        # Блок кнопки и текста для Досье персонажа
        if button_display == 'stats':
            text "{size=[bar_text_size]}[cur_stat.value]/[cur_stat.max_value]{/size}" xalign 0.9 ypos (text_size+1)
            if current_companion.is_secondary_stat_group_upgradable(cur_stat):
                $ cur_stat_icon = cur_stat.get_icon(postfix="gold")
                $ cur_stat_icon_active = cur_stat.get_icon(postfix="lightgold")
            else:
                $ cur_stat_icon = cur_stat.get_icon()
                $ cur_stat_icon_active = cur_stat.get_icon(postfix="light")
            $ renpy.retain_after_load()
            imagebutton:
                xpos 8
                ypos text_size-4
                idle cur_stat_icon
                hover cur_stat_icon_active
                action Show("increment_stat", None, cur_stat, current_companion)
        # Блок кнопок и текста для окна распределения опыта
        elif button_display in ('left', 'right', 'parents'):
            if current_companion.is_stat_upgradable(cur_stat):
                $ cur_stat_icon = cur_stat.get_icon(icon_name='plus', postfix="gold")
                $ cur_stat_icon_active = cur_stat.get_icon(icon_name='plus', postfix="lightgold")
            else:
                $ cur_stat_icon = cur_stat.get_icon(icon_name='plus')
                $ cur_stat_icon_active = cur_stat.get_icon(icon_name='plus', postfix="light")

            if button_display == 'parents':
                text "{size=[bar_text_size]}[cur_stat.value]/[cur_stat.max_value]{/size}" xalign 0.5 ypos (text_size+1)
                imagebutton:
                    xpos -8
                    ypos text_size+13
                    idle cur_stat_icon
                    hover cur_stat_icon_active
                    action Function(current_companion.stat_upgrade, cur_stat, 0)
                imagebutton:
                    xpos bar_xsize-8
                    ypos text_size+13
                    idle cur_stat_icon
                    hover cur_stat_icon_active
                    action Function(current_companion.stat_upgrade, cur_stat, 1)
            elif button_display == 'left':
                text "{size=[bar_text_size]}[cur_stat.value]/[cur_stat.max_value]{/size}" xalign 0.9 ypos (text_size+1)
                imagebutton:
                    xpos -8
                    ypos text_size+13
                    idle cur_stat_icon
                    hover cur_stat_icon_active
                    action Function(current_companion.stat_upgrade, cur_stat)
            elif button_display == 'right':
                text "{size=[bar_text_size]}[cur_stat.value]/[cur_stat.max_value]{/size}" xalign 0.1 ypos (text_size+1)
                imagebutton:
                    xpos bar_xsize-8
                    ypos text_size+13
                    idle cur_stat_icon
                    hover cur_stat_icon_active
                    action Function(current_companion.stat_upgrade, cur_stat)

screen trait_block(trait):
    if trait.orientation == 'positive':
        $ mod = colour['green']
    elif trait.orientation == 'negative':
        $ mod = colour['red']
    $ buttontext = '{color=' + mod + '}{size=26}{u}' + trait.name + '{/u}{/size}{/color}'
    textbutton "[buttontext]":
        xsize 209
        ysize 76
        hovered Show("infobox", None, trait.get_trait_info(), "up")
        unhovered Hide("infobox")
        action NullAction()

# Досье персонажа
screen personage_stats(girl_id=0):
    frame:
        background Frame(im.MatrixColor("gui/frame.png", im.matrix.brightness(-1) * im.matrix.opacity(0.65)))
        xpos 10
        ypos 65
        padding (3, 3, 3, 3)
        vbox:
            xsize 620
            ysize 1000
            $ current_companion = g_base.girls.list[girl_id]
            $ stat_list = [current_companion.stat["service"], current_companion.stat["deception"], current_companion.stat["waitress"], current_companion.stat["classic"], current_companion.stat["finesse"], current_companion.stat["dancer"], current_companion.stat["anal"], current_companion.stat["power"], current_companion.stat["masseuse"], current_companion.stat["fetish"], current_companion.stat["magic"], current_companion.stat["geisha"]] # Характеристики текста и ползунков
            vbox:
                text "[current_companion.name]"
            # Отображение основных характеристик
            vbox:
                yalign 1.0
                grid 3 4:
                    for cur_stat in stat_list:
                        use stat_block(cur_stat, current_companion, button_display = 'stats')
            # Отображение черт персонажа
                hbox:
                    for trait in current_companion.traits:
                        use trait_block(trait)

    # Портрет
    use framed_image(current_companion.profile_image, arg_ypos=65, arg_xalign=0.5, arg_xmax=620, arg_ymax=875)

screen increment_stat(stat, companion):
    frame:
        xalign 0.5
        ypos 65
        xsize 620
        ysize 920
        python:
            parent_stat_1 = companion.stat[stat.parent_1_name]
            parent_stat_2 = companion.stat[stat.parent_2_name]
            parent_stat_1_exp = math.floor(parent_stat_1.exp)
            parent_stat_2_exp = math.floor(parent_stat_2.exp)
            stat_exp = parent_stat_1_exp+parent_stat_2_exp
            expcost = stat.upcost()
            expcost1 = parent_stat_1.upcost()
            expcost2 = parent_stat_2.upcost()
        vbox:
            xalign 0.5
            hbox:
                xalign 0.5
                vbox:
                    use stat_block(parent_stat_1, companion, button_display = 'left')
                    text "{size=23}Опыт: [parent_stat_1_exp]/[expcost1]{/size}":
                        xalign 0.5
                vbox:
                    use stat_block(parent_stat_2, companion, button_display = 'right')
                    text "{size=23}Опыт: [parent_stat_2_exp]/[expcost2]{/size}":
                        xalign 0.5
            vbox:
                xalign 0.5
                use stat_block(stat, companion, button_display = 'parents')
                text "{size=23}Опыт: [stat_exp]/[expcost]{/size}":
                    xalign 0.5

            text ''
            textbutton "Вернуться":
                action Hide("increment_stat")
