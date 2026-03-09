import copy

class AdmiralAI:
    def __init__(self, depth=3):
        self.depth = depth

    def evaluate(self, state):
        score = 0
        for v in state['vessels']:
            mult = 1 if v['side'] == 'AI' else -1
            score += (v['hull'] + (v['marines'] * 0.5)) * mult
        return score

    def minimax(self, state, depth, alpha, beta, maximizing):
        if depth == 0 or self.is_terminal(state):
            return self.evaluate(state)

        if maximizing:
            max_eval = float('-inf')
            for move in self.get_possible_moves(state, 'AI'):
                eval = self.minimax(self.simulate(state, move), depth-1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = float('inf')
            # Minimize player logic...
            return min_eval