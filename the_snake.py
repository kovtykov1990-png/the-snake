from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Координаты центра игрового поля:
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Соответствие текущего направления и нажатой клавиши новому направлению:
DIRECTION_KEYS = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
}

# Цвета фона, границ ячеек и игровых объектов:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
DEFAULT_COLOR = (255, 0, 255)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов.

    Хранит позицию объекта на игровом поле и его цвет,
    содержит общие для игровых объектов методы отрисовки.
    """

    def __init__(self, body_color=DEFAULT_COLOR):
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.

        Абстрактный метод, предназначен для переопределения
        в дочерних классах.
        """
        raise NotImplementedError(
            'Метод draw() должен быть переопределён в классе '
            f'{type(self).__name__}.'
        )

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку игрового поля.

        Если цвет не передан, используется цвет объекта.
        """
        color = color if color is not None else self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле.

    Яблоко занимает одну клетку игрового поля и после того,
    как змейка его съедает, появляется в новой случайной точке
    поля, свободной от других игровых объектов.
    """

    def __init__(self, occupied_positions=None):
        super().__init__(APPLE_COLOR)
        if occupied_positions is None:
            occupied_positions = [self.position]
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайное положение яблока на игровом поле.

        Новая позиция не совпадает ни с одной из занятых позиций.
        """
        if occupied_positions is None:
            occupied_positions = []
        while self.position in occupied_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение.

    Змейка хранится как список координат сегментов, где первый
    элемент списка — голова змейки. Класс отвечает за движение,
    изменение направления, рост и отрисовку змейки.
    """

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки на игровом поле.

        Добавляет новую голову в начало списка сегментов и удаляет
        последний сегмент, если длина змейки не увеличилась.
        При выходе за границу поля змейка появляется с противоположной
        стороны.
        """
        current_x, current_y = self.get_head_position()
        shift_x, shift_y = self.direction
        new_head_position = (
            (current_x + shift_x * GRID_SIZE) % SCREEN_WIDTH,
            (current_y + shift_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head_position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает голову змейки на экране и затирает след."""
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)
        self.draw_cell(self.get_head_position())

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для изменения направления движения."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            new_direction = DIRECTION_KEYS.get(
                (game_object.direction, event.key)
            )
            if new_direction:
                game_object.next_direction = new_direction


def main():
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
