from groq import Groq
from app.config import GROQ_API_KEY
from app.utils.hints import HINT_PROMPTS

client = Groq(api_key=GROQ_API_KEY)

def get_hint(
    problem_title: str,
    problem_description: str,
    user_code: str,
    hint_level: int
) -> str:
    if hint_level not in [1, 2, 3]:
        return "Invalid hint level. Choose 1, 2, or 3."

    prompt = HINT_PROMPTS[hint_level].format(
        problem_title=problem_title,
        problem_description=problem_description,
        user_code=user_code if user_code.strip() else "No code written yet"
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content