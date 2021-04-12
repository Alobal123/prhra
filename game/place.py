from game.task import Task


class Place:
    def __init__(self, name: str, task: Task):
        self.name = name
        self.task = task

    def insert_neighbours(self, nd):
        self.neighbours_distances = nd
        self._moving_options = sorted([(n, d) for n, d in self.neighbours_distances.items()])

    def check_answer(self, answer):
        res = self.task.is_correct(answer)
        if res:
            msg = "Správná odpověď. Teď se přesuňte."
        else:
            msg = "Špatná odpověď. Zkuste to znovu."
        return res, msg

    def check_move(self, newplace: "Place"):
        if newplace.name in self.neighbours_distances:
            d, p = self.neighbours_distances[newplace.name]
            return True, "Přesouváte se do místa %s. Trvá vám to %d času. Stálo vás to %d Kčs." % (newplace, d, p), (
                d, p)
        return False, "Chyba, do místa %s se nemůžete přesunout, není tam cesta." % newplace, (0, 0)

    def moving_options(self):
        return self._moving_options

    def __repr__(self):
        return self.name
