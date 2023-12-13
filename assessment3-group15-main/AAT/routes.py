from flask import render_template, url_for, redirect, flash, request
from AAT import app, db, mail
from sqlalchemy import desc
from AAT.models import (
    User,
    Question,
    Choice,
    TrueFalse,
    Assessment,
    Feedback,
    Result,
    Answers,
)
from AAT.forms import (
    StudentRegistrationForm,
    LecturerRegistrationForm,
    LoginForm,
    ChangePasswordForm,
    UpdateDetailsForm,
    AssessmentDetailsForm,
    QuestionDetailsForm,
    ChoiceDetailsForm,
    TrueFalseDetailsForm,
    ForgotForm,
    PasswordRecoveryForm,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    login_manager,
    current_user,
)
import os
from flask_mail import Message
from AAT.customTokens import (
    generate_email_confirmation_token,
    generate_password_confirmation_token,
    confirm_email_token,
    confirm_password_token,
)

current_dir = os.path.abspath(os.path.dirname(__file__))

login_manager.login_view = "login"


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        if current_user.userType == "student":
            return redirect(url_for("student_home"))
        else:
            return redirect(url_for("lecturer_home"))
    return render_template("home.html")


# loading page


@app.route("/loading")
def loading():
    return render_template("loading.html")


# AAT pages
# student pages


@app.route("/student-home")
@login_required
def student_home():
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    return render_template("student-home.html")


@app.route("/student-summative-main")
@login_required
def student_summative_main():
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))

    assessments = Assessment.query.filter(Assessment.type == "summative").all()
    return render_template("student-summative-main.html", assessments=assessments)


@app.route("/student-summative-question")
@login_required
def student_summative_question():
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    return render_template("student-summative-question.html")


@app.route("/student-formative-main")
@login_required
def student_formative_main():
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    assessments = Assessment.query.filter(Assessment.type == "formative").all()
    return render_template("student-formative-main.html", assessments=assessments)


@app.route("/student-take-assessment/<int:assessment_id>", methods=["GET", "POST"])
@login_required
def student_take_assessment(assessment_id):
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    assessment = Assessment.query.filter(Assessment.id == assessment_id).first()
    questions = Question.query.filter(Question.assessment_id == assessment_id).all()

    attempt_number = (
        max(
            [
                result.attempt
                for result in Result.query.filter(Result.assessment_id == assessment.id)
                .filter(Result.user_id == current_user.id)
                .all()
            ],
            default=0,
        )
        + 1
    )

    if request.method == "POST":
        # print('this should be posted')
        # print(assessment.id)
        result = Result(
            user_id=current_user.id, assessment_id=assessment.id, attempt=attempt_number
        )
        db.session.add(result)
        db.session.commit()
        result_id = result.id
        score = 0

        for question in questions:
            # print(question.id)
            # print(request.form)
            # print(request.form.keys())
            ans = Answers(
                answer=request.form[str(question.id)],
                question_id=question.id,
                result_id=result_id,
            )
            db.session.add(ans)
            db.session.commit()
            # print("trying to add a score")
            # print(bool(not question.truefalse))
            # print(bool(question.choices[0]))
            if not question.truefalse:
                # print(request.form[str(question.id)])
                # print([choice.choice_text for choice in question.choices if choice.is_correct == 'True'])
                if request.form[str(question.id)] in [
                    choice.choice_text
                    for choice in question.choices
                    if choice.is_correct == "True"
                ]:
                    score += 1
            else:
                # print("treying to add a score")
                # print(question.truefalse.is_true)
                # print(request.form[str(question.id)])
                if question.truefalse.is_true == request.form[str(question.id)]:
                    score += 1

        result = Result.query.filter_by(id=result_id).first()
        result.score = score
        # print(result.assessment_id)
        # print("score: " + str(score))
        db.session.commit()
        return redirect(url_for("student_formative_main"))

    return render_template(
        "student-take-assessment.html", assessment=assessment, questions=questions
    )


@app.route("/student-formative-question")
@login_required
def student_formative_question():
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    return render_template("student-formative-question.html")


@app.route("/student-stat-main")
@login_required
def student_stat_main():
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    stats = Result.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "student-stat-main.html",
        stats=stats,
    )


@app.route("/student-stat-explanation/<int:assessment_id>")
@login_required
def student_stat_question(assessment_id):
    if current_user.userType != "student":
        flash("You must be a student to access this page")
        return redirect(url_for("lecturer_home"))
    assessment = Assessment.query.filter(Assessment.id == assessment_id).first()
    questions = Question.query.filter(Question.assessment_id == assessment_id).all()
    return render_template(
        "student-stat-explanation.html", assessment=assessment, questions=questions
    )


# lecturer pages


@app.route("/lecturer-home")
@login_required
def lecturer_home():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-home.html")


@app.route("/lecturer-question")
@login_required
def lecturer_question():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    questions = Question.query.all()
    choice = Choice.query.all()
    return render_template("lecturer-question.html", question=questions, choice=choice)


@app.route("/lecturer-assessment-main")
@login_required
def lecturer_assessment_main():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-assessment-main.html")


@app.route("/lecturer-assessment-create")
@login_required
def lecturer_assessment_create():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-assessment-create.html")


#
# #Create Assessment(Qizhen Ye)--------------------------------------------
# @app.route("/lecturer-assessment-create-formative", methods=["GET", "POST"])
# # @login_required
# def lecturer_assessment_create_formative():
#     form = AssessmentDetailsForm()
#     formQ = QuestionDetailsForm()
#     formC = ChoiceDetailsForm()
#     FormTF = TrueFalseDetailsForm()
#
#     if request.method == 'POST':
#         assessment = Assessment(title=form.title.data, type='formative')
#         db.session.add(assessment)
#         db.session.commit()
#         # assessmentData = Assessment.query.last()
#         assessmentData = Assessment.query.order_by(Assessment.id.desc()).first()
#         # box_count = request.form.get('box_count')
#         # question1 = request.form.getlist('question'+str(box_count))
#         # choice1 = request.form.getlist('choice1')
#         # answer1 = request.form.getlist('answer1')
#         # explanation1 = request.form.getlist('explanation1')
#         # question2 = request.form.getlist('question2')
#         # choice2 = request.form.getlist('choice2')
#         # tof2 = request.form.getlist('tof2')
#         # explanation2 = request.form.getlist('explanation2')
#         # print(question1)
#         # print(choice1)
#         # print(answer1)
#         # print(explanation1)
#         # print(question2)
#         # print(choice2)
#         # print(tof2)
#         # print(explanation2)
#
#         box_count = request.form.get('box_count')
#         print(box_count)
#         print(type(box_count))
#
#         for x in range(1, int(box_count)+1):
#             quest = request.form.get('question'+str(x))
#             cho = request.form.getlist('choice'+str(x))
#             ans = request.form.getlist('answer'+str(x))
#             exp = request.form.get('explanation'+str(x))
#             tof = request.form.get('tof'+str(x))
#             if len(cho) != 0:
#                 question = Question(question_text=quest, type='multi-choice', explanation=exp, assessment_id=assessmentData.id)
#                 db.session.add(question)
#                 db.session.commit()
#             else:
#                 question = Question(question_text=quest, type='trueorfalse', explanation=exp, assessment_id=assessmentData.id)
#                 db.session.add(question)
#                 db.session.commit()
#             # questionData = Question.query.last()
#             questionData = Question.query.order_by(Question.id.desc()).first()
#             if len(cho) != 0:
#                   for x in range(4):
#                         choice = Choice(choice_text=cho[x], is_correct=ans[x], question_id=questionData.id)
#                         db.session.add(choice)
#                         db.session.commit()
#             else:
#                   truefalse = TrueFalse(is_true=tof, question_id=questionData.id)
#                   db.session.add(truefalse)
#                   db.session.commit()
#         flash('the assessment has been created')
#         return redirect(url_for('lecturer_assessment_create_formative'))
#     return render_template("lecturer-assessment-create-formative.html", title='CreateAssessment',form=form, formQ=formQ, formC=formC, formTF=FormTF)
#
# @app.route('/ass_list')
# def ass_list():
#     ass=Assessment.query.order_by(Assessment.id.desc()).all()
#     return render_template('ass_list.html', assessments=ass)
#
# @app.route('/delete_question_in_assessment/<int:ass_id>',methods=['GET','POST'])
# def delete_question_in_assessment(ass_id):
#     assessment = Assessment.query.get(ass_id)
#     questions = assessment.questions
#     if request.method == 'POST':
#         question_id=request.form.get('question_id')
#         question = Question.query.get(question_id)
#         print(question)
#         questions.remove(question)
#         db.session.commit()
#         return redirect(url_for('delete_question_in_assessment',questions=questions,ass_id=ass_id))
#     return render_template('delete_question_in_assessment.html',questions=questions,ass_id=ass_id)
#
#
#
#
# @app.route("/lecturer-assessment-create-summative")
# # @login_required
# def lecturer_assessment_create_summative():
#     form = AssessmentDetailsForm()
#     formQ = QuestionDetailsForm()
#     formC = ChoiceDetailsForm()
#     FormTF = TrueFalseDetailsForm()
#     if request.method == 'POST':
#         assessment = Assessment(title=form.title.data, type=form.data, user_id=current_user.id)
#         db.session.add(assessment)
#         db.session.commit()
#         return redirect(url_for('lecturer-assessment-create-summative'))
#     return render_template("lecturer-assessment-create-summative.html", title='CreateAssessment',form=form, formQ=formQ, formC=formC, formTF=FormTF)


# Create Assessment(Qizhen Ye)--------------------------------------------
@app.route("/lecturer-assessment-create-formative", methods=["GET", "POST"])
@login_required
def lecturer_assessment_create_formative():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    form = AssessmentDetailsForm()
    formQ = QuestionDetailsForm()
    formC = ChoiceDetailsForm()
    FormTF = TrueFalseDetailsForm()

    if request.method == "POST":
        assessment = Assessment(title=form.title.data, type="formative")
        db.session.add(assessment)
        db.session.commit()
        assessmentData = Assessment.query.order_by(Assessment.id.desc()).first()

        box_count = request.form.get("box_count")

        for x in range(1, int(box_count) + 1):
            quest = request.form.get("question" + str(x))
            cho = request.form.getlist("choice" + str(x))
            ans = request.form.getlist("answer" + str(x))
            exp = request.form.get("explanation" + str(x))
            tof = request.form.get("tof" + str(x))
            if len(cho) != 0:
                question = Question(
                    question_text=quest,
                    type="multi-choice",
                    explanation=exp,
                    assessment_id=assessmentData.id,
                )
                db.session.add(question)
                db.session.commit()
            else:
                question = Question(
                    question_text=quest,
                    type="trueorfalse",
                    explanation=exp,
                    assessment_id=assessmentData.id,
                )
                db.session.add(question)
                db.session.commit()
                # questionData = Question.query.last()
            questionData = Question.query.order_by(Question.id.desc()).first()
            if len(cho) != 0:
                for x in range(4):
                    choice = Choice(
                        choice_text=cho[x],
                        is_correct=ans[x],
                        question_id=questionData.id,
                    )
                    db.session.add(choice)
                    db.session.commit()
            else:
                truefalse = TrueFalse(is_true=tof, question_id=questionData.id)
                db.session.add(truefalse)
                db.session.commit()
        flash("the assessment has been created")
        return redirect(url_for("lecturer_assessment_create_formative"))
    return render_template(
        "lecturer-assessment-create-formative.html",
        title="CreateAssessment",
        form=form,
        formQ=formQ,
        formC=formC,
        formTF=FormTF,
    )


@app.route("/modify_lecturer", methods=["GET", "POST"])
@login_required
def modify_lecturer():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    form = AssessmentDetailsForm()
    formQ = QuestionDetailsForm()
    formC = ChoiceDetailsForm()
    FormTF = TrueFalseDetailsForm()

    if request.method == "POST":
        title = request.form.get("title")
        assessment = Assessment(title=title, type="formative")
        db.session.add(assessment)
        db.session.commit()
        assessmentData = Assessment.query.order_by(Assessment.id.desc()).first()
        box_count = request.form.get("box_count")

        for x in range(1, int(box_count) + 1):
            quest = request.form.get("question" + str(x))
            cho = request.form.getlist("choice" + str(x))
            ans = request.form.getlist("answer" + str(x))
            exp = request.form.get("explanation" + str(x))
            tof = request.form.get("tof" + str(x))
            if len(cho) != 0:
                question = Question(
                    question_text=quest,
                    type="multi-choice",
                    explanation=exp,
                    assessment_id=assessmentData.id,
                )
                db.session.add(question)
                db.session.commit()
            else:
                question = Question(
                    question_text=quest,
                    type="trueorfalse",
                    explanation=exp,
                    assessment_id=assessmentData.id,
                )
                db.session.add(question)
                db.session.commit()
                # questionData = Question.query.last()
            questionData = Question.query.order_by(Question.id.desc()).first()
            if len(cho) != 0:
                for x in range(4):
                    choice = Choice(
                        choice_text=cho[x],
                        is_correct=ans[x],
                        question_id=questionData.id,
                    )
                    db.session.add(choice)
                    db.session.commit()
            else:
                truefalse = TrueFalse(is_true=tof, question_id=questionData.id)
                db.session.add(truefalse)
                db.session.commit()
        flash("the assessment has been created")
        ass_id = request.form.get("ass_id")
        assessment_old = Assessment.query.get(ass_id)
        questions_old = assessment_old.questions
        for i in questions_old:
            question = Question.query.get(i.id)
            questions_old.remove(question)
            db.session.commit()
        db.session.delete(assessment_old)
        db.session.commit()
        return redirect(url_for("lecturer_assessment_create_formative"))
    return render_template(
        "lecturer-assessment-create-formative.html",
        title="CreateAssessment",
        form=form,
        formQ=formQ,
        formC=formC,
        formTF=FormTF,
    )


@app.route("/ass_list")
@login_required
def ass_list():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    ass = Assessment.query.order_by(Assessment.id.desc()).all()
    return render_template("ass_list.html", assessments=ass)


@app.route("/delete_question_in_assessment/<int:ass_id>", methods=["GET", "POST"])
@login_required
def delete_question_in_assessment(ass_id):
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    assessment = Assessment.query.get(ass_id)
    questions = assessment.questions
    if request.method == "POST":
        question_id = request.form.get("question_id")
        question = Question.query.get(question_id)
        print(question)
        questions.remove(question)
        db.session.commit()
        return redirect(
            url_for("delete_question_in_assessment", questions=questions, ass_id=ass_id)
        )
    return render_template(
        "delete_question_in_assessment.html", questions=questions, ass_id=ass_id
    )


@app.route("/modify_question_in_assessment/<int:ass_id>", methods=["GET", "POST"])
@login_required
def modify_question_in_assessment(ass_id):
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    assessment = Assessment.query.get(ass_id)
    questions = assessment.questions
    form = AssessmentDetailsForm()
    if request.method == "GET":
        return render_template(
            "modify-assessment.html",
            title=assessment.title,
            questions=questions,
            ass_id=ass_id,
            form=form,
        )
    if request.method == "POST":
        question_id = request.form.get("question_id")
        question = Question.query.get(question_id)
        questions.remove(question)
        db.session.commit()
        return redirect(
            url_for("delete_question_in_assessment", questions=questions, ass_id=ass_id)
        )
    return render_template(
        "delete_question_in_assessment.html", questions=questions, ass_id=ass_id
    )


@app.route("/lecturer-assessment-create-summative", methods=["GET", "POST"])
@login_required
def lecturer_assessment_create_summative():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    form = AssessmentDetailsForm()
    formQ = QuestionDetailsForm()
    formC = ChoiceDetailsForm()
    FormTF = TrueFalseDetailsForm()

    if request.method == "POST":
        assessment = Assessment(title=form.title.data, type="summative")
        db.session.add(assessment)
        db.session.commit()
        assessmentData = Assessment.query.order_by(Assessment.id.desc()).first()

        box_count = request.form.get("box_count")

        for x in range(1, int(box_count) + 1):
            quest = request.form.get("question" + str(x))
            cho = request.form.getlist("choice" + str(x))
            ans = request.form.getlist("answer" + str(x))
            exp = request.form.get("explanation" + str(x))
            tof = request.form.get("tof" + str(x))
            if len(cho) != 0:
                question = Question(
                    question_text=quest,
                    type="multi-choice",
                    explanation=exp,
                    assessment_id=assessmentData.id,
                )
                db.session.add(question)
                db.session.commit()
            else:
                question = Question(
                    question_text=quest,
                    type="trueorfalse",
                    explanation=exp,
                    assessment_id=assessmentData.id,
                )
                db.session.add(question)
                db.session.commit()
                # questionData = Question.query.last()
            questionData = Question.query.order_by(Question.id.desc()).first()
            if len(cho) != 0:
                for x in range(4):
                    choice = Choice(
                        choice_text=cho[x],
                        is_correct=ans[x],
                        question_id=questionData.id,
                    )
                    db.session.add(choice)
                    db.session.commit()
            else:
                truefalse = TrueFalse(is_true=tof, question_id=questionData.id)
                db.session.add(truefalse)
                db.session.commit()
        flash("the assessment has been created")
        return redirect(url_for("lecturer_assessment_create_summative"))
    return render_template(
        "lecturer-assessment-create-summative.html",
        title="CreateAssessment",
        form=form,
        formQ=formQ,
        formC=formC,
        formTF=FormTF,
    )


# ---------------for ajax---------------#
@app.route("/multi")
def multi():
    form = AssessmentDetailsForm()
    formQ = QuestionDetailsForm()
    formC = ChoiceDetailsForm()
    FormTF = TrueFalseDetailsForm()
    return render_template(
        "multi_choice.html", form=form, formQ=formQ, formC=formC, formTF=FormTF
    )


@app.route("/tf")
def tf():
    form = AssessmentDetailsForm()
    formQ = QuestionDetailsForm()
    formC = ChoiceDetailsForm()
    FormTF = TrueFalseDetailsForm()
    return render_template(
        "true_or_false.html", form=form, formQ=formQ, formC=formC, formTF=FormTF
    )


# ---------------------------------------#


@app.route("/delete_assessment", methods=["GET", "POST"])
def delete_assessment():
    assessments = Assessment.query.all()
    if request.method == "POST":
        assessment_id = request.form.get("assessment_id")
        assessment = Assessment.query.get(assessment_id)
        db.session.delete(assessment)
        db.session.commit()
        return redirect(url_for("delete_assessment"))
    return render_template("delete_assessment.html", assessments=assessments)


#
# @app.route("/lecturer-assessment-update",methods=['GET','POST'])
# # @login_required
# def lecturer_assessment_delete():
#     assessments = Assessment.query.all()
#     if request.method == 'POST':
#         id=request.form.get('assessment_id')
#         print(id)
#         assessment = Assessment.query.filter_by(id=id).first()
#         question = Question.query.filter_by(assessment_id=id).all()
#         db.session.delete(assessment)
#         db.session.commit()
#         for q in question:
#             choice = Choice.query.filter_by(question_id=q.id).all()
#             tf = TrueFalse.query.filter_by(question_id=q.id).all()
#             db.session.delete(q)
#             db.session.commit()
#             if len(choice) != 0:
#                  for c in choice:
#                       db.session.delete(c)
#                       db.session.commit()
#             elif len(tf) != 0:
#                  for t in tf:
#                       db.session.delete(t)
#                       db.session.commit()
#         # db.session.delete(choice)
#         # db.session.delete(tf)
#         # db.session.commit()
#         return redirect(url_for('lecturer_assessment_delete',assessments=assessments))
#     return render_template("lecturer-assessment-update.html", assessments = assessments)
#
# @app.route("/lecturer-assessment-question-update/<int:ass_id>",methods=['GET','POST'])
# # @login_required
# def lecturer_assessment_question_update(ass_id):
#     assessment = Assessment.query.filter_by(id=ass_id).first()
#     questions = Question.query.filter_by(assessment_id=ass_id).all()
#     print(questions)
#     if request.method == 'POST':
#         if request.form.get('submit_button') == 'Update':
#             title = request.form["title"]
#             assessment.title = title
#             ques = request.form.getlist('question_text')
#             print(ques)
#             choice = request.form.getlist('choice')
#             ans = request.form.getlist('answer')
#             exp = request.form.getlist('explanation')
#             tf = request.form.getlist('tf')
#             count=0
#             countC=0
#             countA=0
#             countT=0
#             for q in questions:
#
#                     q.question_text = ques[count]
#                     q.explanation = exp[count]
#                     print(ques[count])
#                     print(exp[count])
#                     count += 1
#                     print(q.type)
#                     if q.type == 'multi-choice':
#                         for cho in q.choices:
#
#                             cho.choice_text = choice[countC]
#                             cho.is_correct = ans[countA]
#                             countC += 1
#                             countA += 1
#                         # q.choices[0]=choice[countC]
#                         # q.choices[1]=choice[countC+1]
#                         # q.choices[2]=choice[countC+2]
#                         # q.choices[3]=choice[countC+3]
#                         # q.choices[0].is_correct=ans[countA]
#                         # q.choices[1].is_correct=ans[countA+1]
#                         # q.choices[2].is_correct=ans[countA+2]
#                         # q.choices[3].is_correct=ans[countA+3]
#                         # countC += 4
#                         # countA += 4
#                     elif q.type == "trueorfalse":
#                         print(q.truefalse)
#                         q.truefalse.is_true = tf[countT]
#                         countT += 1
#
#                     db.session.commit()
#             return redirect(url_for('lecturer_assessment_delete',assessment=assessment, questions=questions))
#         elif request.form.get('submit_button') != 'Update':
#             id=request.form.get('question_id')
#             print(id)
#             question = Question.query.filter_by(id=id).first()
#             if question.type == 'multi-choice':
#                 choice = question.choices
#                 for c in choice:
#                     db.session.delete(c)
#             elif question.type == 'trueorfalse':
#                 tf = question.truefalse
#                 db.session.delete(tf)
#             print(question)
#             db.session.delete(question)
#             db.session.commit()
#             return redirect(url_for('lecturer_assessment_question_update', ass_id=ass_id))
#
#     return render_template("lecturer-assessment-question-update.html", assessment=assessment, questions=questions)


@app.route("/lecturer-feedback-main")
@login_required
def lecturer_feedback_main():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    assessment = Assessment.query.filter_by(user_id=current_user.id).all()
    return render_template("lecturer-feedback-main.html", asses)


@app.route("/lecturer-feedback-question")
@login_required
def lecturer_feedback_question():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-feedback-question.html")


@app.route("/lecturer-stat-main")
@login_required
def lecturer_stat_main():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-stat-main.html")


@app.route("/lecturer-stat-individual-main")
@login_required
def lecturer_stat_individual_main():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    stats = Result.query.all()
    print(dir(stats[0]))
    return render_template("lecturer-stat-individual-main.html", stats=stats)


@app.route("/lecturer-stat-individual-question")
@login_required
def lecturer_stat_individual_question():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-stat-individual-question.html")


@app.route("/lecturer-stat-cohorts-main", methods=["GET", "POST"])
@login_required
def lecturer_stat_cohorts_main():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    cohorts = set(
        [user.annual_intake for user in User.query.all() if user.annual_intake]
    )
    return render_template("lecturer-stat-cohorts-main.html", cohorts=cohorts)


@app.route("/lecturer-stat-cohorts-main/<cohort>", methods=["GET", "POST"])
@login_required
def lecturer_stat_cohorts_main_cohort(cohort):
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    stats = (
        db.session.query(Result)
        .join(User, Result.user_id == User.id)
        .filter(User.annual_intake == cohort)
    )
    return render_template("lecturer-stat-cohorts-main-cohort.html", stats=stats)


@app.route("/lecturer-stat-assessment-main", methods=["GET", "POST"])
@login_required
def lecturer_stat_assessment_main():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    assessments = Assessment.query.all()
    return render_template(
        "lecturer-stat-assessment-main.html", assessments=assessments
    )


@app.route("/lecturer-stat-assessment-main/<assessment_id>", methods=["GET", "POST"])
@login_required
def lecturer_stat_assessment_main_assessment(assessment_id):
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    assessment = Assessment.query.filter_by(id=assessment_id).first()
    stats = (
        db.session.query(Result)
        .join(Assessment, Result.assessment_id == Assessment.id)
        .filter(Assessment.id == assessment_id)
    )
    cohorts = set(
        [user.annual_intake for user in User.query.all() if user.annual_intake]
    )
    questions = Question.query.filter_by(assessment_id=assessment_id).all()

    return render_template(
        "lecturer-stat-assessment-main-assessment.html",
        stats=stats,
        cohorts=cohorts,
        assessment=assessment,
        questions=questions,
    )


@app.route(
    "/lecturer-stat-assessment-main-question/<question_id>", methods=["GET", "POST"]
)
@login_required
def lecturer_stat_assessment_main_question(question_id):
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    question = Question.query.filter_by(id=question_id).first()
    # stats = Answers.query.filter_by(question_id=question_id)
    # print(dir(question))
    # print(set([ ans.answers.student.annual_intake for ans in question.answers]))

    # stats = db.session.query(Result).join(Assessment, Result.assessment_id==Assessment.id).filter(Assessment.id==assessment_id)
    cohorts = set(
        [
            ans.answers.student.annual_intake
            for ans in question.answers
            if ans.answers.student.annual_intake
        ]
    )
    # questions = Question.query.filter_by(assessment_id=assessment_id).all()
    print(question)
    return render_template(
        "lecturer-stat-assessment-main-question.html",
        cohorts=cohorts,
        question=question,
    )


@app.route("/lecturer-stat-cohorts-main/<result>", methods=["GET", "POST"])
@login_required
def lecturer_stat_cohorts_main_result(result):
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    stats = db.session.query(Result).all()
    return render_template("lecturer-stat-assessment-main-result.html", stats=stats)


@app.route("/lecturer-stat-cohorts-question")
@login_required
def lecturer_stat_cohorts_question():
    if current_user.userType == "student":
        flash("You must be a lecturer to access this page")
        return redirect(url_for("student_home"))
    return render_template("lecturer-stat-cohorts-question.html")


@app.route("/student-register", methods=["GET", "POST"])
def student_register():
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        emailUser = User.query.filter_by(email=form.email.data).first()
        usernoUser = User.query.filter_by(userno=form.userno.data).first()
        if emailUser:
            flash(
                "That email address is already registered for another user, please enter a different email.",
                "alert-danger",
            )
        if usernoUser:
            flash(
                "That username is already in user, please enter a different username.",
                "alert-danger",
            )
        if not usernoUser and not emailUser:
            user = User(
                name=form.name.data,
                password=form.password.data,
                email=form.email.data,
                userno=form.userno.data,
                userType="student",
                annual_intake=form.annual_intake.data,
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful!", "alert-success")
            # code to send confirmation email to user
            token = generate_email_confirmation_token(user.email)
            msg = Message(
                "Confirm Email",
                sender="AATMailServer@gmail.com",
                recipients=[user.email],
            )
            msg.html = render_template(
                "emails/email-confirm-email.html", user=user, token=token
            )
            mail.send(msg)
            flash(
                "You will receive an email to activate your account shortly",
                "alert-info",
            )
            return redirect(url_for("registered"))
    return render_template("student-register.html", title="register", form=form)


@app.route("/lecturer-register", methods=["GET", "POST"])
def lecturer_register():
    form = LecturerRegistrationForm()
    if form.validate_on_submit():
        emailUser = User.query.filter_by(email=form.email.data).first()
        usernoUser = User.query.filter_by(userno=form.userno.data).first()
        if emailUser:
            flash(
                "That email address is already registered for another user, please enter a different email.",
                "alert-danger",
            )
        if usernoUser:
            flash(
                "That username is already in user, please enter a different username.",
                "alert-danger",
            )
        if not usernoUser and not emailUser:
            user = User(
                name=form.name.data,
                password=form.password.data,
                email=form.email.data,
                userno=form.userno.data,
                userType="lecturer",
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful!", "alert-success")
            # code to send confirmation email to user
            token = generate_email_confirmation_token(user.email)
            msg = Message(
                "Confirm Email",
                sender="AATMailServer@gmail.com",
                recipients=[user.email],
            )
            msg.html = render_template(
                "emails/email-confirm-email.html", user=user, token=token
            )
            mail.send(msg)
            flash(
                "You will receive an email to activate your account shortly",
                "alert-info",
            )

            return redirect(url_for("registered"))
    return render_template("lecturer-register.html", title="register", form=form)


@app.route("/registered")
def registered():
    return render_template("registered.html", title="Thanks!")


@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(userno=form.userno.data).first()
        if (
            user != None
            and user.verify_password(password=form.password.data)
            and user.confirmed
        ):
            login_user(user)
            flash("Login successful", "alert-success")
            return redirect(url_for("student_home"))
        else:
            flash(
                "This account has not been confirmed or the password you entered was incorrect, please try again",
                "alert-danger",
            )
    return render_template("student-login.html", title="Login", form=form)


@app.route("/lecturer-login", methods=["GET", "POST"])
def lecturer_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(userno=form.userno.data).first()
        if (
            user != None
            and user.verify_password(password=form.password.data)
            and user.confirmed
        ):
            login_user(user)
            flash("Login successful", "alert-success")
            return redirect(url_for("lecturer_home"))
        else:
            flash(
                "This account has not been confirmed or the password you entered was incorrect, please try again",
                "alert-danger",
            )
    return render_template("lecturer-login.html", title="Login", form=form)


@app.route("/update-details", methods=["GET", "POST"])
@login_required
def update_details():
    form = UpdateDetailsForm()
    if request.method == "GET":
        form.userno.data = current_user.userno
        form.name.data = current_user.name
    if form.validate_on_submit():
        usernameUser = (
            User.query.filter(User.id != current_user.id)
            .filter_by(userno=form.userno.data)
            .first()
        )
        if usernameUser:
            flash(
                "That username is already in user, please enter a different username.",
                "alert-danger",
            )
        else:
            current_user.userno = form.userno.data
            current_user.name = form.name.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your details have been changed", "alert-success")
            return redirect(url_for("user_dashboard"))
    return render_template("update-details.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out of your account", "alert-info")
    return redirect(url_for("home"))


@app.route("/user-dashboard")
@login_required
def user_dashboard():
    return render_template("user-dashboard.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_password_confirmation_token(user.hashed_password)
            msg = Message(
                "Password Reset",
                sender="FlaskCMT120@gmail.com",
                recipients=[user.email],
            )
            msg.html = render_template(
                "emails/email-forgot-password.html", user=user, token=token
            )
            mail.send(msg)
        # unindent so malicious user does not know if they have correctly identified a user account
        flash("You will receive a password reset email shortly", "alert-info")
        return redirect(url_for("home"))
    return render_template("forgot-password.html", form=form)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(password=form.oldPassword.data):
            current_user.password = form.newPassword.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your password has been changed", "alert-success")
            return redirect(url_for("user_dashboard"))
        else:
            flash("Incorrect password, please try again", "alert-danger")
    return render_template("change-password.html", form=form)


# Email Routes
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        hashed_password = confirm_password_token(token)
    except:
        flash("The reset link is invalid or has expired.", "alert-danger")
        return redirect(url_for("home"))
    user = User.query.filter_by(hashed_password=hashed_password).first_or_404()
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash("Password updated successfully", "alert-success")
        return redirect(url_for("home"))
    return render_template("reset-password.html", form=form)


@app.route("/confirm-email/<token>")
def confirm_email(token):
    try:
        email = confirm_email_token(token)
    except:
        flash("The confirmation link is invalid or has expired.", "alert-danger")
        return redirect(url_for("home"))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Account already confirmed. Please login.", "alert-info")
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "alert-success")
    return redirect(url_for("home"))


# Error Pages


@app.errorhandler(401)
def page_not_found(e):
    flash(
        "You do not currently have access to this page. Please login to an account with access priviledges and try again.",
        "alert-danger",
    )
    return redirect(url_for("login")), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
