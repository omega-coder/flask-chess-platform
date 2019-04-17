function onDrop(source, target, piece) {
  var pn = piece.includes('b')
    ? piece.toUpperCase().substring(1, 2)
    : piece.substring(1, 2);
  pn = piece.includes('P') ? '' : pn;
  var move = piece.includes('P')
    ? source + target
    : pn + source.substring(0, 1) + target;
  move =
    piece.includes('P') && target.includes('8')
      ? target.substring(0, 1) + '8Q'
      : move; // pawn promotion

  $.get('/move', {move: move}, function(data) {
    console.log(data);
    document.querySelector('#pgn').innerText = data.pgn;
    board.position(data.fen);
  });
}

$('#reset').click(function() {
  $.get('/reset', function(data) {
    board.position(data.fen);
    document.querySelector('#pgn').innerText = data.pgn;
  });
});

$('#undo').click(function() {
  if (!$(this).hasClass('text-muted')) {
    $.get('/undo', function(data) {
      board.position(data.fen);
      document.querySelector('#pgn').innerText = data.pgn;
    });
  } else {
    //
  }
});

$('#redo').click(function() {
  if (!$(this).hasClass('text-muted')) {
    $.get('/redo', function(data) {
      board.position(data.fen);
      document.querySelector('#pgn').innerText = data.pgn;
    });
  } else {
    //
  }
});
