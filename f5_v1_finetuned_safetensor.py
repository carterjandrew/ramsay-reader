import os


class Model_Files:
    git_repo_name = 'https://huggingface.co/the-ramsay-experience/finetuned_10000_f5_v1'
    model_dl_dir = '.' + git_repo_name[
        git_repo_name.rfind('/'):
    ]

    def __init__(self):
        os.makedirs(self.model_dl_dir, exist_ok=True)
        os.system(
            f'git submodule add --force {self.git_repo_name}'
        )
        os.system(
            f'git submodule update && cd {self.model_dl_dir} && git lfs install && git lfs fetch origin main'
        )


if __name__ == '__main__':
    mf = Model_Files()
    print(f'Finished downloading files to {mf.model_dl_dir}')
