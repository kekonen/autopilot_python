from collections import deque

import numpy as np
import random

from keras import Sequential
from keras.layers import Input, Dense
from keras.models import Model
from keras.optimizers import Adam
from keras.losses import mse
import keras.backend as K

mse_custom = lambda A, B, ax=0: (np.square(A - B)).mean(axis=ax)


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95 # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    def _build_model(self):
            model = Sequential()
            model.add(Dense(24, input_dim=self.state_size, activation='selu'))
            model.add(Dense(24, activation='selu'))
            model.add(Dense(self.action_size, activation='linear'))
            model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
            return model
        
    def remember(self, state, action, reward, next_state):
        self.memory.appendleft([state, action, reward, next_state])

    def remind(self, *pars):
        return self.memory[pars]
        
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0]) # returns action
        
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state in minibatch: # + done
            target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            # target = reward
            # if not done:
            #     target = (reward + self.gamma *
            #               np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)








    # def _build_model(self):
    #     # Neural Net for Deep-Q learning Model
    #     model = Sequential()
    #     model.add(Dense(24, input_dim=self.state_size, activation='selu'))
    #     model.add(Dense(24, activation='selu'))
    #     model.add(Dense(self.action_size, activation='linear'))

    #     def customLoss(layer_weights, val = 0.01):

    #         def lossFunction(y_true,y_pred):    
    #             loss = mse(y_true, y_pred)
    #             loss += K.sum()
    #             return loss

    #         return lossFunction

    #     # def customLoss(yTrue,yPred):
    #     #     return 

    #     # loss =  K.sum(K.log(yTrue) - K.log(yPred))
    #             # loss += K.sum(val, K.abs(K.sum(K.square(layer_weights), axis=1)))


    #     model.compile(loss=lambda yTrue, yPred: K.sum(K.log(yTrue) - K.log(yPred)),
    #                   optimizer=Adam(lr=self.learning_rate))
    #     return model