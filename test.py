def test_board_ref():
    from board_ref import BoardPieces

    bp = BoardPieces()

    bp.print_board()

    print("piece at e2 before === ", bp.get_piece_at_square("e2"))
    print("piece at e4 before === ", bp.get_piece_at_square("e4"))

    bp.track_move("e2", "e4")

    print("**********************")

    print("piece at e2 before === ", bp.get_piece_at_square("e2"))
    print("piece at e4 after === ", bp.get_piece_at_square("e4"))

    bp.print_board()
