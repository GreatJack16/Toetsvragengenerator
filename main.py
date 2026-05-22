from flask import Flask
from dotenv import load_dotenv

from routes import register_routes

app = Flask(__name__)
app.secret_key = "tijdelijke-secret-key"

load_dotenv(".env.login")

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)