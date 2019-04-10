#!/usr/bin/env python3


# coding : utf-8

from flask import Flask, Response, request
import chess, chess.pgn

class Player(object):
    def __init__(self, board):
        self.__current_board = board

    def make_move(self, move):
        raise NotImplementedError()



class Player1(Player):
    def __init__(self, board):
        self.__current_board = board

    def get_board(self):
        return self.__current_board

    def make_move(self, move):
        if self.__current_board.turn == True:
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's Blacks Turn (Player2)***")
        return self.get_board()

class Player2(Player):
    def __init__(self, board):
        self.__current_board = board

    def get_board(self):
        return self.__current_board


    def make_move(self, move):
        if self.__current_board.turn = False:
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's White's Turn (Player1)***")

        return self.__current_board


def start_demo():
    pass



if __name__ == "__main__":
    start_demo()

