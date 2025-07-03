import pygame
import pygine as pg
from pygine.scene import Scene, SceneManager
from pygine.effects import start_screen_shake, create_explosion, update_effects, draw_effects

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IDLE_TO_STAND = 2.0
TELEPORT_COOLDOWN_TIME = 0.5

class MenuScene(Scene):
    """Сцена главного меню с анимацией и эффектами"""
    
    def __init__(self):
        super().__init__("menu")
        self.title_text = "DUALITY"
        self.instruction_text = "Нажмите ПРОБЕЛ для начала игры"
        self.quit_text = "Нажмите ESC для выхода"
        
        # Фоновые элементы
        self.background = pg.AnimatedSprite("assets/background.png", (WIDTH, HEIGHT))
        self.title_effect = pg.ParticleSystem((WIDTH//2, 100), max_particles=50)
        
    def on_enter(self):
        # Запускаем эффекты при входе в меню
        create_explosion(WIDTH//2, HEIGHT//2, 30)
        start_screen_shake(5.0, 2.0)
        
    def update(self, dt):
        update_effects(dt)
        self.title_effect.update(dt)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            scene_manager.switch_to("game")
        if keys[pygame.K_ESCAPE]:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def draw(self, screen):
        # Рисуем фон
        screen.fill((30, 20, 50))
        self.background.draw(screen)
        
        # Эффекты
        draw_effects(screen)
        self.title_effect.draw(screen)
        
        # Текст
        pg.Text(WIDTH//2, 100, self.title_text, size=48, color=(255, 200, 0), 
               center=True, font_name="Arial", bold=True).draw(screen)
        pg.Text(WIDTH//2, 200, self.instruction_text, size=24, color=(200, 200, 255), 
               center=True).draw(screen)
        pg.Text(WIDTH//2, 250, self.quit_text, size=24, color=(200, 200, 255), 
               center=True).draw(screen)

class GameScene(Scene):
    """Игровая сцена с физикой, телепортацией и эффектами"""
    
    def __init__(self):
        super().__init__("game")
        # Игрок
        self.player = pg.AnimatedSprite("assets/player.png", (21, 21))
        self._setup_player_animations()
        self.player.set_scale(3.0)
        
        # Окружение
        self.wall = pg.AnimatedSprite("assets/ground.png", (84, 21), (WIDTH / 2, HEIGHT / 2))
        self.wall.set_scale(3)
        
        # Физика и управление
        self.speed = 200
        self.run_speed = 400
        self.jump_speed = 0
        self.gravity = 1500
        self.jump_power = -500
        self.idle_timer = 0.0
        self.current_world = "upper"
        self.teleport_cooldown = 0.0
        
        # Начальная позиция
        initial_y = HEIGHT / 2 - (self.player.frame_size[1] * self.player.scale) / 2
        self.player.set_position(WIDTH // 2, initial_y)
        self.player.play_animation("stance")
        
    def _setup_player_animations(self):
        """Настройка анимаций игрока"""
        self.player.add_animation("stance", [0], fps=8, loop=True)
        self.player.add_animation("walk", [1, 7, 8, 9], fps=8, loop=True)
        self.player.add_animation("jump", [9, 10], fps=10, loop=False)
        self.player.add_animation("duck", [2, 3], fps=100, loop=False)
        self.player.add_animation("teleport", [2, 3], fps=10, loop=False)
    
    def on_enter(self):
        """Сброс состояния при входе в сцену"""
        self.current_world = "upper"
        initial_y = HEIGHT / 2 - (self.player.frame_size[1] * self.player.scale) / 2
        self.player.set_position(WIDTH // 2, initial_y)
        self.player.play_animation("stance")
        create_explosion(self.player.x, self.player.y, 15)
    
    def update(self, dt):
        update_effects(dt)
        self.teleport_cooldown = max(0, self.teleport_cooldown - dt)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            scene_manager.switch_to("menu")
            return
        
        self._handle_player_movement(dt, keys)
        self._update_player_position(dt)
        self._check_world_bounds()
        
        self.player.update(dt)
        self.wall.update(dt)
    
    def _handle_player_movement(self, dt, keys):
        """Обработка управления игроком"""
        half_h = (self.player.frame_size[1] * self.player.scale) / 2
        ground_y = HEIGHT / 2 - half_h if self.current_world == "upper" else HEIGHT - half_h
        on_ground = self.player.y >= ground_y - 0.1
        
        # Приседание
        if keys[pygame.K_s] and on_ground:
            self.player.play_animation("duck")
            self.player.set_collision_rect(64, 32, 0, 0)
        else:
            self.player.reset_collision_to_default()
            
            # Прыжок
            if keys[pygame.K_SPACE] and on_ground:
                self.jump_speed = self.jump_power
                self.player.play_animation("jump")
                create_explosion(self.player.x, ground_y, 10)
            
            # Движение
            if keys[pygame.K_a]:
                speed = self.run_speed if keys[pygame.K_LSHIFT] else self.speed
                self.player.x -= speed * dt
                if on_ground: self.player.play_animation("walk")
                self.player.mirror(True)
            elif keys[pygame.K_d]:
                speed = self.run_speed if keys[pygame.K_LSHIFT] else self.speed
                self.player.x += speed * dt
                if on_ground: self.player.play_animation("walk")
                self.player.mirror(False)
        
        # Телепортация
        if (keys[pygame.K_q] or keys[pygame.K_e]) and on_ground and self.teleport_cooldown <= 0:
            target_world = "lower" if keys[pygame.K_q] else "upper"
            if target_world != self.current_world:
                self._perform_teleport(target_world)
    
    def _perform_teleport(self, target_world):
        """Выполнение телепортации между мирами"""
        self.player.play_animation("teleport")
        self.teleport_cooldown = TELEPORT_COOLDOWN_TIME
        saved_x = self.player.x
        
        # Эффекты телепортации
        create_explosion(self.player.x, self.player.y, 20)
        start_screen_shake(8.0, 3.0)
        
        # Смена мира
        self.current_world = target_world
        if self.current_world == "lower":
            self.player.y += HEIGHT / 2
        else:
            self.player.y -= HEIGHT / 2
        
        self.player.x = saved_x
        create_explosion(self.player.x, self.player.y, 20)
    
    def _update_player_position(self, dt):
        """Обновление позиции игрока с учётом физики"""
        half_h = (self.player.frame_size[1] * self.player.scale) / 2
        ground_y = HEIGHT / 2 - half_h if self.current_world == "upper" else HEIGHT - half_h
        
        # Гравитация
        self.jump_speed += self.gravity * dt
        self.player.y += self.jump_speed * dt
        
        # Проверка земли
        if self.player.y > ground_y:
            self.player.y = ground_y
            self.jump_speed = 0
    
    def _check_world_bounds(self):
        """Проверка границ экрана"""
        half_w = (self.player.frame_size[0] * self.player.scale) / 2
        if self.player.x < half_w:
            self.player.x = half_w
        elif self.player.x > WIDTH - half_w:
            self.player.x = WIDTH - half_w
    
    def draw(self, screen):
        # Фон в зависимости от мира
        if self.current_world == "upper":
            screen.fill((220, 230, 240))  # Светлый верхний мир
        else:
            screen.fill((20, 30, 40))    # Тёмный нижний мир
        
        # Отрисовка объектов
        self.wall.draw(screen)
        self.player.draw(screen)
        draw_effects(screen)
        
        # Инструкции
        instructions = [
            "A/D - Движение, Shift - Бег",
            "SPACE - Прыжок, S - Присесть",
            "Q - В нижний мир, E - В верхний мир",
            "ESC - Меню"
        ]
        
        for i, text in enumerate(instructions):
            color = (0, 0, 0) if self.current_world == "upper" else (255, 255, 255)
            pg.Text(10, 10 + i * 25, text, size=20, color=color).draw(screen)

# Инициализация игры
game = pg.Game(WIDTH, HEIGHT, "Duality", FPS)

# Создание менеджера сцен
scene_manager = SceneManager()
scene_manager.add_scene(MenuScene())
scene_manager.add_scene(GameScene())
scene_manager.switch_to("menu")

def update():
    dt = game.get_delta_time()
    scene_manager.update(dt)

def draw():
    scene_manager.draw(game.screen)

# Запуск игры
game.run(update, draw)