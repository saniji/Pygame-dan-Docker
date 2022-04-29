import sys
import random
import pygame
from pygame.locals import *
from abc import ABC, abstractmethod

pygame.init()

player_ship = 'assets/player_ship.png'
enemy_ship = 'assets/enemy1_ship.png'
boss_ship = 'assets/enemy2_ship.png'
player_bullet = 'assets/pbullet.png'
enemy_bullet = 'assets/enemybullet.png'
boss_bullet = 'assets/bossbullet.png'

screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()
clock = pygame.time.Clock()
FPS = 60

background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
bossbullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()

pygame.mouse.set_visible(False)
font = pygame.font.SysFont('freesansbold.ttf', 32)

class Game(ABC):
	@abstractmethod
	def playerbullet_hits_enemy(self):
		pass

	@abstractmethod
	def playerbullet_hits_boss(self):
		pass

	@abstractmethod
	def enemybullet_hits_player(self):
		pass

	@abstractmethod
	def bossbullet_hits_player(self):
		pass

	@abstractmethod
	def player_enemy_crash(self):
		pass

	@abstractmethod
	def player_boss_crash(self):
		pass

class Background(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.image.load('assets/bird.png')
		self.image.set_colorkey('black')
		self.rect = self.image.get_rect()

	def update(self):
		self.rect.y += 1
		self.rect.x += 1 
		if self.rect.y > s_height:
			self.rect.y = random.randrange(-10, 0)
			self.rect.x = random.randrange(-400, s_width)

class Player(pygame.sprite.Sprite):
	def __init__(self, img):
		super().__init__()
		self.image = pygame.image.load(img)
		self.rect = self.image.get_rect()
		self.image.set_colorkey('black')
		self.alive = True
		self.count_to_live = 0 
		self.activate_bullet = True
		self.alpha_duration = 0

	def update(self):
		if self.alive:
			self.image.set_alpha(80)
			self.alpha_duration += 1
			if self.alpha_duration > 170:
				self.image.set_alpha(255)
			mouse = pygame.mouse.get_pos()
			self.rect.x = mouse[0] - 20
			self.rect.y = mouse[1] + 40
		else:
			self.alpha_duration = 0
			expl_x = self.rect.x + 20
			expl_y = self.rect.y + 40
			explosion = Explosion(expl_x, expl_y)
			explosion_group.add(explosion)
			sprite_group.add(explosion)
			pygame.time.delay(22)
			self.rect.y = s_height + 200
			self.count_to_live += 1
			if self.count_to_live > 100:
				self.alive = True
				self.count_to_live = 0
				self.activate_bullet = True

	def shoot(self):
		if self.activate_bullet:
			bullet = PlayerBullet(player_bullet)
			mouse = pygame.mouse.get_pos()
			bullet.rect.x = mouse[0]
			bullet.rect.y = mouse[1]
			playerbullet_group.add(bullet)
			sprite_group.add(bullet)

	def dead(self):
		self.alive = False
		self.activate_bullet = False

class Enemy(Player):
	def __init__(self, img):
		super().__init__(img)
		self.rect.x = random.randrange(0, s_width)
		self.rect.y = random.randrange(-500, 0)
		screen.blit(self.image, (self.rect.x, self.rect.y))

	def update(self):
		self.rect.y += 1
		if self.rect.y > s_height:
			self.rect.x = random.randrange(0, s_width)
			self.rect.y = random.randrange(-2000, 0)
		self.shoot()

	def shoot(self):
		if self.rect.y in (0, 30, 70, 300, 700):
			enemybullet = EnemyBullet(enemy_bullet)
			enemybullet.rect.x = self.rect.x + 20
			enemybullet.rect.y = self.rect.y + 50
			enemybullet_group.add(enemybullet)
			sprite_group.add(enemybullet)

class Boss(Enemy):
	def __init__(self, img):
		super().__init__(img)
		self.rect.x = -200 
		self.rect.y = 200 
		self.move = 1

	def update(self):
		self.rect.x += self.move 
		if self.rect.x > s_width + 200:
			self.move *= -1 
		elif self.rect.x < -200:
			self.move *= -1
		self.shoot()

	def shoot(self):
		if self.rect.x % 50 == 0:
			bossbullet = EnemyBullet(boss_bullet)
			bossbullet.rect.x = self.rect.x + 50
			bossbullet.rect.y = self.rect.y + 70
			bossbullet_group.add(bossbullet)
			sprite_group.add(bossbullet)

class PlayerBullet(pygame.sprite.Sprite):
	def __init__(self, img):
		super().__init__()
		self.image = pygame.image.load(img)
		self.rect = self.image.get_rect()
		self.image.set_colorkey('black')

	def update(self):
		self.rect.y -= 5
		if self.rect.y < 0:
			self.kill()

class EnemyBullet(PlayerBullet):
	def __init__(self, img):
		super().__init__(img)
		self.image.set_colorkey('white')

	def update(self):
		self.rect.y += 3
		if self.rect.y > s_height:
			self.kill()

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.img_list = []
		for i in range(1, 6):
			img = pygame.image.load(f'assets/exp{i}.png').convert()
			img.set_colorkey('black')
			img = pygame.transform.scale(img, (120, 120))
			self.img_list.append(img)
		self.index = 0
		self.image = self.img_list[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.count_delay = 0 

	def update(self):
		self.count_delay += 1
		if self.count_delay >= 12:
			if self.index < len(self.img_list) - 1:
				self.count_delay = 0
				self.index += 1
				self.image = self.img_list[self.index]
		if self.index >= len(self.img_list) - 1:
			if self.count_delay >= 12:
				self.kill()

class PlayGame(Game):
	def __init__(self):
		self.__count_hit = 0
		self.__count_hit2 = 0
		self.__lives = 3
		self.__score = 0

	def playerbullet_hits_enemy(self):
		hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
		for i in hits:
			self.__count_hit += 1
			if self.__count_hit == 3:
				self.__score += 1
				expl_x = i.rect.x + 20
				expl_y = i.rect.y + 40
				explosion = Explosion(expl_x, expl_y)
				explosion_group.add(explosion)
				sprite_group.add(explosion)
				i.rect.x = random.randrange(0, s_width)
				i.rect.y = random.randrange(-3000, -100)
				self.__count_hit = 0

	def playerbullet_hits_boss(self):
		hits = pygame.sprite.groupcollide(boss_group, playerbullet_group, False, True)
		for i in hits:
			self.__count_hit2 += 1
			if self.__count_hit2 == 20:
				self.__score += 8
				expl_x = i.rect.x + 50
				expl_y = i.rect.y + 60
				explosion = Explosion(expl_x, expl_y)
				explosion_group.add(explosion)
				sprite_group.add(explosion)
				i.rect.x = -199
				self.__count_hit2 = 0

	def enemybullet_hits_player(self):
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
			if hits:
				self.__lives -= 1
				self.player.dead()

	def bossbullet_hits_player(self):
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, bossbullet_group, True)
			if hits:
				self.__lives -= 1
				self.player.dead()

	def player_enemy_crash(self):
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
			if hits:
				for i in hits:
					i.rect.x = random.randrange(0, s_width)
					i.rect.y = random.randrange(-3000, -100)
					self.__lives -= 1
					self.player.dead()

	def player_boss_crash(self):
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, boss_group, False)
			if hits:
				for i in hits:
					i.rect.x = -199
					self.__lives -= 1
					self.player.dead()

	def create_background(self):
		for i in range(10):
			x = random.randint(1,6)
			background_image = Background(x,x)
			background_image.rect.x = random.randrange(0, s_width)
			background_image.rect.y = random.randrange(0, s_height)
			background_group.add(background_image)
			sprite_group.add(background_image)

	def create_player(self):
		self.player = Player(player_ship)
		player_group.add(self.player)
		sprite_group.add(self.player)

	def create_enemy(self):
		for i in range(15):
			self.enemy = Enemy(enemy_ship)
			enemy_group.add(self.enemy)
			sprite_group.add(self.enemy)

	def create_boss(self):
		for i in range(1):
			self.boss = Boss(boss_ship)
			boss_group.add(self.boss)
			sprite_group.add(self.boss)

	def create_lives(self):
		self.live_img = pygame.image.load(player_ship)
		self.live_img = pygame.transform.scale(self.live_img, (30,30))
		n = 0
		for i in range(self.__lives):
			screen.blit(self.live_img, (0+n, s_height-50))
			n += 100

	def create_score(self):
		text = font.render("Score: " + str(self.__score), True, (255,255,255))
		screen.blit(text, [0,0])

	def create_game_over(self):
		if self.__lives < 0:
			if self.__score < 30:
				self.text = font.render("Kamu Terlalu Cupu score kamu : " +str(self.__score), True, (0,0,0))
			else:
				self.text = font.render("Kamu Hebat Banget score kamu : " +str(self.__score), True, (0,0,0))
			self.text_rect = self.text.get_rect()
			self.text_rect.center = (s_width/2, s_height/2)
			screen.blit(self.text, self.text_rect)
			pygame.display.update()
			pygame.time.delay(3000) 
			pygame.quit()

	def run_update(self):
		sprite_group.draw(screen)
		sprite_group.update()

	def run_game(self):
		self.create_background()
		self.create_player()
		self.create_enemy()
		self.create_boss()
		while True:
			screen.fill((135, 206, 250))
			self.playerbullet_hits_enemy()
			self.playerbullet_hits_boss()
			self.enemybullet_hits_player()
			self.bossbullet_hits_player()
			self.player_enemy_crash()
			self.player_boss_crash()
			self.create_lives()
			self.create_score()
			self.create_game_over()
			self.run_update()
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()

				if event.type == KEYDOWN:
					self.player.shoot()
					if event.key == K_ESCAPE:
						pygame.quit()
						sys.exit()

			pygame.display.update()
			clock.tick(FPS)

PlayGame().run_game()
