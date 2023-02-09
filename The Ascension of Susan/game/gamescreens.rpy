screen resource_ui:
    frame:
        has hbox
        add "gold_image"
        text " [g_resourses._gold] "
        textbutton "Меню" action ui.callsinnewcontext("test_menu_label")

screen test_menu:
    frame:
        has vbox
        text "Пункт 1"
        text "Пункт 2"
        text "Пункт 3"
        textbutton "Вернуться" action Return()

label test_menu_label:
    call screen test_menu
    return


label screen_test_label:
    call screen screen_test
    return

screen screen_test:
    frame:
        xpos 100
        ypos 100
        xsize 1000
        ysize 800
        background Frame("images/icons/windowset.png", 40, 40, 40, 40, tile=True) 
