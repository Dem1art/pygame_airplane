import pygame
from pygame import mixer
import random


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()


pygame.mouse.set_visible(False)


# определите частоту кадров в секунду
clock = pygame.time.Clock()
fps = 60


SCREEN_WIDTH = 704  # ширина
SCREEN_HEIGHT = 704  # высота


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


TEXT_COL = (200, 200, 200)


# определение шрифтов
font = pygame.font.SysFont("arialblack", 40)
font30 = pygame.font.SysFont('Arial', 30)
font40 = pygame.font.SysFont('Arial', 40)


# загрузка звука
explosion_fx = pygame.mixer.Sound("img/explosion.wav")  # звук взрыва
explosion_fx.set_volume(0.25)  # громкость


explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")  # звук взрыва
explosion2_fx.set_volume(0.25)


laser_fx = pygame.mixer.Sound("img/laser.wav")  # звук выстрела
laser_fx.set_volume(0.25)


# игровые переменные
rows = 6  # строк
cols = 5  # столбцов
alien_cooldown = 1000  # перезарядка пули пришельцев
last_alien_shot = pygame.time.get_ticks()
countdown = 3  # обратный отсчёт
last_count = pygame.time.get_ticks()
game_over = 0  # тригер победы или поражения
hp_aliens = 1  # очки здоровья врагов
lvl = 1  # уровень
score = 0  # рекорд
new_num = 0


with open('max_score.txt', 'r', encoding='utf-8') as max_score:
	best_score = max_score.read()


# цвет
white = (255, 255, 255)


# установка фото
bg = pygame.image.load("img/bg.png")  # задний фон
main_fon = pygame.image.load('img/main_fon.png')
MANUAL_CURSOR = pygame.image.load('img/cursor.png')


def draw_bg(background):
	screen.blit(background, (0, 0))


# функция для создания текста
def draw_text(text, typeface, text_col, x, y):
	img = typeface.render(text, True, text_col)
	screen.blit(img, (x, y))


class Button:
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		# получить положение мыши
		pos = pygame.mouse.get_pos()

		# проверьте условия наведения курсора мыши и щелчка
		if self.rect.collidepoint(pos):

			if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		# кнопка рисования на экране
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action


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
		self.heart = pygame.image.load('img/heart.png')
		self.heart.set_colorkey((255, 255, 255))
		self.mask = ''

	def update(self):
		# скорость перемещения
		speed = 8
		# откат пули
		cooldown = 500  # милисекунды
		game_over = 0

		# получаем нажатие клавиши
		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT] and self.rect.left > 0:
			self.rect.x -= speed

		if key[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
			self.rect.x += speed

		if key[pygame.K_UP] and self.rect.top > 0:
			self.rect.y -= speed

		if key[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
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

		# проверкаа пересечения с врагом
		if pygame.sprite.spritecollide(self, alien_group, True):
			self.health_remaining -= 1
			explosion_fx.play()
			explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
			explosion_group.add(explosion)

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
		self.alien_hp = lvl

	def update(self):
		global score
		if pygame.sprite.spritecollide(self, bullet_group, True):
			self.alien_hp -= 1

			if self.alien_hp <= 0:
				score += 100
				self.kill()  # уничтожить спрайт
				explosion_fx.play()
				explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
				explosion_group.add(explosion)
		self.rect.x += self.move_direction
		self.move_counter += 1

		if abs(self.move_counter) > 100:
			self.move_direction *= -1
			self.move_counter *= self.move_direction


# вражеские пули
class AlienBullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/alien_bullet.png")
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > SCREEN_HEIGHT:
			self.kill()
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
			self.kill()
			explosion2_fx.play()
			# уменьшить хп корабля
			spaceship.health_remaining -= 1
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
			explosion_group.add(explosion)


# класс взрыва
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = []

		for nam in range(1, 6):
			img = pygame.image.load(f"img/exp{nam}.png")
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
	for el in alien_group:
		el.kill()

	# создание мобов
	for row in range(rows):
		for item in range(cols):
			alien = Aliens(150 + item * 100, 100 + row * 70)
			alien_group.add(alien)


# пределение фотографий кнопок
resume_img = pygame.image.load("img/button_resume.png").convert_alpha()  # кнопка продолжения
quit_img = pygame.image.load("img/button_quit.png").convert_alpha()  # кнопка выхода
keys_img = pygame.image.load('img/button_keys.png').convert_alpha()  # кнопка биндов
back_img = pygame.image.load('img/button_back.png').convert_alpha()  # кнопка возвращения


resume_button = Button(260, 125, resume_img, 1)  # кнопка продолжения
quit_button = Button(290, 475, quit_img, 1)  # кнопка выхода
keys_button = Button(200, 300, keys_img, 1)  # кнопка биндов
back_button = Button(290, 550, back_img, 1)  # кнопка возвращения


game_paused = True  # статус паузы
menu_state = "main"  # статус меню


# основной цикл игры
run = True
while run:
	clock.tick(fps)
	if game_paused:
		draw_bg(main_fon)
		pygame.display.set_caption('Space Battles')
		# состояние меню

		if menu_state == 'main':
			# экранные кнопки паузы
			draw_text(f'LVL:{lvl}', font, TEXT_COL, 580, 0)
			draw_text(f'Очки:{score}', font, TEXT_COL, 0, 660)
			screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

			if resume_button.draw(screen):
				game_paused = False
				# создание врагов
				create_aliens()

				# создание персонажа
				for i in spaceship_group:
					i.kill()
				spaceship = MainAirplane(int(SCREEN_WIDTH / 2), SCREEN_HEIGHT - 100, 3)
				spaceship_group.add(spaceship)

				# очистка групп спрайтов
				# группа моих пуль
				for i in bullet_group:
					i.kill()

				# группа пуль врагов
				for i in alien_bullet_group:
					i.kill()

			screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

			if quit_button.draw(screen):
				run = False
				with open('max_score.txt', 'r+', encoding='utf-8') as file:
					num = file.read()

					if int(num) < score:
						new_num = num.replace(num, str(score))

				if int(new_num) > int(num):

					with open('max_score.txt', 'w', encoding='utf-8') as file:
						file.write(new_num)

			screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

			if keys_button.draw(screen):
				menu_state = 'keys'

			screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

		if menu_state == 'keys':
			draw_text('Движение героя - стрелки', font, TEXT_COL, 50, 100)
			draw_text('Стрельба - space', font, TEXT_COL, 180, 250)
			draw_text(f'Лучший рекорд:{best_score}', font, TEXT_COL, 120, 400)
			screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

			if back_button.draw(screen):
				menu_state = 'main'

		screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

	else:
		draw_bg(bg)
		screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))
		menu_state = 0
		draw_text(f'Очки:{score}', font, TEXT_COL, 0, 660)

		if countdown == 0:
			# создание пуль из рандомного врага
			# запись текущего времени
			time_now = pygame.time.get_ticks()

			# стрелять
			if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
				attacking_alien = random.choice(alien_group.sprites())
				alien_bullet = AlienBullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
				alien_bullet_group.add(alien_bullet)
				last_alien_shot = time_now

			# проверка убиты ли все пришельци
			if len(alien_group) == 0:
				game_over = 1

			if game_over == 0:
				# обновление гг
				game_over = spaceship.update()

				# обновление групп спрайтов
				bullet_group.update()
				alien_group.update()
				alien_bullet_group.update()

			else:

				if game_over == -1:
					draw_text('GAME OVER!', font40, white, int(SCREEN_WIDTH / 2 - 100), int(SCREEN_HEIGHT / 2 + 50))

					if back_button.draw(screen):
						game_paused = True
						menu_state = 'main'
						countdown = 3
						game_over = 0

				screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

				if game_over == 1:
					draw_text('YOU WIN!', font40, white, int(SCREEN_WIDTH / 2 - 100), int(SCREEN_HEIGHT / 2 + 50))

					if back_button.draw(screen):
						menu_state = 'main'
						game_paused = True
						countdown = 3
						game_over = 0
						if lvl < 6:
							lvl += 1

				screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

		if countdown > 0:
			draw_text('GET READY!', font40, white, int(SCREEN_WIDTH / 2 - 110), int(SCREEN_HEIGHT / 2 + 50))
			draw_text(str(countdown), font40, white, int(SCREEN_WIDTH / 2 - 10), int(SCREEN_HEIGHT / 2 + 100))
			count_timer = pygame.time.get_ticks()

			if count_timer - last_count > 1000:
				countdown -= 1
				last_count = count_timer

		# обновить взрывную группу
		explosion_group.update()

		# нарисуйте группы спрайтов
		spaceship_group.draw(screen)
		bullet_group.draw(screen)
		alien_group.draw(screen)
		alien_bullet_group.draw(screen)
		explosion_group.draw(screen)

	# обработчики событий
	for event in pygame.event.get():

		if event.type == pygame.MOUSEMOTION:
			# рисование курсора
			screen.blit(MANUAL_CURSOR, (pygame.mouse.get_pos()))

		if event.type == pygame.QUIT:
			run = False

			with open('max_score.txt', 'r+', encoding='utf-8') as file:
				num = file.read()

				if int(num) < score:
					new_num = num.replace(num, str(score))

			if int(new_num) > int(num):
				with open('max_score.txt', 'w', encoding='utf-8') as file:
					file.write(new_num)

	pygame.display.update()

pygame.quit()
