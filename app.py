from crypt import methods
from http.client import responses
from urllib import response
from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey, personality_quiz, surveys

app = Flask(__name__)
app.config["SECRET_KEY"] = "this_is_my_temp_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

QUESTIONS_NUM = 4


@app.route("/")
def show_homepage():
    return render_template("homepage.html")


@app.route("/sessions", methods=["POST"])
def set_sessions():
    survey_type = request.form["survey_type"]
    if session.get(f"{survey_type}_done") == True:
        return redirect(f"/{survey_type}/thank-you")
    else:
        session[survey_type] = []
        return redirect(f"/{survey_type}/questions/1")


@app.route("/<survey_type>/questions/<num>")
def show_question(survey_type, num):
    idx = int(num)
    if len(session.get(survey_type)) == QUESTIONS_NUM:
        session[f"{survey_type}_done"] = True
        return redirect(f"/{survey_type}/thank-you")
    else:
        if len(session.get(survey_type)) < idx - 1:
            flash("You can't skip the question!", "warning")
            return redirect(f"/{survey_type}/questions/{len(session.get(survey_type))+1}")
        else:
            question = surveys[survey_type].questions[idx - 1]
            if len(session.get(survey_type)) > idx - 1:
                checked_value = session.get(survey_type)[idx-1]
            else:
                checked_value = ""
            return render_template("question.html", question=question, num=idx, survey_type=survey_type, value=checked_value)


@app.route("/<survey_type>/answer/<num>", methods=["POST"])
def save_answer(survey_type, num):
    idx = int(num)
    choice = request.form["choices"]
    comment = request.form.get("comment")
    if comment:
        choice = choice + ": " + comment
    answers = session.get(survey_type)
    if len(session.get(survey_type)) > idx - 1:
        answers = answers[:idx-1]
    answers.append(choice)
    session[survey_type] = answers
    flash("Your answer has been saved!", "success")
    return redirect(f"/{survey_type}/questions/{len(session.get(survey_type))+1}")


@app.route("/<survey_type>/thank-you")
def show_thank_you(survey_type):
    return render_template("thank_you.html", survey=surveys[survey_type], type=survey_type)
