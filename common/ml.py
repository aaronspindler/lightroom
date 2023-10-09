import coremltools as ct

def load_model():
    # Load the Image Model
    model = ct.models.MLModel('common/BlurDetection.mlmodel')
    return model

def predict(model, image):
    return model.predict({'image': image})

def get_prediction_result(prediction):
    return prediction['classLabel']