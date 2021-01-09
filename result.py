class Result:
    """
    results of the extract are tracked here
    games_file and moves_file are ResultFile objects
    """

    def __init__(self, is_complete, games_file, moves_file):
        self.is_complete = is_complete
        self.games_file = games_file
        self.moves_file = moves_file

    @staticmethod
    def get_empty_result():
        return Result(False, ResultFile("", 0), ResultFile("", 0))


class ResultFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size
