# Вы можете расположить сценарий своей игры в этом файле.

# Вместо использования оператора image можете просто
# складывать все ваши файлы изображений в папку images.
# Например, сцену bg room можно вызвать файлом "bg room.png",
# а eileen happy — "eileen happy.webp", и тогда они появятся в игре.

# Игра начинается здесь:
label start:
    $ gold = 250
    $ companions = Personage_List()
    $ companions.add(Personage('Susan', pic_directory = 'Susan', base_sex_exp=1000, base_combat_exp=500, base_job_exp=300, base_charm_exp=700, base_grace_exp=900, base_strength_exp=800, base_erudition_exp=200))
    $ companions.add(Personage('Angelise', pic_directory = 'Angelise'))
    $ companions.add(Personage('Empty', pic_directory = 'Empty'))
    scene forest with dissolve
    "Начало"
    jump strt
    return
