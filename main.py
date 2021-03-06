from tensorflow.keras import datasets
from core.model import MHSADrugVQA, create_model
import numpy as np
import tensorflow as tf
import random
from dataTF import *
from utils import *
import matplotlib.pyplot as plt
import tensorflow_addons as tfa
from tqdm import tqdm

EPOCHS = 30
train_loss = []
model = create_model()

def train(model):
    
    optimizer = tfa.optimizers.AdamW(learning_rate = 0.001, weight_decay = 1e-4)
    loss_obj = tf.keras.losses.CategoricalCrossentropy()
    dataset = get_data_train(trainDataSet, seqContactDict)

    for epoch in range(EPOCHS):
        epoch_loss_avg = tf.keras.metrics.Mean()
        print(epoch)
        for lines, contactMap, proper in tqdm(dataset):
            """
            Input to model: 
            String: Smiles --> shape = [1,x]
            Feature 2D: Contactmap --> Shape = [1, size, size, 1]
            """
            contactMap = np.reshape(contactMap, (1,contactMap.shape[1], contactMap.shape[-1],1))
            contactMap_size = tf.shape(contactMap)[1]
        
            #Fixed: Pass a fixed size variabels
            contactMap = tf.keras.layers.ZeroPadding2D(padding = ((0,1024-contactMap_size), (0, 1024-contactMap_size)), data_format = 'channels_last')(contactMap) 
            smiles, length, y = make_variables([lines], proper, smiles_letters)
            smiles = tf.reshape(smiles, [1, smiles.shape[-1]])
            
            with tf.GradientTape() as tape:
                logits = model(smiles, contactMap, training=True) 
                
                loss =loss_obj(y, logits)

            grads = tape.gradient(loss, model.trainable_variables)
        
            optimizer.apply_gradients((grads, var) for (grads, var) in zip(grads, model.trainable_variables))
            
            epoch_loss_avg.update_state(loss)
            #if batch % 10 == 0:
            #    print("Loss: {} -- After {} points".format(epoch_loss_avg.result(), batch))
                
        train_loss.append(epoch_loss_avg.result())
        plt.plot(train_loss)
        plt.show()
            
train(model)   
#datasets = get_data_train(trainDataSet, seqContactDict)
#for batch, (lines, mapp, proper) in enumerate(datasets):
#    print("Lines :{} - Map :{}".format(lines, mapp))
                