import sys
import pygame
from game_class import *


main_fon = pygame.image.load("data/main_fon.png")
main_fon = pygame.transform.scale(main_fon, (704, 704))


def get_font(size):
    pass


# класс начального экрана
def main_window():
    pygame.display.get_caption('Air Battles')  # название экрана

    while True:
        screen.blit(main_fon, (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render('Главное меню', True, '#b68f40')
        menu_rect = menu_text.get_rect(center=(352, 100))

        play_button = Button(pos=(352, 300), text_input=('Играть'), font=get_font(75),
                             base_color='b7fcd4', hovering_color='White')
        control_button = Button(pos=(352, 500), text_input=('Играть'), font=get_font(75),
                             base_color='b7fcd4', hovering_color='White')
        exit_game_button = Button(pos=(352, 700), text_input=('Играть'), font=get_font(75),
                             base_color='b7fcd4', hovering_color='White')

        screen.blit(menu_text, menu_rect)

        for button in [play_button, control_button, exit_game_button]:
            button.changeColor(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(menu_mouse_pos):
                    play()
                if control_button.checkForInput(menu_mouse_pos):
                    control()
                if exit_game_button.checkForInput(menu_mouse_pos):
                    exit_game()
                    sys.exit()

def play():
    pass


def control():
    pass


def exit_game():
    pass
