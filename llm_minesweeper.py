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


def flag_remaining_tiles():
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] == -1:  # Unrevealed bomb
                board[x][y] = -5  # Automatically flag it as a bomb

# Create the board and place the bombs
board = create_board()


# Main game loop
running=True
board_reset = False  # The board doesn't need an immediate reset at the start
waiting_for_reset = False
reset_acknowledged = False  # New flag to acknowledge a reset without proceeding with a game action
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if waiting_for_reset:
                # Reset the game and acknowledge the reset
                board = create_board()
                waiting_for_reset = False
                reset_acknowledged = True  # Acknowledge that we've just reset the game
                continue  # Proceed to the next iteration to avoid this click being processed as game action

            # Process the first click after a game reset properly
            if reset_acknowledged:
                reset_acknowledged = False  # Clear the flag to allow normal game actions
                # Do NOT continue; let the logic below handle the click as a normal game action

            x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
            if event.button == 1:  # Left mouse button
                if board_reset and not board[x][
                                           y] == -4:  # If the board was just reset and the click is not on a revealed bomb
                    board = create_board(x,
                                         y)  # Ensure this is your logic for initializing the board with the first click avoiding a bomb placement
                    board_reset = False
                elif board[x][y] == -1:  # If a bomb is clicked
                    board[x][y] = -4  # Mark the bomb as revealed
                    waiting_for_reset = True  # Indicate that the next click should reset the game
                else:
                    reveal_tile(x, y)
                    if check_win():
                        flag_remaining_tiles()  # Make sure this function correctly flags all bombs
                        waiting_for_reset = True
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
                if board[x][y] > 0:
                    font = pygame.font.Font(None, 18)
                    # Get the color for the number, default to BLACK if not found
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
