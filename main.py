class PlayerAgent:

    def __init__(self, name):
        self.name = name

    def notify_other_players_move(self, r, c):
        print(f'{self.name}: I see the other player marked ({r},{c}).')

    def request_move(self):
        print(f'{self.name}:')
        r = input('Row: ')
        c = input('Col: ')
        return (int(r),int(c))

    def notify_game_over(self, outcome):
        print(f'{self.name}: I {outcome}!')

class Board:
    def __init__(self):
        self.spaces = [[' ', ' ', ' '],
                       [' ', ' ', ' '],
                       [' ', ' ', ' ']]

    def print(self):
        for row in self.spaces:
            for space in row:
                print('%s|' % space, end='')
            print('')
            print('-' * 6)

    def is_full(self):
        for row in self.spaces:
            for space in row:
                if space == ' ':
                    return False
        return True

    def set(self, row, col, mark):
        assert(row < 3)
        assert(col < 3)
        assert(self.spaces[row][col] == ' ')
        self.spaces[row][col] = mark

    def find_winner(self):
        return self.find_winner_rowwise() or self.find_winner_colwise() or self.find_winner_diagwise()

    def find_winner_rowwise(self, r=None):
        if r is None:
            return self.find_winner_rowwise(0) or self.find_winner_rowwise(1) or self.find_winner_rowwise(2)
        else:
            return self.spaces[r][0] if self.spaces[r][0] == self.spaces[r][1] and self.spaces[r][0] == self.spaces[r][2] and self.spaces[r][0] != ' ' else None

    def find_winner_colwise(self, c=None):
        if c is None:
            return self.find_winner_colwise(0) or self.find_winner_colwise(1) or self.find_winner_colwise(2)
        else:
            return self.spaces[0][c] if self.spaces[0][c] == self.spaces[1][c] and self.spaces[0][c] == self.spaces[2][c] and self.spaces[0][c] != ' ' else None

    def find_winner_diagwise(self, m=None):
        if m is None:
            return self.find_winner_diagwise(-1) or self.find_winner_diagwise(1)
        else:
            return self.spaces[1][1] if self.spaces[1][1] == self.spaces[0][1+m] and self.spaces[1][1] == self.spaces[2][1-m] and self.spaces[1][1] != ' ' else None

def main():
    board = Board()

    player_x = PlayerAgent('Alice')
    player_o = PlayerAgent('Bob')

    mark = 'x'
    current_player = player_x
    other_player = player_o

    board.print()
    print('')

    while not board.is_full():
        (r, c) = current_player.request_move()
        board.set(r, c, mark)
        other_player.notify_other_players_move(r, c)
        board.print()
        winner = board.find_winner()
        if winner:
            print(f'{winner} won')
            current_player.notify_game_over('win')
            other_player.notify_game_over('lose')
            break

        (current_player, other_player) = (other_player, current_player)
        mark = 'o' if mark == 'x' else 'x'

main()
