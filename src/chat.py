import json
import torch
import random
from neural_net import NeuralNet
import config as c
from sentence_processor import SentenceProcessor


class Chat:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = NeuralNet(0, 0, 0)
        self.sp = SentenceProcessor()
        self.all_words = []
        self.tags = []

    def load_data(self):
        with open("data/intents.json", "r") as f:
            intents = json.load(f)

        FILE = c.OUT_PATH + c.TRAINED_DATA_FILENAME
        data = torch.load(FILE)
        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size = data["output_size"]
        self.all_words = data["all_words"]
        self.tags = data["tags"]
        model_state = data["model_state"]

        self.model = NeuralNet(input_size, hidden_size, output_size).to(self.device)
        self.model.load_state_dict(model_state)
        self.model.eval()

    def get_response(self):
        with open(c.INTENTS_DATA, "r") as f:
            intents = json.load(f)
        while True:
            sentence = input('You: ')
            if sentence == "quit":
                break

            sentence = self.sp.tokenize(sentence)
            X = self.sp.bag_of_words(sentence, self.all_words)
            X = X.reshape(1, X.shape[0])
            X = torch.from_numpy(X).to(self.device)

            output = self.model(X)
            _, predicted = torch.max(output, dim=1)
            tag = self.tags[predicted.item()]
            probs = torch.softmax(output, dim=1)
            prob = probs[0][predicted.item()]

            if prob.item() > 0.75:
                for intent in intents["intents"]:
                    if tag == intent["tag"]:
                        print(f"{c.BOT_NAME}: {random.choice(intent['responses'])}")
                    else:
                        print(f"{c.BOT_NAME}: I don't understand...")


