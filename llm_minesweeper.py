import pygame
import random
import enum

# Initialize Pygame
pygame.init()

# Set the window title
pygame.display.set_caption("LLM Minesweeper")

# Set up some constants
WIDTH, HEIGHT = 400, 400
TILE_SIZE = 20
BOARD_SIZE = WIDTH // TILE_SIZE
BOMB_COUNT = 40

# Set up some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (192, 192, 192)
LIGHT_ORANGE = (255, 165, 0)  # RGB value for a light orange color

# Number to color mapping
NUMBER_COLORS = {
    1: (0, 0, 255),        # Blue
    2: (0, 128, 0),        # Green
    3: (255, 0, 0),        # Red
    4: (0, 0, 128),        # Dark Blue
    5: (128, 0, 0),        # Maroon
    6: (64, 224, 208),     # Turquoise
    7: (0, 0, 0),          # Black
    8: (128, 128, 128)     # Gray
}

class FieldState(enum.Enum):
    UNREVEALED_SAFE = -2
    UNREVEALED_MINE = -1
    FLAGGED_SAFE = -3
    FLAGGED_MINE = -5
    REVEALED_MINE = -4

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def create_board(first_click_x=None, first_click_y=None):
    board = [[FieldState.UNREVEALED_SAFE for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    bombs_placed = 0
    while bombs_placed < BOMB_COUNT:
        x, y = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
        if x == first_click_x and y == first_click_y:
            continue  # Skip placing a bomb on the first click
        if board[x][y] != FieldState.UNREVEALED_MINE:
            board[x][y] = FieldState.UNREVEALED_MINE
            bombs_placed += 1
    return board

def count_neighboring_bombs(x, y):
    count = 0
    for i in range(max(x - 1, 0), min(x + 2, BOARD_SIZE)):
        for j in range(max(y - 1, 0), min(y + 2, BOARD_SIZE)):
            if board[i][j] in [FieldState.UNREVEALED_MINE, FieldState.FLAGGED_MINE]:
                count += 1
    return count

def reveal_all_mines():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] in [FieldState.UNREVEALED_MINE, FieldState.FLAGGED_MINE]:
                board[x][y] = FieldState.REVEALED_MINE

def reveal_tile(x, y):
    if board[x][y] in [FieldState.UNREVEALED_MINE, FieldState.FLAGGED_MINE]:
        return
    if board[x][y] in [FieldState.FLAGGED_SAFE] or (isinstance(board[x][y], int) and board[x][y] >= 0):
        return
    reveal = count_neighboring_bombs(x, y)
    board[x][y] = reveal
    if reveal == 0:
        for i in range(max(x - 1, 0), min(x + 2, BOARD_SIZE)):
            for j in range(max(y - 1, 0), min(y + 2, BOARD_SIZE)):
                if board[i][j] not in [FieldState.FLAGGED_SAFE, FieldState.FLAGGED_MINE]:
                    reveal_tile(i, j)

def check_win():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if (isinstance(board[x][y], int) and board[x][y] >= 0) or board[x][y] == FieldState.FLAGGED_SAFE:
                continue
            if board[x][y] == FieldState.UNREVEALED_SAFE:
                return False
    return True

def flag_remaining_tiles():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == FieldState.UNREVEALED_MINE:
                board[x][y] = FieldState.FLAGGED_MINE

# Create the board and place the bombs
board = create_board()

# Main game loop
running = True
board_reset = False
waiting_for_reset = False
reset_acknowledged = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if waiting_for_reset:
                board = create_board()
                waiting_for_reset = False
                reset_acknowledged = True
                continue

            x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
            if event.button == 1:
                if board_reset and not board[x][y] == FieldState.REVEALED_MINE:
                    board = create_board(x, y)
                    board_reset = False
                elif board[x][y] == FieldState.UNREVEALED_MINE:
                    board[x][y] = FieldState.REVEALED_MINE
                    reveal_all_mines()
                    waiting_for_reset = True
                else:
                    reveal_tile(x, y)
                    if check_win():
                        flag_remaining_tiles()
                        waiting_for_reset = True
            elif event.button == 3:
                if board[x][y] == FieldState.UNREVEALED_SAFE:
                    board[x][y] = FieldState.FLAGGED_SAFE
                elif board[x][y] == FieldState.UNREVEALED_MINE:
                    board[x][y] = FieldState.FLAGGED_MINE
                elif board[x][y] == FieldState.FLAGGED_SAFE:
                    board[x][y] = FieldState.UNREVEALED_SAFE
                elif board[x][y] == FieldState.FLAGGED_MINE:
                    board[x][y] = FieldState.UNREVEALED_MINE

    # Draw the board
    screen.fill(WHITE)
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if board[x][y] in [FieldState.UNREVEALED_SAFE, FieldState.UNREVEALED_MINE]:
                pygame.draw.rect(screen, GRAY, rect)
            elif board[x][y] in [FieldState.FLAGGED_SAFE, FieldState.FLAGGED_MINE]:
                pygame.draw.rect(screen, LIGHT_ORANGE, rect)
            elif board[x][y] == FieldState.REVEALED_MINE:
                pygame.draw.rect(screen, RED, rect)
                pygame.draw.circle(screen, BLACK, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2),
                                   TILE_SIZE // 2 - 2)
            elif isinstance(board[x][y], int):
                if board[x][y] > 0:
                    font = pygame.font.Font(None, 18)
                    text_color = NUMBER_COLORS.get(board[x][y], BLACK)
                    text = font.render(str(board[x][y]), True, text_color)
                    text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
                    screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)  # Draw an empty white tile for 0

    # Add a grid
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (i * TILE_SIZE, 0), (i * TILE_SIZE, HEIGHT))
        pygame.draw.line(screen, BLACK, (0, i * TILE_SIZE), (WIDTH, i * TILE_SIZE))

    pygame.display.flip()

pygame.quit()