import unidecode


# https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string


class Task:
    def __init__(self, index, d):
        self.id = index
        self.solution = d['solution']
        self.hints = d['hints']
        self.link = d['link']
        self.clue = d['clue']
        self.points = d['points']

        self.norm_solution = self.normalize_answer(self.solution)

    def __str__(self):
        return f'''Task(index={self.id}, solution={self.solution}, hints={self.hints}, link={self.link})'''

    def __repr__(self):
        return str(self)

    def normalize_answer(self, answ):
        answer = ", ".join(sorted(answ.split(',')))
        for c in ".,!?;\'\"":
            answer = answer.replace(c, " ")
        return " ".join(unidecode.unidecode(answer).lower().split())

    def is_correct(self, answer):
        return self.norm_solution == self.normalize_answer(answer)

    def check_answer(self, answer):
        res = self.is_correct(answer)
        if res:
            msg = "Gratulujeme, to je vskutku správná odpověď. Vyberte si další úkol."
        else:
            msg = "Je nám líto, to je špatná odpověď. Zkuste to znovu."
        return res, msg
