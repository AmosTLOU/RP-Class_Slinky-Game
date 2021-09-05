import random
import os
import math
import pygame as pg

PI = 3.1415926
Multiplier_AngleToRad = PI / 180

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# START
FPS = 60
Size_Screen = [1080, 720]
SCREENRECT = pg.Rect(0, 0, Size_Screen[0], Size_Screen[1])
Size_PlayerImage = [160, 160]
Size_ChaserImage = [200, 200]
Size_InteractableImage = [64, 64]

Len_StaticSlinky = 45  # the distance from top to bottom when stationary
LongestStretchingDistance = 100  # better not changed, or the movement would look like anti-intuitive
LeastDistanceForDraggingSlinky = 35 
LeastDistanceForLandingSlinky = 30
Speed_Camera = 7   # pixel(s) per frame
Time_Chaser_Move = 0.05  # how long cat should wait for next move
StepLength_Chaser = 3         # when cat moves, how many pixels does it move
StepBackUp_Chaser = 10         # when cat moves, how many pixels does it move
Time_Frame_Chaser = 0.1   # how long one chaser frame would play
Time_Freeze_Chaser = 2   # how long chaser would be frozen
Time_Freeze_Player = 2   # how long player would be frozen
Time_FurtherStretch_Player = 5   # how long player could further stretch

background_ImageName = "background.jpg"
background_MusicName = "nervous.mp3"
Imagefiles_items = ["1.gif", "2.gif", "3.gif", "4.gif", "5.gif", "6.gif"]

Name_Platforms =     [  "6.gif",         "6.gif",      "2.gif"                  ]
Position_Platforms = [  [1180, 1195],  [1308, 1195],   [1090, 940]              ]

Name_Interactables =  [  "honey",                             ]
Position_Interactables = [  [1350, 1126]                ]

StartPos_Player = [1220, 1190]  # pos of the slinky's bottom midpoint
Origin_Local = [StartPos_Player[0]-Size_Screen[0]//2, StartPos_Player[1]-3*Size_Screen[1]//4]
# END


Instances_platform = []
Instances_interactable = []
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert_alpha()


def load_sound(file):
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data\music", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


def e_dst(coord_a, coord_b):
    return math.sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)


def globalToLocal(coord_global):
    return [coord_global[0] - Origin_Local[0], coord_global[1] - Origin_Local[1]]


def localToGlobal(coord_local):
    return [coord_local[0] + Origin_Local[0], coord_local[1] + Origin_Local[1]]


def touched_PointBox(coord, box):
    return True if box[0][0] <= coord[0] and coord[0] <= box[1][0] and box[0][1] <= coord[1] and coord[1] <= box[1][1] else False 

def touched_BoxBox(box_1, box_2):
    for i in range(2):
        if box_1[0][i] > box_2[1][i] or box_2[0][i] > box_1[1][i]:
            return False
    return True


class Platform(pg.sprite.Sprite):
    images = []
    imagesGetHIt = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.imageGetHit = self.imagesGetHit[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [0, 0]
        self.box = []
        self.boxes = []
        self.angle_boxes = []
        self.life_max = 4
        self.life_now = self.life_max

    def setPosAndSize(self, left, top):
        self.pos[0], self.pos[1] = left, top
        self.rect = self.image.get_rect()
        self.size[:] = self.rect[2:4]

    def setColliderBoxes(self):
        l = self.pos[0]
        t = self.pos[1]
        w = self.size[0]
        h = self.size[1]
        thickness = 10
        self.box = [[l, t], [l+w, t+h]]
        self.boxes.append([[l, t-thickness], [l+w, t]])
        self.boxes.append([[l, t+h], [l+w, t+h+thickness]])
        self.boxes.append([[l-thickness, t], [l, t+h]])
        self.boxes.append([[l+w, t], [l+w+thickness, t+h]])
        self.angle_boxes = [0, 180, 90, 270]        
    
    def getHit(self):
        self.life_now -= 1
        if self.life_now == self.life_max // 2:
            self.image = self.imageGetHit
        if self.life_now == 0:
            self.image = load_image("transparent.png")
            return True
        else:
            return False

    def update(self):
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0], local_coord[1], self.size[0], self.size[1])


class Interactable(pg.sprite.Sprite):
    images = []
    player = None
    chaser = None
    
    def __init__(self, ind_reaction_):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [self.rect[2], self.rect[3]]
        self.box = []
        self.frame_cnt = 0
        self.ind_reaction = ind_reaction_
    
    def react(self):  # 0 honey 1 stopwatch 2 power
        # TODO play some sound effect
        if self.ind_reaction == 0:
            self.player.beingStuck = True
        elif self.ind_reaction == 1:
            self.chaser.frozen = True
        elif self.ind_reaction == 2:
            self.player.getPower = True
        self.image = load_image("transparent.png")

    def setPosAndSize(self, left, top):
        self.pos[0], self.pos[1] = left, top
        self.rect = self.image.get_rect()
        self.size[:] = self.rect[2:4]
        self.setBox()

    def setBox(self):
        l = self.pos[0]
        t = self.pos[1]
        w = self.size[0]
        h = self.size[1]  
        self.box = [[l, t], [l+w, t+h]]        
    
    def update(self):
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0], local_coord[1], self.size[0], self.size[1])


class Player(pg.sprite.Sprite):   
    images = []  # class static variable
    music = None

    def __init__(self):   # instance variable!
        pg.sprite.Sprite.__init__(self, self.containers)
        self.angle = 0
        self.image = self.assignImage(self.images[0])
        self.rect = self.image.get_rect()
        self.size = [self.image.get_rect().width, self.image.get_rect().height]
        self.pos_bottom = [StartPos_Player[0], StartPos_Player[1]]
        self.pos_top = [self.pos_bottom[0], self.pos_bottom[1]-Len_StaticSlinky]
        self.markPoint = None
        self.shift_dst = [0, 0]
        self.shift_dir = [1, 1]
        self.beingHold = False
        self.beingStuck = False
        self.stuck_frame = 0
        self.getPower = False
        self.power_frame = 0
    
    def getTop(self):
        x = 0
        y = Len_StaticSlinky
        cos_theta = round(math.cos(self.angle * Multiplier_AngleToRad))
        sin_theta = round(math.sin(self.angle * Multiplier_AngleToRad))
        x_ =  cos_theta * x - sin_theta * y
        y_ =  sin_theta * x + cos_theta * y
        return [self.pos_bottom[0] + x_, self.pos_bottom[1] - y_]

    def getStandardXY(self, x, y):        
        if self.angle < 0 or self.angle > 360:
            print("Error: angele out of range")
            exit()
        cos_theta = round(math.cos(self.angle * Multiplier_AngleToRad))
        sin_theta = round(math.sin(self.angle * Multiplier_AngleToRad))
        x_ =  cos_theta * x + sin_theta * y
        y_ =  -sin_theta * x + cos_theta * y
        return x_, y_

    def assignImage(self, image):
        return pg.transform.rotate(image, self.angle)

    def release(self, land=False):
        if not land and not self.beingStuck:
            self.music.play(0)
        self.image = self.assignImage(self.images[0])
        self.pos_top = self.getTop()
        self.markPoint.pos = self.pos_top[:]
        self.markPoint.adjustImage(self.angle)
        self.beingHold = False


    def drag(self, coord_mouse): 
        coord_mouse = localToGlobal(coord_mouse)
        if self.beingStuck or e_dst(self.pos_top, coord_mouse) > LeastDistanceForDraggingSlinky :  # if the mouse was too far from the top-end, then the slinky couldn't be dragged
            return
        if not self.beingHold:  # if it was the first mouse click on slinky and the mouse was in the range of any collider box, then do nothing
            for p in Instances_platform:
                for box in p.boxes:
                    if touched_PointBox(coord_mouse, box):
                        self.release()
                        return
        x, y = self.getStandardXY(coord_mouse[0] - self.pos_bottom[0],  -coord_mouse[1] + self.pos_bottom[1])
        euler_distance = math.sqrt(abs(x)**2 + abs(y)**2)
        if euler_distance > LongestStretchingDistance:  # get the top-end back
            self.release()
        else:
            self.beingHold = True
            self.pos_top = coord_mouse[:] 
            # TODO Apply the image according to (x, y)   which is the relative distance
            x_to_scale = round(abs(x)//3)
            num_pics = 17
            if x > 0:
                dir_markPoint = 1
                self.image = self.assignImage(self.images[min(x_to_scale, num_pics-1)])
                if y < 0:
                    TODO = 1
            else:
                dir_markPoint = 0
                self.image = self.assignImage(pg.transform.flip(self.images[min(x_to_scale, num_pics-1)], 1, 0))
                if y < 0:
                    TODO = 1
            self.markPoint.pos = self.pos_top[:]
            self.markPoint.adjustImage(self.angle, dir_markPoint)
            for item in Instances_interactable:
                if touched_PointBox(self.pos_top, item.box):
                    item.react()
                    Instances_interactable.remove(item)
            for p in Instances_platform:
                for i in range(len(p.boxes)):
                    if touched_PointBox(self.pos_top, p.boxes[i]):
                        if e_dst(self.pos_bottom, self.pos_top) < LeastDistanceForLandingSlinky:  # if landpoint too close to bottom, then don't move
                            self.release()
                            return
                        self.angle = p.angle_boxes[i]
                        self.land()
                        return
            
        
    def land(self):
        # print("Slinky lands on a new point!")
        self.music.play(1)
        bias = 5
        if self.angle == 0:
            self.pos_top[1] += bias
        elif self.angle == 180:
            self.pos_top[1] -= bias
        elif self.angle == 90:
            self.pos_top[0] += bias
        elif self.angle == 270:
            self.pos_top[0] -= bias
        self.shift_dst[0], self.shift_dst[1] = abs(self.pos_top[0] - self.pos_bottom[0]), abs(self.pos_top[1] - self.pos_bottom[1])
        self.shift_axis_further = 0 if self.shift_dst[0] >= self.shift_dst[1] else 1
        self.shift_dir[0] = 1 if (self.pos_top[0] - self.pos_bottom[0]) > 0 else -1
        self.shift_dir[1] = 1 if (self.pos_top[1] - self.pos_bottom[1]) > 0 else -1
        self.pos_bottom = self.pos_top[:]
        self.release(land=True)

    def getStuck(self):
        self.markPoint.getStuck()
        f = round(Time_Freeze_Player * FPS)
        self.stuck_frame += 1
        if f == self.stuck_frame:
            self.release()
            self.stuck_frame = 0
            self.beingStuck = False
    
    def PowerCountDown(self):
        self.power_frame += 1
        f = round(Time_FurtherStretch_Player * FPS)
        if f == self.power_frame:
            self.power_frame = 0
            self.getPower = False


    def update(self):
        if self.shift_dst[0] > 0 or self.shift_dst[1] > 0:
            for i in range(2):
                s = Speed_Camera if self.shift_dst[i] > Speed_Camera else self.shift_dst[i]
                Origin_Local[i] += s if self.shift_dir[i] > 0 else -s
                self.shift_dst[i] -= s
        if self.beingStuck:
            self.getStuck()
        if self.getPower:
            self.PowerCountDown()
        self.markPoint.pos = self.pos_top[:]
        local_coord = globalToLocal(self.pos_bottom)
        self.rect = pg.Rect(local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])
        

class MarkPoint(pg.sprite.Sprite):
    images = []
    imagesStuck = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [self.rect[2], self.rect[3]]
        self.cycle_stuck = 2
        self.ind_cycle_stuck = 0

    def adjustImage(self, angle, dir=0):
        self.image = pg.transform.rotate(pg.transform.flip(self.images[0], dir, 0), angle)

    def getStuck(self):
        self.ind_cycle_stuck = (self.ind_cycle_stuck + 1) % self.cycle_stuck
        self.image = self.imagesStuck[self.ind_cycle_stuck]
        
    def update(self):
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])


class Chaser(pg.sprite.Sprite):
    images = []
    
    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [Origin_Local[0] + 100, Origin_Local[1] + 100]
        self.size = [self.rect[2], self.rect[3]]
        self.cycle = len(self.images)
        self.index_in_cycle = 0
        self.frame_cnt = 0
        self.prey = None
        self.just_hit_platform = False
        self.frozen = False
        self.frozen_frame = 0

    def chase(self):
        # TODO
        potential_move = [0, 0]
        for i in range(2):
            if self.prey.pos_bottom[i] - self.pos[i] > 0:
                potential_move[i] = StepLength_Chaser
            elif self.prey.pos_bottom[i] - self.pos[i] < 0:
                potential_move[i] = -StepLength_Chaser
        if self.just_hit_platform:
            self.pos[0] -= StepBackUp_Chaser * potential_move[0]
            self.pos[1] -= StepBackUp_Chaser * potential_move[1]
            self.just_hit_platform = False
        else:
            f = round(Time_Chaser_Move * FPS)
            if self.frame_cnt % f == 0: 
                self.pos[0] += potential_move[0]
                self.pos[1] += potential_move[1]
            edge_shortened = 20
            box = [[self.pos[0]-self.size[0]//2+edge_shortened, self.pos[1]-self.size[1]//2+edge_shortened], 
                   [self.pos[0]+self.size[0]//2-edge_shortened, self.pos[1]+self.size[1]//2-edge_shortened]]
            if touched_PointBox(self.prey.pos_bottom, box) or touched_PointBox(self.prey.pos_top, box):
                print("Game Over!")
            for p in Instances_platform:
                if touched_BoxBox(box, p.box):
                    self.just_hit_platform = True
                    if p.getHit():
                        Instances_platform.remove(p)
                    return

    def getFrozen(self):
        f = round(Time_Freeze_Chaser * FPS)
        self.frozen_frame += 1
        if f == self.frozen_frame:
            self.frozen_frame = 0
            self.frozen = False
            # TODO
            # self.image = 

    def update(self):
        if not self.frozen:
            self.frame_cnt += 1
            f = round(Time_Frame_Chaser * FPS)
            if self.frame_cnt % f == 0:
                self.index_in_cycle = (self.index_in_cycle + 1) % 3
                self.image = self.images[self.index_in_cycle]
            self.chase()
        else:
            self.getFrozen()
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])


class Music():
    def __init__(self):
        self.sfx = [load_sound("slinky_back.wav"), load_sound("slinky_land.wav")]
        self.music_mixer = pg.mixer

    def play(self, ind):
        self.sfx[ind].play()


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
    music = Music()
    if music.music_mixer and not music.music_mixer.get_init():
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
    for ind in range(1, 18):
        imagefiles_slinky.append("slinky_17\slinky (" + str(ind) + ").png")
    Player.images = [load_image(im) for im in imagefiles_slinky]
    for i in range(len(Player.images)):
        Player.images[i] = pg.transform.scale(Player.images[i], Size_PlayerImage)
    
    
    imagefiles_items = []
    for i in range(len(Imagefiles_items)):
        imagefiles_items.append("item\\" + Imagefiles_items[i])
    Platform.images = [load_image(im) for im in imagefiles_items]
    Platform.imagesGetHit = [load_image(im) for im in imagefiles_items]

    MarkPoint.images = [load_image("eyes_.png")]
    MarkPoint.imagesStuck = [load_image("eyes_.png"), load_image("eyes.png")]

    Chaser.images = [load_image(im) for im in ["cat\\cat (1).png", "cat\\cat (2).png", "cat\\cat (3).png"]]
    for i in range(len(Chaser.images)):
        Chaser.images[i] = pg.transform.scale(Chaser.images[i], Size_ChaserImage)

    Interactable.images = [load_image(im) for im in ["item\\honey trap.png", "item\\stop watch.jpg", "item\\stretch power.jpg"]]
    for i in range(len(Interactable.images)):
        Interactable.images[i] = pg.transform.scale(Interactable.images[i], Size_InteractableImage)
    
    # decorate the game window
    icon = pg.transform.scale(load_image("icon.jpg"), (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Slinky Game")

    # create the background, tile the bgd image
    bgdtile = load_image(background_ImageName)
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    if music.music_mixer:
        music_file = os.path.join(main_dir, "data", "music\\" + background_MusicName)
        music.music_mixer.music.load(music_file)
        music.music_mixer.music.play(-1)

    Player.music = music

    # Initialize Game Groups
    all = pg.sprite.OrderedUpdates()

    # assign default groups to each sprite class
    Platform.containers = all
    Player.containers = all
    MarkPoint.containers = all
    Chaser.containers = all
    Interactable.containers = all

    # Create Some Starting Values
    clock = pg.time.Clock()

    # Initialize Instances
    dct = {}
    index = 0
    for name in Imagefiles_items:
        dct[name] = index
        index += 1
    dct["honey"] = 0
    dct["stopwatch"] = 1
    dct["power"] = 2

    for i in range(len(Name_Interactables)):
        ind = dct[Name_Interactables[i]]
        Instances_interactable.append(Interactable(ind))        
        Instances_interactable[i].image = Interactable.images[ind]
        Instances_interactable[i].setPosAndSize(Position_Interactables[i][0], Position_Interactables[i][1]) 

    player = Player()
    markPoint = MarkPoint()
    player.markPoint = markPoint

    for i in range(len(Name_Platforms)):
        Instances_platform.append(Platform()) 
        ind = dct[Name_Platforms[i]]
        Instances_platform[i].image = Platform.images[ind]
        Instances_platform[i].imageGetHit = Platform.imagesGetHit[ind]
        Instances_platform[i].setPosAndSize(Position_Platforms[i][0], Position_Platforms[i][1])
        Instances_platform[i].setColliderBoxes()       

    cat = Chaser()
    cat.prey = player

    Interactable.player = player
    Interactable.chaser = cat

    # Run our main loop whilst the player is alive.
    while player.alive():
        for event in pg.event.get():
            # get mouse input:
            mouse_1_hold = pg.mouse.get_pressed(3)[0]
            if mouse_1_hold:
                player.drag(pg.mouse.get_pos())
            elif player.beingHold and not player.beingStuck:
                player.release()
            # get keys input:
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

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # draw the scene
        dirty = all.draw(screen)
        pg.display.update(dirty)

        # set the framerate
        clock.tick(FPS)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)
    pg.quit()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
