import os
from decisionengine_modules.AWS.sources import DEAccountContants

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SAMPLE_FILE = os.path.join(DATA_DIR, "AccountConstants_sample.py")

class TestAccountContantsk(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load(self):
        account_dict = DEAccountContants.load_constants(SAMPLE_FILE)
        self.assertIsNotNone(account_dict)

if __name__ == "__main__":
        unittest.main()
