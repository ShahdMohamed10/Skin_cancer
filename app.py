from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Define the skin cancer types
SKIN_CANCER_TYPES = {
    "0": "Melanocytic nevi",
    "1": "Melanoma",
    "2": "Benign keratosis-like lesions",
    "3": "Basal cell carcinoma",
    "4": "Actinic keratoses",
    "5": "Vascular lesions",
    "6": "Dermatofibroma"
}

try:
    # Load the TFLite model
    model_path = os.path.join('saved models', 'model.tflite')
    class_mapping_path = os.path.join('saved models', 'class_mapping.json')

    logger.info(f"Loading model from {model_path}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    if not os.path.exists(class_mapping_path):
        raise FileNotFoundError(f"Class mapping file not found at {class_mapping_path}")

    # Load class mapping
    with open(class_mapping_path, 'r') as f:
        class_mapping = json.load(f)
        logger.info(f"Loaded class mapping with {len(class_mapping)} classes")

    # Initialize interpreter with additional configurations
    interpreter = tf.lite.Interpreter(
        model_path=model_path,
        experimental_delegates=None,
        num_threads=4
    )
    interpreter.allocate_tensors()

    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    logger.info(f"Model loaded successfully")
    logger.info(f"Input details: {input_details}")
    logger.info(f"Output details: {output_details}")
    
    # Get input shape from model
    input_shape = input_details[0]['shape']
    input_height = input_shape[1]
    input_width = input_shape[2]
    logger.info(f"Model expects input shape: {input_shape}")

except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise

def preprocess_image(image_bytes):
    try:
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        logger.debug(f"Original image size: {image.size}")
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
            logger.debug("Converted image to RGB")
        
        # Resize image to match model input size
        image = image.resize((input_width, input_height))
        logger.debug(f"Resized image to: {image.size}")
        
        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32) / 255.0
        logger.debug(f"Image array shape after normalization: {image_array.shape}")
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        logger.debug(f"Final input shape: {image_array.shape}")
        
        return image_array
    except Exception as e:
        logger.error(f"Error in preprocessing image: {str(e)}")
        raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        logger.debug("Received prediction request")
        
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_bytes = image_file.read()
        logger.debug(f"Received image of size: {len(image_bytes)} bytes")
        
        # Preprocess image
        processed_image = preprocess_image(image_bytes)
        
        # Ensure the input data type matches what the model expects
        input_dtype = input_details[0]['dtype']
        processed_image = processed_image.astype(input_dtype)
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], processed_image)
        logger.debug("Set input tensor")
        
        # Run inference
        logger.debug("Running inference")
        interpreter.invoke()
        logger.debug("Inference complete")
        
        # Get prediction
        output_data = interpreter.get_tensor(output_details[0]['index'])
        logger.debug(f"Raw prediction shape: {output_data.shape}")
        logger.debug(f"Raw prediction values: {output_data}")
        
        # Get the predicted class and probability
        predicted_class_index = np.argmax(output_data[0])
        probabilities = tf.nn.softmax(output_data[0]).numpy()
        probability = float(probabilities[predicted_class_index])
        
        # Get class name from mapping and cancer type
        class_str = str(predicted_class_index)
        cancer_type = SKIN_CANCER_TYPES.get(class_str, f"Unknown Type (Class {class_str})")
        
        # Format the result
        result = {
            'prediction': cancer_type,
            'probability': probability,
            'percentage': f"{probability * 100:.2f}%",
            'details': {
                'type': cancer_type,
                'confidence': f"{probability * 100:.2f}%",
                'risk_level': 'High' if probability > 0.7 else 'Medium' if probability > 0.4 else 'Low'
            }
        }
        logger.debug(f"Prediction result: {result}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 