import math
import random

PLAYER1, PLAYER2 = 0, 1

class Mancala:

    def __init__(self):
        self.side = [[4] * 6, [4] * 6]
        self.store = [0, 0]
        self.to_move = PLAYER1
        self.last_mover = None        
        self.last_extra_turn = False  
        self.last_captured = 0        

    def copy(self):
        new = Mancala()
        new.side = [row[:] for row in self.side]
        new.store = self.store[:]
        new.to_move = self.to_move
        new.last_mover = self.last_mover
        new.last_extra_turn = self.last_extra_turn
        new.last_captured = self.last_captured
        return new

    def legal_moves(self, player):
        return [i for i in range(6) if self.side[player][i] > 0]

    def is_terminal(self):
        return sum(self.side[0]) == 0 or sum(self.side[1]) == 0

    def apply_move(self, player, pit):
        opp = 1 - player
        stones = self.side[player][pit]
        self.side[player][pit] = 0

        bin_index = pit
        last_side, last_bin = None, None
        while stones > 0:
            # filling my bins
            bin_index += 1
            while bin_index < 6 and stones > 0:
                self.side[player][bin_index] += 1
                stones -= 1
                last_side, last_bin = player, bin_index
                if stones == 0:
                    break
                bin_index += 1
            if stones == 0:
                break

            self.store[player] += 1
            stones -= 1
            last_side, last_bin = 'store', None
            if stones == 0:
                break

            # filling his bins
            opp_index = -1
            while opp_index < 5 and stones > 0:
                opp_index += 1
                self.side[opp][opp_index] += 1
                stones -= 1
                last_side, last_bin = opp, opp_index
                if stones == 0:
                    break

            bin_index = -1 

        extra_turn = (last_side == 'store')

        captured = 0
        if last_side == player and self.side[player][last_bin] == 1:
            opp_idx = 5 - last_bin
            opp_stones = self.side[opp][opp_idx]
            if opp_stones > 0:
                self.store[player] += opp_stones + 1
                self.side[opp][opp_idx] = 0
                self.side[player][last_bin] = 0
                captured = opp_stones + 1

        self._sweep_if_terminal()

        self.last_mover = player
        self.last_extra_turn = extra_turn
        self.last_captured = captured
        self.to_move = player if extra_turn else opp
        return extra_turn

    def _sweep_if_terminal(self):
        if sum(self.side[0]) == 0:
            self.store[1] += sum(self.side[1])
            self.side[1] = [0] * 6
        elif sum(self.side[1]) == 0:
            self.store[0] += sum(self.side[0])
            self.side[0] = [0] * 6

    def heuristic1(self, player):
        opp = 1 - player
        return self.store[player] - self.store[opp]

    def heuristic2(self, player, W1=1, W2=1):
        opp = 1 - player
        return W1 * self.heuristic1(player) + W2 * (sum(self.side[player]) - sum(self.side[opp]))

    def heuristic3(self, player, W1=1, W2=1, W3=1):
        opp = 1 - player
        bonus = 0
        if self.last_extra_turn:
            if self.last_mover == player:
                bonus = 1
            elif self.last_mover == opp:
                bonus = -1
        return self.heuristic2(player, W1, W2) + W3 * bonus

    def heuristic4(self, player, W1=1, W2=1, W3=1, W4=1):
        opp = 1 - player
        bonus = 0
        if self.last_mover == player:
            bonus = self.last_captured
        elif self.last_mover == opp:
            bonus = -self.last_captured
            
        return self.heuristic3(player, W1, W2, W3) + W4 * bonus

    def evaluate(self, player, heuristic_num, weights):
        if heuristic_num == 1:
            return self.heuristic1(player)
        if heuristic_num == 2:
            return self.heuristic2(player, *weights)
        if heuristic_num == 3:
            return self.heuristic3(player, *weights)
        return self.heuristic4(player, *weights)

    def print_board(self, mover_label):
        print(f"\n[Player 2 store = {self.store[1]}]")
        print("  P2 bins:", self.side[1])
        print("  P1 bins:", self.side[0])
        print(f"[Player 1 store = {self.store[0]}]   <- to move: {mover_label}\n")

def max_value(state, depth, alpha, beta, heuristic_num, weights):
    if depth == 0 or state.is_terminal():
        return state.evaluate(PLAYER1, heuristic_num, weights), None
    moves = state.legal_moves(PLAYER1)
    if not moves:
        return state.evaluate(PLAYER1, heuristic_num, weights), None
    random.shuffle(moves) 
    v, best_move = -math.inf, moves[0]
    for m in moves:
        child = state.copy()
        child.apply_move(PLAYER1, m)
        if child.to_move == PLAYER1:  #extra turn
            val, move = max_value(child, depth - 1, alpha, beta, heuristic_num, weights)
        else:
            val, move = min_value(child, depth - 1, alpha, beta, heuristic_num, weights)
        if val > v:
            v, best_move = val, m
        alpha = max(alpha, v)
        if alpha >= beta:
            break  # prune
    return v, best_move


def min_value(state, depth, alpha, beta, heuristic_num, weights):
    if depth == 0 or state.is_terminal():
        return state.evaluate(PLAYER1, heuristic_num, weights), None
    moves = state.legal_moves(PLAYER2)
    if not moves:
        return state.evaluate(PLAYER1, heuristic_num, weights), None
    random.shuffle(moves)
    v, best_move = math.inf, moves[0]
    for m in moves:
        child = state.copy()
        child.apply_move(PLAYER2, m)
        if child.to_move == PLAYER2:  # extra turn
            val, move = min_value(child, depth - 1, alpha, beta, heuristic_num, weights)
        else:
            val, move = max_value(child, depth - 1, alpha, beta, heuristic_num, weights)
        if val < v:
            v, best_move = val, m
        beta = min(beta, v)
        if alpha >= beta:
            break  # prune
    return v, best_move


def best_move(state, depth, heuristic_num, weights):
    if state.to_move == PLAYER1:
        return max_value(state, depth, -math.inf, math.inf, heuristic_num, weights)
    else:
        return min_value(state, depth, -math.inf, math.inf, heuristic_num, weights)

def main():
    win1 = 0
    win2 = 0
    heuristics = [1, 2, 3, 4]
    depths = [2, 3, 4, 5, 6]
    heuristicwithdepth = [(h, d, h2, d2) for h in heuristics for d in depths for h2 in heuristics for d2 in depths]

    for heuristic_1, depth_1, heuristic_2, depth_2 in heuristicwithdepth:
        state = Mancala()
        weights1 = (1, 1, 1, 1)[: heuristic_1] if heuristic_1 > 1 else ()
        weights2 = (1, 1, 1, 1)[: heuristic_2] if heuristic_2 > 1 else ()

        while not state.is_terminal():
            # state.print_board(f"Player {state.to_move + 1}")
            mover = state.to_move
            if mover == PLAYER1:
                val, move = best_move(state, depth_1, heuristic_1, weights1)
            else:
                val, move = best_move(state, depth_2, heuristic_2, weights2)
            # print(f"Computer (Player {mover + 1}) plays bin {move + 1}")
            state.apply_move(mover, move)

        print(f"\nPlayer 1 (Heuristic {heuristic_1}, Depth {depth_1})")
        print(f"Player 2 (Heuristic {heuristic_2}, Depth {depth_2})")
        print(f"Player 1 store: {state.store[0]}")
        print(f"Player 2 store: {state.store[1]}")
        with open("log.txt", "a") as file:
            file.write(f"Player 1 (Heuristic {heuristic_1}, Depth {depth_1}): {state.store[0]}\n")
            file.write(f"Player 2 (Heuristic {heuristic_2}, Depth {depth_2}): {state.store[1]}\n")
            if state.store[0] > state.store[1]:
                file.write("Player 1 wins!\n")
            elif state.store[1] > state.store[0]:
                file.write("Player 2 wins!\n")
            else:
                file.write("It's a draw!\n")
        if state.store[0] > state.store[1]:
            print("Player 1 wins!")
            win1 += 1
        elif state.store[1] > state.store[0]:
            print("Player 2 wins!")
            win2 += 1
        else:
            print("It's a draw!")

    total = len(heuristicwithdepth)
    print(f"\nFinal results after {total} games: Player 1 wins: {win1}, Player 2 wins: {win2}, Draws: {total - win1 - win2}")
    with open("log.txt", "a") as file:
        file.write(f"\nFinal results after {total} games: Player 1 wins: {win1}, Player 2 wins: {win2}, Draws: {total - win1 - win2}\n")

if __name__ == "__main__":
    main()