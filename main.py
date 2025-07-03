"""
Пример системы управления сценами (состояниями) игры.
Демонстрирует переключение между главным меню и игровой сценой.
"""

import pygame
import pygine as pg
from pygine.scene import Scene, SceneManager

WIDTH,HEIGHT = 800, 600
IDLE_TO_STAND = 2.0

# Инициализация игры
game = pg.Game(WIDTH, HEIGHT, "Duality", background_image="background.png")

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
        self.instruction_text = "Нажмите ESC для возврата в меню"
        # Создание игрока
        self.player = pg.AnimatedSprite("player_sheet.png", (21, 21))
        self.player.add_animation("stance", [0], fps=8, loop=True)
        self.player.add_animation("walk", [1, 7, 8, 9], fps=8, loop=True)
        self.player.add_animation("run", [1, 7, 8, 9], fps=24, loop=True)
        self.player.add_animation("jump", [9, 10], fps=10, loop=False)
        self.player.add_animation("duck", [2, 3], fps=100, loop=False)
        self.player.add_animation("teleport1", [2], fps=10, loop=False)
        self.player.add_animation("teleport2", [3], fps=10, loop=False)
        self.player.set_scale(3.0)

        self.initial_ground_y = HEIGHT - (self.player.frame_size[1] * self.player.scale) / 2
        self.player.set_position(WIDTH // 2, self.initial_ground_y)
        self.player.play_animation("stance")

        # Скорости движения
        self.speed = 200
        self.run_speed = 400

        # Параметры прыжка
        self.jump_speed = 0
        self.gravity = 1500
        self.jump_power = -500

        self.idle_timer = 0.0  # таймер покоя

    

        game.add_sprite(self.player)
    
    def update(self, dt):
        # game.set_background_image("background.png")
        keys = pygame.key.get_pressed()

    # Вычисляем границу земли и половину ширины на каждый кадр – учитываем масштаб
        half_w = (self.player.frame_size[0] * self.player.scale) / 2
        half_h = (self.player.frame_size[1] * self.player.scale) / 2
        ground_y = HEIGHT / 2 - half_h
        
        # Стоим ли на земле?
        on_ground = self.player.y >= ground_y - 0.1
        is_teleport = False
        # Приседаем
        if keys[pygame.K_s] and on_ground:
            self.player.play_animation("duck")
            self.player.set_collision_rect(64, 32, 0, 0)
        else:
            self.player.reset_collision_to_default()

            # Прыгаем
            if keys[pygame.K_SPACE] and on_ground:
                self.jump_speed = self.jump_power
                self.player.play_animation("jump")

            # Ходим или бегаем
            elif keys[pygame.K_a]:
                self.player.x -= (self.run_speed if keys[pygame.K_LSHIFT] else self.speed) * dt
                if on_ground:
                    self.player.play_animation("run" if keys[pygame.K_LSHIFT] else "walk")
                self.player.mirror(True)
            elif keys[pygame.K_d]:
                self.player.x += (self.run_speed if keys[pygame.K_LSHIFT] else self.speed) * dt
                if on_ground:
                    self.player.play_animation("run" if keys[pygame.K_LSHIFT] else "walk")
                self.player.mirror(False)

                
        # Логика покоя
        moving = keys[pygame.K_a] or keys[pygame.K_d]
        crouching = keys[pygame.K_s]
        jumping = not on_ground

        if not moving and not crouching and not jumping:
            self.idle_timer += dt
            if self.idle_timer < IDLE_TO_STAND and self.player.get_current_animation() != "stance":
                self.player.play_animation("stance")
            elif self.idle_timer >= IDLE_TO_STAND and self.player.get_current_animation() != "stand":
                self.player.play_animation("stand")
        else:
            self.idle_timer = 0.0

        if keys[pygame.K_q] and on_ground:
            if self.player.y >= HEIGHT / 2 - half_h:
                is_teleport = True
                self.player.play_animation("teleport1")
                ground_y = HEIGHT - half_h
                self.player.y = self.player.y + HEIGHT / 2
                self.player.play_animation("teleport2")
                is_teleport = False
        if keys[pygame.K_e] and on_ground:
            if self.player.y < HEIGHT / 2 - half_h:
                is_teleport = True
                self.player.play_animation("teleport1")
                ground_y = HEIGHT / 2 - half_h
                self.player.y = self.player.y - HEIGHT / 2
                self.player.play_animation("teleport2")
                is_teleport = False

        
        # Применяем гравитацию
        self.jump_speed += self.gravity * dt
        self.player.y += self.jump_speed * dt

        # Не проваливаемся сквозь землю
        if self.player.y > ground_y and not is_teleport:
            self.player.y = ground_y
            self.jump_speed = 0

        # Не выходим за пределы экрана
        if self.player.x < half_w:
            self.player.x = half_w
        elif self.player.x > WIDTH - half_w:
            self.player.x = WIDTH - half_w
            
            # Возврат в меню при нажатии Escape

        if keys[pygame.K_ESCAPE]:
            scene_manager.switch_to("menu")
    
    def draw(self, screen):
        # Фон игры
        screen.fill((50, 100, 50))
        
        # Отрисовка игрока
        screen.blit(self.player.image, self.player.rect)
        
        # Отображение инструкции
        pg.Text(20, 20, self.instruction_text, size=18, color=(255, 255, 255)).draw(screen)


class FirstLevel(GameScene):
    def __init__(self):
        super().__init__()
        self.door = pg.AnimatedSprite("door.png", (21, 21))
        self.key = pg.AnimatedSprite("key.png", (21, 21))
        self.close_key = pg.AnimatedSprite("close_key.png", (21, 21))

        self.door.set_scale(3.0)

        self.initial_ground_x = WIDTH - (self.door.frame_size[1] * self.door.scale) / 2
        self.initial_ground_y = HEIGHT / 2 - (self.door.frame_size[1] * self.door.scale) / 2
        self.door.set_position(self.initial_ground_x, self.initial_ground_y)
        self.close_key.set_position(self.initial_ground_x, self.initial_ground_y - self.door.frame_size[1] * self.door.scale)


        self.initial_ground_y = HEIGHT - (self.key.frame_size[1] * self.key.scale)
        self.key.set_position(WIDTH - 100, self.initial_ground_y)
        
        game.add_sprite([self.door, self.key, self.close_key])
    def draw(self, screen):
        screen.blit(self.door.image, self.door.rect)
        screen.blit(self.key.image, self.key.rect)
        screen.blit(self.close_key.image, self.close_key.rect)
        
        


# Создание и добавление сцен в менеджер
menu_scene = MenuScene()
# game_scene = GameScene()
firstlevel = FirstLevel()

scene_manager.add_scene(menu_scene)
# scene_manager.add_scene(game_scene)
scene_manager.add_scene(firstlevel)

# Установка начальной сцены
scene_manager.switch_to("menu")


def update():
    dt = game.get_delta_time()
    scene_manager.update(dt)


def draw():
    scene_manager.draw(game.screen)



# Запуск игры
game.run(update, draw) 
