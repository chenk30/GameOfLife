
class GOL(dict):
    """A Game of Life board, represented as a dictionary."""

    def __init__(self, initial_board, board_size, *args, **kwargs):
        """Setting up our constructor."""
        super(GOL, self).__init__(*args, **kwargs)
        self.board_size = board_size
        self.is_stable = False
        self.max_size = len(initial_board)
        self.previous_boards = set()
        for k in initial_board.keys():
            self[k] = initial_board[k]

        self.previous_boards.add(tuple(self.keys()))

    def __missing__(self, *args, **kwargs):
        """An empty cell returns value zero.

        This is what lets us store a huge board and ignore dead cells.
        An Array based implementation would be very space intensive and
        expensive to iterate over."""
        return 0

    def check_cell(self, x: int, y: int):
        """check step for a cell. Determine if it lives or dies.

        Returns:
            live, dead: Two Lists of cells that live or die respectively.
        """
        total = 0

        # Sum up the value of all adjacent cells. You can easily speculate
        # neighbors from this total.
        for x_coord in (x-1, x, x+1):
            for y_coord in (y-1, y, y+1):
                total += self[x_coord, y_coord]

        # Creating the death and birth counts related to this cell.
        cell = self[x, y]
        change = 2 # 0 - dead, 1 - live, 2 - no change

        if total == 3 and not cell:
            change = 1
        elif total < 3 or total > 4 and cell:
            change = 0

        return change

    def queue_cells(self):
        """Get a list of all cells that need to be checked this transition.

        Rather than just calculating alive cells, we need to calculate values
        for their neighbors too, so life can spread. We also don't want to cycle
        through every cell in the world. The Game of Life is super sparse.
        """
        cells = set()
        for x, y in self.keys():
            # Add all cell neighbors to the function.
            x_coords = (x-1, x, x+1)
            y_coords = (y-1, y, y+1)
            for x_coord in x_coords:
                for y_coord in y_coords:
                    if 0 <= x_coord < self.board_size and 0 <= y_coord < self.board_size:
                        cells.add((x_coord, y_coord))
        return cells

    def play_game(self):
        """Play one turn in the game of life."""
        live, dead = [], []
        # Create all the transitions for the turn
        for x, y in self.queue_cells():
            change = self.check_cell(x, y)
            if change == 0:
                dead.append((x, y))
            elif change == 1:
                live.append((x, y))

        # Apply all transitions. Remember that in Life, the state of the board
        # doesn't change until every cell is accounted for.
        for x, y in dead:
            if self[x, y]:
                del self[x, y]
        for x, y in live:
            self[x, y] = 1

        const_board = tuple(self.keys())
        if const_board in self.previous_boards:
            self.is_stable = True

        self.previous_boards.add(const_board)
        if len(self) > self.max_size:
            self.max_size = len(self)

    def play_until_stable(self, max_turns):
        for i in range(max_turns):
            self.play_game()
            if self.is_stable:
                break

        return i

    def get_board_size(self):
        return self.board_size

    def get_max_size(self):
        return self.max_size
