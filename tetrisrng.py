import pygame
import sys
import serial
import threading

# === UART SETUP ===
ser = serial.Serial('COM9', 9600, timeout=1)
BLOCKS = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
current_block = 'I'

def uart_listener():
    global current_block
    buffer = ""
    while True:
        try:
            char = ser.read().decode('utf-8', errors='ignore')
            if char.upper() in "0123456789ABCDEF":
                buffer += char.upper()
                if len(buffer) == 4:
                    value = int(buffer, 16)
                    current_block = BLOCKS[value % 7]
                    buffer = ""
            elif char not in ['\n', '\r', '']:
                buffer = ""

        except:
            pass

# Start UART listener in a thread
threading.Thread(target=uart_listener, daemon=True).start()

# === TETRIS GAME SETUP ===
pygame.init()
WIDTH, HEIGHT = 300, 600
CELL_SIZE = 30
COLUMNS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FPGA Tetris")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
COLORS = {
    'I': (0, 255, 255), 'O': (255, 255, 0), 'T': (128, 0, 128),
    'S': (0, 255, 0), 'Z': (255, 0, 0), 'J': (0, 0, 255), 'L': (255, 165, 0)
}

# Block shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# Game grid
grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]    
score = 0
lives = 3
font = pygame.font.SysFont("consolas", 20)

class Block:
    def __init__(self, shape):
        self.shape = SHAPES[shape]
        self.color = COLORS[shape]
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def draw(self):
        for dy, row in enumerate(self.shape):
            for dx, val in enumerate(row):
                if val:
                    pygame.draw.rect(screen, self.color,
                        pygame.Rect((self.x + dx) * CELL_SIZE, (self.y + dy) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def can_move(self, dx, dy):
        for y, row in enumerate(self.shape):
            for x, val in enumerate(row):
                if val:
                    nx, ny = self.x + x + dx, self.y + y + dy
                    if nx < 0 or nx >= COLUMNS or ny >= ROWS or (ny >= 0 and grid[ny][nx]):
                        return False
        return True

    def lock(self):
        for y, row in enumerate(self.shape):
            for x, val in enumerate(row):
                if val:
                    grid[self.y + y][self.x + x] = self.color

    def rotate(self):
        rotated = list(zip(*self.shape[::-1]))
        old_shape = self.shape
        self.shape = [list(row) for row in rotated]
        if not self.can_move(0, 0):
            self.shape = old_shape

# Spawn first block
block = Block(current_block)
fall_time = 0
FALL_SPEED = 500

def clear_lines():
    global grid, score
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    cleared = ROWS - len(new_grid)
    score += cleared * 100
    for _ in range(cleared):
        new_grid.insert(0, [None] * COLUMNS)
    grid = new_grid

def is_game_over():
    return any(grid[0][x] is not None for x in range(COLUMNS))

def draw_ui():
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 5))
    screen.blit(lives_text, (WIDTH - 100, 5))

# === GAME LOOP ===
running = True
while running:
    screen.fill(BLACK)
    dt = clock.tick(30)
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and block.can_move(-1, 0):
                block.x -= 1
            elif event.key == pygame.K_RIGHT and block.can_move(1, 0):
                block.x += 1
            elif event.key == pygame.K_DOWN and block.can_move(0, 1):
                block.y += 1
            elif event.key == pygame.K_UP:
                block.rotate()

    if fall_time > FALL_SPEED:
        if block.can_move(0, 1):
            block.y += 1
        else:

            if block.y <= 0:
                lives -= 1

                if lives <= 0:
                    print("Game Over! Final Score:", score)
                    running = False

            else:
                block.lock()
                clear_lines()
            block = Block(current_block)
        fall_time = 0

    block.draw()

    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x]:
                pygame.draw.rect(screen, grid[y][x], pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()