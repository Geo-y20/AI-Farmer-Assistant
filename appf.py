from flask import Flask, render_template, jsonify, request
import random
import json
from flask import Flask, render_template, Response
import cv2
import numpy as np
from keras.models import load_model


app = Flask(__name__)



# Load responses from a JSON file
with open('responses.json', 'r') as file:
    all_responses = json.load(file)

# Extracting keywords for later comparison
keywords = all_responses['keywords']

def find_matching_keyword(user_input):
    for keyword in keywords:
        if keyword.lower() in user_input.lower():
            return keyword
    return None

@app.route('/chatBot', methods=['GET', 'POST'])
def chatBot():
    response_data = None  # Initialize response_data to None

    if request.method == 'POST':
        user_input = request.form.get('user_input', '')

        # Find the matching keyword in the entered text
        matched_keyword = find_matching_keyword(user_input)

        if matched_keyword:
            # If a keyword is found, use the corresponding responses from the JSON file
            responses_key = f"response_{random.randint(1, 3)}"
            advices_key = f"advice_{random.randint(1, 3)}"

            response_data = {
                "response": keywords[matched_keyword].get(responses_key, ""),
                "advice": keywords[matched_keyword].get(advices_key, "")
            }
        else:
            # If no keyword is found, provide a default response
            responses_key = f"response_{random.randint(1, 1)}"
            advices_key = f"advice_{random.randint(1, 1)}"

            response_data = {
                "response": all_responses['default'].get(responses_key, ""),
                "advice": all_responses['default'].get(advices_key, "")
            }

    # Use the or operator to provide default values if response_data is None
    response = response_data["response"] if response_data else ""
    advice = response_data["advice"] if response_data else ""

    return render_template('chatBot.html', response=response, advice=advice)



loaded_model = load_model('wheatDiseaseModel.h5')
img_size = 64

label_to_disease = {
    "0001": "Healthy",
    "0010": "Root rot",
    "1000": "Leaf rust",
    "0100": "Loose smut"
}

def predict_image(image):
    resized_image = cv2.resize(image, (img_size, img_size))
    preprocessed_image = np.array(resized_image) / 255.0
    preprocessed_image = np.expand_dims(preprocessed_image, axis=0)
    prediction = loaded_model.predict(preprocessed_image)
    rounded_prediction = np.round(prediction)
    return rounded_prediction

def gen_frames():  # generate video frames
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Check if the frame is already in RGB format
            if frame.shape[2] == 3 and frame.shape[0] > 0 and frame.shape[1] > 0:
                rgb_frame = frame
            else:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            prediction = predict_image(frame)
            predicted_label = ''.join(map(str, prediction[0].astype(int)))
            if predicted_label in label_to_disease:
                predicted_disease = label_to_disease[predicted_label]
            else:
                predicted_disease = "Unknown Disease"

            cv2.putText(rgb_frame, f"Predicted Disease: {predicted_disease}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', rgb_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/streaming')
def streaming():
    return render_template('streaming.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')






















# Define your existing routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Define routes for the new functionality
def get_sensor_data():
    # Simulate sensor data
    simulated_temp = round(random.uniform(23, 27), 1)
    simulated_hum = round(random.uniform(47, 51), 2)
    simulated_light = True  # Simulate light being on
    simulated_water = "Normal"

    return {'temp': simulated_temp, 'hum': simulated_hum, 'water': simulated_water, 'light': simulated_light}

def is_recommendation(sensor_data):
    # Check if sensor values meet planting criteria
    return sensor_data['hum'] == 50 and sensor_data['temp'] == 24.0 and sensor_data['ph'] == 6.1 and sensor_data['light']

# Test route
@app.route('/test')
def test():
    sensor_data = get_sensor_data()  # Get simulated sensor data
    return render_template('test.html', sensor_data=sensor_data)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Simulate sensor data
        sensor_data = get_sensor_data()

        # Check if the current sensor values meet planting criteria
        recommendation = is_recommendation(sensor_data)

        # Provide specific details for recommended planting or not recommended
        if recommendation:
            output_message = 'Recommended for planting'
        else:
            output_message = 'Not recommended for planting. Recommended planting conditions are:\n' \
                             'Humidity: 50%\nTemperature: 24 C\npH: 6.1\nLight: On\nWater Level: Normal'

        # Update the HTML with the simulated sensor data values
        return jsonify({
            'output': output_message,
            'temperature': sensor_data['temp'],
            'humidity': sensor_data['hum'],
            'water_level': sensor_data['water'],
            'light_intensity': sensor_data['light']
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
