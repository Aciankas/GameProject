init:
    image gold_image = ("images/icons/gold.png")
    image red_light_night_bg = Transform("images/locations/scene_red_light_night.jpg", fit='contain', xsize = 1920, ysize = 1080)
    image nothing_bg = Transform("gui/Empty.png", fit='contain', xsize = 1920, ysize = 1080)
    image anim_example:
        "red_light_night_bg"
        "nothing_bg" with Dissolve(0.5)