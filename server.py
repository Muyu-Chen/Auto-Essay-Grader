from flask import Flask, request, jsonify, Response  # Ensure jsonify is imported
from flask_cors import CORS
from openai import OpenAI
import json

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
api_key_get = config.get('backend', {}).get('api-key', 'api-key-error')
api_key_get = str(api_key_get)
port_default = config.get('backend', {}).get('port', '5000')  # Default port
model_default = config.get('backend', {}).get('model', 'qwen-plus-0806')  # Default model
app = Flask(__name__)

# THIS IS NOT FOR SAFETY USE.
# YOU SHOULD USE A WHITELIST TO CONTROL ACCESS.
CORS(app, origins="*")  # Allow all origins
# This allows cross-origin requests from any domain, suitable for development purposes.
# Even if origins are restricted to trusted domains, non-browser clients (e.g., bots, scripts) 
# can still access the server. CORS only controls browser-based cross-origin requests 
# and does not prevent unauthorized or malicious access.
# For better security, implement additional measures like authentication, IP restrictions, or rate limiting.


with app.app_context():
    client = OpenAI(
        api_key= api_key_get,            
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        model = model_default  # default model
        data = request.json
        messages = data.get("messages")
        systemContent = data.get("systemContent")
        model_get = data.get("model")
        if model_get is None or model_get == "":
            model_set = model
            print("no model set has been recieved, use default model: " + str(model_set))
        else:
            model_set = model_get
            print("model get is: " + str(model_set))

        send_message = [
            {
                "role": "system",
                "content": systemContent,
            },
            {
                "role": "user",
                "content": messages,
            },
        ]

        completion = client.chat.completions.create(
            model=model_set,
            messages=send_message,
            stream=False,
        )

        def generate():
            if completion:
                print(completion.model_dump_json())
                print("completed as above")
                return completion.choices[0].message.content

        # print(completion.model_dump_json())
        return Response(generate(), content_type="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_default)
