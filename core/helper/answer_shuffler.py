import random
import re

def shuffle_question(question):

    # regex pattern to recognize the header, four answer options and the correct answer option
    pattern = re.compile(
        r"(Vraag\s\d+\:.*?\n)"
        r"(\s*A\).*?\n)"
        r"(\s*B\).*?\n)"
        r"(\s*C\).*?\n)" 
        r"(\s*D\).*?\n)"
        r"\s*Correct antwoord:\s*([A-D])"
    )
 
    match = pattern.search(question)
    if not match:
        print("no match found with regular expression", question)
        return question
 
    question_header = match.group(1)
    answer_options = [match.group(2), match.group(3), match.group(4), match.group(5)]
    correct_letter = match.group(6).strip()
 
    # seperates the letter option from the question
    option_text = [re.sub(r"^\s*[A-D]\)\s*", "", o) for o in answer_options]
 
    # looks up which answer is correct
    letter_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct_answer = option_text[letter_to_index[correct_letter]]
 
    # Shuffle the answers
    random.shuffle(option_text)
 
    # find new position of the correct answer
    new_index = option_text.index(correct_answer)
    new_letter = ["A", "B", "C", "D"][new_index]
 
    # label the new order of questions
    labels = ["A", "B", "C", "D"]
    new_options = ""
    for i, inhoud in enumerate(option_text):
        new_options += f" {labels[i]}) {inhoud}"
 
    # subistute the correct answer at the bottom. 
    new_question = (
        question_header
        + new_options
        + f" Correct antwoord: {new_letter}"
    )
 
    # subsitute only the header, answers and correct answer
    start, end = match.span()
    return question[:start] + new_question + question[end:]
 
 
def randomise_exam(exam_tekst):
    
    questions = re.split(r"(?=Vraag\s\d+:)", exam_tekst)
    questions = [x for x in questions]
 
    processed = []
    for question in questions:
        processed.append(shuffle_question(question))
 
    return "\n".join(processed)