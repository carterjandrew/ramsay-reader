import os
from ollama import generate, GenerateResponse
from multiprocessing import Pool
from tqdm import tqdm


class Generator:
    def __init__(
            self,
            output_dir='./data/ollama/inputs',
            model_name='gemma3',
            workers=5,
            num_samples=20,
            prompt='Generate a plain text script for cooking a random recipe in the voice of Gordon Ramsay. Do not inlude headers for who is talking.'
    ):
        self.output_dir = output_dir
        self.model_name = model_name
        self.prompt = prompt
        self.num_samples = num_samples
        self.workers = workers
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_response(self, index):
        response: GenerateResponse = generate(
            model=self.model_name,
            prompt=self.prompt
        )
        return response.response

    def generate(self):
        with Pool(self.workers) as p:
            self.outputs = list(
                tqdm(
                    p.imap(
                        self.generate_response,
                        range(self.num_samples)
                    ),
                    total=self.num_samples
                )
            )
    def save(self):
        if len(self.outputs) == 0:
            raise Exception("No stored outputs")
        for i, txt in enumerate(self.outputs):
            path = os.path.join(self.output_dir, f'{i}.txt')
            with open(path, 'w') as f:
                f.write(txt)


if __name__ == '__main__':
    g = Generator()
    print("Generator initalized")
    g.generate()
    print(g.outputs)
    g.save()
