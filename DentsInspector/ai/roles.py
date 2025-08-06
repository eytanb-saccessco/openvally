class Role:
    def __init__(self, name):
        self.name = name

    @property
    def cap_name(self):
        return self.name.upper()


User = Role("user")
Model = Role("model")
ROLES = {"User": User, "Model": Model}
