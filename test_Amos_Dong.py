import random
import os
import math
import pygame as pg

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# SCREENRECT = pg.Rect(0, 0, 640, 480)
SCREENRECT = pg.Rect(0, 0, 1200, 480)
SizePlayerImage = [64, 64]
SCORE = 0

instances_platform = []
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()

def load_sound(file):
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None

def e_dst(coord_a, coord_b):
    return math.sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)

def touched(coord, box):
    return True if box[0][0] <= coord[0] and coord[0] <= box[1][0] and box[0][1] <= coord[1] and coord[1] <= box[1][1] else False 

class Player(pg.sprite.Sprite):   

    images = []  # class static variable!

    def __init__(self):   # instance variable!
        pg.sprite.Sprite.__init__(self, self.containers)
        self.dir = 0  # 0 upwards    1 to left    2 downwards    3 to right
        self.image = self.assignImage(self.images[0])
        # self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.rect = pg.Rect(160, 250, 64, 64)
        
        self.point_bottom = [self.rect[0]+20, self.rect[1]+64]
        self.point_top = self.point_bottom[:]

    def assignImage(self, image):
        return pg.transform.rotate(image, self.dir * 90)

    def getNewRect(self, coord_bottom):   
        if self.dir == 0:
            bias_x, bias_y = -20, -64
        elif self.dir == 1:
            bias_x, bias_y = -64, -64
        elif self.dir == 2:
            bias_x, bias_y = -64, -20
        elif self.dir == 3:
            bias_x, bias_y = 0, 0
        return pg.Rect(coord_bottom[0]+bias_x, coord_bottom[1]+bias_y, SizePlayerImage[0], SizePlayerImage[1])

    # def platformDirection(self, box): # 0 horizontal   1 vertical
    #     tmp = [box[0][0] - box[1][0], box[0][1] - box[1][1]]
    #     return 0 if abs(tmp[0]) > abs(tmp[1]) else 1
        

    def drag(self, coord_mouse):
        dst_MouseToTop = e_dst(self.point_top, coord_mouse)
        if dst_MouseToTop > 20:  # if the mouse was too far from the top-end, then the slinky couldn't be dragged
            return
        x, y = coord_mouse[0] - self.point_bottom[0], self.point_bottom[1] - coord_mouse[1]
        relative_distance = abs(x) + abs(y)
        if relative_distance > 100:  # get the top-end back
            self.point_top = self.point_bottom[:]
            # TODO Apply the animation of slinky getting back
        else:
            self.point_top = coord_mouse[:]
            # self.trace.append(self.point_top[:])
            # if len(self.trace) > 2:
            #     self.trace.pop(0)
            # TODO Apply the image according to (x, y)   which is the relative distance
            self.image = self.assignImage(self.images[min(abs(x)//3, 11)])
            for p in instances_platform:
                for i in range(len(p.boxes)):
                    if touched(self.point_top, p.boxes[i]):
                        self.dir = p.dir_boxes[i]
                        self.land(self.point_top)
        
    def land(self, coord_land):
        print("Slinky lands on a new point!")
        self.rect = self.getNewRect(coord_land)
        self.point_bottom = self.point_top[:]
        # TODO Apply the animation of slinky getting back
        

        
        
        

class Platform(pg.sprite.Sprite):
    images = []
    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.boxes = []
        self.dir_boxes = []  # 0 upwards    1 to left    2 downwards    3 to right
        # self.rect.move_ip(random.randrange(100, 400), random.randrange(100, 400))    


pg.init()
# Set the display mode
winstyle = 0  # |FULLSCREEN
bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)


def main(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    imagefiles_slinky = []
    for ind in range(1, 22):
        imagefiles_slinky.append("Slinky_21\Slinky_21_" + str(ind) + ".jpeg")
    Player.images = [load_image(im) for im in imagefiles_slinky]
    Platform.images = [load_image(im) for im in ["danger.gif", "danger_.gif"]]

    # decorate the game window
    # icon = pg.transform.scale(Alien.images[0], (32, 32))
    # pg.display.set_icon(icon)
    pg.display.set_caption("Slinky Game")

    # create the background, tile the bgd image
    bgdtile = load_image("background.gif")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    if pg.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    # Initialize Game Groups
    platforms = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()

    # assign default groups to each sprite class
    Player.containers = all
    Platform.containers = platforms, all

    # Create Some Starting Values
    clock = pg.time.Clock()

    # initialize our starting sprites
    player = Player()
    
    for _ in range(3):
        instances_platform.append(Platform()) 
    w = 260
    h = 70
    thickness = 10

    left_top = [80, 80]
    index = 0
    instances_platform[index].rect = pg.Rect(left_top[0], left_top[1], w, h)
    instances_platform[index].boxes.append([[left_top[0], left_top[1]], [left_top[0]+w, left_top[1]+thickness]])
    instances_platform[index].boxes.append([[left_top[0], left_top[1]+h], [left_top[0]+w, left_top[1]+h+thickness]])
    instances_platform[index].boxes.append([[left_top[0], left_top[1]], [left_top[0]+thickness, left_top[1]+h]])
    instances_platform[index].boxes.append([[left_top[0]+w, left_top[1]], [left_top[0]+w+thickness, left_top[1]+h]])
    instances_platform[index].dir_boxes = [0, 2, 1, 3]

    left_top = [80, 300]
    index = 1
    instances_platform[index].rect = pg.Rect(left_top[0], left_top[1], w, h)
    instances_platform[index].boxes.append([[left_top[0], left_top[1]], [left_top[0]+w, left_top[1]+thickness]])
    instances_platform[index].boxes.append([[left_top[0], left_top[1]+h], [left_top[0]+w, left_top[1]+h+thickness]])
    instances_platform[index].boxes.append([[left_top[0], left_top[1]], [left_top[0]+thickness, left_top[1]+h]])
    instances_platform[index].boxes.append([[left_top[0]+w, left_top[1]], [left_top[0]+w+thickness, left_top[1]+h]])
    instances_platform[index].dir_boxes = [0, 2, 1, 3]
    
    left_top = [80, 100]
    index = 2
    w, h = h, w
    instances_platform[2].image = instances_platform[2].images[1]
    instances_platform[2].rect = pg.Rect(50, 100, 70, 260)
    instances_platform[index].rect = pg.Rect(left_top[0], left_top[1], w, h)
    instances_platform[index].boxes.append([[left_top[0], left_top[1]], [left_top[0]+w, left_top[1]+thickness]])
    instances_platform[index].boxes.append([[left_top[0], left_top[1]+h], [left_top[0]+w, left_top[1]+h+thickness]])
    instances_platform[index].boxes.append([[left_top[0], left_top[1]], [left_top[0]+thickness, left_top[1]+h]])
    instances_platform[index].boxes.append([[left_top[0]+w, left_top[1]], [left_top[0]+w+thickness, left_top[1]+h]])
    instances_platform[index].dir_boxes = [0, 2, 1, 3]


    # Run our main loop whilst the player is alive.
    while player.alive():
        # get mouse input
        
        pg.event.get()
        mouse_1_hold = pg.mouse.get_pressed(3)[0]
        if mouse_1_hold:
            coord_mouse = pg.mouse.get_pos()
            # print("Mouse Postion right now is: ", coord_mouse)
            player.drag(coord_mouse)
            # player.rect = pg.Rect(coord_mouse[0], coord_mouse[1], 40, 50)

        for event in pg.event.get():
            # if event.type == pg.MOUSEBUTTONDOWN:
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    pg.display.flip()
                    fullscreen = not fullscreen

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # Detect collisions between player and platforms.
        # for platform in pg.sprite.spritecollide(player, platforms, 1):
        #     if pg.mixer:
        #         boom_sound.play()
        #     player.land(platform.rect)

        # draw the scene
        dirty = all.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(60)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)
    pg.quit()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
