import frappe
import random
from datetime import datetime

def get_context(context):
    context.user = frappe.session.user
    questions_per_page = frappe.get_doc("QMK Settings").questions_per_page
    units = frappe.get_all("QMK Unit")
    questions = []
    for unit in units:
        unit_doc = frappe.get_doc("QMK Unit", unit.name)
        questions.extend(unit_doc.questions)
    # select a random sample of questions
    if len(questions) > questions_per_page: 
        context.questions = random.sample(questions, questions_per_page)
    else:
        context.questions = questions
    # if caching is enabled, random sampling will not always work
    
    # get score of logged in user from QMK Score
    if (context.user != 'Guest'):
        scores = frappe.get_list(
            "QMK Score",
            filters={"user_name": context.user},
            fields=['submit_date',"correct_count","total_count"]
            )
        context.scores = scores

    context.no_cache = 1
    return context

@frappe.whitelist()
def save_score(user, correct_answer_count, total_question_count):
    doc = frappe.new_doc("QMK Score")
    doc.user_name  = user
    doc.correct_count = correct_answer_count
    doc.total_count = total_question_count
    doc.submit_date = datetime.now()
    doc.insert(ignore_permissions=True)
    return "Score saved successfully"
