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
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.ithLast = 0
        self.discount_rate_last = 0.7
        
    def _build_model(self):
        inputs = Input(shape=(self.state_size, ))

        x = Dense(24, activation='selu')(inputs)
        x = Dense(24, activation='selu')(x)
        action = Dense(self.action_size, activation='sigmoid')(x)
        reward = Input(shape=(1,))

        model = Model(inputs=[inputs, reward], outputs=action)
        
        # def custom_loss_wrapper(reward):
        #     def custom_loss(y_true, y_pred):
        #         return K.sum(reward * K.mse(y_true, y_pred))
        #     return custom_loss

        
        # model.compile(loss=custom_loss_wrapper(input_reward), optimizer='adam', metrics=['accuracy'])
#                                                               K.variable(rewardy, dtype=yTrue.dtype)
        model.compile(loss=lambda yTrue, yPred: K.sum(reward * mse(yTrue, yPred)), optimizer=Adam(lr=self.learning_rate))
        return model
        
    def remember(self, state, action, reward, next_state):
        self.memory.appendleft([state, action, reward, next_state])

    def remind(self, *pars):
        return self.memory[pars]

    def reward(self, state, next_state, last_reward = 0):
        des = np.array(state[10:])
        sa = np.array(state[1:5])

        nsa = np.array(next_state[1:5])

        dS = mse_custom(des, sa) - mse_custom(des, nsa)

        return last_reward*self.discount_rate_last + dS
        
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            print('Act random')
            return (np.random.random((1,4))*2 -1 )/5  # replace with random output
        print('Act self')
        action = self.model.predict([state.reshape((1,14)),  np.ones((1,1))])
        return action  # returns action
        
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state in minibatch:
            reward =+ self.gamma * self.reward(state, next_state, reward)
            # target_f = self.model.predict(state)
            # target_f[0][action] = target
            # print("state ---------->", state.shape, reward.reshape((1,1)), action.shape)
            self.model.fit([state.reshape((1,14)), reward.reshape((1,1))], action, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay











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