import random							# Memunculkan enemy secara random
import pygame							# Memunculkan background
from pygame import mixer				# Mengeload background music
from pygame.locals import *				# Untuk membuat layar fullscreen
from abc import ABC, abstractmethod		# Modul abstract class


pygame.init()

# List gambar yang digunakan
player_ship = 'assets/Gambar/player_ship.png'
enemy_ship = 'assets/Gambar/enemy1_ship.png'
boss_ship = 'assets/Gambar/enemy2_ship.png'
player_bullet = 'assets/Gambar/pbullet.png'
enemy_bullet = 'assets/Gambar/enemybullet.png'
boss_bullet = 'assets/Gambar/bossbullet.png'

# Mengatur ukuran layar dan frame rate per detik
screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()
clock = pygame.time.Clock()
FPS = 60

# Mengelompokkan ke dalam sprite group
background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
bossbullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()

# Mengatur font
def get_font(size): 
    return pygame.font.Font("assets/font.ttf", size)

# Membuat class abstrak dan method abstrak
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

# Membuat class background dari class pygame.sprite.Sprite
class Background(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		# Memberikan backsound dan membuat gambar pada background
		mixer.music.load('assets/Audio/background.wav')
		mixer.music.play(-1)
		#atribut yang diguakan terdapat gambar burung sebagai tekstur
		#rect atribut untuk mengatur pergerakan dan letak burung
		self.image = pygame.image.load('assets/Gambar/bird.png')
		self.image.set_colorkey('black')
		self.rect = self.image.get_rect()

	#fungsi untuk membuat gambar burung bergerak
	def update(self):
        #diawali posisi y dan x 1 lalu bertambah 1 terusmenerus 
		#sehingga burung selalu bergerak terusmenerus
		self.rect.y += 1
		self.rect.x += 1
        #untuk mengembalikan posisi burung keposisi awal jika telah melewati layar 
		if self.rect.y > s_height:
			self.rect.y = random.randrange(-10, 0)
			self.rect.x = random.randrange(-400, s_width)

#kelas player untuk mengatur semua pergerakan yang dilakukan playe
class Player(pygame.sprite.Sprite):
	def __init__(self, img):
		super().__init__()
        #atribut yang digunakan kelas player
		#terdapat gambar sebagai karakter dari player
		#rect sebagai pengatur posisi dan pergerakan playe
		self.image = pygame.image.load(img)
		self.rect = self.image.get_rect()
		self.image.set_colorkey('black')
		self.alive = True
		#untuk menghitung durasi hilang nya pesawat dari layar
		self.count_to_live = 0 
		#kondisi untuk peluru dari pesawat aktiv atau tidak
		self.activate_bullet = True
		#menghitung durasi ketika pesawat dalm keadaan transparan
		self.alpha_duration = 0

	#fungsi untuk mengatur seluruh pergerakan dari pesawat player
	def update(self):
		#jika pesawat player hidup
		if self.alive:
			#tampilan pesawat player kan transparan selama durasi 170
			#dan pesawat player tidak akan terkena tembakan selama tampilan pesawat transparan
			self.image.set_alpha(80)
			self.alpha_duration += 1
			if self.alpha_duration > 170:
				self.image.set_alpha(255)
			#pergerakan posisi dari pesawat player mengikuti posisi dari mouse kita
			mouse = pygame.mouse.get_pos()
			self.rect.x = mouse[0] - 20
			self.rect.y = mouse[1] + 40
		else:
			self.alpha_duration = 0
			#mengatur posisi dari ledakan pesawat player
			expl_x = self.rect.x + 20
			expl_y = self.rect.y + 40
			#instansiasi kelas Explosion
			explosion = Explosion(expl_x, expl_y)
			explosion_group.add(explosion)
			sprite_group.add(explosion)
			pygame.time.delay(22)
			#jika player terkena peluru dari musuh maka pesawat player akan hilang
			self.rect.y = s_height + 200
			#mengembalikan pesawat player jika nya masih ada
			self.count_to_live += 1
			#pesawat kembali jika durasi hilang sanmpai 100
			if self.count_to_live > 100:
				#pesawat akan hidup kembai
				self.alive = True
				#durasi dari pesawat hilang di kembalikan ke 0
				self.count_to_live = 0
				#peluru akan di aktivkan kembali sehingga dapat menembak kembali
				self.activate_bullet = True

    #fungsi shoot untuk mengatur kapan muncul nya peluru 
	#dan kapan hilang nya peluru
	def shoot(self):
		if self.activate_bullet:
            #instansiasi kelas player bullet
			bullet = PlayerBullet(player_bullet)
			bullet_sound = mixer.Sound('assets/Audio/shoot.mp3')
			bullet_sound.play()
            #muncul nya peluru akan mengikuti posisi dimana mouse kita berada
			mouse = pygame.mouse.get_pos()
			bullet.rect.x = mouse[0]
			bullet.rect.y = mouse[1]
            #meload gambar kedalam grub
			playerbullet_group.add(bullet)
			sprite_group.add(bullet)

	def dead(self):
		#jika pesawat player terkena peluru musuh maka akan bernilai false artinya mati
		self.alive = False
		#pesawat akan mati dan peluru dari pesawat di matikan
		self.activate_bullet = False

#kelas enemy untuk mengatur pergerakan dan kemunculan dari pesawat musuh
#merupakan kelas turunan dari kelas Player
class Enemy(Player):
	def __init__(self, img):
		super().__init__(img)
        #atribut yang digunakan
		#terdapat rect x dan y untuk mengatur pergerakan dan posisi si musuh
		self.rect.x = random.randrange(0, s_width)
		self.rect.y = random.randrange(-500, 0)
		screen.blit(self.image, (self.rect.x, self.rect.y))

    #fungsi untuk mengatur pergerakan dan posisi si musuh akan muncul
	def update(self):
        #posisi y musuh di beri y +=1 maka si musuh akan ergerak terus kebawah
		self.rect.y += 1
        #kondisi jika si musuh telah melewati batas layar game maka pesawat musuh
		#akan kembali lagi ke atas
		if self.rect.y > s_height:
			self.rect.x = random.randrange(0, s_width)
			self.rect.y = random.randrange(-2000, 0)
		self.shoot()

    #fungsi untuk mengatur kemunculan peluru dan pergerakan peluru musuh
	def shoot(self):
        #peluru musuh diberi kondisi jika posisi y musuh berada di 0, 30, 70, 300, 700
		#maka peluru akan muncul
		if self.rect.y in (0, 30, 70, 300, 700):
            #instansiasi kelas EnemyBullet
			enemybullet = EnemyBullet(enemy_bullet)
            # x dan y di beri nilai sama dengan posisi si pesawat musuh
			# x dan y di beri +20 +50 agar peluru muncul tepat di depan pesawat musuh
			enemybullet.rect.x = self.rect.x + 20
			enemybullet.rect.y = self.rect.y + 50
			enemybullet_group.add(enemybullet)
			sprite_group.add(enemybullet)

#kelas Boos untuk mengatur pergerakan dan kemunculan pesawat boos
#kelas ini merupakan turunan dari kelas Enemy
class Boss(Enemy):
	def __init__(self, img):
		super().__init__(img)
        #atribut yang digunakan
		#atribut dibawah adalah sebuah nialai untuk mengatur pergerakan pesawat boss
		self.rect.x = -200 
		self.rect.y = 200 
		self.move = 1

    #fungsi untuk mengatur pergerakan pesawat boss
	def update(self):
        #x pesawat bos di eri nilai +1 
		#sehingga boss akan bergerak menyamping
		#jika nilai x - maka akan bergerak ke kiri begitupun sebalik nya
		self.rect.x += self.move 
        #kondisi jika pesawat boss melebihi layar maka nilai x akan dikali -1
		#sehingga pergerakan secara zigzag 
		if self.rect.x > s_width + 200:
			self.move *= -1 
		elif self.rect.x < -200:
			self.move *= -1
		self.shoot()

    #fungsi untuk mengatur kemunculan peluru dari pesawat boss
	def shoot(self):
        #kondisi kemunculan peluru jika nilai x dari posisi pesawat di beri modulus 50
		#dan hasil nya 0 maka peluru akan muncul
		if self.rect.x % 50 == 0:
            #instansiasi dari kelas EnemyBullet
			bossbullet = EnemyBullet(boss_bullet)
            #sama seperti enemy peluru muncul mengikuti posisi dari pesawat
			# nilai x dan y diberi +50 dan +70 agar peluru tepat muncul di depat pesawat
			bossbullet.rect.x = self.rect.x + 50
			bossbullet.rect.y = self.rect.y + 70
			bossbullet_group.add(bossbullet)
			sprite_group.add(bossbullet)

#kelas PlayerBullet untuk mengatur pergerakan peluru dari pesawat player
class PlayerBullet(pygame.sprite.Sprite):
	def __init__(self, img):
		super().__init__()
        #atribut yang digunakan
		#terdapat gambar dari peluru itu sendiri
		#lalu rect adalah sebuah nilai yang dapat mengatur pergerakan dari peluru tersebut
		self.image = pygame.image.load(img)
		self.rect = self.image.get_rect()
		self.image.set_colorkey('black')

    #fungsi untuk mengatur pergerakan peluru
	def update(self):
        #peluru diposisi y di kurang 5 secara terus menerus
		#sehingga peluru akan bergerak terus ke atas
		self.rect.y -= 5
        #jika perluru melebihi layar maka peluru akan dihapus
		if self.rect.y < 0:
			self.kill()

#kelas untuk mengatur pergeraka dari peluru enemy dan boss
#kelas ini merupakan turunan dari kelas PlayerBullet
class EnemyBullet(PlayerBullet):
	def __init__(self, img):
		super().__init__(img)
		self.image.set_colorkey('white')

    #fungsi untuk mengatur pergerakan peluru
	def update(self):
        #posisi y dari peluru di beri +3
		#sehing peluru akan terus berjalan kearah bawah
		self.rect.y += 3
        #jika peluru melebihi layar maka peluru akan di hapus
		if self.rect.y > s_height:
			self.kill()

# Membuat class Explosion dari class pygame.sprite.Sprite
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		# memberikan efek suara ledakan dan efek animasi saat player, enemy, dan boss mati
		self.img_list = []
		explosion_sound = mixer.Sound('assets/Audio/explosion.wav')
		explosion_sound.play()
		for i in range(1, 6):
			img = pygame.image.load(f'assets/Gambar/exp{i}.png').convert()
			img.set_colorkey('black')
			img = pygame.transform.scale(img, (120, 120))
			self.img_list.append(img)
		self.index = 0
		self.image = self.img_list[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.count_delay = 0 

	# Mengatur efek delay ledakan
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

# Menerapkan fungsi abstract pada class Game
class PlayGame(Game):
	def __init__(self):
		# constructor
		self.__count_hit = 0
		self.__count_hit2 = 0
		self.__lives = 3
		self.__score = 0
		self.pause_objek = True

	#fungsi untuk membuat pesawat musuh menghilang ketika terkena peluru player
	def playerbullet_hits_enemy(self):
		hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
		for i in hits:
			#nilai dari count_hit diberi +1
			#sehingga jika musuh terkena peluru player maka count_hit akan bertambah 1
			self.__count_hit += 1
			#jika count_hit mencapai 3 maka pesawat musuh akan meledak
			#dan akan kembali keposisi semula di awal dia muncul
			if self.__count_hit == 3:
				#untuk menghitung score ketika telah menghancurkan pesawat musuh
				self.__score += 1
				expl_x = i.rect.x + 20
				expl_y = i.rect.y + 40
				#instansisasi kelas Explosion agar tampil gambar ledakan 
				explosion = Explosion(expl_x, expl_y)
				explosion_group.add(explosion)
				sprite_group.add(explosion)
				#mengembalikan posisi pesawat musuh keposisi semula dia muncul
				i.rect.x = random.randrange(0, s_width)
				i.rect.y = random.randrange(-3000, -100)
				#nilai count_hit menjadi 0 kembali
				self.__count_hit = 0

	#fungsi ini samaseperti fungsi di atas
	#yang membedakam batas count_hit 20 dan score yang didapat akan bertambah 8
	#karna fungsu ini untuk mengahancurkan pesawat boss ketika terkena peluru dari player
	def playerbullet_hits_boss(self):
		hits = pygame.sprite.groupcollide(boss_group, playerbullet_group, False, True)
		for i in hits:
			self.__count_hit2 += 1
			if self.__count_hit2 == 20:
				self.__score += 5
				expl_x = i.rect.x + 50
				expl_y = i.rect.y + 60
				explosion = Explosion(expl_x, expl_y)
				explosion_group.add(explosion)
				sprite_group.add(explosion)
				i.rect.x = -199
				self.__count_hit2 = 0

	#fungsi untuk mengahncurkan pesawat player ketika player terkena peluru dari pesawat musuh
	def enemybullet_hits_player(self):
		#jika tampilan dari pesawat full tidak transparan maka pesawat dapat ditembak oleh musuh
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
			#jika pesawat terkenan peluru musuh
			if hits:
				#nyawa akan berkurang 1
				self.__lives -= 1
				#pemanggilan method dead pada kelas palyer
				self.player.dead()

	#fungsi untuk mengahncurkan pesawat player ketika player terkena peluru dari pesawat boss
	def bossbullet_hits_player(self):
		#jika tampilan dari pesawat full tidak transparan maka pesawat dapat ditembak oleh boss
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, bossbullet_group, True)
			#jika pesawat terkenan peluru musuh
			if hits:
				#nyawa akan berkurang 1
				self.__lives -= 1
				#pemanggilan method dead pada kelas palyer
				self.player.dead()

	def player_enemy_crash(self):
		#jika tampilan dari pesawat full tidak transparan maka pesawat dapat bertabrakan dengan musuh
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
			#jika pesawat bertabrakan 
			if hits:
				#setiap kali terjadi tabrakan posisi dari setiap pesawat akan di riset
				for i in hits:
					#posisi dari peswat musuh akan kembaili keposisi awal dia muncul
					i.rect.x = random.randrange(0, s_width)
					i.rect.y = random.randrange(-3000, -100)
					#nyawa dari player akan berkurang 1
					self.__lives -= 1
					#pemanggilan method dead pada kelas palyer
					self.player.dead()

	def player_boss_crash(self):
		#jika tampilan dari pesawat full tidak transparan maka pesawat dapat bertabrakan dengan boss
		if self.player.image.get_alpha() == 255:
			hits = pygame.sprite.spritecollide(self.player, boss_group, False)
			#jika pesawat bertabrakan 
			if hits:
				#setiap kali terjadi tabrakan posisi dari setiap pesawat akan di riset
				for i in hits:
					#posisi dari peswat boss akan kembaili keposisi awal dia muncul
					i.rect.x = -199
					#nyawa dari player akan berkurang 1
					self.__lives -= 1
					#pemanggilan method dead pada kelas palyer
					self.player.dead()

	# Mengatur jumlah, ukuran, dan posisi muncul gambar burung pada layar
	def create_background(self):
		#perulangan ini berfungsi untuk menampilkan banyak nya tesktur burung
		for i in range(10):
			#untuk menagtur ukuran burung dari 1 pixel sampai 6 pixel
			x = random.randint(1,6)
			#instansiasi kelas
			background_image = Background(x,x)
			background_image.rect.x = random.randrange(0, s_width)
			background_image.rect.y = random.randrange(0, s_height)
			background_group.add(background_image)
			sprite_group.add(background_image)

	# Menampilkan gambar player pada layar
	def create_player(self):
		self.player = Player(player_ship)
		player_group.add(self.player)
		sprite_group.add(self.player)

	# Mengatur jumlah enemy dan menampilkannya pada layar
	def create_enemy(self):
		for i in range(15):
			self.enemy = Enemy(enemy_ship)
			enemy_group.add(self.enemy)
			sprite_group.add(self.enemy)

	# Mengatur jumlah boss dan menampilkannya pada layar
	def create_boss(self):
		for i in range(1):
			self.boss = Boss(boss_ship)
			boss_group.add(self.boss)
			sprite_group.add(self.boss)

	# menampilkan posisi nyawa player yang tersisah pada layar
	def create_lives(self):
		self.live_img = pygame.image.load(player_ship)
		self.live_img = pygame.transform.scale(self.live_img, (30,30))
		n = 0
		for i in range(self.__lives):
			screen.blit(self.live_img, (0+n, s_height-50))
			n += 100

	# menampilkan score pada layar
	def create_score(self):
		font = get_font(20)
		text = font.render("Score: " + str(self.__score), True, ('black'))
		screen.blit(text, [5,5])

	#untuk mangatur tesk yang ada di layar start
	def teks_start(self):
		font = get_font(40)
		text = font.render ('JET WAR', True, 'black')
		text_rect = text.get_rect(center = (s_width/2, s_height/2))
		screen.blit(text, text_rect)

		font = get_font(25)
		text1 = font.render ('Press enter to start or esc to exit', True, 'black')
		text_rect1 = text1.get_rect(center = (s_width/2, s_height/2+55))
		screen.blit(text1, text_rect1)

		pesawat = pygame.image.load('assets/Gambar/player_ship.png')
		pesawat_rect = pesawat.get_rect(center = (s_width/2, s_height/2-70))
		screen.blit( pesawat, pesawat_rect)

	#mengatur tombol yang ada di layar start
	def create_start(self):
		self.create_background()
		while True:
			screen.fill((135, 206, 250))
			self.teks_start()
			self.run_update()
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					quit()
				
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						pygame.quit()
						quit()
				
					if event.key == K_RETURN:
						self.run_game()

			pygame.display.update()
	
	#mengatur teks yang ada di layar pause
	def teks_pause(self):
		font = get_font(40)
		text = font.render ('PAUSE', True, 'black')
		text_rect = text.get_rect(center = (s_width/2, s_height/2))
		screen.blit(text, text_rect)

		font = get_font(25)
		text1 = font.render ('Press enter to continue or esc to exit', True, 'black')
		text_rect1 = text1.get_rect(center = (s_width/2, s_height/2+55))
		screen.blit(text1, text_rect1)

	#mengatur tombol yang ada di layar pause
	def create_pause(self):
		self.pause_objek = False
		while True:
			self.teks_pause()
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					quit()
				
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						pygame.quit()
						quit()
				
					if event.key == K_RETURN:
						self.run_game()

			pygame.display.update() 
                                    
	# Kondisi jika game telah berakhir
	def create_game_over(self):
		#jika nyawa dari player kurang dari 0 maka akan menampilkan game over
		if self.__lives < 0:
			font = get_font(40)
			text_gameover = font.render ('GAME OVER', True, 'black')
			text_rect_gameover = text_gameover.get_rect(center = (s_width/2, s_height/2))
			screen.blit(text_gameover, text_rect_gameover)

			font = get_font(20)
			#jika score nya kurang dari 30
			if self.__score < 30:
				self.text = font.render("Kamu Terlalu Cupu score kamu : " +str(self.__score), True, (0,0,0))
			#jika score nya kurang lebih dari 30
			else:
				self.text = font.render("Kamu Hebat Banget score kamu : " +str(self.__score), True, (0,0,0))
			#pengaturan tampilan dari layar game over
			self.text_rect = self.text.get_rect()
			self.text_rect.center = (s_width/2, s_height/2+55)
			screen.blit(self.text, self.text_rect)

			pygame.display.update()
			pygame.time.delay(8000) 
			pygame.quit()
		
	# Menampilkan gambar burung dan membuatnya bergerak
	def run_update(self):
		sprite_group.draw(screen)
		sprite_group.update()

	# Menjalankan game
	def run_game(self):
		if self.pause_objek:
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
					quit()

				if event.type == KEYDOWN:
					if event.key == K_SPACE:
						self.player.shoot()
					
					if event.key == K_RETURN:
						self.create_pause()
						
					if event.key == K_ESCAPE:
						pygame.quit()
						quit()
					
			pygame.display.update()
			clock.tick(FPS)

PlayGame().create_start()
