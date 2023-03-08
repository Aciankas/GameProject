init python:
    # Служебные функции для Ren`py:
    def hide_screens():
        user_screen_list = ["personage_screen", "personage_stats", "increment_stat", "resources", "main_hub"]
        for screen in user_screen_list:
            renpy.hide_screen(screen)
    
    def to_story(label):
        hide_screens()
        renpy.call('lock_label', label)

# Экран пропуска экранов
screen skip_screen:
    key config.keymap["skip"]+["game_menu", ' ', 'K_KP_ENTER'] action Return()
    imagebutton:
        xsize 1920
        ysize 1080
        idle "gui/Empty.png"
        action Return()


# Экран кубика
screen dice_screen(p_dice, p_xpos, p_ypos, p_size):
    python:
        l_font = g_num_font_bold
        l_text_size = p_size//2-1
        l_text_color = colour["basic_gold"]
    frame:
        style "frame_empty"
        xpos p_xpos
        ypos p_ypos
        xsize p_size
        ysize p_size*3//2
        image Transform(p_dice.picture, xysize = (p_size, p_size))
        text "{font=[l_font]}{color=[l_text_color]}{size=[l_text_size]}d[p_dice.max_value]{/size}{/color}{/font}" xpos p_size ypos 0
        text "{font=[l_font]}{color=[p_dice.color]}{size=[l_text_size]}  [p_dice.roll]{/size}{/color}{/font}" xpos p_size ypos l_text_size+1

# Изображение в рамке
screen framed_image(pic_path, p_xalign=None, p_yalign=None, p_xpos=None, p_ypos=None, p_xmax=None, p_ymax=None, p_xsize=None, p_ysize=None, p_xpadding = 16, p_ypadding = 16):
    frame:
        style "frame_empty"
        xalign p_xalign
        yalign p_yalign
        python:
            if p_xmax is None and p_xsize is None:
                pic_xsize = 150
            elif p_xmax is not None:
                p_xsize = None
                pic_xsize = p_xmax-p_xpadding*2
            else:
                pic_xsize = p_xsize-p_xpadding*2
            if p_ymax is None and p_ysize is None:
                pic_ysize = 300
            elif p_ymax is not None:
                p_ysize = None
                pic_ysize = p_ymax-p_ypadding*2
            else:
                pic_ysize = p_ysize-p_ypadding*2
        frame:
            xpos p_xpos
            ypos p_ypos
            xmaximum p_xmax
            ymaximum p_ymax
            xsize p_xsize
            ysize p_ysize
            padding (p_xpadding, p_ypadding)
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
        l_font = g_num_font_bold
        g_base_gold = math.floor(g_base.gold)
        res_menu_text_size = 20
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
        text "{font=[l_font]}{size=[res_menu_text_size]} [g_base_gold] {/size}{/font}" ypos 3

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