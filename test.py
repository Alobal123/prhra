from game.game import Game


if __name__ == '__main__':
    tasks = Game.load_tasks('data/tasks.csv')
    paths = Game.load_task_paths('data/task_path.json', tasks)