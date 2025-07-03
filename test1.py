import pygame
import pygine as pg
from pygine.scene import Scene, SceneManager

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IDLE_TO_STAND = 2.0  # время до перехода в анимацию "stand"

class MenuScene(Scene):
    """Сцена главного меню"""
    
    def __init__(self):
        super().__init__("menu")
        self.title_text = "ГЛАВНОЕ МЕНЮ"
        self.instruction_text = "Нажмите ПРОБЕЛ для перехода в игру"
        self.quit_text = "Нажмите ESC для выхода"
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            scene_manager.switch_to("game")
        if keys[pygame.K_ESCAPE]:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def draw(self, screen):
        screen.fill((100, 50, 150))
        pg.Text(WIDTH//2, 100, self.title_text, size=32, color=(255, 255, 0), center=True).draw(screen)
        pg.Text(WIDTH//2, 200, self.instruction_text, size=20, color=(255, 255, 255), center=True).draw(screen)
        pg.Text(WIDTH//2, 250, self.quit_text, size=20, color=(255, 255, 255), center=True).draw(screen)

class GameScene(Scene):
    """Игровая сцена с физикой и управлением персонажем"""
    
    def __init__(self):
        super().__init__("game")
        # Создаём игрока и его анимации
        self.player = pg.AnimatedSprite("player_sheet.png", (21, 21))
        self.player.add_animation("stance", [0], fps=8, loop=True)
        self.player.add_animation("walk", [1, 7, 8, 9], fps=8, loop=True)
        self.player.add_animation("jump", [9, 10], fps=10, loop=False)
        self.player.add_animation("duck", [2, 3], fps=100, loop=False)
        self.player.add_animation("teleport1", [2], fps=10, loop=False)
        self.player.add_animation("teleport2", [3], fps=10, loop=False)
        self.player.set_scale(3.0)
        
        # Создаем платформу
        self.wall = pg.AnimatedSprite("ground.png", (84, 21), (WIDTH / 2, HEIGHT / 2))
        self.wall.set_scale(3)
        
        # Начальная позиция игрока
        initial_ground_y = HEIGHT / 2 - (self.player.frame_size[1] * self.player.scale) / 2
        self.player.set_position(WIDTH // 2, initial_ground_y)
        self.player.play_animation("stance")
        
        # Параметры движения
        self.speed = 200
        self.run_speed = 400
        self.jump_speed = 0
        self.gravity = 1500
        self.jump_power = -500
        self.idle_timer = 0.0
        self.is_teleport = False
        
        # Инструкции
        self.instructions = [
            "A/D - шаг, Shift+A/D - бег",
            "S - присесть, Space - прыжок",
            "Q/E - телепорт между уровнями",
            "ESC - вернуться в меню"
        ]
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Возврат в меню
        if keys[pygame.K_ESCAPE]:
            scene_manager.switch_to("menu")
            return
        
        # Вычисляем границы
        half_w = (self.player.frame_size[0] * self.player.scale) / 2
        half_h = (self.player.frame_size[1] * self.player.scale) / 2
        ground_y = HEIGHT / 2 - half_h
        
        # Проверка нахождения на земле
        on_ground = self.player.y >= ground_y - 0.1
        
        # Приседание
        if keys[pygame.K_s] and on_ground:
            self.player.play_animation("duck")
        else:
            # Прыжок
            if keys[pygame.K_SPACE] and on_ground:
                self.jump_speed = self.jump_power
                self.player.play_animation("jump")
            
            # Движение влево/вправо
            elif keys[pygame.K_a]:
                self.player.x -= (self.run_speed if keys[pygame.K_LSHIFT] else self.speed) * dt
                if on_ground:
                    self.player.play_animation("walk")
                self.player.mirror(True)
            elif keys[pygame.K_d]:
                self.player.x += (self.run_speed if keys[pygame.K_LSHIFT] else self.speed) * dt
                if on_ground:
                    self.player.play_animation("walk")
                self.player.mirror(False)
        
        # Логика покоя
        moving = keys[pygame.K_a] or keys[pygame.K_d]
        crouching = keys[pygame.K_s]
        jumping = not on_ground
        
        if not moving and not crouching and not jumping:
            self.idle_timer += dt
            if self.idle_timer < IDLE_TO_STAND and self.player.get_current_animation() != "stance":
                self.player.play_animation("stance")
        else:
            self.idle_timer = 0.0
        
        # Телепортация между уровнями
        if keys[pygame.K_q] and on_ground:
            if self.player.y >= HEIGHT / 2 - half_h:
                self.is_teleport = True
                self.player.play_animation("teleport1")
                ground_y = HEIGHT - half_h
                self.player.y = self.player.y + HEIGHT / 2
                self.player.play_animation("teleport2")
                self.is_teleport = False
        if keys[pygame.K_e] and on_ground:
            if self.player.y < HEIGHT / 2 - half_h:
                self.is_teleport = True
                self.player.play_animation("teleport1")
                ground_y = HEIGHT / 2 - half_h
                self.player.y = self.player.y - HEIGHT / 2
                self.player.play_animation("teleport2")
                self.is_teleport = False
        
        # Применяем гравитацию
        self.jump_speed += self.gravity * dt
        self.player.y += self.jump_speed * dt
        
        # Не проваливаемся сквозь землю
        if self.player.y > ground_y and not self.is_teleport:
            self.player.y = ground_y
            self.jump_speed = 0
        
        # Не выходим за пределы экрана
        if self.player.x < half_w:
            self.player.x = half_w
        elif self.player.x > WIDTH - half_w:
            self.player.x = WIDTH - half_w
        
        # Обновляем анимации
        self.player.update(dt)
        self.wall.update(dt)
    
    def draw(self, screen):
        # Рисуем фон (два уровня)
        first_half = pygame.Rect(0, 0, WIDTH, HEIGHT / 2)
        second_half = pygame.Rect(0, HEIGHT / 2, WIDTH, HEIGHT / 2)
        screen.fill((255, 255, 255), first_half)
        screen.fill((0, 0, 0), second_half)
        
        # Рисуем объекты
        screen.blit(self.wall.image, self.wall.rect)
        screen.blit(self.player.image, self.player.rect)
        
        # Рисуем инструкции
        for i, text in enumerate(self.instructions):
            pg.Text(10, 10 + i * 25, text, size=20).draw(screen)

# Инициализация игры
game = pg.Game(WIDTH, HEIGHT, "Duality", FPS, background_color=WHITE)

# Создание менеджера сцен
scene_manager = SceneManager()

# Создание и добавление сцен
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