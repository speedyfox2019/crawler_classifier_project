import os, sys

top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not top_path in sys.path:
    sys.path.insert(1, top_path)

from keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
# from tensorflow.keras.applications.vgg16 import preprocess_input
# from tensorflow.keras.applications.vgg16 import decode_predictions
# from tensorflow.keras.applications.vgg16 import VGG16

# Try with VGG19 to see if it's better than VGG16
from tensorflow.keras.applications.vgg19 import preprocess_input
from tensorflow.keras.applications.vgg19 import decode_predictions
from tensorflow.keras.applications.vgg19 import VGG19

import pprint
from time import sleep

def clasify_image(img_data, img_bytes=None):

    # load an image from file
    if img_bytes is not None:
        image = load_img(img_bytes, target_size=(224, 224))
    else:
        image = load_img(img_data['local_file'], target_size=(224, 224))

    # convert the image pixels to a numpy array
    image = img_to_array(image)
    
    # reshape data for the model
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    
    # prepare the image for the VGG model
    image = preprocess_input(image)
    
    # For now use a VGG16 model as a starting point.
    # May need to experiment with other pre-trained models to see which ones
    # perform better
    model = VGG19()
    
    # predict the probability across all output classes
    predictions = model.predict(image)

    # convert the probabilities to class labels
    label = decode_predictions(predictions)

    # retrieve the most likely result, e.g. highest probability
    label = label[0][0]

    # print the classification
    probability = label[2]*100
    print(f">> For {img_data['src']} --> label: {label}, probability: {probability}", flush=True)    

    # pass the result back to caller.
    # For now just populate the same image data dictionary so to make it
    # convenient to return the result from this API call.
    img_data['predicted_label'] = label[1]
    img_data['probability'] = probability

