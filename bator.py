import pygame
import pygine as pg
from pygine.scene import Scene, SceneManager

#Константы
WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


IDLE_TO_STAND = 2.0
TELEPORT_COOLDOWN_TIME = 0.5


# Инициализация игры
game = pg.Game(WIDTH, HEIGHT, "Duality", FPS, background_image="assets/background.png")

background = pygame.transform.scale(pygame.image.load("assets/background.png").convert(), (WIDTH, HEIGHT))
# Создание менеджера сцен
scene_manager = SceneManager()

def start():
    scene_manager.switch_to("game")

class MenuScene(Scene):
    """Сцена главного меню"""
    
    def __init__(self):
        super().__init__("menu")
        self.title_text = "Duality"
        self.instruction_text = "Duality - это игра"
        
        self.btn_start = pg.Button(340, 480, 120, 35, "Играть",color=(50, 50, 150), hover_color=(80, 80, 200), callback=start)

        self.btn_quit = pg.Button(340, 520, 120, 35, "Выход", color=(50, 50, 150), hover_color=(80, 80, 200), callback=game.quit)

    
    def update(self, dt):
        self.btn_start.update(dt)
        self.btn_quit.update(dt)
        
    
    def draw(self, screen):
        # Фон меню
        screen.fill((100, 50, 150))

        self.btn_start.draw(game.screen)
        self.btn_quit.draw(game.screen)
        
        # Отображение заголовка (центрировано)
        pg.Text(WIDTH / 2, HEIGHT / 2 - HEIGHT / 4, self.title_text, size=32, color=(255, 255, 0)).draw(screen)
        
        # Отображение инструкции (центрировано)
        pg.Text(WIDTH / 2, HEIGHT / 2, self.instruction_text, size=20, color=(255, 255, 255)).draw(screen)

    def handle_event(self, event):
        self.btn_start.handle_event(event)
        self.btn_quit.handle_event(event)

def restart_menu():
    menu_scene.btn_start.text = "Заново"
    scene_manager.switch_to("menu")
    first_scene.player.set_position(0, first_scene.initial_ground_y)
    first_scene.is_complete = False
    first_scene.key.play_animation("key")
    first_scene.close_key.play_animation("no_key")
    first_scene.door.play_animation("closed")

class GameScene(Scene):
    """Игровая сцена"""
    
    def __init__(self):
        super().__init__("game")
        self.instruction_text = "A/D - влево/вправо \nS - присесть\nQ/E - телепортация вверх/вниз\nShift + A/D - бег"
        
        # Создание игрока
        self.player = pg.AnimatedSprite("assets/player.png", (21, 21), (400, 300))
        self.player.add_animation("stance", [0], fps=8, loop=True)
        self.player.add_animation("walk", [1, 7, 8, 9], fps=8, loop=True)
        self.player.add_animation("run", [1, 7, 8, 9], fps=24, loop=True)
        self.player.add_animation("jump", [9, 10], fps=8, loop=False)
        self.player.add_animation("duck", [2, 3], fps=8, loop=False)
        self.player.add_animation("teleport", [2, 3], fps=8, loop=False)
        self.player.set_scale(2.0)
        
        # Начальная позиция игрока
        initial_ground_y = HEIGHT - (self.player.frame_size[1] * self.player.scale) / 2
        self.player.set_position(0, initial_ground_y)
        self.player.play_animation("stance")
        
        # Параметры движения
        self.speed = 200
        self.run_speed = 400
        self.jump_speed = 0
        self.gravity = 1500
        self.jump_power = -500
        self.idle_timer = 0.0
        self.current_world = "upper"
        self.teleport_cooldown = 0.0
        
        # Добавление спрайта в игру
        game.add_sprite(self.player)
    def update(self, dt):
        # Возврат в меню при нажатии Escape
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            scene_manager.switch_to("menu")
    
        self.teleport_cooldown = max(0, self.teleport_cooldown - dt)
        half_w = (self.player.frame_size[0] * self.player.scale) / 2
        half_h = (self.player.frame_size[1] * self.player.scale) / 2
        ground_y = HEIGHT / 2 - half_h
        
        # Определяем текущую землю в зависимости от мира
        if self.current_world == "upper":
            ground_y = HEIGHT / 2 - half_h
        else:
            ground_y = HEIGHT - half_h
            
        # Стоим ли на земле?
        on_ground = self.player.y >= ground_y - 0.1


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

        if (keys[pygame.K_q] or keys[pygame.K_e]) and on_ground and self.teleport_cooldown <= 0:
            target_world = "lower" if keys[pygame.K_q] else "upper"

            # Если пытаемся телепортироваться в текущий мир - игнорируем
            if target_world != self.current_world:
                self.player.play_animation("teleport")
                self.teleport_cooldown = TELEPORT_COOLDOWN_TIME

                # Сохраняем текущую позицию
                saved_x = self.player.x
                saved_y = self.player.y

                # Меняем мир
                self.current_world = target_world

                # Вычисляем новую позицию
                if self.current_world == "lower":
                    new_y = saved_y + HEIGHT / 2
                else:
                    new_y = saved_y - HEIGHT / 2

                # Устанавливаем новую позицию
                self.player.set_position(saved_x, new_y)
                
                # Сбрасываем скорость прыжка после телепортации
                self.jump_speed = 0

        # Применяем гравитацию
        self.jump_speed += self.gravity * dt
        self.player.y += self.jump_speed * dt

        # Не проваливаемся сквозь землю
        if self.player.y > ground_y:
            self.player.y = ground_y
            self.jump_speed = 0

        # Не выходим за пределы экрана
        if self.player.x < half_w:
            self.player.x = half_w
        elif self.player.x > WIDTH - half_w:
            self.player.x = WIDTH - half_w


    def draw(self, screen):
        # Фон игры
        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        # # Отрисовка игрока
        screen.blit(self.player.image, self.player.rect)

        # Отображение инструкции
        pg.Text(20, 20, self.instruction_text, size=18, color=(255, 255, 255)).draw(screen)


class FirstScene(GameScene):
    def __init__(self):
        super().__init__()
        self.door = pg.AnimatedSprite("assets/doors.png", (21, 42))
        self.key = pg.AnimatedSprite("assets/yellow_keys.png", (21, 21))
        self.close_key = pg.AnimatedSprite("assets/yellow_keys.png", (21, 21))
        self.sign = pg.AnimatedSprite("assets/right_sign.png", (21, 21))

        self.door.add_animation("closed", [0], fps=1, loop=True)
        self.door.add_animation("open", [1], fps=1, loop=True)
        self.door.play_animation("closed")

        self.key.add_animation("key", [0], fps=1, loop=True)
        self.key.add_animation("no_key", [1], fps=1, loop=True)
        self.key.play_animation("key")

        self.close_key.add_animation("key", [0], fps=1, loop=True)
        self.close_key.add_animation("no_key", [1], fps=1, loop=True)
        self.close_key.play_animation("no_key")

        self.door.set_scale(3.0)
        self.key.set_scale(2.0)
        self.close_key.set_scale(2.0)
        self.sign.set_scale(2.0)

        self.initial_ground_x = WIDTH - (self.door.frame_size[1] * self.door.scale) / 2
        self.initial_ground_y = HEIGHT / 2 - (self.door.frame_size[1] * self.door.scale) / 2
        self.door.set_position(self.initial_ground_x, self.initial_ground_y)
        self.close_key.set_position(self.initial_ground_x, self.initial_ground_y - (self.door.frame_size[1] * self.door.scale) / 2)

        self.initial_ground_y = HEIGHT / 2 - (self.sign.frame_size[1] * self.sign.scale) / 2
        self.sign.set_position(self.initial_ground_x - 100, self.initial_ground_y)

        self.initial_ground_y = HEIGHT - (self.key.frame_size[1] * self.key.scale)
        self.key.set_position(WIDTH / 2, self.initial_ground_y)

        game.add_sprite([self.door, self.key, self.close_key, self.sign])

        self.is_complete = False
    def new_update(self):
        if self.player.collides_with(self.key) and not self.is_complete:
            self.key.play_animation("no_key")
            self.close_key.play_animation("key")
            self.door.play_animation("open")
            self.is_complete = True
        if self.player.collides_with(self.door) and self.is_complete:
            restart_menu()
            
    def draw(self, screen):
        self.new_update(screen)
        screen.blit(self.door.image, self.door.rect)
        screen.blit(self.key.image, self.key.rect)
        screen.blit(self.close_key.image, self.close_key.rect)
        
    


# Создание и добавление сцен в менеджер
menu_scene = MenuScene()
first_scene = FirstScene()
scene_manager.add_scene(menu_scene)
scene_manager.add_scene(first_scene)

# Установка начальной сцены
scene_manager.switch_to("menu")

def update():
    dt = game.get_delta_time()
    scene_manager.update(dt)

def draw():
    scene_manager.draw(game.screen)

game.add_event_callback(menu_scene.handle_event)
# Запуск игры
game.run(update, draw) 
