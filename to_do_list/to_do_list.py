from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Task

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

@app.route('/tasks', methods = ['GET'])
def get_list_of_tasks():
    tasks = db.session.query(Task.title)
    task_list= [task.title for task in tasks]
    return jsonify(task_list), 200

@app.route('/tasks', methods = ['POST'])
def create_task():
    data = request.json
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    new_task = Task(
        title = data['title'],
        description = data.get('description', '')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"id": new_task.id, "title": new_task.title, "description": new_task.description}), 201


@app.route('/tasks/<int:task_id>', methods = ['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"id": task.id, "title": task.title, "description": task.description}), 200


@app.route('/tasks/<int:task_id>', methods = ['DELETE'])
def delete_task(task_id):
    task = Task.query.get(int(task_id))
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"result": True}), 200


@app.route('/tasks/<int:task_id>', methods = ['PUT'])
def update_task(task_id):
    task = Task.query.get(int(task_id))
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"id": task.id, "title": task.title, "description": task.description}), 200



if __name__ == '__main__':
    app.run(debug=True)