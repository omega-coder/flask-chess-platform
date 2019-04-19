# flask-chess-platform


This repo contains code for a chess platform built with chessboard.js, python-chess && flask microframework.

## Features

- Play against stockfish engine as a second player.
- See game moves in a pretty formatted table. (Standard Algebraic Notation).
- Reset the game whenever you want.
- Undo and redo your moves.

----------------------------------------------

## How to deploy

1. Clone/fork this repository.

```
git clone https://github.com/omega-coder/flask-chess-platform.git
```

2. Install requirements.

```
python3 -m pip install -r requirements.txt
```

3. Install stockfish engine in your system.  
        1. download engine from [stockfish Download](https://stockfishchess.org/download/).  
        2. For linux users, extract and move engine binary to `/usr/bin`.  
        3. change the engine path in Player2 class  
              ```python
              self.__engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")
              ```

4. Run app.py
```
python3 app.py
```

5. Go to http://127.0.0.1:1337

# TODOS
1. Add game time to fontend and synchronize with backend time
2. recognize engines automatically.
3. Allow users to add engine from fontend.
4. Allow user to choose sides.
5. Make board Analysis possible (using ECO). 

