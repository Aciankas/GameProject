# Определение персонажей игры.
define susan = Character('Сьюзан', color="#ffc8c9", image = "susan")
define father = Character('Отец', color="#CDE0FF")
define elmir = Character('Эльмир', color = "#2525B0")

image side susan = Transform("images/characters/susan side.png", fit='contain', xysize = (350,350))

label strt:
    menu:
        "Пропустить пролог?"
        "Нет":
            jump prologue
        "Да":
            jump chapter_1
        "Params test":
            jump personage_screen_label
