import json

class Model:
    def __init__(self, bins=0, parsing_function=lambda x: x):
        self._data = [{"average": 0, "n": 0} for i in range(bins)]
        self._parsing_function = parsing_function
    
    def __repr__(self):
        return self._data
    
    def __str__(self):
        return str(self.__repr__())

    def load(self, filename):
        with open(filename, "r") as file:
            self._data = json.load(file)
    
    def save(self, filename):
        with open(filename, "w") as file:
            json.dump(self._data, file, sort_keys=True, indent=4)

    def train(self, x, y):
        index = self._parsing_function(x)
        data = self._data[index]
        data["average"] = (data["average"] * data["n"] + y) / (data["n"] + 1)
        data["n"] += 1

    def predict(self, x, parse=True):
        x = self._parsing_function(x) if parse else x
        data = self._data[x]
        guess = data["average"]
        return guess
    
    def predictall(self):
        return [self.predict(i, parse=False) for i in range(len(self._data))]

if __name__ == "__main__":
    m = Model(96)
    m.train(0, 1)
    m.train(0, 4)
    m.save("models/stopher_321_model.json")
    print(m)
    print(m.predict(0))
    print(m.predictall())