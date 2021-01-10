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

    def print_summary(self):
        """
        return a summary to console
        """
        print("is complete: {}".format(str(self.is_complete)))
        print("games file: {} size: {}".format(self.games_file.name, self.games_file.size))
        print("moves file: {} size: {}".format(self.moves_file.name, self.moves_file.size))


class ResultFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size
