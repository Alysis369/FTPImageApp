

class ftp_app_controller():
    def __init__(self):
        self.version = 0.0

    @staticmethod
    def img_list_producer(job):
        print(f'executing job {job}')
        return list(range(30))