# pgn2data library

A library that converts a chess pgn files into tabulated data sets.

A pgn file can contain one or multiple chess games. The library parses the pgn file and creates two csv files:

- Games file: contains high level information (e.g. date, site, event, score, players etc...)

- Moves file: contains the moves for each game  (e.g. notation, squares, fen position, is in check etc...)

The two files can be mapped together using a GUID which the process inserts into both files.


## Installation

Run the following command on the python terminal:

    pip install pgn2data


## Implementation

Here is a basic example of how to convert a PGN file:

    from converter.pgn_data import PGNData
    
    pgn_data = PGNData("data/pgn/tal_bronstein_1982.pgn")
    result = pgn_data.export()
    result.print_summary()
    
The Result object is a return value from the process, which allows you to check whether the dataset creation was successful.

To group multiple files into the same output file you can do the following:

    pgn_data = PGNData(["data/pgn/file1.pgn","data/pgn/file/file2.pgn"],"output")
    result = pgn_data.export()
    result.print_summary()
    
This process the two pgn files in the specified list and exports them to file called "output.csv".

