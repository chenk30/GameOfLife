import random
import datetime
from dataclasses import dataclass
from tqdm import trange
from gol import GOL

# logging information and creating a new file for each configuration
import logging
logger = logging.getLogger(__name__)
now = datetime.datetime.now().strftime("%m_%d_%H_%M_%S")
logging.basicConfig(filename=f'logs\\genetic_run_{now}.txt', level=logging.DEBUG)


@dataclass
class Score:
    score: int
    size: int = 0
    time: float = 0.0

    def __le__(self, other):
        return self.score <= other.score

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        return self.score == other.score

    def __str__(self):
        return f"({self.score:.3f}, {self.size}, {self.time:.3f})"

class GeneticAlg:
    def __init__(self,
                 board_size=40,
                 initial_living_count_min=6,
                 initial_living_count_max=15,
                 initial_living_board_size=5,
                 population_size=10,
                 mutation_chance=0.3,
                 max_turns=1500,
                 generations=5000):
        self.board_size = board_size
        self.initial_living_count_min = initial_living_count_min
        self.initial_living_count_max = initial_living_count_max
        self.initial_living_board_size = initial_living_board_size
        self.population_size = population_size
        self.max_turns = max_turns
        self.generations = generations
        self.mutation_chance = mutation_chance

        self.cache = {}
        self.population_to_score = {}
        self.best = (None, Score(0))

        self.mutations_this_gen = 0
        self.stats_file = open(f'logs\\genetic_run_stats_{now}.csv', 'w')
        self.stats_file.write("gen,best_fit,avg_fit,min_fit,max_fit,mut\n")
        logger.info(str(self))

    def __str__(self):
        return f"""{self.board_size=}
        {self.initial_living_count_min=}
        {self.initial_living_count_max=}
        {self.initial_living_board_size=}
        {self.population_size=}
        {self.max_turns=}
        {self.generations=}
        {self.mutation_chance=}"""

    def _log_evolution_step(self, gen, population):
        avg_fit = 1.0 * sum([x[1].score for x in population]) / len(population)
        min_fit = population[-1][1].score
        max_fit = population[0][1].score
        self.stats_file.write(f"{gen},{self.best[1].score},{avg_fit},{min_fit},{max_fit},{self.mutations_this_gen}\n")
        logger.info(f"gen: {gen}/{self.generations} best: {self.best[1].score} avg: {avg_fit} min: {min_fit} max: {max_fit} mut: {self.mutations_this_gen}")

    def run(self):
        self.create_initial_population()
        t = trange(self.generations)
        for gen in t:
            self.mutations_this_gen = 0
            self.rank_current_population()
            sorted_by_fitness = self.choose_fittest()
            fittest, fittest_rank = sorted_by_fitness[0]
            if fittest_rank > self.best[1]:
                self.best = (fittest, fittest_rank)  # finding new fittest

            t.set_description(f"Max Fit: {self.best[1]} CurrFit: {fittest_rank}", refresh=True)
            self.create_new_gen_from_fittest(sorted_by_fitness)
            self._log_evolution_step(gen, sorted_by_fitness)
        self.rank_current_population()

    def _gen_random_living_cell(self):
        living_board_middle = self.initial_living_board_size // 2
        x = random.randint(-living_board_middle, living_board_middle) + self.board_size // 2
        y = random.randint(-living_board_middle, living_board_middle) + self.board_size // 2
        return x, y

    def _create_random_board(self, living_count):
        living = {}
        while len(living) != living_count:
            # choose points in a grid in the middle of the board
            x, y = self._gen_random_living_cell()
            living[x, y] = 1
        return tuple(living.items())

    def _add_random_board_to_population(self):
        living_count = random.randint(self.initial_living_count_min, self.initial_living_count_max)
        random_board = self._create_random_board(living_count)
        if random_board not in self.population_to_score:
            self.population_to_score[random_board] = Score(0)

    def create_initial_population(self):
        for _ in range(self.population_size):
            self._add_random_board_to_population()

    def _score_board(self, board):
        gol = GOL(dict(board), self.board_size)
        stable_iter = gol.play_until_stable(self.max_turns)
        size = gol.get_max_size() - len(board)
        time = (stable_iter / self.max_turns)
        score = (gol.get_max_size() - len(board)) * (stable_iter / self.max_turns)
        score_class = Score(score, size, time)
        self.population_to_score[board] = score_class
        if not gol.is_stable:
            print(board)
            print(f"Wasn't stable in {self.max_turns}!")

        self.cache[board] = score_class

    def rank_current_population(self):
        for_mutation = []
        for initial_board in self.population_to_score:
            if initial_board in self.cache:
                #for_mutation.append(initial_board)
                self.population_to_score[initial_board] = self.cache[initial_board]
            else:
                self._score_board(initial_board)

        for to_mutate_board in for_mutation:
            del self.population_to_score[to_mutate_board]  # if mutated - we need to delete the already seen board
            while to_mutate_board in self.cache:
                to_mutate_board = self._create_mutation(to_mutate_board)
            self._score_board(to_mutate_board)


    def choose_fittest(self):
        return sorted(self.population_to_score.items(), key=lambda item: item[1].score, reverse=True)

    def _create_mutation(self, child):
        self.mutations_this_gen += 1
        if random.random() < 0.5:
            # kill cell
            i = random.randint(0, len(child))
            child = child[:i] + child[i+1:]
        else:
            # add cell
            x, y = self._gen_random_living_cell()
            if ((x, y), 1) not in child:
                child += (((x, y), 1),)
        return child

    def _mutate(self, child):
        rand = random.random()
        if rand < self.mutation_chance * self.mutation_chance:
            # two mutations
            child = self._create_mutation(child)
        if rand < self.mutation_chance:
            # one mutation
            child = self._create_mutation(child)
        return child

    def _create_children(self, father, mother):
        # get living coords
        father = father[0]
        mother = mother[0]

        # cutoff in middle
        mid_board = self.board_size // 2

        child1 = [((x, y), 1) for ((x, y), _) in father if x < mid_board] + [((x, y), 1) for ((x, y), _) in mother if x >= mid_board]
        child2 = [((x, y), 1) for ((x, y), _) in father if y < mid_board] + [((x, y), 1) for ((x, y), _) in mother if y >= mid_board]
        child3 = [((x, y), 1) for ((x, y), _) in mother if x < mid_board] + [((x, y), 1) for ((x, y), _) in father if x >= mid_board]
        child4 = [((x, y), 1) for ((x, y), _) in mother if y < mid_board] + [((x, y), 1) for ((x, y), _) in father if y >= mid_board]
        children = [child1, child2, child3, child4]
        return [tuple(self._mutate(child)) for child in children]

    def create_new_gen_from_fittest(self, fittest):
        children = []

        # pick top pairs
        for i in range(0, 2 * (self.population_size // 4), 2):
            father, mother = fittest[i], fittest[i+1]
            children += self._create_children(father, mother)

        self.population_to_score = {child: Score(0) for child in children}
        for _ in range(self.population_size - len(self.population_to_score)):
            # add remainder if necessary to get to needed population size
            self._add_random_board_to_population()


def main():
    g = GeneticAlg()
    try:
        g.run()
    except MemoryError:
        pass
    print(g.best)


if __name__ == '__main__':
    main()
