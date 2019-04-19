#!/usr/bin/env python3


# coding : utf-8

from flask import Flask, Response, request, render_template, url_for
import chess, chess.pgn
import chess.engine
import traceback
import time
import collections
import json
from gevent.pywsgi import WSGIServer


class Player(object):
    def __init__(self, board, game_time=300):
        self.__current_board = board

    def make_move(self, move):
        raise NotImplementedError()

class Player1(Player):
    def __init__(self, board, game_time=300):
        self.__current_board = board
        self.__game_time = game_time
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None

    def get_board(self):
        return self.__current_board

    def set_board(self, board):
        self.__current_board = board

    def make_move(self, move):
        if self.__current_board.turn == True:
            if self.__first_move_timestamp is not None:
                self.__first_move_timestamp = int(time.time())
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's Blacks Turn (Player2)***")

        return self.__current_board

    def undo_last_move(self):
        self.__current_board.pop()
        return self.__current_board

    def is_turn(self):
        return self.__current_board.turn == True


    def get_game_time(self):
        return self.__game_time

    def get_time_left(self):
        return self.__time_left

    def reset(self):
        self.__current_board = None
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None


class Player2(Player):
    def __init__(self, board, game_time=300):
        self.__current_board = board
        self.__game_time = game_time
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None
        self.__engine = False
    def get_board(self):
        return self.__current_board

    def set_board(self, board):
        self.__current_board = board

    def make_move(self, move):
        if self.__current_board.turn == False:
            if self.__first_move_timestamp is not None:
                self.__first_move_timestamp = int(time.time())
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's White's Turn (Player1)***")

        return self.__current_board

    def undo_last_move(self):
        self.__current_board.pop()
        return self.__current_board

    def is_turn(self):
        return self.__current_board.turn == False

    def get_game_time(self):
        return self.__game_time

    def get_time_left(self):
        return self.__time_left

    def reset(self):
        self.__current_board = None
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None


    def init_stockfish(self):
        self.__is_engine = True
        try:
            self.__engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")
            return True
        except Exception:
            return False


    def is_engine(self):
        return self.__engine


    def engine_move(self):
        result = self.__engine.play(self.__current_board, chess.engine.Limit(time=0.100))
        move = result.move
        try:
            self.__current_board.push(move)
        except Exception:
            print("Cant push move")
        return self.__current_board


def board_to_game(board):
    game = chess.pgn.Game()

    # undo all moves
    switchyard = collections.deque()
    while board.move_stack:
        switchyard.append(board.pop())

    game.setup(board)
    node = game

    # Replay all moves
    while switchyard:
        move = switchyard.pop()
        node = node.add_variation(move)
        board.push(move)

    game.headers["Result"] = board.result()
    return game


def console_demo():
    global board
    board = chess.Board()
    p1 = Player1(board)
    p2 = Player2(board)
    print(board)
    print("------------------------------------------")

    while True:
        move_san = input('White move: ').strip()
        board = p1.make_move(move_san)
        print(board)
        print('-'*50)
        move_san = input('Black to move: ').strip()
        board = p2.make_move(move_san)
        print(board)
        print("-"*50)


def run_game():
    global board
    global undo_moves_stack
    undo_moves_stack = []
    board = chess.Board()
    Human  = Player1(board)
    engine = Player2(board)
    engine.init_stockfish()

    app = Flask(__name__, static_url_path='')
    @app.route('/', methods=['GET'])
    def index():
        global board
        return render_template('index.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))


    @app.route('/move', methods=['GET'])
    def move():
        global board
        global undo_moves_stack
        if not board.is_game_over():
            move_san = request.args.get('move', default='')
            if move_san is not None and move_san != '':
                try:
                    if Human.is_turn():
                        print("White's turn to play:")
                    else:
                        print("Black's turn to play")
                    if Human.is_turn():
                        board = Human.make_move(str(move_san))
                        undo_moves_stack = [] #make undo moves stack empty if any move is done.
                        if engine.is_turn():
                            board = engine.engine_move()
                    print(board)
                except Exception:
                    traceback.print_exc()
                game_moves_san = [move_uci.san() for move_uci in board_to_game(board).mainline()]
                print(game_moves_san)
                if board.is_game_over():
                    resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'true'}
                else:
                    resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'false'}
                response = app.response_class(
                    response=json.dumps(resp),
                    status=200,
                    mimetype='application/json'
                )
                return response
        else:
            game_moves_san = [move_uci.san() for move_uci in board_to_game(board).mainline()]
            print(game_moves_san)
            resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'true'}
            response = app.response_class(
                response=json.dumps(resp),
                status=200,
                mimetype='application/json'
            )
            return response
        return index()

    @app.route("/reset", methods=["GET"])
    def reset():
        global board
        Human.reset()
        engine.reset()
        board = chess.Board()
        Human.set_board(board)
        engine.set_board(board)

        resp = {"fen": board.board_fen(), 'pgn': str(board_to_game(board).mainline_moves())}
        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )

        return response


    @app.route("/undo", methods=["GET"])
    def undo():
        global board
        global undo_moves_stack
        try:
            undo_moves_stack.append(board.pop())
        except IndexError:
            print("fuck")

        resp = {'fen': board.board_fen(), 'pgn': str(board_to_game(board).mainline_moves())}
        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )
        return response


    @app.route("/redo", methods=["GET"])
    def redo():
        global board
        global undo_moves_stack
        if len(undo_moves_stack) != 0:
            board.push(undo_moves_stack.pop())
        else:
            pass

        resp = {'fen': board.board_fen(), 'pgn': str(board_to_game(board).mainline_moves())}

        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )

        return response


    http_server = WSGIServer(('0.0.0.0', 1337), app)
    http_server.serve_forever()

    #app.run(host='127.0.0.1', debug=True)


if __name__ == "__main__":
    #console_demo()
    run_game()


