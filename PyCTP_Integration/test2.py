# -*-coding : utf8


class Car:
    def __init__(self, lungu):
        print('init class Car')
        self.lungu = lungu

    def get_lungu(self):
        return self.lungu


class Benz(Car):
    def __init__(self, lungu, pailiang):
        Car.__init__(self, lungu=lungu)
        print('init class Benz')
        self.pailiang = pailiang

    def get_pailiang(self):
        return self.pailiang

c1 = Car(4)
b1 = Benz(4, 2.0)
b2 = Benz(5, 3.0)
print(b1.get_lungu(), b1.get_pailiang())
print(b2.get_lungu(), b2.get_pailiang())