import pygame
import random

# Initialize Pygame
pygame.init()

# Set the window title
pygame.display.set_caption("LLM Minesweeper")

# Set up some constants
WIDTH, HEIGHT = 400, 400
TILE_SIZE = 20
BOARD_SIZE = WIDTH // TILE_SIZE
BOMB_COUNT = 10

# Set up some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def create_board(first_click_x=None, first_click_y=None):
    board = [[-2 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    bombs_placed = 0
    while bombs_placed < BOMB_COUNT:
        x, y = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
        if x == first_click_x and y == first_click_y:
            continue  # Skip placing a bomb on the first click
        if board[x][y] != -1:
            board[x][y] = -1
            bombs_placed += 1
    return board

def count_neighboring_bombs(x, y):
    count = 0
    for i in range(max(x - 1, 0), min(x + 2, BOARD_SIZE)):
        for j in range(max(y - 1, 0), min(y + 2, BOARD_SIZE)):
            if board[i][j] == -1 or board[i][j] == -5:  # Check if the tile is a bomb or flagged bomb
                count += 1
    return count

def reveal_tile(x, y):
    if board[x][y] == -1 or board[x][y] == -5:  # Check if the tile is a bomb or flagged potential bomb
        return
    if board[x][y] >= 0 or board[x][y] == -3:
        return
    reveal = count_neighboring_bombs(x, y)
    if board[x][y] == -5:  # If the tile was flagged as a potential bomb, keep it as a potential bomb
        board[x][y] = -5
    else:
        board[x][y] = reveal
    if reveal == 0:
        for i in range(max(x - 1, 0), min(x + 2, BOARD_SIZE)):
            for j in range(max(y - 1, 0), min(y + 2, BOARD_SIZE)):
                if board[i][j] != -3 and board[i][j] != -5:  # Check if the tile is not flagged or flagged potential bomb
                    reveal_tile(i, j)

def check_win():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] >= 0 or board[x][y] == -3:
                continue
            if board[x][y] == -2:
                return False
    return True

# Create the board and place the bombs
board = create_board()




# Main game loop
running=True
board_reset = True
waiting_for_reset = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
            if event.button == 1:  # Left mouse button
                if waiting_for_reset:
                    # Reset the game without revealing any tile
                    board = create_board()
                    waiting_for_reset = False
                    board_reset = False  # Prepare for a new game
                    continue  # Skip the rest of the loop to avoid revealing a tile
                if board_reset:
                    # If the game was over and is now reset, prepare the board
                    board = create_board(x, y)
                    board_reset = False
                if board[x][y] == -1:  # If a bomb is clicked
                    # Reveal all bombs and prepare for reset
                    board = [[-4 if cell == -1 else cell for cell in row] for row in board]
                    board_reset = True
                    waiting_for_reset = True  # Indicate that the next click should reset the game
                else:
                    reveal_tile(x, y)
                    if check_win():
                        # Handle win condition
                        board_reset = True
            elif event.button == 3:  # Right mouse button
                # Toggle flag state for unrevealed tiles and mines
                if board[x][y] == -2:  # Unrevealed safe tile
                    board[x][y] = -3  # Flag it
                elif board[x][y] == -1:  # Unrevealed mine
                    board[x][y] = -5  # Flag it as a mine
                elif board[x][y] == -3:  # Flagged safe tile
                    board[x][y] = -2  # Unflag it
                elif board[x][y] == -5:  # Flagged mine
                    board[x][y] = -1  # Unflag it


    # Draw the board
    screen.fill(WHITE)
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if board[x][y] == -2:  # Unrevealed tile
                pygame.draw.rect(screen, GRAY, rect)
            elif board[x][y] == -1:  # Unrevealed mine
                pygame.draw.rect(screen, GRAY, rect)
            elif board[x][y] == -3 or board[x][y] == -5:  # Flagged tile or flagged bomb
                pygame.draw.rect(screen, BLUE, rect)
            elif board[x][y] == -4:  # Revealed mine (red)
                pygame.draw.rect(screen, RED, rect)
            elif board[x][y] >= 0:  # Revealed tile
                if board[x][y] > 0:  # Only draw numbers for tiles with a count greater than 0
                    font = pygame.font.Font(None, 18)
                    text = font.render(str(board[x][y]), True, BLACK)
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
