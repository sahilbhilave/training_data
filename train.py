from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def load_exercise_data():
    try:
        url = "https://raw.githubusercontent.com/sahilbhilave/training_data/main/exercise_data.json"
        response = requests.get(url)
        if response.status_code == 200:
            exercise_data = response.json()
            return exercise_data
        else:
            return None
    except Exception as e:
        return None

def preprocess_exercise_data(exercise_data):
    exercise_descriptions = [
        f"{exercise['exercise_name']} {exercise['category']} {' '.join(exercise['health_conditions'])} {' '.join(exercise['equipment_required'])} {exercise['youtube_link']} {exercise['reps']}"
        for exercise in exercise_data
    ]
    return exercise_descriptions

def get_random_exercises(exercise_data, num_recommendations=5):
    return random.sample(exercise_data, min(num_recommendations, len(exercise_data)))

def get_recommendations(user_age, liked_exercises, user_health_conditions, recent_exercises, user_equipment, user_category='', user_difficulty='', num_recommendations=5):
    exercise_data = load_exercise_data()
    if exercise_data is None:
        return jsonify({"error": "Failed to fetch exercise data."})

    # Filter exercise data based on user requirements
    filtered_exercises = [
        exercise for exercise in exercise_data
        if not any(condition in exercise["health_conditions"] for condition in user_health_conditions)
        and all(equipment in user_equipment for equipment in exercise["equipment_required"])
        and (user_category == '' or exercise["category"] == user_category)
        and (user_difficulty == '' or exercise["difficulty"].lower() == user_difficulty.lower())
        and exercise["exercise_name"] not in recent_exercises
    ]

    # If there are enough filtered exercises, return them
    if len(filtered_exercises) >= num_recommendations:
        return filtered_exercises[:num_recommendations]

    # Otherwise, get additional random exercises to meet the required number
    remaining_recommendations = num_recommendations - len(filtered_exercises)
    random_recommendations = get_random_exercises(exercise_data, remaining_recommendations)

    return filtered_exercises + random_recommendations

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json

    user_age = data.get('user_age')
    liked_exercises = data.get('liked_exercises', [])
    user_health_conditions = data.get('user_health_conditions', [])
    recent_exercises = data.get('recent_exercises', [])
    user_equipment = data.get('user_equipment', [])
    user_category = data.get('user_category', '')
    user_difficulty = data.get('user_difficulty', '')

    recommendations = get_recommendations(user_age, liked_exercises, user_health_conditions, recent_exercises, user_equipment, user_category, user_difficulty, num_recommendations=5)

    return jsonify({"recommended_exercises": recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

