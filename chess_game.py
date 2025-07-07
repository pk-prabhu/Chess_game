import pygame
import os

# Initialize mixer early for sound
pygame.mixer.init()

# Window and board settings
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
BUTTON_HEIGHT = 60
TOTAL_HEIGHT = HEIGHT + BUTTON_HEIGHT + 30

# Colors
WHITE = (255, 255, 255)
GRAY = (125, 135, 150)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)

PIECE_IMAGES = {}

# Load piece images
def load_images():
    pieces = [
        "b_bishop", "b_king", "b_knight", "b_pawn", "b_queen", "b_rook",
        "w_bishop", "w_king", "w_knight", "w_pawn", "w_queen", "w_rook"
    ]
    for piece in pieces:
        PIECE_IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(os.path.join("pieces", piece + ".png")),
            (SQUARE_SIZE, SQUARE_SIZE)
        )

# Draw the board
def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                pygame.draw.rect(win, GRAY, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Highlight squares
def draw_highlight(win, row, col, color):
    pygame.draw.rect(win, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

# Draw pieces on the board
def draw_pieces(win, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "--":
                win.blit(PIECE_IMAGES[piece], (col*SQUARE_SIZE, row*SQUARE_SIZE))

# Create initial board layout
def create_initial_board():
    return [
        ["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"],
        ["b_pawn"] * 8,
        ["--"] * 8,
        ["--"] * 8,
        ["--"] * 8,
        ["--"] * 8,
        ["w_pawn"] * 8,
        ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"]
    ]

# Get valid moves for a selected piece
def get_piece_moves(board, row, col):
    piece = board[row][col]
    if piece == "--": return []
    color, p_type = piece[0], piece[2:]
    directions = {
        "rook": [(0,1), (1,0), (0,-1), (-1,0)],
        "bishop": [(1,1), (-1,1), (1,-1), (-1,-1)],
        "queen": [(1,1), (-1,1), (1,-1), (-1,-1), (0,1), (1,0), (0,-1), (-1,0)],
        "king": [(1,1), (-1,1), (1,-1), (-1,-1), (0,1), (1,0), (0,-1), (-1,0)],
        "knight": [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
    }
    def in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8
    moves = []
    if p_type == "pawn":
        direction = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1
        if in_bounds(row+direction, col) and board[row+direction][col] == "--":
            moves.append((row+direction, col))
            if row == start_row and board[row+2*direction][col] == "--":
                moves.append((row+2*direction, col))
        for dc in [-1, 1]:
            r, c = row + direction, col + dc
            if in_bounds(r, c) and board[r][c] != "--" and board[r][c][0] != color:
                moves.append((r, c))
    elif p_type in ["rook", "bishop", "queen"]:
        for dr, dc in directions[p_type]:
            r, c = row + dr, col + dc
            while in_bounds(r, c):
                if board[r][c] == "--":
                    moves.append((r, c))
                elif board[r][c][0] != color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
    elif p_type == "knight":
        for dr, dc in directions["knight"]:
            r, c = row + dr, col + dc
            if in_bounds(r, c) and (board[r][c] == "--" or board[r][c][0] != color):
                moves.append((r, c))
    elif p_type == "king":
        for dr, dc in directions["king"]:
            r, c = row + dr, col + dc
            if in_bounds(r, c) and (board[r][c] == "--" or board[r][c][0] != color):
                moves.append((r, c))
    return moves

# Make move
def make_move(board, from_pos, to_pos, captured_white, captured_black):
    move = {
        "from": from_pos,
        "to": to_pos,
        "moved_piece": board[from_pos[0]][from_pos[1]],
        "captured_piece": board[to_pos[0]][to_pos[1]]
    }
    # Add captured piece to list
    if move["captured_piece"] != "--":
        if move["captured_piece"].startswith("w"):
            captured_white.append(move["captured_piece"])
        else:
            captured_black.append(move["captured_piece"])
    board[to_pos[0]][to_pos[1]] = move["moved_piece"]
    board[from_pos[0]][from_pos[1]] = "--"
    return move

# Undo move
def undo_move(board, move, captured_white, captured_black):
    board[move["from"][0]][move["from"][1]] = move["moved_piece"]
    board[move["to"][0]][move["to"][1]] = move["captured_piece"]
    if move["captured_piece"] != "--":
        if move["captured_piece"].startswith("w") and captured_white:
            captured_white.pop()
        elif captured_black:
            captured_black.pop()

# Get square under mouse
def get_square_under_mouse():
    x, y = pygame.mouse.get_pos()
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

# Get all legal moves for a player
def get_all_moves(board, color):
    all_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece.startswith(color[0]):
                moves = get_piece_moves(board, row, col)
                for move in moves:
                    all_moves.append(((row, col), move))
    return all_moves

# Is king in check?
def is_king_in_check(board, color):
    king_pos = None
    opponent_color = 'black' if color == 'white' else 'white'
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece == f"{color[0]}_king":
                king_pos = (row, col)
                break
        if king_pos:
            break

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece.startswith(opponent_color[0]):
                moves = get_piece_moves(board, row, col)
                if king_pos in moves:
                    return True
    return False

# Check if current player is in checkmate
def is_checkmate(board, color):
    if not is_king_in_check(board, color):
        return False
    original_board = [row[:] for row in board]
    moves = get_all_moves(board, color)
    for move in moves:
        from_pos, to_pos = move
        moved_piece = board[from_pos[0]][from_pos[1]]
        captured_piece = board[to_pos[0]][to_pos[1]]
        board[to_pos[0]][to_pos[1]] = moved_piece
        board[from_pos[0]][from_pos[1]] = "--"
        if not is_king_in_check(board, color):
            board[from_pos[0]][from_pos[1]] = moved_piece
            board[to_pos[0]][to_pos[1]] = captured_piece
            return False
        board[from_pos[0]][from_pos[1]] = moved_piece
        board[to_pos[0]][to_pos[1]] = captured_piece
    return True

# Draw buttons
def draw_button(win, rect, text, font):
    color = (200, 200, 200)
    hover_color = (170, 170, 170)
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(win, hover_color, rect)
    else:
        pygame.draw.rect(win, color, rect)
    pygame.draw.rect(win, BLACK, rect, 2)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    win.blit(label, label_rect)

# Draw captured pieces with wrapping
def draw_captured(win, captured_pieces, offset_x):
    for i, piece in enumerate(captured_pieces):
        x = offset_x + (i % 8) * 25
        y = HEIGHT + 10 + (i // 8) * 25
        win.blit(PIECE_IMAGES[piece], (x, y))

# Draw board labels (A-H, 1-8)
def draw_labels(win, font):
    for col in range(COLS):
        label = font.render(chr(65 + col), True, BLACK)
        win.blit(label, (col * SQUARE_SIZE + SQUARE_SIZE // 4, HEIGHT - 25))
    for row in range(ROWS):
        label = font.render(str(8 - row), True, BLACK)
        win.blit(label, (5, row * SQUARE_SIZE + 5))

# Main function
def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("ChessMate")
    load_images()
    font = pygame.font.SysFont(None, 36)
    label_font = pygame.font.SysFont(None, 28)

    board = create_initial_board()
    selected = None
    possible_moves = []
    turn = 'white'
    captured_white = []
    captured_black = []
    move_history = []
    redo_stack = []

    # Button positions
    undo_button = pygame.Rect(WIDTH // 4 - 60, HEIGHT + 10, 120, 40)
    redo_button = pygame.Rect(WIDTH // 2 + WIDTH // 4 - 60, HEIGHT + 10, 120, 40)

    run = True
    clock = pygame.time.Clock()
    game_over = False
    checkmate_sound_played = False

    # Load checkmate sound
    try:
        checkmate_sound = pygame.mixer.Sound('checkmate.mp3')  # Ensure this file exists
    except pygame.error:
        print("Checkmate sound not found. Voice-over disabled.")

    while run:
        clock.tick(60)
        draw_board(win)

        # Highlight selected piece and its moves
        row, col = get_square_under_mouse()
        if not game_over and 0 <= row < 8 and 0 <= col < 8 and selected is None and board[row][col] != "--":
            possible_moves = get_piece_moves(board, row, col)
            draw_highlight(win, row, col, BLUE)
            for move in possible_moves:
                draw_highlight(win, move[0], move[1], GREEN)

        draw_pieces(win, board)
        draw_labels(win, label_font)

        # Turn indicator
        if not game_over:
            turn_text = "White's Turn" if turn == 'white' else "Black's Turn"
            turn_label = font.render(turn_text, True, BLACK)
            win.blit(turn_label, (WIDTH // 2 - turn_label.get_width() // 2, HEIGHT + 15))
        else:
            msg = "Checkmate! Game Over."
            msg_label = font.render(msg, True, RED)
            win.blit(msg_label, (WIDTH // 2 - msg_label.get_width() // 2, HEIGHT + 15))
            if not checkmate_sound_played:
                try:
                    checkmate_sound.play()
                except:
                    pass
                checkmate_sound_played = True

        # Draw captured pieces
        draw_captured(win, captured_black, 10)
        draw_captured(win, captured_white, WIDTH - len(captured_white) * 25 - 10)

        # Draw buttons
        draw_button(win, undo_button, "Undo", font)
        draw_button(win, redo_button, "Redo", font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if undo_button.collidepoint(mx, my) and move_history and not game_over:
                    last_move = move_history.pop()
                    undo_move(board, last_move, captured_white, captured_black)
                    redo_stack.append(last_move)
                    selected = None
                    possible_moves = []
                    turn = 'black' if turn == 'white' else 'white'
                    continue
                if redo_button.collidepoint(mx, my) and redo_stack and not game_over:
                    move = redo_stack.pop()
                    make_move(board, move["from"], move["to"], captured_white, captured_black)
                    move_history.append(move)
                    selected = None
                    possible_moves = []
                    turn = 'black' if turn == 'white' else 'white'
                    continue
                if my < HEIGHT and not game_over:
                    row, col = get_square_under_mouse()
                    if 0 <= row < 8 and 0 <= col < 8:
                        piece = board[row][col]
                        if selected:
                            if (row, col) in possible_moves:
                                move = make_move(board, selected, (row, col), captured_white, captured_black)
                                move_history.append(move)
                                redo_stack.clear()
                                turn = 'black' if turn == 'white' else 'white'
                            selected = None
                            possible_moves = []
                        elif piece != "--" and ((turn == 'white' and piece.startswith('w')) or (turn == 'black' and piece.startswith('b'))):
                            selected = (row, col)
                            possible_moves = get_piece_moves(board, row, col)

        # Check for checkmate
        if not game_over and is_checkmate(board, 'white' if turn == 'black' else 'black'):
            game_over = True

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()