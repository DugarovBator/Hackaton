import pygine as pg
from pygine.scene import *
from pygine.effects import create_explosion, create_smoke, create_sparkles, update_effects, draw_effects
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600

game = pg.Game(800, 600, "Система сцен")

# Создание менеджера сцен
scene_manager = SceneManager()


class MenuScene(Scene):
    """Сцена главного меню"""
    
    def __init__(self):
        super().__init__("menu")
        self.title_text = "ГЛАВНОЕ МЕНЮ"
        self.instruction_text = "Нажмите ПРОБЕЛ для перехода в игру"
    
    def update(self, dt):
        # Переход в игру при нажатии пробела
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            scene_manager.switch_to("game")
    
    def draw(self, screen):
        # Фон меню
        screen.fill((100, 50, 150))
        
        # Отображение заголовка (центрировано)
        pg.Text(20, 20, self.title_text, size=32, color=(255, 255, 0)).draw(screen)
        
        # Отображение инструкции (центрировано)
        pg.Text(20, 60, self.instruction_text, size=20, color=(255, 255, 255)).draw(screen)


class GameScene(Scene):
    """Игровая сцена"""
    
    def __init__(self):
        super().__init__("game")
        # Создание игрока
        self.player = pg.AnimatedSprite("player_sheet.png", (21, 21), (400, 300))
        self.player.add_animation("idle", [0], fps=1)
        self.player.add_animation("run", [1, 2, 3, 4, 5, 6], fps=5, loop=True)
        self.player.play_animation("run")
        self.player.set_scale(16.0)

        self.instruction_text = "Нажмите ESC для возврата в меню" 

    def update(self, dt):
        # Перемещение игрока за курсором мыши
        # mouse_x, mouse_y = pygame.mouse.get_pos()

        # self.player.x = mouse_x
        # self.player.y = mouse_y
        self.player.play_animation('run')
        # Возврат в меню при нажатии Escape
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            scene_manager.switch_to("menu")

            
    
    def draw(self, screen):
        # Фон игры
        screen.fill((50, 100, 50))
        
        # Отрисовка игрока
        screen.blit(self.player.image, self.player.rect)
        
        # Отображение инструкции
        pg.Text(20, 20, self.instruction_text, size=18, color=(255, 255, 255)).draw(screen)


# Создание и добавление сцен в менеджер
menu_scene = MenuScene()
game_scene = GameScene()

scene_manager.add_scene(menu_scene)
scene_manager.add_scene(game_scene)

# Установка начальной сцены
scene_manager.switch_to("menu")

def update():
    dt = game.get_delta_time()
    scene_manager.update(dt)
    


def draw():
    scene_manager.draw(game.screen)


# Запуск игры
game.run(update, draw) 
