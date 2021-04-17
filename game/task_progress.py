from typing import List


class TaskPath(List):

    def __init__(self, name):
        super().__init__()
        self.name = name



class TaskProgressTracker:

    def __init__(self, paths: List[TaskPath]):
        self.paths = paths
        self.path_names = [path.name for path in paths]

    def get_path_names(self):
        return self.path_names

    def _check_not_finished(self, progress: List[int], task_path_name: str):
        for i, path in enumerate(self.paths):
            if path.name == task_path_name and len(path) <= progress[i]:
                return False
        return True

    def get_progress(self, solved_tasks):
        progress = [0] * len(self.paths)
        for task in solved_tasks:
            for i, path in enumerate(self.paths):
                for task2 in path:
                    if task2.id == task:
                        progress[i] += 1
        return progress

    def get_next_task_in_path(self, path_number, solved_tasks):
        # tasks in paths must have ascending ids
        return min(set([task.id for task in self.paths[path_number]]) - solved_tasks)

    def check_move(self, task_path_name: str, progress: List[int]):
        if not task_path_name in self.path_names:
            return False, f"Bohužel, dějová linie {task_path_name} neexistuje. Třeba příští rok! Prozatím vyberte jinou."

        if self._check_not_finished(progress):
            return True, f"K dalšímu řešení jste si vybrali úkol z linie {task_path_name}"

        return False, f"Dějová linie {task_path_name} již byla úspěšně dokončena, vyberte prosím jinou."
