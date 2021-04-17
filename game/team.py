import os
from typing import Dict, List

from game.task import Task
from utils import get_time


class Team:
    STARTING_VALUES = {
        "state": "MOVE",
        "task" : -1
    }

    NULL_TASK = Task(-1, {'link': 'nic', 'clue': "", 'hints': [], 'solution': "",'points':0})

    def __init__(self, secpassw: str, name: str, tasks: List[Task]):
        self.secpassw = secpassw
        self.name = name

        self.answers = set()
        self.solved_tasks = set()
        self.unlocked_hints = set()

        self.filename = "team_%s_%s" % (self.name.replace(" ", "-"), secpassw)

        starting_values = self.load() if os.path.isfile(self.filename) else Team.STARTING_VALUES

        self.state = starting_values["state"]  # "MOVE" # or "ANSWER"
        self.task = tasks[int(starting_values["task"])]

    def parse_answer(self, line):
        _, corr_wrong, task, *answ = line.split()
        if corr_wrong == "correct_answer":
            self.solved_tasks.add(int(task))
            c = True
        elif corr_wrong == "wrong_answer":
            c = False
        else:
            print(corr_wrong)
            hint = answ[0]
            self.unlocked_hints.add((int(task), int(hint)))
            return
        self.answers.add((c, int(task), " ".join(answ)))

    def save(self, msg):
        with open(self.filename, "a") as f:
            print("@ %s" % get_time(), file=f)
            print(msg, file=f)

    def load(self):
        # načte se stav týmu z databáze (ze souboru)
        starting_values = {}
        with open(self.filename, "r") as f:
            for line in f:
                a, *b = line.split()
                if a == "#":
                    self.parse_answer(line)
                    continue
                if a == "@":
                    continue
                b = " ".join(b)
                starting_values[a] = b
        return starting_values

    def statustext(self):
        text = f"Vítej týme {self.name}."

        if self.state == "ANSWER":
            text += "Právě máte plnit&nbsp;"
            text += ' <a href="%s" target=_blank>úkol na tomto odkazu.</a>' % self.task.link
        else:
            text += " Vyberte si nový úkol."
        return text

    def get_points(self, tasks):
        return sum([tasks[i].points for i in self.solved_tasks])

    def get_results(self, tasks):
        """ row for the results table """
        return [self.name, ", ".join(map(str, sorted(self.solved_tasks))), self.get_points(tasks)]

    def check_answer(self, answer):
        if self.state != "ANSWER":
            raise Exception("invalid state")
        res, msg = self.task.check_answer(answer)
        if res:
            s = "# correct_answer"
            self.set_state("MOVE")
        else:
            s = "# wrong_answer"
        s += " %d %s" % (self.task.id, answer)
        self.save(s)
        return res, msg

    def set_task(self, task: Task):
        self.task = task.id
        self.set_state("ANSWER")
        self.save(f"task {task.id}")

    def set_state(self, new):
        self.state = new
        self.save("state %s" % new)

    def get_solved_tasks(self):
        return self.solved_tasks

    def task_table(self, tasks: Dict):
        def answ(i):
            a = [(ans, c) for c, t, ans in self.answers if t == i]
            return a

        def unlock(i, j):
            if (i, j) in self.unlocked_hints:
                return tasks[i].hints[j]
            if j == 0:
                k = 1
            else:
                k = 4
            return "<a href=/tasks/%s/unlock/%d/%d>odemknout nápovědu %d za %d Kčs.</a>" % (
                self.secpassw, i, j, j + 1, k)

        def solved_task(i):
            clue = tasks[i].clue
            return [i, tasks[i].link, answ(i), unlock(i, 0), unlock(i, 1), clue, "success"]

        def current_task(i):
            t = solved_task(i)
            t[6] = "danger"
            t[5] = ""  # remove clue
            return t

        def t(i):
            # číslo úkolu, link, [("odpověď",False), ("správně",True)], 
            # "náp. 1", "náp. 2", "indicie", table row style class
            if i == self.task.id:
                return current_task(i)
            if i in self.solved_tasks:
                return solved_task(i)
            # unresolved tasks:
            return [i, "", [], "", "", "", ""]

        tab = [t(i) for i in sorted(tasks.keys()) if i > 0]
        return tab

    def unlock_hint(self, task, hint):
        t = int(task)
        h = int(hint)
        if (t, h) in self.unlocked_hints:
            return
        self.unlocked_hints.add((t, h))
        self.save("# hint %s %s" % (task, hint))
        if h == 0:
            m = 1
        else:
            m = 4
        return ""
