"""
Игра с полным управлением персонажем и физикой.
Демонстрирует движение, прыжки, анимации и различные состояния игрока.
"""

import pygine as pg
import pygame
from pygine.effects import start_screen_shake, create_explosion, update_effects, draw_effects

# Запускаем pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
# Коэффициент спустя который анимация "stand" включается
IDLE_TO_STAND = 2.0

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Test Game")
clock = pygame.time.Clock()

# Создаём игрока и его анимации
player = pg.AnimatedSprite("assets/player.png", (21, 21))
player.add_animation("stance", [0], fps=8, loop=True)
player.add_animation("walk", [1, 7, 8, 9], fps=8, loop=True)
player.add_animation("jump", [9, 10], fps=10, loop=False)
player.add_animation("duck", [2, 3], fps=100, loop=False)
player.add_animation("teleport", [2, 3], fps=10, loop=False)  # Объединённая анимация телепортации

player.set_scale(3.0)

wall = pg.AnimatedSprite("assets/background.png", (84, 21), (WIDTH / 2, HEIGHT / 2))
wall.set_scale(3)

# Ставим игрока на землю с учётом масштаба
initial_ground_y = HEIGHT / 2 - (player.frame_size[1] * player.scale) / 2
player.set_position(WIDTH // 2, initial_ground_y)
player.play_animation("stance")

# Скорости движения
speed = 200
run_speed = 400

# Параметры прыжка
jump_speed = 0
gravity = 1500
jump_power = -500

idle_timer = 0.0  # таймер покоя
current_world = "upper"  # 'upper' или 'lower'
teleport_cooldown = 0.0
TELEPORT_COOLDOWN_TIME = 0.5  # время между телепортациями

def player_update(dt):
    global idle_timer, jump_speed, current_world, teleport_cooldown
    update_effects(dt=dt)
    teleport_cooldown = max(0, teleport_cooldown - dt)
    keys = pygame.key.get_pressed()

    # Вычисляем границу земли и половину ширины на каждый кадр – учитываем масштаб
    half_w = (player.frame_size[0] * player.scale) / 2
    half_h = (player.frame_size[1] * player.scale) / 2
    
    # Определяем текущую землю в зависимости от мира
    if current_world == "upper":
        ground_y = HEIGHT / 2 - half_h
    else:
        ground_y = HEIGHT - half_h

    # Стоим ли на земле?
    on_ground = player.y >= ground_y - 0.1

    # Приседаем
    if keys[pygame.K_s] and on_ground:
        player.play_animation("duck")
        player.set_collision_rect(64, 32, 0, 0)
    else:
        player.reset_collision_to_default()

        # Прыгаем
        if keys[pygame.K_SPACE] and on_ground:
            jump_speed = jump_power
            player.play_animation("jump")

        # Ходим или бегаем
        elif keys[pygame.K_a]:
            player.x -= (run_speed if keys[pygame.K_LSHIFT] else speed) * dt
            if on_ground:
                player.play_animation("walk")
            player.mirror(True)
        elif keys[pygame.K_d]:
            player.x += (run_speed if keys[pygame.K_LSHIFT] else speed) * dt
            if on_ground:
                player.play_animation("walk")
            player.mirror(False)

    # Логика покоя
    moving = keys[pygame.K_a] or keys[pygame.K_d]
    crouching = keys[pygame.K_s]
    jumping = not on_ground

    if not moving and not crouching and not jumping:
        idle_timer += dt
        if idle_timer < IDLE_TO_STAND and player.get_current_animation() != "stance":
            player.play_animation("stance")
    else:
        idle_timer = 0.0

    # Телепортация между мирами
    if (keys[pygame.K_q] or keys[pygame.K_e]) and on_ground and teleport_cooldown <= 0:
        target_world = "lower" if keys[pygame.K_q] else "upper"
        
        # Если пытаемся телепортироваться в текущий мир - игнорируем
        if target_world != current_world:
            player.play_animation("teleport")
            teleport_cooldown = TELEPORT_COOLDOWN_TIME
            
            # Сохраняем позицию по X для точного возврата
            saved_x = player.x
            
            # Меняем мир и позицию по Y
            current_world = target_world
            if current_world == "lower":
                player.y += HEIGHT / 2
            else:
                player.y -= HEIGHT / 2
            
            # Восстанавливаем позицию по X
            player.x = saved_x

    # Применяем гравитацию
    jump_speed += gravity * dt
    player.y += jump_speed * dt

    # Не проваливаемся сквозь землю
    if player.y > ground_y:
        player.y = ground_y
        jump_speed = 0
    start_screen_shake(10.0, 4.0)
    create_explosion(400, 300, 25)
    # Не выходим за пределы экрана
    if player.x < half_w:
        player.x = half_w
    elif player.x > WIDTH - half_w:
        player.x = WIDTH - half_w

# Главный цикл игры
running = True
while running:
    dt = clock.tick(60) / 1000.0

    # Проверяем выход
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    player_update(dt)
    # Обновляем анимацию
    player.update(dt)
    wall.update(dt)
    draw_effects(window)
    # Рисуем кадр
    window.fill((255, 255, 255)) if current_world == "upper" else window.fill((0, 0, 0))
    window.blit(player.image, player.rect)
    window.blit(wall.image, wall.rect)
    
    instructions = pg.Text(10, 10, "A/D - шаг, Shift+A/D - бег, S - присесть, Space - прыжок, Q/E - телепорт", size=20)
    instructions.draw(window)

    pygame.display.update()

pygame.quit()