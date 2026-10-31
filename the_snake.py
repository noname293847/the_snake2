"""Игра «Изгиб Питона» — классическая змейка на Pygame."""

from random import choice

import pygame

# Размеры поля и клеток.
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения: (изменение X, изменение Y).
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета и скорость игры.
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

# Все возможные позиции на игровом поле.
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}
CENTER = ((SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE,
          (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE)

# Создаём окно и таймер — переменные нужны также автотестам.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()

# Сопоставление кнопок и направлений.
KEY_TO_DIRECTION = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}


class GameObject:
    """Базовый класс всех объектов игрового поля."""

    def __init__(self, position=CENTER, body_color=None):
        """Сохранить положение объекта и его цвет."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Предоставить дочерним классам интерфейс рисования."""
        pass


class Apple(GameObject):
    """Яблоко, возникающее в случайной свободной клетке."""

    def __init__(self, occupied_positions=()):
        """Создать яблоко и выбрать клетку, не занятую змейкой."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Переставить яблоко в свободную клетку игрового поля."""
        free_cells = ALL_CELLS - set(occupied_positions)
        if free_cells:
            self.position = choice(tuple(free_cells))
        else:
            self.position = None

    def draw(self):
        """Нарисовать красное яблоко с рамкой."""
        if self.position is None:
            return
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка, управляемая стрелками на клавиатуре."""

    def __init__(self):
        """Создать змейку длиной в одну клетку в центре поля."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Вернуть змейку к одной клетке и начальному направлению."""
        self.position = CENTER
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Принять новое направление, если оно было запрошено."""
        if self.next_direction is not None:
            next_x, next_y = self.next_direction
            current_x, current_y = self.direction
            if (next_x, next_y) != (-current_x, -current_y):
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Переместить змейку на клетку, замкнув края поля."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None
        self.position = self.get_head_position()
        if self.position in self.positions[1:]:
            self.reset()

    def draw(self):
        """Нарисовать каждый сегмент змейки."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Считать команды пользователя и назначить направление змейке."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type != pygame.KEYDOWN:
            continue
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            raise SystemExit
        new_direction = KEY_TO_DIRECTION.get(event.key)
        if new_direction is None:
            continue
        dx, dy = game_object.direction
        if new_direction != (-dx, -dy):
            game_object.next_direction = new_direction


def main():
    """Создать объекты и вести игру до закрытия окна."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            # Прибавляем сегмент сразу в момент поедания яблока.
            if snake.last is not None:
                snake.positions.append(snake.last)
                snake.last = None
            apple.randomize_position(snake.positions)

        # После самоукуса яблоко не должно находиться на голове.
        if apple.position in snake.positions:
            apple.randomize_position(snake.positions)

        # Рисуем игровое поле заново, чтобы не оставалось следов.
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
