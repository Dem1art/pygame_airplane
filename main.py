import pygame
from pygame import mixer
from pygame.locals import *
import random


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()


# определите частоту кадров в секунду
clock = pygame.time.Clock()
fps = 60


screen_width = 704  # ширина
screen_height = 704  # высота

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Air Battles')


# определение шрифтов
font30 = pygame.font.SysFont('Arial', 30)
font40 = pygame.font.SysFont('Arial', 40)


# загрузка звука
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)  # громкость

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)


# игровые переменные
rows = 6  # строк
cols = 5  # столбцов
alien_cooldown = 1000  # перезарядка пули пришельцев
last_alien_shot = pygame.time.get_ticks()
countdown = 3  # обратный отсчёт
last_count = pygame.time.get_ticks()
game_over = 0  # тригер победы или поражения

# цвета
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)


# установка фото
bg = pygame.image.load("img/bg.png")  # задний фон


def draw_bg():
	screen.blit(bg, (0, 0))


# функция для создания текста
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


# класс самолёта
class MainAirplane(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/airplane_defender.png")  # изображение самолёта
		self.rect = self.image.get_rect()  # размер спрайта
		self.rect.center = [x, y]  # центр спрайта
		self.health_start = health  # стартовые жизни
		self.health_remaining = health  # оставшееся здоровье
		self.last_shot = pygame.time.get_ticks()  # последний выстрел
		self.last_ability = pygame.time.get_ticks()  # последнее исполюзование ульты
		self.heart = pygame.image.load('img/heart.png')
		self.heart.set_colorkey((255, 255, 255))

	def update(self):
		# скорость перемещения
		speed = 8
		# откат пули
		cooldown = 500  #  милисекунды
		game_over = 0
		ability_cooldawn = 10000


		# получаем нажатие клавиши
		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT] and self.rect.left > 0:
			self.rect.x -= speed
		if key[pygame.K_RIGHT] and self.rect.right < screen_width:
			self.rect.x += speed
		if key[pygame.K_UP] and self.rect.top > 0:
			self.rect.y -= speed
		if key[pygame.K_DOWN] and self.rect.bottom < screen_height:
			self.rect.y += speed

		# запись текущего времени
		time_now = pygame.time.get_ticks()
		# стрелять
		# проверка отката времени
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			laser_fx.play()
			bullet = Bullets(self.rect.centerx, self.rect.top)
			bullet_group.add(bullet)
			self.last_shot = time_now

		# откат ульты
		# использование ульты



		# обновить маску
		self.mask = pygame.mask.from_surface(self.image)

		# отображение жизней
		if self.health_remaining == 3:
			screen.blit(self.heart, (0, 0))
			screen.blit(self.heart, (30, 0))
			screen.blit(self.heart, (60, 0))
		elif self.health_remaining == 2:
			screen.blit(self.heart, (0, 0))
			screen.blit(self.heart, (30, 0))
		elif self.health_remaining == 1:
			screen.blit(self.heart, (0, 0))
		elif self.health_remaining <= 0:
			explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
			explosion_group.add(explosion)
			self.kill()
			game_over = -1
		return game_over


# класс снарядов
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/bullet.png")
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y -= 5
		if self.rect.bottom < 0:
			self.kill()
			# проверка столкновения
		if pygame.sprite.spritecollide(self, alien_group, True):
			self.kill()  # уничтожить спрайт
			explosion_fx.play()
			explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
			explosion_group.add(explosion)


# класс пришельцев
class Aliens(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/alien" + str(random.randint(1, 3)) + ".png")
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.move_counter = 0
		self.move_direction = 1

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 100:
			self.move_direction *= -1
			self.move_counter *= self.move_direction


# вражеские пули
class Alien_Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/alien_bullet.png")
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > screen_height:
			self.kill()
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
			self.kill()
			explosion2_fx.play()
			#reduce spaceship health
			spaceship.health_remaining -= 1
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
			explosion_group.add(explosion)




# класс взрыва
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f"img/exp{num}.png")
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
			# добавление изображение в список
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0


	def update(self):
		explosion_speed = 5
		# обновление анимации взрыва
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		# удалить взрыв если анимация закончилась
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()




# группы спрайтов
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


def create_aliens():
	# создание мобов
	for row in range(rows):
		for item in range(cols):
			alien = Aliens(150 + item * 100, 100 + row * 70)
			alien_group.add(alien)

create_aliens()


# создание персонажа
spaceship = MainAirplane(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)



run = True
while run:

	clock.tick(fps)

	#draw background
	draw_bg()


	if countdown == 0:
		#create random alien bullets
		#record current time
		time_now = pygame.time.get_ticks()
		#shoot
		if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
			attacking_alien = random.choice(alien_group.sprites())
			alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
			alien_bullet_group.add(alien_bullet)
			last_alien_shot = time_now

		#check if all the aliens have been killed
		if len(alien_group) == 0:
			game_over = 1

		if game_over == 0:
			#update spaceship
			game_over = spaceship.update()

			#update sprite groups
			bullet_group.update()
			alien_group.update()
			alien_bullet_group.update()
		else:
			if game_over == -1:
				draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
			if game_over == 1:
				draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

	if countdown > 0:
		draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
		draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
		count_timer = pygame.time.get_ticks()
		if count_timer - last_count > 1000:
			countdown -= 1
			last_count = count_timer


	#update explosion group
	explosion_group.update()


	#draw sprite groups
	spaceship_group.draw(screen)
	bullet_group.draw(screen)
	alien_group.draw(screen)
	alien_bullet_group.draw(screen)
	explosion_group.draw(screen)


	#event handlers
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False


	pygame.display.update()

pygame.quit()
