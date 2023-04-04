import re
import copy
class CheckerGame:
    def __init__(self):
        self.board = [
            ['-', 'A', '-', 'A', '-', 'A', '-', 'A'],
            ['A', '-', 'A', '-', 'A', '-', 'A', '-'],
            ['-', 'A', '-', 'A', '-', 'A', '-', 'A'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['B', '-', 'B', '-', 'B', '-', 'B', '-'],
            ['-', 'B', '-', 'B', '-', 'B', '-', 'B'],
            ['B', '-', 'B', '-', 'B', '-', 'B', '-']
        ]
        self.player_turn = 'A'
        self.taken_pieces = {'A': "", 'B': ""}

    def display_board(self, board, taken_pieces):
        print("  0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣" + "    " + taken_pieces['A'])
        for i in range(8):
            row = f"{chr(i+65)}|"
            for j in range(8):
                if board[i][j] == 'A':
                    row += '🔴'
                elif board[i][j] == 'B':
                    row += '🔵'
                elif board[i][j] == 'C':
                    row += '❤️'
                elif board[i][j] == 'D':
                    row += '💙'
                elif (i + j) % 2 == 0:
                    row += '◻️ '
                else:
                    row += '◼️ '
            row+=f"|{chr(i+65)}"
            print(row)
        print("  0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣" + "     "+ taken_pieces['B'])

    def is_valid_move(self, move):
        move = move.replace(' ', '').upper()
        moves = move.split(',')
        board_copy = copy.deepcopy(self.board)
        jumper = None
        for i, mv in enumerate(moves):
            if not re.match(r'^([A-H][0-7]TO[A-H][0-7])+$', mv):
                print('format is invalid')
                return False
            start_row, start_col, end_row, end_col = ord(mv[0]) - ord('A'), int(mv[1]), ord(mv[4]) - ord('A'), int(mv[5])
            if i > 0:
                if jumper is None:
                    print('cannot make multiple moves without jumping')
                    return False
                elif jumper != (start_row, start_col):
                    print('must continue jumping')
                    return False
            if (ord(board_copy[start_row][start_col]) - ord(self.player_turn)) % 2 != 0:
                print('not your piece')
                return False
            if board_copy[end_row][end_col] != '-':
                print('destination is not empty')
                return False
            if abs(start_row - end_row) != abs(start_col - end_col):
                print('not a diagonal move')
                return False
            if board_copy[start_row][start_col] == 'A' and end_row <= start_row:
                print('red must move down')
                return False
            if board_copy[start_row][start_col] == 'B' and end_row >= start_row:
                print('blue must move up')
                return False 
            if abs(start_row - end_row) == 1:
                board_copy[end_row][end_col] = board_copy[start_row][start_col]
                board_copy[start_row][start_col] = '-'
            elif abs(start_row - end_row) == 2:
                if board_copy[(start_row + end_row) // 2][(start_col + end_col) // 2] == '-':
                    print('no piece to jump')
                    return False
                if (ord(board_copy[(start_row + end_row) // 2][(start_col + end_col) // 2]) - ord(self.player_turn)) % 2 == 0:
                    print('cannot jump your own piece')
                    return False
                board_copy[end_row][end_col] = board_copy[start_row][start_col]
                board_copy[(start_row + end_row) // 2][(start_col + end_col) // 2] = '-'
                board_copy[start_row][start_col] = '-'
                jumper = (end_row, end_col)
        return True
        
    def make_move(self, move, input_board, taken_pieces):
        move = move.replace(' ', '').upper()
        moves = move.split(',')
        for mv in moves:
            start_row, start_col, end_row, end_col = ord(mv[0]) - ord('A'), int(mv[1]), ord(mv[4]) - ord('A'), int(mv[5])
            if abs(start_row - end_row) == 1:
                input_board[end_row][end_col] = input_board[start_row][start_col]
                input_board[start_row][start_col] = '-'
            elif abs(start_row - end_row) == 2:
                input_board[end_row][end_col] = input_board[start_row][start_col]
                taken = input_board[(start_row + end_row) // 2][(start_col + end_col) // 2]
                if taken == 'A':
                    taken = '🔴'
                elif taken == 'B':
                    taken = '🔵'
                elif taken == 'C':
                    taken = '❤️'
                elif taken == 'D':
                    taken = '💙'
                taken_pieces[self.player_turn] += taken
                input_board[(start_row + end_row) // 2][(start_col + end_col) // 2] = '-'
                input_board[start_row][start_col] = '-'
            if self.player_turn == 'B' and end_row == 0:
                input_board[end_row][end_col] = 'D'
            elif self.player_turn == 'A' and end_row == 7:
                input_board[end_row][end_col] = 'C'

    def is_game_over(self):
        return len(self.taken_pieces['A']) == 12 or len(self.taken_pieces['B']) == 12

    def play_game(self):
        while not self.is_game_over():
            self.display_board(self.board, self.taken_pieces)
            move = input(f"{ 'Red' if self.player_turn == 'A' else 'Blue' }'s turn.\nEnter your move: [row][col]to[row][col] (comma sep for multiple moves)\n")
            if self.is_valid_move(move):
                self.make_move(move,self.board, self.taken_pieces)
                self.player_turn = 'B' if self.player_turn == 'A' else 'A'
            else:
                print("Invalid move. Try again.")
        print(f"{ 'Red' if self.player_turn == 'B' else 'Blue' } wins!")
    def start_game(self):
        self.display_board(self.board, self.taken_pieces)
        player_count = None
        while(player_count not in ['0', '1', '2']):
            player_count = input("How many players? (0, 1 or 2)\n")
        if player_count == '0':
            print('sorry, not implemented yet')
        elif player_count == '1':
            print('sorry, not implemented yet')
        elif player_count == '2':
            self.play_game()
    
    def get_all_moves(self):
        pass

if __name__ == '__main__':
    game = CheckerGame()
    game.start_game()