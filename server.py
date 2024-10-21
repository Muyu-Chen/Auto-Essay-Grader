from flask import Flask, request, jsonify, Response  # Ensure jsonify is imported
from flask_cors import CORS
from openai import OpenAI

port_default = 5000  # Default port

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins

model = "qwen-turbo-0919" # default model

with app.app_context():
    client = OpenAI(
        api_key="sk-xxx", # Replace with your API key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        model = "qwen-turbo-0919"  # default model
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
            model=model_get,
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
