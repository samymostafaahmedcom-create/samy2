from fastapi import FastAPI
import string
import secrets

app = FastAPI(title="Password Generator API")

history = []

def password_strength(password: str) -> str:
    score = 0
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 1:
        return "Weak"
    elif score == 2:
        return "Medium"
    else:
        return "Strong"


@app.get("/")
def home():
    return {"message": "API is working 🚀"}


@app.get("/generate")
def generate_password(
    length: int = 12,
    upper: bool = True,
    digits: bool = True,
    symbols: bool = True
):
    chars = string.ascii_lowercase

    if upper:
        chars += string.ascii_uppercase
    if digits:
        chars += string.digits
    if symbols:
        chars += string.punctuation

    password = "".join(secrets.choice(chars) for _ in range(length))
    strength = password_strength(password)

    history.append(password)
    if len(history) > 5:
        history.pop(0)

    return {
        "password": password,
        "strength": strength,
        "history": history
    }
