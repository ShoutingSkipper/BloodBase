import os
import requests
from flask import Flask, request, jsonify
from markupsafe import escape

app = Flask(__name__)

# IPFS API endpoint (local node by default)
IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"
HASH_FILE_PATH = os.path.join(os.getcwd(), "hash.txt")  # Use an absolute path for safety

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>IPFS Data Submission</title>
    </head>
    <body>
        <h1>Submit Data to IPFS</h1>
        <form action="/submit" method="post">
            <label for="data">Enter your data:</label><br>
            <textarea name="data" id="data" rows="10" cols="50" maxlength="5000"></textarea><br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    '''


@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Validate input length to avoid resource exhaustion
        user_data = request.form['data']
        if not user_data or len(user_data) > 5000:  # 5KB limit
            return "<p>Invalid input: Data is either empty or exceeds the allowed size (5KB).</p>", 400

        # Sanitize user input
        sanitized_data = escape(user_data)

        # Save sanitized data to a temporary file
        temp_file_path = "temp_data.txt"
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(sanitized_data)

        # Upload the file to IPFS
        with open(temp_file_path, "rb") as temp_file:
            files = {"file": temp_file}
            response = requests.post(IPFS_API_URL, files=files, timeout=10)  # Set a timeout for requests

        # Check if the upload was successful
        if response.status_code == 200:
            ipfs_hash = response.json().get("Hash", "")

            # Debugging: Log the hash and response
            print(f"IPFS Response: {response.json()}")
            print(f"Generated IPFS Hash: {ipfs_hash}")

            # Validate IPFS hash format
            if not ipfs_hash or len(ipfs_hash) != 46:
                return "<p>Invalid IPFS hash received from the server.</p>", 500

            # Append the hash to hash.txt
            try:
                with open(HASH_FILE_PATH, "a", encoding="utf-8") as hash_file:
                    hash_file.write(ipfs_hash + "\n")
                print(f"Hash written to {HASH_FILE_PATH}")
            except Exception as e:
                print(f"Failed to write to {HASH_FILE_PATH}: {str(e)}")
                return "<p>Failed to store the hash. Please check server logs for more details.</p>", 500

            # Delete the temporary file securely
            try:
                os.remove(temp_file_path)
            except FileNotFoundError:
                pass  # File might have already been deleted

            return f'''
                <p>Data successfully uploaded to IPFS!</p>
                <p><strong>IPFS Hash:</strong> {ipfs_hash}</p>
                <p>The hash has been stored in <strong>{HASH_FILE_PATH}</strong>.</p>
                <a href="/">Submit More Data</a>
            '''
        else:
            return f"<p>Failed to upload to IPFS. Status code: {response.status_code}</p><p>{escape(response.text)}</p>", 500
    except requests.exceptions.Timeout:
        return "<p>The request to IPFS timed out. Please try again later.</p>", 504
    except Exception as e:
        return f"<p>An error occurred: {escape(str(e))}</p>", 500


if __name__ == "__main__":
    # Run the Flask application securely
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
