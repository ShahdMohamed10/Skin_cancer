import tensorflow as tf

# Load the Keras model
model = tf.keras.models.load_model('saved models/model.h5')

# Get input shape
input_shape = model.input_shape[1:]

# Create a concrete function
run_model = tf.function(lambda x: model(x))
concrete_func = run_model.get_concrete_function(
    tf.TensorSpec([1] + list(input_shape), model.input_dtype)
)

# Convert the model
converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS
]
tflite_model = converter.convert()

# Save the model
with open('saved models/model.tflite', 'wb') as f:
    f.write(tflite_model) 