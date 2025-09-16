from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 定义JSON文件路径
JSON_FILE_PATH = "data.json"

# 初始化JSON文件（如果不存在）
def init_json_file():
    if not os.path.exists(JSON_FILE_PATH):
        initial_data = {
            "allWords": [],
            "masteredWords": [],
            "difficultWords": []
        }
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

# 初始化JSON文件
init_json_file()

# 获取所有单词数据
@app.route('/api/words', methods=['GET'])
def get_words():
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 保存单词数据
@app.route('/api/words', methods=['POST'])
def save_words():
    try:
        # 获取前端发送的JSON数据
        data = request.get_json()

        # 验证数据结构
        required_keys = ["allWords", "masteredWords", "difficultWords"]
        if not all(key in data for key in required_keys):
            return jsonify({"error": "数据结构不完整"}), 400

        # 写入JSON文件
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "message": "数据已保存"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)