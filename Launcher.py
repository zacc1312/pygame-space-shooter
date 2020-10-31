# sets up all of the current libraries needed
import pygame
import os
import time
import random
import pickle
import os.path
pygame.font.init()

if os.path.isfile("save.dat"):
	highscore = pickle.load(open("save.dat", "rb"))
else:
	highscore=0


# setting up the window
WIDTH, HEIGHT=750, 750 # width and height of window
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) # creates the new window
pygame.display.set_caption("Space Shooter") # sets the space shooter caption for the window

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("","pixel_ship_blue_small.png"))

# player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("","pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("","pixel_laser_yellow.png"))

# background image for the gamea
BG=pygame.transform.scale(pygame.image.load(os.path.join("","background-black.png")),(WIDTH, HEIGHT))


class Laser:
	def __init__(self, x, y, img):
		self.x=x
		self.y=y
		self.img=img
		self.mask=pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x,self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not(self.y <= height and self.y >=0)

	def collision(self, obj):
		return collide(obj, self)


def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



# creating a general player class where we can create stuff from
class Ship:

	COOLDOWN = 15

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	# defining a function to draw something to the window
	def draw(self, window):
		window.blit(self.ship_img, (self.x,self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self,vel,obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter>0:
			self.cool_down_counter+=1

	def shoot(self):
		if self.cool_down_counter==0:
			laser = Laser(self.x,self.y,self.laser_img)
			self.lasers.append(laser)

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()

class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img=YELLOW_SPACE_SHIP
		self.laser_img=YELLOW_LASER
		self.mask=pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def move_lasers(self,vel,objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						self.lasers.remove(laser)

class Enemy(Ship):

	COLOR_MAP = {"red":(RED_SPACE_SHIP, RED_LASER), "green":(GREEN_SPACE_SHIP, GREEN_LASER), "blue":(BLUE_SPACE_SHIP, BLUE_LASER)}

	def __init__(self, x, y, color, health=100):
		super().__init__(x,y,health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

# mainloop
def main():
	run = True # runs the while loop to keep the game running
	FPS = 30 # frames per second/how many times the games checks per something per second
	level = 0 # sets level to 1 when the game starts
	lives = 5 # sets the amount of lives to 5 when the game starts
	clock = pygame.time.Clock() # the clock to keep the game running
	lost=False
	lost_count=0
	main_font = pygame.font.Font(os.path.join("","Pixellari.ttf"),30) # sets a font to put on the screens
	lost_font = pygame.font.Font(os.path.join("","Pixellari.ttf"),50) # sets a font to put on the screens

	enemies = []
	wave_length = 5
	enemy_vel = 1

	player = Player(325, 600) # variable for the test rectangle

	player_vel = 5
	laser_vel = 4

	# redraw window to specifications
	def redraw_window():

		WIN.blit(BG, (0,0)) # draws the background image to the screen
		
		#draw text
		lives_label=main_font.render(f"Lives: {lives}",1,(255,255,255)) # lives text
		level_label=main_font.render(f"Level: {level}",1,(255,255,255)) # levels text
		highscore_label=main_font.render(f"Highscore: {highscore}",1,(255,255,255))

		WIN.blit(lives_label,(10,10)) # publishes the lives text to the screen
		WIN.blit(level_label,(WIDTH-level_label.get_width()-10,10)) # publishes the level text to the screen
		WIN.blit(highscore_label,(300,10))

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN) # draws the test square to the screen

		if lost:
			lost_label = lost_font.render("You Lost! Rerun the program to play again!", 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

		if lost:
			if level > highscore:
				pickle.dump(level, open("save.dat", "wb"))

		pygame.display.update() # updates the changes to this display

	# keeps the game running, updates all the stuff
	while run:

		clock.tick(FPS) # checks for things 60 times every 1 second
		redraw_window() # redraws the window to the stuff we specified earlier

		for enemy in enemies[:]:
				enemy.move(enemy_vel)
				enemy.move_lasers(laser_vel, player)
				if enemy.y + enemy.get_height() > HEIGHT:
					lives -= 1
					enemies.remove(enemy)

		player.move_lasers(-laser_vel, enemies)

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 5:
				run = False
			else:
				continue

		if len(enemies)==0:
			level += 1
			wave_length+=5

			for i in range (wave_length):
				enemy = Enemy(random.randrange(50,WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)

		# shuts down the program if the window is closed
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				if level > highscore:
					pickle.dump(level, open("save.dat", "wb"))
				run=False

			keys = pygame.key.get_pressed()

			#define the key movements
			if keys[pygame.K_a] and player.x - player_vel > 0: #left 
				player.x -= player_vel
				
			if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right 
				player.x += player_vel

			if keys[pygame.K_SPACE]:
				player.shoot()

			

			



main() # runs the main script that we define above
