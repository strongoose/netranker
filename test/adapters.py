from netranker.ports import CardSampler

class TestSampler(CardSampler):

    def __init__(self, mock_sample):
        self._mock_sample = mock_sample

    def sample(self):
        return self._mock_sample
