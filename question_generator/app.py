from flask import Flask, render_template, request, jsonify
import spacy
import requests
from bs4 import BeautifulSoup
import random
from spacy.cli import download

app = Flask(__name__)

# Step 1: Check if the model is downloaded, if not, download it
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Step 2: Function to scrape content from a Wikipedia page
def scrape_content(topic):
    try:
        # Replace spaces with underscores for Wikipedia URL
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first few paragraphs in the Wikipedia page
        content = ""
        for paragraph in soup.find_all('p', limit=3):  # Grabbing up to 3 paragraphs
            content += paragraph.get_text()
        
        return content
    except Exception as e:
        return f"Error scraping content: {str(e)}"

# Step 3: Define a function to generate questions
def generate_questions(text):
    doc = nlp(text)
    questions = []
    
    question_templates = {
        "what": [
            "What is {0}?",
            "What are the main features of {0}?",
            "What makes {0} significant?",
            "What role does {0} play in the context of {1}?",
            "What are the challenges faced by {0}?"
        ],
        "how": [
            "How did {0} originate?",
            "How has {0} influenced {1}?",
            "How does {0} contribute to {1}?",
            "How is {0} used in practice?",
            "How is {0} connected to {1}?"
        ],
        "describe": [
            "Describe {0}.",
            "Describe the significance of {0}.",
            "Describe the impact of {0} on {1}.",
            "How would you describe the key characteristics of {0}?"
        ],
        "analyze": [
            "Analyze the evolution of {0}.",
            "Analyze the key components of {0}.",
            "What are the main factors influencing {0}?",
            "Analyze the impact of {0} on {1}."
        ]
    }

    for chunk in doc.noun_chunks:
        question_type = random.choice(list(question_templates.keys()))
        topic = chunk.text.strip()
        if topic:
            question = random.choice(question_templates[question_type]).format(topic, 'its context')
            questions.append(question)
    
    return questions[:15] if len(questions) >= 10 else questions + ['Not enough content to generate 10 questions.']

# Flask route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Flask route to generate questions
@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get('topic')
    content = scrape_content(topic)
    if "Error" not in content:
        questions = generate_questions(content)
        return jsonify(questions=questions)
    else:
        return jsonify(questions=[content])

if __name__ == '__main__':
    app.run(debug=True)
