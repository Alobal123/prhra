import json
from typing import List

import pandas as pd

from game.task import Task
from game.task_progress import TaskProgressTracker, TaskPath


class Game:

    def __init__(self, task_file: str, path_file: str):
        print('Loading game')
        self.tasks = sorted(Game.load_tasks(task_file), key= lambda x: x.id)
        self.progress_tracker = Game.load_task_paths(path_file, self.tasks)

    @staticmethod
    def load_tasks(task_definition_file: str) -> List[Task]:
        tasks_data = pd.read_csv(task_definition_file)
        tasks_data = tasks_data.dropna(subset=['stručný popis úkolu'])

        def create_task(row: pd.Series) -> Task:
            hints = [row['nápověda 1'], row['nápověda 2']]
            return Task(row['číslo úkolu'],
                        {'solution': row['správné řešení'], 'hints': hints, 'link': row['odkaz pro hráče (read-only)'],
                         'clue': row['indicie'], 'points':row['body']})

        return tasks_data.apply(create_task, axis=1).tolist()

    @staticmethod
    def load_task_paths(task_path_definiton_file: str, tasks: List[Task]) -> TaskProgressTracker:
        paths = []
        with open(task_path_definiton_file, "r", encoding='utf-8') as f:
            path_dicts = json.load(f)
            for path in path_dicts:
                new_path = TaskPath(name=path["name"])
                paths.append(new_path)
                for task_id in path['tasks']:
                    for task in tasks:
                        if task_id == task.id:
                            new_path.append(task)
        return TaskProgressTracker(paths)
