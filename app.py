from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

# get random number
@app.route('/random', methods=['GET'])
def generate_random():
    # Generate a random number between 1 and 100
    random_number = random.randint(1, 100)


    wait_time = random_number % 10

    # Wait for "x" milliseconds
    time.sleep(wait_time / 1000.0)  # time.sleep expects seconds, so convert milliseconds to seconds

    # Check if the original random number is divisible by 5
    if random_number % 5 == 0:
        # Simulate a server error
        return jsonify({'error': 'Server encountered an error processing your request.'}), 500
    else:
        # Return the random number
        return jsonify({'number': random_number}), 200

# get color
@app.route('/color', methods=['GET'])
def generate_color():
    # Generate a random number between 1 and 100
    random_number = random.randint(1, 100)


    wait_time = random_number % 10

    # Wait for "x" milliseconds
    time.sleep(wait_time / 1000.0)  # time.sleep expects seconds, so convert milliseconds to seconds

    # Check if the original random number is divisible by 5
    if random_number % 5 == 0:
        # Simulate a server error
        return jsonify({'error': 'Server encountered an error processing your request.'}), 500
    else:
        # Return the random number
        return jsonify({'color': "red"}), 200



if __name__ == '__main__':
    app.run(port=8080, debug=True)
