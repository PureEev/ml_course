from flask import Flask, request, jsonify
import mlflow.pyfunc
import numpy as np
import mlflow
app = Flask(__name__)

model_uri = 'models:/WineApp/Production'
model = mlflow.pyfunc.load_model(model_uri)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = np.array([data['Company'],
                         data['Specific_Bean_Origin'],
                         data['Review'],
                         data['Cocoa_Percent'],
                         data['Company_Location'],
                         data['Bean_Type'],
                         data['Broad_Bean_Origin']]).reshape(1, -1)

    prediction = model.predict(features).tolist()
    return jsonify({'rating': prediction[0]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

