import chess
import chess.pgn, chess.engine
import re
from io import StringIO
from typing import List, Dict
from utils.testing_utils import profile

def init_engine(stockfish_path: str) -> chess.engine:
    return chess.engine.SimpleEngine.popen_uci(stockfish_path)

def load_game(pgn_str: str) -> chess.pgn:
    pgn_io = StringIO(pgn_str)
    game = chess.pgn.read_game(pgn_io)
    return game

def get_metadata(game: chess.pgn, username: str) -> Dict:
    headers = game.headers
    return {
        "Opponent": headers.get("Black") if headers["White"] == username else headers.get("White"),
        "OpponentRating": headers.get("BlackElo") if headers["White"] == username else headers.get("WhiteElo"),
        "Date": headers.get("Date"),
        "MoveCount": len(list(game.mainline_moves())),
        "Result": headers.get("Result"),
        "Termination": headers.get("Termination"),
        "Opening": headers.get("ECO"),
        "Opening_url": headers.get("ECOUrl"),
        "TimeControl": headers.get("TimeControl"),
        "Link": headers.get("Link")
    }

def is_opening(board: chess.Board) -> bool:
    if board.fullmove_number > 14:
        return False
    
    if board.is_check():
        return False
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    white_castled = white_king_square in [chess.G1, chess.C1]
    black_castled = black_king_square in [chess.G8, chess.C8]

    if white_castled or black_castled:
        return False

    def count_developed_minors(color):
        original_squares = {
            chess.WHITE: [chess.B1, chess.G1, chess.C1, chess.F1],
            chess.BLACK: [chess.B8, chess.G8, chess.C8, chess.F8]
        }
        minors = board.pieces(chess.KNIGHT, color) | board.pieces(chess.BISHOP, color)
        return sum(1 for sq in minors if sq not in original_squares[color])

    white_dev = count_developed_minors(chess.WHITE)
    black_dev = count_developed_minors(chess.BLACK)

    if white_dev >= 3 and black_dev >= 3:
        return False

    return True

def is_endgame(board: chess.Board) -> bool:
    piece_values = {
        chess.QUEEN: 9,
        chess.ROOK: 5,
        chess.BISHOP: 3,
        chess.KNIGHT: 3
    }

    total_material = sum(
        len(board.pieces(piece, chess.WHITE)) * piece_values[piece] +
        len(board.pieces(piece, chess.BLACK)) * piece_values[piece]
        for piece in piece_values
    )

    white_queen = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queen = len(board.pieces(chess.QUEEN, chess.BLACK))
    total_queens = white_queen + black_queen

    if total_material <= 14 or total_queens <= 1:
        return True

    return False

def classify_phase_sequence(game: chess.pgn) -> str:
    board = game.board()
    phases = []
    current_phase = "opening"

    for node in game.mainline():
        move = node.move
        board.push(move)

        is_open = is_opening(board)
        is_end = is_endgame(board)

        if current_phase == "opening":
            if not is_open:
                current_phase = "middlegame"
        elif current_phase == "middlegame":
            if is_end:
                current_phase = "endgame"

        phases.append(current_phase)

    return phases

def classify_eval_change(prev_cp: int, score_cp: int, player_moved: bool) -> str:
    if abs(score_cp) == 10000:
        if abs(prev_cp) == 10000:
            return "good"
        else:
            return "blunder" if (player_moved and score_cp < 0) or (not player_moved and score_cp > 0) else "good"

    def eval_got_worse(prev_cp, score_cp, white_moved):
        return (white_moved and score_cp < prev_cp) or (not white_moved and score_cp > prev_cp)

    if not eval_got_worse(prev_cp, score_cp, player_moved):
        return "good"
    
    delta_cp = abs(score_cp - prev_cp)

    if abs(prev_cp) > 500:
        if delta_cp >= 500:
            return "blunder"
        elif delta_cp >= 300:
            return "mistake"
        elif delta_cp >= 150:
            return "inaccuracy"
        else:
            return "good"

    if delta_cp >= 300:
        return "blunder"
    elif delta_cp >= 175:
        return "mistake"
    elif delta_cp >= 85:
        return "inaccuracy"
    else:
        return "good"

def analyze_game(game: chess.pgn, engine: chess.engine, player_color: str, depth:int =15) -> List:
    
    board = game.board()
    phases = classify_phase_sequence(game)
    
    evals = []
    eval_graph = [0]
    phase_errors = {
        'opening': {
            'blunder': 0,
            'mistake': 0,
            'inaccuracy': 0
        },
        'middlegame': {
            'blunder': 0,
            'mistake': 0,
            'inaccuracy': 0
        },
        'endgame': {
            'blunder': 0,
            'mistake': 0,
            'inaccuracy': 0
        }
    }
    
    last_eval = 0
    move_number = 0

    is_white = player_color.lower() == "white"
    next_best_move = chess.Move.from_uci("d2d4")
    
    for node in game.mainline():
        player_moved = board.turn  # board.turn returns the person next to move, so do before push
        move = node.move
        board.push(move)

        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        
        if info['score'].is_mate():
            mate_score = info['score'].white().mate()
            score_cp = 10000 if mate_score > 0 else -10000
            score = ('-' if mate_score < 0 else '') + 'M' + str(abs(mate_score))
        else:
            score_cp = info['score'].white().score()
            score = str(score_cp / 100)
            
        category = classify_eval_change(last_eval, score_cp, player_moved)
        eval_graph.append(score_cp)
        
        time = None
        comment = node.comment
        if "%clk" in comment:
            match = re.search(r'%clk\s+(\d+:\d+:\d+)', comment)
            if match:
                time = match.group(1) 

        phase = phases[move_number]
        
        if (player_moved == is_white):    
            if category != 'good':
                phase_errors[phase][category] += 1
        
        evals.append({
            "player": "white" if player_moved else "black",
            "move": board.peek().uci(),
            "move_number": move_number + 1,
            "eval": score,
            "category": category,
            "phase": phase,
            "best_move": next_best_move.uci() if next_best_move else None,
            "time_left": time,
        })
        
        last_eval = score_cp
        move_number += 1
        next_best_move = info.get("pv", [None])[0]
 
    return evals, phase_errors, eval_graph