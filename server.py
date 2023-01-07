import datetime
import random
from typing import Dict, List, Tuple
from flask import Flask, render_template, jsonify, request
import twl


class WordGrid:
    """
    A class for managing a wordgrid.

    >>> g = WordGrid(4, 4, ["cat", "dog", "rat", "goat"])

    >>> # Set a word:
    >>> g[0, 0:3] = "DOG"
    >>> g[0:3, 0] = "DOG"
    >>> g[2, 1:4] = "OAT"
    """

    def __init__(self, n: int, m: int):
        """
        Initialize a wordgrid with n rows and m columns.

        Arguments:
            n (int): The number of rows.
            m (int): The number of columns.
            words (List[str]): The words to be placed in the wordgrid.

        """
        self.n = n
        self.m = m
        self.grid = self._generate_grid()

    def _generate_grid(self) -> List[List[str]]:
        """
        Generate a wordgrid with n rows and m columns

        Returns:
            List[List[str]]: The generated wordgrid.

        """
        return [["" for _ in range(self.m)] for _ in range(self.n)]

    @staticmethod
    def from_list_of_lists(grid: List[List[str]]) -> "WordGrid":
        """
        Create a wordgrid from a list of lists.

        Arguments:
            grid (List[List[str]]): The list of lists to create the wordgrid from.

        Returns:
            WordGrid: The created wordgrid.

        """
        n = len(grid)
        m = len(grid[0])
        wordgrid = WordGrid(n, m)
        wordgrid.grid = grid
        return wordgrid

    @staticmethod
    def from_list_of_strings(grid: List[str]) -> "WordGrid":
        """
        Create a wordgrid from a list of strings.

        Arguments:
            grid (List[str]): The list of strings to create the wordgrid from.

        Returns:
            WordGrid: The created wordgrid.

        """
        n = len(grid)
        m = len(grid[0])
        wordgrid = WordGrid(n, m)
        wordgrid.grid = [
            [c.lower() if c.isalpha() else "" for c in row] for row in grid
        ]
        return wordgrid

    @staticmethod
    def from_positions(positions: List[Dict]) -> "WordGrid":
        """
        Create a wordgrid from a list of {x, y, letter}

        """
        n = max([p["y"] for p in positions]) + 1
        m = max([p["x"] for p in positions]) + 1
        wordgrid = WordGrid(n, m)
        for p in positions:
            wordgrid.grid[p["y"]][p["x"]] = (
                p["letter"].lower() if p["letter"].isalpha() else ""
            )
        return wordgrid

    def get_rows(self) -> List[List[str]]:
        """
        Get the rows of the wordgrid.

        Returns:
            List[List[str]]: The rows of the wordgrid.

        """
        return self.grid

    def get_columns(self) -> List[List[str]]:
        """
        Get the columns of the wordgrid.

        Returns:
            List[List[str]]: The columns of the wordgrid.

        """
        return list(zip(*self.grid))

    def get_all_words(self) -> List[str]:
        """
        Get all the words in the wordgrid.

        Returns:
            List[str]: The words in the wordgrid.

        """
        rows = self.get_rows()
        columns = self.get_columns()
        words = []
        for row in rows:
            row_words = "".join([w if w else " " for w in row]).split()
            words.extend(row_words)

        for column in columns:
            column_words = "".join([w if w else " " for w in column]).split()
            words.extend(column_words)

        return [w for w in words if len(w) > 1]

    def check_all_words(self) -> List[Tuple[str, bool]]:
        """
        Check all the words in the wordgrid.

        Returns:
            List[Tuple[str, bool]]: A list of tuples of the form (word, is_valid).

        """
        words = self.get_all_words()
        return [(w, twl.check(w)) for w in words]

    def count_connected_components(self):
        """
        Get the connected components of a grid and the number of elements in each component.
        """
        grid = self.grid
        n = len(grid)
        m = len(grid[0])
        visited = [[False for _ in range(m)] for _ in range(n)]
        components = []
        for i in range(n):
            for j in range(m):
                if not visited[i][j] and grid[i][j] != "":
                    component = []
                    stack = [(i, j)]
                    while stack:
                        x, y = stack.pop()
                        if not visited[x][y]:
                            visited[x][y] = True
                            component.append((x, y))
                            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                                if (
                                    0 <= x + dx < n
                                    and 0 <= y + dy < m
                                    and not visited[x + dx][y + dy]
                                    and grid[x + dx][y + dy] != ""
                                ):
                                    stack.append((x + dx, y + dy))
                    components.append(component)
        return components, [len(c) for c in components]

    def __setitem__(self, key, value):
        """
        Set the value of the wordgrid at the given key.

        Arguments:
            key (tuple[int, int]): The key of the wordgrid.
            value (str): The value to set at the given key.

        """
        value = value.lower()
        # key can be (int, int), in which case, just set the value:
        if (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
            and isinstance(key[1], int)
        ):
            self.grid[key[0]][key[1]] = value

        # key can also be a tuple of an int and a slice, like [1, 2:4], in
        # which case, we need to first verify that at least one of the key
        # items is an integer, and then set the value at the given key:
        elif (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
            and isinstance(key[1], slice)
        ):
            start = key[1].start
            stop = key[1].stop
            step = key[1].step
            if start is None:
                start = 0
            if stop is None:
                stop = self.m
            if step is None:
                step = 1
            for j, i in enumerate(range(start, stop, step)):
                self.grid[key[0]][i] = value[j]

        # key can also be a tuple of a slice and an int, like [2:4, 1], in
        # which case we do the same, but with the rows:
        elif (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], slice)
            and isinstance(key[1], int)
        ):
            start = key[0].start
            stop = key[0].stop
            step = key[0].step
            if start is None:
                start = 0
            if stop is None:
                stop = self.n
            if step is None:
                step = 1
            for j, i in enumerate(range(start, stop, step)):
                self.grid[i][key[1]] = value[j]

    def __getitem__(self, key):
        """
        Get the value of the wordgrid at the given key.

        Arguments:
            key (tuple[int, int]): The key of the wordgrid.

        Returns:
            str: The value of the wordgrid at the given key.

        """
        # key can be (int, int), in which case, just get the value:
        if (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
            and isinstance(key[1], int)
        ):
            return self.grid[key[0]][key[1]]

        # key can also be a tuple of an int and a slice, like [1, 2:4], in
        # which case, we need to first verify that at least one of the key
        # items is an integer, and then get the value at the given key:
        elif (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
            and isinstance(key[1], slice)
        ):
            start = key[1].start
            stop = key[1].stop
            step = key[1].step
            if start is None:
                start = 0
            if stop is None:
                stop = self.m
            if step is None:
                step = 1
            return [self.grid[key[0]][i] for i in range(start, stop, step)]

        # key can also be a tuple of a slice and an int, like [2:4, 1], in
        # which case we do the same, but with the rows:
        elif (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], slice)
            and isinstance(key[1], int)
        ):
            start = key[0].start
            stop = key[0].stop
            step = key[0].step
            if start is None:
                start = 0
            if stop is None:
                stop = self.n
            if step is None:
                step = 1
            return [self.grid[i][key[1]] for i in range(start, stop, step)]

        elif (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], slice)
            and isinstance(key[1], slice)
        ):
            # Return the 2D slice
            start0 = key[0].start
            stop0 = key[0].stop
            step0 = key[0].step
            start1 = key[1].start
            stop1 = key[1].stop
            step1 = key[1].step
            if start0 is None:
                start0 = 0
            if stop0 is None:
                stop0 = self.n
            if step0 is None:
                step0 = 1
            if start1 is None:
                start1 = 0
            if stop1 is None:
                stop1 = self.m
            if step1 is None:
                step1 = 1
            return [
                [self.grid[i][j] for j in range(start1, stop1, step1)]
                for i in range(start0, stop0, step0)
            ]

    def __str__(self):
        """
        Get a string representation of the wordgrid.

        Returns:
            str: The string representation of the wordgrid.

        """
        return "\n".join([" ".join(r if r else "_" for r in row) for row in self.grid])

    def get_bounding_box_extents(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get the bounding box extents of the wordgrid.

        Returns:
            Tuple[Tuple[int, int], Tuple[int, int]]: The bounding box extents of the wordgrid.

        """
        rows = self.get_rows()
        columns = self.get_columns()
        min_row = None
        max_row = None
        min_column = None
        max_column = None
        for i, row in enumerate(rows):
            if any(row):
                if min_row is None:
                    min_row = i
                max_row = i
        for i, column in enumerate(columns):
            if any(column):
                if min_column is None:
                    min_column = i
                max_column = i
        return (min_row, max_row), (min_column, max_column)  # type: ignore

    def get_bounding_box_area(self) -> int:
        """
        Get the bounding box area of the wordgrid.

        Returns:
            int: The bounding box area of the wordgrid.

        """
        (min_row, max_row), (min_column, max_column) = self.get_bounding_box_extents()
        return (max_row - min_row + 1) * (max_column - min_column + 1)


# GAMES = [
#     "MOLTEDAAVOPBOT",
# ]

GAMES = {
    "2023-01-06": {"letters": "MOLTEDAAVOPBOT", "best_score": 20},
    "2023-01-07": {"letters": "MOLTEDAAVOPBOT", "best_score": 20},
    "2023-01-08": {"letters": "BARNAREALIARLADY", "best_score": 16},
    "2023-01-09": {"letters": "SLAMTILEEATSPROS", "best_score": 16},
}


def get_todays_game() -> dict:
    """
    Get the letters for today's game.

    Returns:
        str: The letters for today's game.

    """
    today = datetime.date.today().isoformat()
    return GAMES[today]


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(
        dict(
            block_start_string="<%",
            block_end_string="%>",
            variable_start_string="%%",
            variable_end_string="%%",
            comment_start_string="<#",
            comment_end_string="#>",
        )
    )


app = CustomFlask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/game", methods=["GET"])
def get_game():
    game = get_todays_game()
    letters = game["letters"]
    # Shuffle:
    letters = "".join(random.sample(letters, len(letters)))
    return jsonify({"letters": letters})


@app.route("/api/submit", methods=["POST"])
def submit():
    data = request.get_json()
    try:
        wg = WordGrid.from_positions(data["positions"])
        error = None
        check = wg.check_all_words()
        any_word_fail = any([not c[1] for c in check])
        if any_word_fail:
            error = "The following words are not allowed: {}".format(
                ", ".join([c[0] for c in check if not c[1]])
            )
        components = wg.count_connected_components()
        if len(components[1]) > 1:
            error = "All words must be connected."

        return jsonify(
            {
                "error": error,
                "words": wg.get_all_words(),
                "word_check": check,
                "bounding_box_area": wg.get_bounding_box_area(),
                "lowest_score": get_todays_game()["best_score"],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5030, host="0.0.0.0")
