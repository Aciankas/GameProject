init python:
    # Служебные функции для Ren`py:
    def hide_screens():
        user_screen_list = ["personage_screen", "personage_stats", "increment_stat", "resources", "main_hub"]
        for screen in user_screen_list:
            renpy.hide_screen(screen)
    
    def to_story(label):
        hide_screens()
        renpy.call('lock_label', label)

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

screen infobox(info='default', orientation='down'):
    frame:
        style "frame_thin_line"
        pos renpy.get_mouse_pos()
        if orientation == 'up':
            anchor (0.0, 1.0)
        elif orientation == 'down':
            anchor (0.0, 0.0)
        text "[info]"

screen resources:
    python:
        g_base_gold = math.floor(g_base.gold)
        res_menu_text_size = 26
    frame:
        style "frame_thin_line"
        xpos -10
        yalign 0
        xsize 1940
        ysize 50
        has hbox
        text ' '
        imagebutton:
            xsize 64
            ysize 64
            xpos -4
            ypos -10
            idle Transform(g_time.button_picture(), xysize = (64,64))
            action Function(g_time.next)
        image Transform("gold_image", fit='contain', xysize = (30,30))
        text "{size=[res_menu_text_size]}[g_base_gold]{/size}" ypos 0

screen main_hub:
    python:
        main_hub_menu_text_size = 26
    frame:
        style "frame_empty"
        xalign 0.5
        ypos 50
        xsize 1920
        ysize 1030
        has hbox
        textbutton "{size=[main_hub_menu_text_size]}Меню персонажей{/size}" action [Hide("main_hub"), Show("personage_screen")]
        textbutton "{size=[main_hub_menu_text_size]}Продолжить историю{/size}" action [Function(to_story, "prologue")]
        textbutton "{size=[main_hub_menu_text_size]}Проверка{/size}" action [ToggleScreen("the_test_screen")]

label main_hub_label:
    scene scene_tavern with dissolve
    show screen main_hub
    call screen resources