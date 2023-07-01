class ExtractorMock(type):

    def __new__(cls, name):
        return super().__new__(cls, name, (), {'IE_NAME': name})

    def __repr__(self):
        return f'<EM: {self.IE_NAME}>'

    def __eq__(self, other):
        if not isinstance(other, ExtractorMock):
            return NotImplemented
        return self.IE_NAME == other.IE_NAME

    def __hash__(self):
        return hash(self.IE_NAME)
