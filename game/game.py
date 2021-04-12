import re
from typing import List

import pandas as pd

from game.place import Place
from game.task import Task


class Game:

    def __init__(self, task_file: str, place_file):
        print('Loading game')
        self.tasks = {t.index: t for t in self.load_tasks(task_file)}
        places_neighbours, place_tasks = self.load_places(place_file)
        list_places = [Place(n, self.tasks[t]) for n, t in place_tasks]
        self.places = {p.name: p for p in list_places}

        for pn in places_neighbours.keys():
            p = self.places[pn]
            p.insert_neighbours(places_neighbours[pn])

    def load_tasks(self, fname: str) -> List[Task]:
        tasks_data = pd.read_csv(fname, skiprows=1)
        tasks_data = tasks_data.dropna(subset=['stručný popis úkolu'])

        def create_task(row: pd.Series) -> Task:
            hints = [row['nápověda 1'], row['nápověda 2']]
            return Task(row['číslo úkolu'],
                        {'solution': row['správné řešení'], 'hints': hints, 'link': row['odkaz pro hráče (read-only)'],
                         'clue': row['indicie']})

        return tasks_data.apply(create_task, axis=1).tolist()

    def load_places(self, fname: str):
        places = {}
        tasks = []
        first = True
        with open(fname, "r", encoding='utf-8') as f:
            curr = None
            for line in f:
                if first:
                    first = False
                    continue
                *a, b, dur, task, price = re.split("\t", line.rstrip())
                dur = int(dur)
                task = int(task)
                price = int(price)
                x = a[0]
                if not x:
                    x = curr
                curr = x

                if curr not in places:
                    places[curr] = {}
                    tasks.append((curr, task))

                places[curr][b] = (dur, price)
        return places, tasks
