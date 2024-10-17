import frappe
import random
from datetime import datetime

def get_context(context):
    context.user = frappe.session.user

    # Get the quiz selected by the user (if any)
    selected_quiz = frappe.form_dict.get('quiz')
    context.selected_quiz = selected_quiz

    # Fetch all Quiz Names
    all_quizzes = frappe.get_all('Quiz', fields=['quiz_name'])
    context.all_quizzes = [quiz['quiz_name'] for quiz in all_quizzes]

    # Fetch all quizzes if no quiz is selected, otherwise filter by the selected quiz
    if selected_quiz:
        filters = {'quiz_name': selected_quiz}
    else:
        filters = {}
    quizzes = frappe.get_all("Quiz",filters=filters)
    qandas = []
    for quiz in quizzes:
        quiz_doc = frappe.get_doc("Quiz", quiz.name)
        qandas.extend(quiz_doc.qanda_text_input)
        # if a quiz is selected, get questions_per_page from that quiz.
        questions_per_page = quiz_doc.questions_per_page
    # if no quiz is selected fetch questions_per_page from "Quiz Settings" doctype.
    if not selected_quiz:
        questions_per_page = frappe.get_doc("Quiz Settings").questions_per_page

    # select a random sample of questions
    if len(qandas) > questions_per_page: 
        context.qandas = random.sample(qandas, questions_per_page)
    else:
        context.qandas = qandas
    # if caching is enabled, random sampling will not always work
    
    # get score of logged in user from Quiz Score
    if (context.user != 'Guest'):
        scores = frappe.get_list(
            "Quiz Score",
            filters={"user_name": context.user},
            fields=['submit_date',"correct_count","total_count"]
            )
        context.scores = scores

    context.no_cache = 1
    return context

@frappe.whitelist()
def save_score(user, correct_answer_count, total_question_count, submit_date):
    doc = frappe.new_doc("Quiz Score")
    doc.user_name  = user
    doc.correct_count = correct_answer_count
    doc.total_count = total_question_count
    doc.submit_date = submit_date
    doc.insert(ignore_permissions=True)
    return "Score saved successfully"
