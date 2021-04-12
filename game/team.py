import os
from typing import Dict

from game.place import Place
from utils import get_time


class Team:
    STARTING_VALUES = {
        "state": "MOVE",
        "place": "start",
        "time": "360",
        "money": "5",
    }

    def __init__(self, secpassw: str, name: str, places):
        self.secpassw = secpassw
        self.name = name

        self.answers = set()
        self.solved_tasks = set()
        self.unlocked_hints = set()

        self.filename = "team_%s_%s" % (self.name.replace(" ", "-"), secpassw)

        starting_values = self.load() if os.path.isfile(self.filename) else Team.STARTING_VALUES

        self.state = starting_values["state"]  # "MOVE" # or "ANSWER"
        self.time = int(starting_values["time"])
        self.place = places[starting_values["place"]]
        self.money = int(starting_values["money"])

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
        text = "Jste tým %s. Nacházíte se na místě %s. Máte %s času a %d Kčs. "
        text = text % (self.name, self.place, self.time, self.money)

        if self.state == "ANSWER":
            text += "Právě máte plnit&nbsp;"
            text += ' <a href="%s" target=_blank>úkol na tomto odkazu.</a>' % self.place.task.link
        else:
            text += "Právě se máte přesouvat."
        return text

    def moving_options(self):
        return self.place.moving_options()

    def get_points(self):
        return 4 * len(self.solved_tasks) + min(0, self.money) + min(0, self.time // 15)

    def get_results(self):
        """ row for the results table """
        return [self.name, self.time, self.money, ", ".join(map(str, sorted(self.solved_tasks))), self.get_points()]

    def check_answer(self, answer):
        if self.state != "ANSWER":
            raise Exception("invalid state")
        res, msg = self.place.check_answer(answer)
        if res:
            s = "# correct_answer"
            self.set_state("MOVE")
        else:
            s = "# wrong_answer"
        s += " %d %s" % (self.place.task.index, answer)
        self.save(s)
        return res, msg

    def check_move(self, newplace: Place):
        if self.state != "MOVE":
            raise Exception("can't  move in answer state")
        res, msg, (d, p) = self.place.check_move(newplace)
        if res:
            self.set_place(newplace)
            self.set_state("ANSWER")
            self.set_time(self.time - d)
            self.set_money(self.money - p)
        return res, msg

    def set_state(self, new):
        self.state = new
        self.save("state %s" % new)

    def set_place(self, new_place: Place):
        self.place = new_place  # places[new]
        self.save("place %s" % new_place.name)

    def set_time(self, new):
        self.time = new
        self.save("time %s" % new)

    def set_money(self, new):
        self.money = new
        self.save("money %s" % new)

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
            if i == self.place.task.index:
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
        self.money -= m
        self.set_money(self.money)
        return ""
