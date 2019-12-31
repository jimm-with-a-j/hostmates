import fire
from config import Config


class CLI:
    def __init__(self):
        self.config = Config()



if __name__ == '__main__':
    fire.Fire(CLI)