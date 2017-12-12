import tensorflow as tf
import numpy as np
import os,glob,cv2
import sys,argparse
import requests
import io
import urllib.request
import ssl
def predict_house(url:None):
    ssl._create_default_https_context = ssl._create_unverified_context
    context = ssl._create_unverified_context()
    if url == None:
        url = "https://s-media-cache-ak0.pinimg.com/originals/7f/67/4f/7f674f7d115c654ad2e610bae1ea7c27.jpg"

    urllib.request.urlretrieve(url, 'house.png')
    # r= urllib.request.urlopen(url)
    # imgdata = r.read()
    # resized_image = Image.open(io.BytesIO(r.data))

    #print(resized_image)

    # First, pass the path of the image
    dir_path = os.path.dirname(os.path.realpath(__file__))
    image_path = "house.png"
    filename = image_path
    image_size=128
    num_channels=3
    images = []
    # Reading the image using OpenCV
    #image = cv2.imread(filename)
    # Resizing the image to our desired size and preprocessing will be done exactly as done during training
    image = cv2.imread(filename)
    image = cv2.resize(image, (image_size, image_size),0,0, cv2.INTER_LINEAR)
    images.append(image)
    images = np.array(images, dtype=np.uint8)
    images = images.astype('float32')
    images = np.multiply(images, 1.0/255.0)
    #The input to the network is of shape [None image_size image_size num_channels]. Hence we reshape.
    x_batch = images.reshape(1, image_size,image_size,num_channels)
    model_directory = [ dir_path+'/house_models/chimney_smoke_none_model',dir_path+'/house_models/house_door_model'  ]
    transmitting_sentences = ''
    ind = [0, 0, 0]
    cnt = 0


    for i in model_directory :
        ## Let us restore the saved model
        sess = tf.Session()
        # saver = tf.train.Saver()
        # Step-1: Recreate the network graph. At this step only graph is created.
        saver = tf.train.import_meta_graph(i+'/model.meta')
        # Step-2: Now let's load the weights saved using the restore method.
        saver.restore(sess, tf.train.latest_checkpoint(i))

        # Accessing the default graph which we have restored
        graph = tf.get_default_graph()

        # Now, let's get hold of the op that we can be processed to get the output.
        # In the original network y_pred is the tensor that is the prediction of the network
        y_pred = graph.get_tensor_by_name("y_pred:0")

        ## Let's feed the images to the input placeholders
        x= graph.get_tensor_by_name("x:0")
        y_true = graph.get_tensor_by_name("y_true:0")
        if cnt == 0:
            print(cnt)
            y_test_images = np.zeros((1, 3))
        else:
            y_test_images = np.zeros((1, 2))
        ### Creating the feed_dict that is required to be fed to calculate y_pred
        feed_dict_testing = {x: x_batch, y_true: y_test_images}
        result=sess.run(y_pred, feed_dict=feed_dict_testing)
        # result is of this format [probabiliy_of_rose probability_of_sunflower]
        print(result)
        tf.reset_default_graph()

        ind[cnt] = np.argmax(result)
        cnt = cnt+1

    file_add = [ 'chimney_', 'door_']
    transmitting_sentences = ""
    ind = [0, 0]
    for i in file_add :
        file_read = dir_path + '/' + i+ str(ind[0]) +'.txt'
        print(file_read)
        f = io.open(file_read, 'rb')
        line = f.read()
        transmitting_sentences += line.decode('euc-kr') + '\n'
        print(transmitting_sentences)
        f.close()

    print(transmitting_sentences)
    return transmitting_sentences
