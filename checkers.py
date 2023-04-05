import re
import copy
import random
import pickle
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
        self.transition_table = {}
        self.value_table = {}
        self.transition_counts = {}
        self.epsilon = 0.1
        try:
            with open('transition_table.pickle', 'rb') as f:
                self.transition_table = pickle.load(f)
        except FileNotFoundError:
            print("Transition table pickle file not found. Creating new transition table.")
        try:
            with open('state_values.pickle', 'rb') as f:
                self.state_values = pickle.load(f)
        except FileNotFoundError:
            print("State values pickle file not found. Creating new state values.")

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
                    row += '❌'
                elif board[i][j] == 'D':
                    row += '💙'
                elif (i + j) % 2 == 0:
                    row += '◻️ '
                else:
                    row += '◼️ '
            row+=f"|{chr(i+65)}"
            print(row)
        print("  0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣" + "     "+ taken_pieces['B'])

    def is_valid_move(self, move, board, player):
        move = move.replace(' ', '').upper()
        moves = move.split(',')
        board_copy = copy.deepcopy(board)
        jumper = None
        for i, mv in enumerate(moves):
            if not re.match(r'^([A-H][0-7]TO[A-H][0-7])+$', mv):
                return False
            start_row, start_col, end_row, end_col = ord(mv[0]) - ord('A'), int(mv[1]), ord(mv[4]) - ord('A'), int(mv[5])
            if i > 0:
                if jumper is None:
                    return False
                elif jumper != (start_row, start_col):
                    return False
            if (ord(board_copy[start_row][start_col]) - ord(player)) % 2 != 0:
                return False
            if board_copy[start_row][start_col] == '-':
                return False
            if board_copy[end_row][end_col] != '-':
                return False
            if abs(start_row - end_row) != abs(start_col - end_col):
                return False
            if board_copy[start_row][start_col] == 'A' and end_row <= start_row:
                return False
            if board_copy[start_row][start_col] == 'B' and end_row >= start_row:
                return False 
            if abs(start_row - end_row) == 1:
                board_copy[end_row][end_col] = board_copy[start_row][start_col]
                board_copy[start_row][start_col] = '-'
            elif abs(start_row - end_row) == 2:
                if board_copy[(start_row + end_row) // 2][(start_col + end_col) // 2] == '-':
                    return False
                if (ord(board_copy[(start_row + end_row) // 2][(start_col + end_col) // 2]) - ord(player)) % 2 == 0:
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
                    taken = '❌'
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

    def play_game(self, humans, cpu_1_mode, cpu_2_mode):
        game_history = []
        while not self.is_game_over():
            self.display_board(self.board, self.taken_pieces)
            move = None
            if not humans[self.player_turn]:
                options = self.get_all_moves(self.board, self.player_turn)
                move = self.computer_move(options, cpu_1_mode if self.player_turn == 'A' else cpu_2_mode)
                print(f"Robo{'Red' if self.player_turn == 'A' else 'Blue' }'s move: {move}")
            else:
                move = input(f"{ 'Red' if self.player_turn == 'A' else 'Blue' }'s turn.\nEnter your move: [row][col]to[row][col] (comma sep for multiple moves)\n")
            if move == 'help':
                print(self.get_all_moves(self.board, self.player_turn))
            elif move == 'quit':
                break
            elif self.is_valid_move(move,self.board, self.player_turn):
                old_board = copy.deepcopy(self.board)
                old_taken = self.taken_pieces['A'], self.taken_pieces['B']
                old_turn = self.player_turn
                self.make_move(move,self.board, self.taken_pieces)
                game_history.append((old_board, old_taken, old_turn, move, self.board, (self.get_reward(self.taken_pieces, 'A'), self.get_reward(self.taken_pieces, 'B')), self.is_game_over()))
                self.player_turn = 'B' if self.player_turn == 'A' else 'A'
            else:
                print("Invalid move. Try again.")
        if self.has_won('A', self.taken_pieces):
            print("Red wins!")
        elif self.has_won('B', self.taken_pieces):
            print("Blue wins!")
        self.display_board(self.board, self.taken_pieces)
        return game_history
    
    def start_game(self):
        self.display_board(self.board, self.taken_pieces)
        player_count = None
        while(player_count not in ['0', '1', '2']):
            player_count = input("How many players? (0, 1 or 2)\n")
        humans = {'A':True, 'B':True}
        if player_count < '2':
            humans['B'] = False
        if player_count < '1':
            humans['A'] = False
        self.play_game(humans, 'random', 'random')
    
    def get_all_moves(self, board, player):
        valid_actions = []
        for row in range(8):
            for col in range(8):
                if (ord(board[row][col]) - ord(player)) % 2 == 0:
                    self.get_all_singles(board, player, (row, col), valid_actions)
                    self.get_all_jumps(board, player, (row, col), valid_actions)
        return valid_actions
    

    def get_all_singles(self, board, player, pos, valid_actions):
        row, col = pos
        if (ord(board[row][col]) - ord(player)) % 2 == 0:
            for drow, dcol in [(-1, -1), (-1,1), (1,-1), (1,1)]:
                new_row, new_col = row + drow, col + dcol
                single_move = f'{chr(row+ord("A"))}{col}to{chr(new_row+ord("A"))}{new_col}'
                if self.is_valid_move(single_move, board, player):
                    valid_actions.append(single_move)


    def get_all_jumps(self, board, player, pos, valid_actions):
        row, col = pos
        if (ord(board[row][col]) - ord(player)) % 2 != 0:
            return       
        bfs_queue = [(row, col, '')]
        while bfs_queue:
            row, col, path = bfs_queue.pop(0)
            for drow, dcol in [(-2, -2), (-2,2), (2,-2), (2,2)]:
                new_row, new_col = row + drow, col + dcol
                jump_move = f'{chr(row+ord("A"))}{col}to{chr(new_row+ord("A"))}{new_col}'
                if path != '':
                    jump_move = path + ',' + jump_move
                if self.is_valid_move(jump_move, board, player):
                    valid_actions.append(jump_move)
                    bfs_queue.append((new_row, new_col, jump_move))

    def get_reward(self, taken_pieces, player):
        if self.has_won(player, taken_pieces):
            return 1
        elif self.has_lost(player, taken_pieces):
            return -1
        else:
            return 0
        
    def computer_move(self, moves, mode):
        if mode == 'random':
            return self.do_random_move(moves)
        elif mode == 'explore':
            return self.do_explore_move(moves)
        elif mode == 'exploit':
            return self.do_exploit_move(moves)
        
    def do_exploit_move(self, moves):
        move = None
        max_value = -1
        for m in moves:
            if self.value_table.get(m, 0) > max_value:
                move = m
                max_value = self.value_table.get(m, 0)
        return move
    
    def do_explore_move(self, moves):
        if random.random() < self.epsilon:
            return self.do_random_move(moves)
        else:
            return self.do_exploit_move(moves)
        
    def do_random_move(self, moves):
        move = random.choice(moves)
        return move
    def has_won(self, player, taken_pieces):
        return len(taken_pieces[player]) == 12
    
    def has_lost(self, player, taken_pieces):
        opponent = 'B' if player == 'A' else 'A'
        return len(taken_pieces[opponent]) == 12
    
    def train(self):
        print("Training...")
        history = self.play_game({'A':False, 'B':False}, 'random', 'explore')
        print(f'played {len(history)} turns')
        print('Done training!')
        with open('transition_table.pickle', 'wb') as f:
            pickle.dump(self.transition_table, f)
        with open('value_table.pickle', 'wb') as f:
            pickle.dump(self.value_table, f)
        

if __name__ == '__main__':
    game = CheckerGame()
    play_or_train = input("Play or train? ([p]/t)\n")
    if play_or_train == 't':
        game.train()
    else:
        game.start_game()