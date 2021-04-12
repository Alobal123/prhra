from os import path

from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, validators, SelectField

from game.game import Game
from game.team import Team
from game_variables import *

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

PROJECT_DIR = path.dirname(__file__)
TASKS = path.join(PROJECT_DIR, 'Data POH - úkoly--pro server.csv')
PLACES = path.join(PROJECT_DIR, 'Data POH - kostely--pro server.tsv')
app.game = Game(task_file=TASKS, place_file=PLACES)


class TeamLogin(Form):
    team = TextField('Team:', validators=[validators.required()])
    password = TextField('Password:', validators=[validators.required()])

    def check_login(self, team, passw):
        if team in teams_passwords:
            if teams_passwords[team] == passw:
                return True, "Správně!"
            else:
                return False, "Špatné heslo. Přihlašování bude zpřístupněno v 19.30."
        else:
            return False, "Špatný název týmu. Přihlašování bude zpřístupněno v 19.30."


@app.route("/", methods=['GET', 'POST'])
def teamlogin():
    form = TeamLogin(request.form)
    res = False
    if request.method == 'POST':
        team = request.form['team']
        password = request.form['password']

        if form.validate():
            res, msg = form.check_login(team, password)
            flash(msg)
        else:
            flash('Chyba: Vyplň jméno týmu a heslo.')

    # wrong or no login yet
    if not res or request.method == 'GET':
        return render_template('index.html', form=form)

    # correct login
    sec = teams_secret_passwords[team]
    return redirect("/home/%s" % sec)


class SubmitTask(Form):
    answer = TextField('Answer:', validators=[validators.required()])


# class Move(Form):
#    place = SelectField('Place:', validators=[validators.required()])

@app.route("/home/<teamsec>", methods=['GET', 'POST'])
def home(teamsec):
    team = Team(teamsec, name=secpasswords_teams[teamsec], places=app.game.places)
    text = team.statustext()

    form = SubmitTask(request.form)
    if team.state == "MOVE":
        templ = "move"
        moving_options = team.moving_options()
        ch = [(i, "%s (%d času, %d Kčs)" % (n, d, p)) for i, (n, (d, p)) in enumerate(moving_options)]
        form.answer = SelectField('Place:', validators=[validators.required()],
                                  choices=ch
                                  )
        form.ch = "".join('<option value="%d">%s</option>' % o for o in ch)

    else:
        templ = "home"
        moving_options = []

    if form.validate():
        answer = request.form["answer"]
        if team.state == "MOVE":
            try:
                new_place = moving_options[int(answer)][0]
            except ValueError:
                return "Posíláš odpověď na úkol, který už někdo z tvého týmu vyřešil. Refreshuj."

            res, msg = team.check_move(app.game.places[new_place])
            if res:
                templ = "home"
                flash(msg)
                return redirect('/home/%s' % teamsec)
            flash(msg)
        else:  # answering question
            res, msg = team.check_answer(answer)
            if res:  # correct answer changes state
                flash(msg)
                return redirect('/home/%s' % teamsec)
            flash(msg)
    else:
        if request.method == "POST":
            flash("Pošli odpověď.")
    return render_template('%s.html' % templ, teamsec=teamsec, text=text, form=form, moving=moving_options)


@app.route("/results/<teamsec>", methods=['GET'])
def results(teamsec):
    team = Team(teamsec, name=secpasswords_teams[teamsec], places=app.game.places)

    table = []
    for ts in teams_secret_passwords.values():
        x = Team(ts, name=secpasswords_teams[ts], places=app.game.places).get_results()
        table.append(x)
    for i, t in enumerate(sorted(table, key=lambda x: -x[-1])):
        t = [i + 1] + t
        table[i] = t
    return render_template('results.html', teamsec=teamsec, table=table)


@app.route("/tasks/<teamsec>", methods=['GET'])
def tasks(teamsec, msg=""):
    team = Team(teamsec, name=secpasswords_teams[teamsec], places=app.game.places)
    ttable = team.task_table(tasks=app.game.tasks)

    def render_answ(x):
        a = ""
        for answ, c in x:
            if c:
                tag = "b"
            else:
                tag = "del"
            a += "<%s>%s</%s> " % (tag, answ, tag)
        return a

    for t in ttable:
        link = t[1]
        if link:
            t[1] = '<a href="%s">odkaz</a>' % link
        t[2] = render_answ(t[2])

    return render_template('tasks.html', teamsec=teamsec, table=ttable, msg=msg)


@app.route("/tasks/<teamsec>/unlock/<task>/<hint>", methods=['GET'])
def unlock_hint(teamsec, task, hint):
    team = Team(teamsec, name=secpasswords_teams[teamsec], places=app.game.places)
    msg = team.unlock_hint(task, hint)
    return tasks(teamsec)


if __name__ == "__main__":
    app.run()
