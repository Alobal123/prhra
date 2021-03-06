import unidecode
# https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string


class Task:
    def __init__(self, index, d):
        self.index = index
        self.solution = d['solution']
        self.hints = d['hints']
        self.link = d['link']
        self.clue = d['clue']

        self.norm_solution = self.normalize_answer(self.solution)

    def __str__(self):
        return f'''Task(index={self.index}, solution={self.solution}, hints={self.hints}, link={self.link})'''

    def __repr__(self):
        return str(self)

    def normalize_answer(self, answ):
        answer = ", ".join(sorted(answ.split(',')))
        for c in ".,!?;\'\"":
            answer = answer.replace(c, " ")
        return " ".join(unidecode.unidecode(answer).lower().split())

    def is_correct(self, answer):
        return self.norm_solution == self.normalize_answer(answer)
