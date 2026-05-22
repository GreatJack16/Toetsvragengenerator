Date project: 28 may 2026
Authors: Lin Chen, Tyra George, Jacob Gransjean, Jaap van Uitert, Lina Xu
Contact: lin.chen@student.uva.nl, tyra.george@student.uva.nl, jacob.gransjean@student.uva.nl, jaap.van.uitert@student.uva.nl, lina.xu@student.uva.nl

This repository contains the examquestion generator.
- To create an exam, run from main.py.

pip install -r requirements.txt
python main.py

. You can specify variables and paths in the website. If some error occurs, please check inputs are present and correct first.
- Generating the exam may take some time, please be patient.
- Een 'subdoel' is een gesplits leerdoel. Een leerdoel kan namelijk heel lang zijn. Als dat het geval is, is het beter om deze op te splitsen in kortere subdoelen.

Structure:

genai-vragen-generator/
│
├── main.py                        # main script, loads in all necessary objects.
├── file_handler.py                # handles different files such as docx and pdf.
├── document_generator.py          # generates the document to download.
├── routes.py                      # contains all the routes for the generation.
│
├── .venv
│  
├── core/
│   └──  helper/
│       └──  answer_shuffler.py    # makes sure the correct answer isn't always the same option
│   ├── apikey.py                  # holds api-key
│   ├── apirequest.py              # handles api requests
│   ├── prompt.py                  # handles prompt definition
|   ├── test_apirequest.py         # script to test api-requests and api-keys
│   └── utils.py                   # helpers: text wrapping, I/O, etc.
│
├── data/
│   ├── studymaterial/             # source material (PDFs, docs, text)
│   ├── prompts/                   # system/user prompts as .txt
│   └── outputs/                   # generated exams go here
│
├── extra/                         # extra files, such as example questions
│
├── static/                        # all .js and .css files
│
└── templates/                     # all .html files
