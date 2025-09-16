# Importing packages
import pyray as game
import EasyJson as json
import math
import random
import keyboard

# Importing Custom Packages
from Content.Plugins import Frequency as fc

# Importing Settings
Settings = json.Load("Content\\Game\\Settings.json")
WindowWidth, WindowHeight = Settings["window"]["width"], Settings["window"]["height"]
MoveRight1 = Settings["keybinds"]["MoveRight1"]
MoveRight2 = Settings["keybinds"]["MoveRight2"]
MoveLeft1 = Settings["keybinds"]["MoveLeft1"]
MoveLeft2 = Settings["keybinds"]["MoveLeft2"]
Close_Door = Settings["keybinds"]["Close_Door"]

# Creating Window
game.init_window(WindowWidth, WindowHeight, "RealDoors")
game.set_target_fps(60)

if str(Settings["window"]["mode"]) == "borderless":
    game.toggle_borderless_windowed()
elif str(Settings["window"]["mode"]) == "fullscreen":
    game.toggle_fullscreen()
else:
    pass


class PlayerCharacter:
    def __init__(self):
        self.x, self.y = 0, 0
        self.speed = 5
        self.camera = game.Camera2D()
        self.camera.target = game.Vector2(self.x, self.y)
        self.camera.offset = game.Vector2(WindowWidth/2, WindowHeight-75)  # Center of screen
        self.camera.rotation = 0.0
        self.camera.zoom = 1.0
        self.camera_smoothing = 10
        self.sets = 0
        self.last_position_x = self.x  # Store initial x position
        self.last_position_y = self.y  # Store initial y position
        self.last_time = game.get_time()  # Store initial time
    
    def get_velocity(self, OneDirection: bool = True):
        """One Direction is always output an + value, not nigative, even if you move to other way"""
        current_time = game.get_time()
        delta_time = current_time - self.last_time
        
        if delta_time <= 0:
            return 0, 0  
        
        x_velocity = (self.x - self.last_position_x) / delta_time
        y_velocity = (self.y - self.last_position_y) / delta_time
        
        self.last_position_x = self.x
        self.last_position_y = self.y
        self.last_time = current_time
        if OneDirection:
            if x_velocity < 0:
                x_velocity *= -1
                
            if y_velocity < 0:
                y_velocity *= -1
        return x_velocity, y_velocity
    
    def Update(self):
        prev_x, prev_y = self.x, self.y
        
        self.mouse_x, self.mouse_y = game.get_mouse_x(), game.get_mouse_y()
        if keyboard.is_pressed(MoveRight1) or keyboard.is_pressed(MoveRight2):
            self.x += self.speed
        if keyboard.is_pressed(MoveLeft1) or keyboard.is_pressed(MoveLeft2):
            self.x -= self.speed

        self.camera.zoom += game.get_mouse_wheel_move() * 0.05
        t = 1.0 - math.exp(-self.camera_smoothing * game.get_frame_time())
        self.camera.target.x = game.lerp(float(self.camera.target.x), float(self.x), t)
        self.camera.rotation = game.lerp(float(self.camera.rotation), (((self.mouse_x - (WindowWidth / 2))) / (WindowWidth / 2)) * 5 * Settings["window"]["camera_max_rotation"]*8, t)
                
        this_time = game.get_time()
        x_vel, y_vel = self.get_velocity()




        


    def Draw(self):
        game.draw_rectangle(int(self.x-25), int(self.y-25), 50, 50, (255, 255, 255, 255))
        game.draw_rectangle_lines_ex(game.Rectangle(self.x-25-1, self.y-25-1, 52, 52), 5, (0, 0, 0, 255))
        game.draw_text(f"{game.get_time():.2f}", int(self.x-(WindowWidth/3)), int(self.y-(WindowHeight/1.5)), 50, (255, 255, 255, 100))




OpenedDoorTexture = game.load_texture("Content\\Game\\Textures\\OpenedDoor.png")
HalfOpenedDoorTexture = game.load_texture("Content\\Game\\Textures\\HalfOpenedDoor.png")
ClosedDoorTexture = game.load_texture("Content\\Game\\Textures\\ClosedDoor.png")
class DoorObject:
    def __init__(self, x: int, y: int, door_name):
        self.x, self.y = x, y
        self.closed = False
        self.name = door_name
        self.hm = False
        self.HaveMonster = 0
        self.monster_spawn_time = None  # Timer for monster spawn delay
        self.wait_duration = 10  # Wait for 2 seconds (adjust as needed)
        
    def Update(self, PlayerRefrence: PlayerCharacter):
        game.draw_rectangle(int(self.x), int(self.y-270), 151, int(270), game.BLACK)
        if self.closed:
            game.draw_texture_ex(ClosedDoorTexture, game.Vector2(self.x, self.y-270), 0, 1, game.WHITE)
        else:
            game.draw_texture_ex(OpenedDoorTexture, game.Vector2(self.x, self.y-270), 0, 1, game.WHITE)
        
        if int(PlayerRefrence.x-25) < int(self.x+(260/2)) and int(PlayerRefrence.x+25) > self.x:
            if not self.closed:
                game.draw_text("Close!", int(PlayerRefrence.x-(WindowWidth/3)), PlayerRefrence.y, 50, (255, 255, 255, 100))
            else:
                game.draw_text("Open!", int(PlayerRefrence.x-(WindowWidth/3)), PlayerRefrence.y, 50, (255, 255, 255, 255))

        if int(PlayerRefrence.x-25) < int(self.x+(260/2)) and int(PlayerRefrence.x+25) > self.x and (keyboard.is_pressed(Close_Door)):
            self.closed = True
        else:
            self.closed = False

        if self.hm == False:
            self.HaveMonster = random.randint(0, 1000)
            
        if self.HaveMonster == 1:
            if self.monster_spawn_time is None:  # First time monster spawns
                print(f"SPAWN! at {self.name}")
                self.monster_spawn_time = game.get_time()  # Start the timer
                self.hm = True
            
            elif game.get_time() - self.monster_spawn_time >= self.wait_duration:
                if self.closed:
                    self.hm = False
                    self.monster_spawn_time = None  # Reset timer for next spawn
                    self.HaveMonster = 0  # Reset monster chance
                    print("monster saw that the door is closed, and then left")
                else:
                    print(f"DIE!!!!!!!!!! from {self.name}")
                    self.hm = False
                    self.monster_spawn_time = None  # Reset timer
                    self.HaveMonster = 0  # Reset monster chance



# BeginPlay
Player = PlayerCharacter()
RandomBoxes = []
Doors = []
for i in range(100):
    x = random.randint(int(-1*(WindowWidth/2)*2), int(WindowWidth/2*2))
    y = random.randint(-WindowHeight, 0)
    RandomBoxes.append({"x": x, "y": y})


Doors.append(DoorObject(-400, 0, "far left door"))
Doors.append(DoorObject(-150, 0, "close left door"))
Doors.append(DoorObject(150, 0, "close right door"))
Doors.append(DoorObject(400, 0, "far right door"))

while not game.window_should_close():
    game.begin_drawing()
    game.clear_background((25, 25, 25, 255))
    game.begin_mode_2d(Player.camera)

    for Door in Doors:
        Door.Update(Player)

    Player.Update()
    Player.Draw()
    Player.camera.rotation *= -1
    for box in RandomBoxes:
        game.draw_rectangle(int(box["x"]), int(box["y"]), 5, 5, (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100), 255))

    game.end_mode_2d()
    game.end_drawing()