#!/usr/bin/env python3


# coding : utf-8

from flask import Flask, Response, request, render_template
import chess, chess.pgn
import traceback
import time



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
    board = chess.Board()
    Human  = Player1(board)
    Human2 = Player2(board)

    app = Flask(__name__, static_url_path='')
    @app.route('/')
    def index():
        global board
        return render_template('index.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))
        #ret_page = open('index.html').read()
        #return ret_page.replace('start', board.board_fen())


    @app.route('/move')
    def move():
        global board
        if not board.is_game_over():
            move_san = request.args.get('move', default="")
            if move_san is not None and move_san != '':
                try:
                    if Human.is_turn():
                        print("White's turn to play:")
                    else:
                        print("Black's turn to play")
                    if Human.is_turn():
                        board = Human.make_move(str(move_san))
                    else:
                        board = Human2.make_move(str(move_san))
                    print(board)
                except Exception:
                    traceback.print_exc()
                response = app.response_class(
                    response=board.board_fen(),
                    status=200
                )
                return response
            else:
                response = app.response_class(
                    response="game over",
                    status=200
                )
                return response
            return index()

    @app.route("/reset", methods=["GET"])
    def reset():
        global board
        Human.reset()
        Human2.reset()
        board = chess.Board()
        Human.set_board(board)
        Human2.set_board(board)
        return render_template("index.html", fen=board.board_fen())



    app.run(host='0.0.0.0', debug=True)

if __name__ == "__main__":
    #console_demo()
    run_game()


