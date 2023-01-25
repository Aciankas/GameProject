init python:
    import renpy.store as store
    import renpy.exports as renpy
    from os import listdir
    from os.path import isfile, join
    import random

    def upcost(value):
        if value < 20:
            cost = 10
        elif value < 40:
            cost = 20
        elif value < 60:
            cost = 40
        elif value < 80:
            cost = 70
        elif value < 100:
            cost = 100
        elif value < 120:
            cost = 150
        elif value < 140:
            cost = 200
        else:
            cost = 250
        return cost

    stat_ru_name = {
        "Sex": "Секс",
        "Combat": "Бой",
        "Job": "Услуги",
        "Charm": "Очарование",
        "Grace": "Грация",
        "Strength": "Сила",
        "Erudition": "Эрудиция",
        "Service": "Ласки",
        "Classic": "Классика",
        "Anal": "Анал",
        "Fetish": "Фетиш",
        "Deception": "Уловки",
        "Finesse": "Искусность",
        "Power": "Мощь",
        "Magic": "Магия",
        "Waitress": "Официантка",
        "Dancer": "Танцовщица",
        "Masseuse": "Массажистка",
        "Geisha": "Гейша"
    }

    stat_system_name = {
        "Секс": "Sex",
        "Бой": "Combat",
        "Услуги": "Job",
        "Очарование": "Charm",
        "Грация": "Grace",
        "Сила": "Strength",
        "Эрудиция": "Erudition",
        "Ласки": "Service",
        "Классика": "Classic",
        "Анал": "Anal",
        "Фетиш": "Fetish",
        "Уловки": "Deception",
        "Искусность": "Finesse",
        "Мощь": "Power",
        "Магия": "Magic",
        "Официантка": "Waitress",
        "Танцовщица": "Dancer",
        "Массажистка": "Masseuse",
        "Гейша": "Geisha"
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
            if option in ('service', 'ласки'):
                if self.naughtiness >= 20:
                    return True
                else:
                    return False
            elif option in ('sex', 'classic', 'секс', 'классика'):
                if self.naughtiness >= 40:
                    return True
                else:
                    return False
            elif option in ('anal', 'анал'):
                if self.naughtiness >= 60:
                    return True
                else:
                    return False
            elif option in ('fetish', 'bdsm', 'фетиш', 'бдсм'):
                if self.naughtiness >= 80:
                    return True
                else:
                    return False
            else:
                return False

        def event(self, event, value=1, param='all'):
            #param: изменяемый параметр личности
            #value: коэффициент изменения
            #event: событие/модификаторы характера воздействия
            subevents       = event.split()
            multiplier_mod  = 1
            loyalty_mod     = 0
            discipline_mod  = 0
            mood_mod        = 0
            naughtiness_mod = 0
            print(subevents)
            for subevent in subevents:
                subevent = subevent.lower()
                if subevent in ('battle', 'бой'): #Миролюбие-Кровожадность
                    print(' check')
                    if self.has_trait('Кровожадность'):
                        mood_mod += 0.5
                        if self.affection_flag == 'discipline':
                            discipline_mod += 0.5
                    elif self.has_trait('Миролюбие'):
                        mood_mod += -0.5
                        if self.affection_flag == 'loyalty':
                            loyalty_mod += -0.5
                elif subevent in ('peace', 'мир'): #Миролюбие-Кровожадность
                    print(' check')
                    if self.has_trait('Кровожадность'):
                        mood_mod += -0.5
                        if self.affection_flag == 'discipline':
                            discipline_mod += -0.5
                    elif self.has_trait('Миролюбие'):
                        mood_mod += 0.5
                        if self.affection_flag == 'loyalty':
                            loyalty_mod += 0.5
                elif subevent in ('punishment', 'punish', 'discipline', 'наказание', 'муштра'): #Дисциплина-Свобода
                    print(' check')
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
                elif subevent in ('reward', 'поощрение', 'награда', 'похвала'): #Дисциплина-Свобода
                    print(' check')
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
                    print(' check')
                    if self.has_trait('Интроверсия'):
                        mood_mod       +=-0.25
                        multiplier_mod +=-0.25
                    elif self.has_trait('Экстраверсия'):
                        mood_mod       += 0.25
                        multiplier_mod += 0.25
                elif subevent in ('personal', 'личное', 'личная', 'личный'): #Интроверсия-Экстраверсия
                    print('личный check')
                    if self.has_trait('Интроверсия'):
                        mood_mod       += 0.25
                        multiplier_mod += 0.25
                    elif self.has_trait('Экстраверсия'):
                        mood_mod       +=-0.25
                        multiplier_mod +=-0.25
                elif subevent in ('lust', 'sex', 'секс', 'похоть'): #Раскованность-Скромность
                    print(' check')
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
                    print(' check')
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
                    print(' check')
                    if self.has_trait('Аскетизм'):
                        mood_mod       += 0.25
                        multiplier_mod += 0.25
                    elif self.has_trait('Гедонизм'):
                        mood_mod       +=-0.25
                        multiplier_mod +=-0.25
                elif subevent in ('hedonism', 'гедонизм', 'жадность', 'меркантильность'): #Аскетизм-Гедонизм
                    print(' check')
                    if self.has_trait('Аскетизм'):
                        multiplier_mod +=-0.25
                        mood_mod       +=-0.25
                    elif self.has_trait('Гедонизм'):
                        multiplier_mod += 0.25
                        mood_mod       += 0.25
                elif subevent in ('selfishness', 'selfish', 'эгоистичность', 'эгоистичный', 'эгоизм'): #Эгоистичность-Альтруистичность
                    print(' check')
                    if self.has_trait('Эгоистичность'):
                        multiplier_mod += 0.25
                        mood_mod       += 0.25
                    elif self.has_trait('Альтруистичность'):
                        multiplier_mod +=-0.25
                        mood_mod       +=-0.25
                elif subevent in ('altruism', 'altruistic', 'альтруистичность', 'альтруистичный', 'альтруизм'): #Эгоистичность-Альтруистичность
                    print(' check')
                    if self.has_trait('Эгоистичность'):
                        multiplier_mod +=-0.25
                        mood_mod       +=-0.25
                    elif self.has_trait('Альтруистичность'):
                        multiplier_mod += 0.25
                        mood_mod       += 0.25
                else:
                    pass

            print(multiplier_mod)
            print(loyalty_mod)
            print(discipline_mod)
            print(mood_mod)
            print(naughtiness_mod)

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
                print('picked_trait: '+str(picked_trait)+'; len(traits_not_in_list): '+str(len(traits_not_in_list))) #logging
                picked_orientation = random.randint(0,1)
                trait_list += [traits_not_in_list[picked_trait][picked_orientation]]
                traits_not_in_list.remove(traits_not_in_list[picked_trait])
            return trait_list

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
                result += '\n' + stat_ru_name[name] + ' '
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
                Trait("Нимфоманка",           "", {"Sex": ("exp_rate", 30)},                                   "positive"),
                Trait("Грамотные тренировки", "", {"Combat": ("exp_rate", 30)},                                "positive"),
                Trait("Гениальная служанка",  "", {"Job": ("exp_rate", 30)},                                   "positive"),
                Trait("Чуткая",               "", {"Charm": ("exp_rate", 35)},                                 "positive"),
                Trait("Природная гибкость",   "", {"Grace": ("exp_rate", 35)},                                 "positive"),
                Trait("Растущая мощь",        "", {"Strength": ("exp_rate", 35)},                              "positive"),
                Trait("Осознанная",           "", {"Erudition": ("exp_rate", 35)},                             "positive"),
                Trait("Чувствительная грудь", "", {"Charm": ("exp_rate", 18), "Sex": ("exp_rate", 18)},        "positive"),
                Trait("Карманница",           "", {"Charm": ("exp_rate", 18), "Combat": ("exp_rate", 18)},     "positive"),
                Trait("Быстрое обслуживание", "", {"Charm": ("exp_rate", 18), "Job": ("exp_rate", 18)},        "positive"),
                Trait("Податливая",           "", {"Grace": ("exp_rate", 18), "Sex": ("exp_rate", 18)},        "positive"),
                Trait("Уроки охоты",          "", {"Grace": ("exp_rate", 18), "Combat": ("exp_rate", 18)},     "positive"),
                Trait("Чувство ритма",        "", {"Grace": ("exp_rate", 18), "Job": ("exp_rate", 18)},        "positive"),
                Trait("Пышные формы",         "", {"Strength": ("exp_rate", 18), "Sex": ("exp_rate", 18)},     "positive"),
                Trait("Развитые мышцы",       "", {"Strength": ("exp_rate", 18), "Combat": ("exp_rate", 18)},  "positive"),
                Trait("Знание анатомии",      "", {"Strength": ("exp_rate", 18), "Job": ("exp_rate", 18)},     "positive"),
                Trait("Любительница нового",  "", {"Erudition": ("exp_rate", 18), "Sex": ("exp_rate", 18)},    "positive"),
                Trait("Тайны магии",          "", {"Erudition": ("exp_rate", 18), "Combat": ("exp_rate", 18)}, "positive"),
                Trait("Умелый собеседник",    "", {"Erudition": ("exp_rate", 18), "Job": ("exp_rate", 18)},    "positive"),

                Trait("Ночь напролёт",       "", {"Sex": ("max_value", 20), "Service": ("max_value", 20), "Classic": ("max_value", 20), "Anal": ("max_value", 20), "Fetish": ("max_value", 20)},      "positive"),
                Trait("Боевой раж",          "", {"Combat": ("max_value", 20), "Deception": ("max_value", 20), "Finesse": ("max_value", 20), "Power": ("max_value", 20), "Magic": ("max_value", 20)}, "positive"),
                Trait("Семейное дело",       "", {"Job": ("max_value", 20), "Waitress": ("max_value", 20), "Dancer": ("max_value", 20), "Masseuse": ("max_value", 20), "Geisha": ("max_value", 20)},  "positive"),
                Trait("Живая мимика",        "", {"Charm": ("max_value", 30), "Service": ("max_value", 30), "Deception": ("max_value", 30), "Waitress": ("max_value", 30)},                           "positive"),
                Trait("Идеальная фигура",    "", {"Grace": ("max_value", 30), "Classic": ("max_value", 30), "Finesse": ("max_value", 30), "Dancer": ("max_value", 30)},                               "positive"),
                Trait("Природная мощь",      "", {"Strength": ("max_value", 30), "Anal": ("max_value", 30), "Power": ("max_value", 30), "Masseuse": ("max_value", 30)},                               "positive"),
                Trait("Пытливый ум",         "", {"Erudition": ("max_value", 30), "Fetish": ("max_value", 30), "Magic": ("max_value", 30), "Geisha": ("max_value", 30)},                              "positive"),
                Trait("Глубокий поцелуй",    "", {"Service": ("max_value", 70)},   "positive"),
                Trait("Невидимка",           "", {"Deception": ("max_value", 70)}, "positive"),
                Trait("Марафонец",           "", {"Waitress": ("max_value", 70)},  "positive"),
                Trait("Возбуждающие изгибы", "", {"Classic": ("max_value", 70)},   "positive"),
                Trait("Зоркий глаз",         "", {"Finesse": ("max_value", 70)},   "positive"),
                Trait("Танцевальный азарт",  "", {"Dancer": ("max_value", 70)},    "positive"),
                Trait("Крепкий орешек",      "", {"Anal": ("max_value", 70)},      "positive"),
                Trait("Безграничная сила",   "", {"Power": ("max_value", 70)},     "positive"),
                Trait("Сильные руки",        "", {"Masseuse": ("max_value", 70)},  "positive"),
                Trait("Богатая фантазия",    "", {"Fetish": ("max_value", 70)},    "positive"),
                Trait("Духовная стойкость",  "", {"Magic": ("max_value", 70)},     "positive"),
                Trait("Эрудиция",            "", {"Geisha": ("max_value", 70)},    "positive"),

                Trait("Развратница",          "", {"Service": ("modifier", 1), "Classic": ("modifier", 1), "Anal": ("modifier", 1), "Fetish": ("modifier", 1)},     "positive"),
                Trait("Прирождённый боец",    "", {"Deception": ("modifier", 1), "Finesse": ("modifier", 1), "Power": ("modifier", 1), "Magic": ("modifier", 1)},   "positive"),
                Trait("Лояльная",             "", {"Waitress": ("modifier", 1), "Dancer": ("modifier", 1), "Masseuse": ("modifier", 1), "Geisha": ("modifier", 1)}, "positive"),
                Trait("Обольстительница",     "", {"Service": ("modifier", 2), "Deception": ("modifier", 2), "Waitress": ("modifier", 2)},                          "positive"),
                Trait("Изящество",            "", {"Classic": ("modifier", 2), "Finesse": ("modifier", 2), "Dancer": ("modifier", 2)},                              "positive"),
                Trait("Подавляющая",          "", {"Anal": ("modifier", 2), "Power": ("modifier", 2), "Masseuse": ("modifier", 2)},                                 "positive"),
                Trait("Гуру",                 "", {"Fetish": ("modifier", 2), "Magic": ("modifier", 2), "Geisha": ("modifier", 2)},                                 "positive"),
                Trait("Мягкие губы",          "", {"Service": ("modifier", 3)},   "positive"),
                Trait("Амбидекстр",           "", {"Deception": ("modifier", 3)}, "positive"),
                Trait("Боковое зрение",       "", {"Waitress": ("modifier", 3)},  "positive"),
                Trait("Влажные губы",         "", {"Classic": ("modifier", 3)},   "positive"),
                Trait("Следопыт",             "", {"Finesse": ("modifier", 3)},   "positive"),
                Trait("Кураж",                "", {"Dancer": ("modifier", 3)},    "positive"),
                Trait("Притягательные бёдра", "", {"Anal": ("modifier", 3)},      "positive"),
                Trait("Берсерк",              "", {"Power": ("modifier", 3)},     "positive"),
                Trait("Расслабляющие обряды", "", {"Masseuse": ("modifier", 3)},  "positive"),
                Trait("Раскрепощенная",       "", {"Fetish": ("modifier", 3)},    "positive"),
                Trait("Гибкая энергия",       "", {"Magic": ("modifier", 3)},     "positive"),
                Trait("Мечтательница",        "", {"Geisha": ("modifier", 3)},    "positive"),


                Trait("Фригидная",        "", {"Sex": ("exp_rate", -30)},       "negative"),
                Trait("Растерянность",    "", {"Combat": ("exp_rate", -30)},    "negative"),
                Trait("Ленивая",          "", {"Job": ("exp_rate", -30)},       "negative"),
                Trait("Чёрствая",         "", {"Charm": ("exp_rate", -35)},     "negative"),
                Trait("Деревянная",       "", {"Grace": ("exp_rate", -35)},     "negative"),
                Trait("Болезненная",      "", {"Strength": ("exp_rate", -35)},  "negative"),
                Trait("Забывчивая",       "", {"Erudition": ("exp_rate", -35)}, "negative"),
                Trait("Консерватор",      "", {"Charm": ("exp_rate", -18), "Sex": ("exp_rate", -18)},       "negative"),
                Trait("TEMPORARY_2_2_3",  "", {"Charm": ("exp_rate", -18), "Combat": ("exp_rate", -18)},    "negative"),
                Trait("Халатность",       "", {"Charm": ("exp_rate", -18), "Job": ("exp_rate", -18)},       "negative"),
                Trait("Бревно",           "", {"Grace": ("exp_rate", -18), "Sex": ("exp_rate", -18)},       "negative"),
                Trait("Неустойчивость",   "", {"Grace": ("exp_rate", -18), "Combat": ("exp_rate", -18)},    "negative"),
                Trait("Замкнутая",        "", {"Grace": ("exp_rate", -18), "Job": ("exp_rate", -18)},       "negative"),
                Trait("Неприступная",     "", {"Strength": ("exp_rate", -18), "Sex": ("exp_rate", -18)},    "negative"),
                Trait("TEMPORARY_2_4_3",  "", {"Strength": ("exp_rate", -18), "Combat": ("exp_rate", -18)}, "negative"),
                Trait("TEMPORARY_2_4_4",  "", {"Strength": ("exp_rate", -18), "Job": ("exp_rate", -18)},    "negative"),
                Trait("Ханжа",            "", {"Erudition": ("exp_rate", -18), "Sex": ("exp_rate", -18)},   "negative"),
                Trait("Неуравновешенная", "", {"Erudition": ("exp_rate", -18), "Combat": ("exp_rate", -18)},"negative"),
                Trait("Тугодум",          "", {"Erudition": ("exp_rate", -18), "Job": ("exp_rate", -18)},   "negative"),

                Trait("Аногразмия",              "", {"Sex": ("max_value", -20), "Service": ("max_value", -20), "Classic": ("max_value", -20), "Anal": ("max_value", -20), "Fetish": ("max_value", -20)},      "negative"),
                Trait("Трусость",                "", {"Combat": ("max_value", -20), "Deception": ("max_value", -20), "Finesse": ("max_value", -20), "Power": ("max_value", -20), "Magic": ("max_value", -20)}, "negative"),
                Trait("Растяпа",                 "", {"Job": ("max_value", -20), "Waitress": ("max_value", -20), "Dancer": ("max_value", -20), "Masseuse": ("max_value", -20), "Geisha": ("max_value", -20)},  "negative"),
                Trait("Грубая",                  "", {"Charm": ("max_value", -30), "Service": ("max_value", -30), "Deception": ("max_value", -30), "Waitress": ("max_value", -30)}, "negative"),
                Trait("Неуклюжая",               "", {"Grace": ("max_value", -30), "Classic": ("max_value", -30), "Finesse": ("max_value", -30), "Dancer": ("max_value", -30)},     "negative"),
                Trait("Немощная",                "", {"Strength": ("max_value", -30), "Anal": ("max_value", -30), "Power": ("max_value", -30), "Masseuse": ("max_value", -30)},     "negative"),
                Trait("Легкомысленная",          "", {"Erudition": ("max_value", -30), "Fetish": ("max_value", -30), "Magic": ("max_value", -30), "Geisha": ("max_value", -30)},    "negative"),
                Trait("Слабая чувствительность", "", {"Service": ("max_value", -70)},   "negative"),
                Trait("TEMPORARY_4_2_3",         "", {"Deception": ("max_value", -70)}, "negative"),
                Trait("TEMPORARY_4_2_4",         "", {"Waitress": ("max_value", -70)},  "negative"),
                Trait("Мимолетное возбуждение",  "", {"Classic": ("max_value", -70)},   "negative"),
                Trait("Хромая",                  "", {"Finesse": ("max_value", -70)},   "negative"),
                Trait("TEMPORARY_4_3_4",         "", {"Dancer": ("max_value", -70)},    "negative"),
                Trait("TEMPORARY_4_4_2",         "", {"Anal": ("max_value", -70)},      "negative"),
                Trait("Хилая",                   "", {"Power": ("max_value", -70)},     "negative"),
                Trait("TEMPORARY_4_4_4",         "", {"Masseuse": ("max_value", -70)},  "negative"),
                Trait("TEMPORARY_4_5_2",         "", {"Fetish": ("max_value", -70)},    "negative"),
                Trait("Рассеяная",               "", {"Magic": ("max_value", -70)},     "negative"),
                Trait("Сонный голос",            "", {"Geisha": ("max_value", -70)},    "negative"),

                Trait("Стеснительная",       "", {"Service": ("modifier", -1), "Classic": ("modifier", -1), "Anal": ("modifier", -1), "Fetish": ("modifier", -1)},     "negative"),
                Trait("Пацифист",            "", {"Deception": ("modifier", -1), "Finesse": ("modifier", -1), "Power": ("modifier", -1), "Magic": ("modifier", -1)},   "negative"),
                Trait("Неряха",              "", {"Waitress": ("modifier", -1), "Dancer": ("modifier", -1), "Masseuse": ("modifier", -1), "Geisha": ("modifier", -1)}, "negative"),
                Trait("Медлительная",        "", {"Service": ("modifier", -2), "Deception": ("modifier", -2), "Waitress": ("modifier", -2)},                           "negative"),
                Trait("Нелепая",             "", {"Classic": ("modifier", -2), "Finesse": ("modifier", -2), "Dancer": ("modifier", -2)},                               "negative"),
                Trait("Слабая",              "", {"Anal": ("modifier", -2), "Power": ("modifier", -2), "Masseuse": ("modifier", -2)},                                  "negative"),
                Trait("Простачка",           "", {"Fetish": ("modifier", -2), "Magic": ("modifier", -2), "Geisha": ("modifier", -2)},                                  "negative"),
                Trait("TEMPORARY_6_2_2",     "", {"Service": ("modifier", -3)},   "negative"),
                Trait("TEMPORARY_6_2_3",     "", {"Deception": ("modifier", -3)}, "negative"),
                Trait("TEMPORARY_6_2_4",     "", {"Waitress": ("modifier", -3)},  "negative"),
                Trait("TEMPORARY_6_3_2",     "", {"Classic": ("modifier", -3)},   "negative"),
                Trait("Одноглазая",          "", {"Finesse": ("modifier", -3)},   "negative"),
                Trait("TEMPORARY_6_3_4",     "", {"Dancer": ("modifier", -3)},    "negative"),
                Trait("TEMPORARY_6_4_2",     "", {"Anal": ("modifier", -3)},      "negative"),
                Trait("TEMPORARY_6_4_3",     "", {"Power": ("modifier", -3)},     "negative"),
                Trait("TEMPORARY_6_4_4",     "", {"Masseuse": ("modifier", -3)},  "negative"),
                Trait("Скованная",           "", {"Fetish": ("modifier", -3)},    "negative"),
                Trait("Безумная",            "", {"Magic": ("modifier", -3)},     "negative"),
                Trait("Плохая дикция",       "", {"Geisha": ("modifier", -3)},    "negative")
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

    class Personage(store.object):
        def __init__(self, name='default', pic_directory = 'default', traits = [],
        base_sex=0, base_combat=0, base_job=0, base_charm=0, base_grace=0, base_strength=0, base_erudition=0,
        sec_service=0, sec_classic=0, sec_anal=0, sec_fetish=0, sec_deception=0, sec_finesse=0, sec_power=0, sec_magic=0, sec_waitress=0, sec_dancer=0, sec_masseuse=0, sec_geisha=0,
        base_sex_exp=0, base_combat_exp=0, base_job_exp=0, base_charm_exp=0, base_grace_exp=0, base_strength_exp=0, base_erudition_exp=0
        ):
            self.name = name
            self.pic_directory = pic_directory
            self.profile_image = self.picture('profile')

            # Характеристики
            self.stat = {
                "Sex"       : Stat(name="Секс",        eng_name="Sex"       ,value=base_sex,       max_value=100, modifier=None, exp=base_sex_exp,      exp_rate=1,    parent_1_name="Sex",       parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Combat"    : Stat(name="Бой",         eng_name="Combat"    ,value=base_combat,    max_value=100, modifier=None, exp=base_combat_exp,   exp_rate=1,    parent_1_name="Combat",    parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Job"       : Stat(name="Услуги",      eng_name="Job"       ,value=base_job,       max_value=100, modifier=None, exp=base_job_exp,      exp_rate=1,    parent_1_name="Job",       parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Charm"     : Stat(name="Очарование",  eng_name="Charm"     ,value=base_charm,     max_value=100, modifier=None, exp=base_charm_exp,    exp_rate=1,    parent_1_name="Charm",     parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Grace"     : Stat(name="Грация",      eng_name="Grace"     ,value=base_grace,     max_value=100, modifier=None, exp=base_grace_exp,    exp_rate=1,    parent_1_name="Grace",     parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Strength"  : Stat(name="Сила",        eng_name="Strength"  ,value=base_strength,  max_value=100, modifier=None, exp=base_strength_exp, exp_rate=1,    parent_1_name="Strength",  parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Erudition" : Stat(name="Эрудиция",    eng_name="Erudition" ,value=base_erudition, max_value=100, modifier=None, exp=base_erudition_exp,exp_rate=1,    parent_1_name="Erudition", parent_2_name=None,     bar_texture="dynamic", icon=""),
                "Service"   : Stat(name="Ласки",       eng_name="Service"   ,value=sec_service,    max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Charm",     parent_2_name="Sex",    bar_texture="dynamic", icon="service"),
                "Deception" : Stat(name="Уловки",      eng_name="Deception" ,value=sec_deception,  max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Charm",     parent_2_name="Combat", bar_texture="dynamic", icon="rogue"),
                "Waitress"  : Stat(name="Официантка",  eng_name="Waitress"  ,value=sec_waitress,   max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Charm",     parent_2_name="Job",    bar_texture="dynamic", icon="waitress"),
                "Classic"   : Stat(name="Классика",    eng_name="Classic"   ,value=sec_classic,    max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Grace",     parent_2_name="Sex",    bar_texture="dynamic", icon="sex"),
                "Finesse"   : Stat(name="Искусность",  eng_name="Finesse"   ,value=sec_finesse,    max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Grace",     parent_2_name="Combat", bar_texture="dynamic", icon="archer"),
                "Dancer"    : Stat(name="Танцовщица",  eng_name="Dancer"    ,value=sec_dancer,     max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Grace",     parent_2_name="Job",    bar_texture="dynamic", icon="dancer"),
                "Anal"      : Stat(name="Анал",        eng_name="Anal"      ,value=sec_anal,       max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Strength",  parent_2_name="Sex",    bar_texture="dynamic", icon="anal"),
                "Power"     : Stat(name="Мощь",        eng_name="Power"     ,value=sec_power,      max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Strength",  parent_2_name="Combat", bar_texture="dynamic", icon="warrior"),
                "Masseuse"  : Stat(name="Массажистка", eng_name="Masseuse"  ,value=sec_masseuse,   max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Strength",  parent_2_name="Job",    bar_texture="dynamic", icon="masseuse"),
                "Fetish"    : Stat(name="Фетиш",       eng_name="Fetish"    ,value=sec_fetish,     max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Erudition", parent_2_name="Sex",    bar_texture="dynamic", icon="fetish"),
                "Magic"     : Stat(name="Магия",       eng_name="Magic"     ,value=sec_magic,      max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Erudition", parent_2_name="Combat", bar_texture="dynamic", icon="mage"),
                "Geisha"    : Stat(name="Гейша",       eng_name="Geisha"    ,value=sec_geisha,     max_value=100, modifier=0,    exp=None,              exp_rate=None, parent_1_name="Erudition", parent_2_name="Job",    bar_texture="dynamic", icon="geisha")
            }

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

        def is_stat_upgradable(self, stat): #Можно ли улучшить конкретную характеристику
            main_stat_higher_flag = True #Выше ли доп статы основная?
            if stat.parent_2_name is None:
                cur_exp = stat.exp
            else:
                parent_stat_1 = self.stat[stat.parent_1_name]
                parent_stat_2 = self.stat[stat.parent_2_name]
                cur_exp = parent_stat_1.exp + parent_stat_2.exp
                if (float(stat.value)/float(stat.max_value) >= float(parent_stat_1.value)/float(parent_stat_1.max_value)) or (float(stat.value)/float(stat.max_value) >= float(parent_stat_2.value)/float(parent_stat_2.max_value)): #Процентно ниже ли доп стата основных, от которых зависит?
                    main_stat_higher_flag = False
            if (stat.value<stat.max_value) and (cur_exp >= upcost(stat.value)) and main_stat_higher_flag:
                return True
            else:
                return False

        def change_exp(self, stat, value):
            if type(stat) is str:
                self.stat[stat].exp += value
            elif type(stat) is Stat:
                stat.exp += value

        def stat_upgrade(self, stat, mode=0): #mode - какую характеристику использовать первой при апгрейде. 0 - Очарование, Грация, Сила, Эрудиция; Другое - Секс, Бой, Услуги
            if self.is_stat_upgradable(stat):
                # Расчёт расхода экспы
                expense_exp = upcost(stat.value)
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
                path = "../Project/The Ascension of Susan/game/images/Girls/" + self.pic_directory
            pic_list = os.listdir(path)
            result_list = []
            for title in titles:
                for pic in pic_list:
                    if title in pic:
                        result_list.append(pic)
                if len(result_list) != 0:
                    break
            result = "images/Girls/" + self.pic_directory + "/" + str(result_list[random.randint(0,len(result_list)-1)])
            return result

        def make_profile_image(self):
            self.profile_image = self.picture('profile')

    class Personage_List (store.object):
        def __init__(self):
            self.list = []

        def add(self, personage):
            self.list.append(personage)

        def remove(self, personage):
            self.list.remove(personage)

        def make_profile_image(self):
            for character in self.list:
                character.make_profile_image()

    class Sexual_Interaction (store.object):
        def __init__(self):
            pass

screen personage_screen:
    frame:
        background Frame(im.MatrixColor("gui/frame.png", im.matrix.brightness(-1) * im.matrix.opacity(0.65)))
        xpos 1290
        ypos 20
        padding (3, 3, 3, 3)
        vbox:
            xsize 620
            ysize 1000
            for companion_iterator in range(1,len(companions.list)):
                hbox:
                    $ displayed_name = companions.list[companion_iterator].name
                    textbutton "[displayed_name]" action Show("personage_stats", None, companion_iterator)
            textbutton "Вернуться" action Return()

label personage_screen_label:
    $ companions.make_profile_image()
    call screen personage_screen
    return

style textstat:
    color colour['neutral']

screen infobox(info='default', orientation='down'):
    frame:
        style "frame_thin_line"
        pos renpy.get_mouse_pos()
        if orientation == 'up':
            anchor (0.0, 1.0)
        elif orientation == 'down':
            anchor (0.0, 0.0)
        text "[info]"

# Отображение блока характеристики
screen stat_block(cur_stat, current_companion, button_display='observe'):
    $ bar_xsize = 200
    $ bar_ysize = 20
    $ text_size = 24
    $ bar_text_size = bar_ysize-3
    $ cur_stat_colour = current_companion.get_stat_color(cur_stat)
    $ cur_bar_texture = cur_stat.get_bar_texture()
    fixed:
        xmaximum bar_xsize+10
        ymaximum bar_ysize+text_size+5
        text "{color=[cur_stat_colour]}{size=[text_size]}[cur_stat.name]{/size}{/color}" xalign 0.5
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

# Изображение в рамке
screen framed_image(pic_path, arg_xalign=None, arg_yalign=None, arg_xpos=None, arg_ypos=None, arg_xmax=None, arg_ymax=None, arg_xsize=None, arg_ysize=None):
    frame:
        style "frame_empty"
        xalign arg_xalign
        yalign arg_yalign
        python:
            arg_xpadding = 16
            arg_ypadding = 16
            if arg_xmax is None and arg_xsize is None:
                pic_xsize = 150
            elif arg_xmax is not None:
                arg_xsize = None
                pic_xsize = arg_xmax-arg_xpadding
            else:
                pic_xsize = arg_xsize-arg_xpadding
            if arg_ymax is None and arg_ysize is None:
                pic_ysize = 300
            elif arg_ymax is not None:
                arg_ysize = None
                pic_ysize = arg_ymax-arg_ypadding
            else:
                pic_ysize = arg_ysize-arg_ypadding
        frame:
            xpos arg_xpos
            ypos arg_ypos
            xmaximum arg_xmax
            ymaximum arg_ymax
            xsize arg_xsize
            ysize arg_ysize
            padding (arg_xpadding, arg_ypadding)
            foreground Frame("gui/frame_corner_background.png", 68, 68, 68, 68, tile=True)
            background None
            image Transform(pic_path, fit='contain', xysize = (pic_xsize,pic_ysize))

# Досье персонажа
screen personage_stats(companion_id=0):
    frame:
        background Frame(im.MatrixColor("gui/frame.png", im.matrix.brightness(-1) * im.matrix.opacity(0.65)))
        xpos 10
        ypos 20
        padding (3, 3, 3, 3)
        vbox:
            xsize 620
            ysize 1000
            $ current_companion = companions.list[companion_id]
            $ stat_list = [current_companion.stat["Service"], current_companion.stat["Deception"], current_companion.stat["Waitress"], current_companion.stat["Classic"], current_companion.stat["Finesse"], current_companion.stat["Dancer"], current_companion.stat["Anal"], current_companion.stat["Power"], current_companion.stat["Masseuse"], current_companion.stat["Fetish"], current_companion.stat["Magic"], current_companion.stat["Geisha"]] # Характеристики текста и ползунков
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
    use framed_image(current_companion.profile_image, arg_ypos=20, arg_xalign=0.5, arg_xmax=620, arg_ymax=920)

screen increment_stat(stat, companion):
    frame:
        xalign 0.5
        ypos 20
        xsize 620
        ysize 920
        $ parent_stat_1 = companion.stat[stat.parent_1_name]
        $ parent_stat_2 = companion.stat[stat.parent_2_name]
        $ stat_exp = parent_stat_1.exp+parent_stat_2.exp
        $ expcost = upcost(stat.value)
        $ expcost1 = upcost(parent_stat_1.value)
        $ expcost2 = upcost(parent_stat_2.value)
        vbox:
            xalign 0.5
            hbox:
                xalign 0.5
                vbox:
                    use stat_block(parent_stat_1, companion, button_display = 'left')
                    text "{size=23}Опыт: [parent_stat_1.exp]/[expcost1]{/size}":
                        xalign 0.5
                vbox:
                    use stat_block(parent_stat_2, companion, button_display = 'right')
                    text "{size=23}Опыт: [parent_stat_2.exp]/[expcost2]{/size}":
                        xalign 0.5
            vbox:
                xalign 0.5
                use stat_block(stat, companion, button_display = 'parents')
                text "{size=23}Опыт: [stat_exp]/[expcost]{/size}":
                    xalign 0.5

            text ''
            textbutton "Вернуться":
                action Hide("increment_stat")
