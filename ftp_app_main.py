from ftp_app_view import ftp_app_view
import queue
import threading
import time


class main_thread():
    VIEW = ftp_app_view

    def __init__(self):
        # Create queues
        self.status_queue = queue.Queue()
        self.job_queue = queue.Queue()

        # Create threads
        self.threads_list = []
        self.view_thread = self.spawn_thread(self.run_view, status_queue=self.status_queue, job_queue=self.job_queue)


    def start(self):
        """ Start all the threads """
        for thread in self.threads_list:
            thread.start()

    def stop(self):
        """ Check for all thread to join """

        for thread in self.threads_list:
            print(f'waiting for thread: {thread}')
            thread.join()
            print('thread stopped')

    def spawn_thread(self, target, **kwargs):
        """ Spawns a new thread with specified target and append to threads list"""
        thread = threading.Thread(target=target, kwargs=kwargs)
        self.threads_list.append(thread)

        return thread

    def run_view(self, **kwargs):
        """ Run GUI """
        if 'status_queue' not in kwargs:
            raise AttributeError('Missing status_queue arg for View')
        if 'job_queue' not in kwargs:
            raise AttributeError('Missing job_queue arg for View')

        app = self.VIEW(kwargs['status_queue'], kwargs['job_queue'])
        app.mainloop()
        print('bye')
        print(self.threads_list)

if __name__ == "__main__":
    main = main_thread()
    main.start()

    time.sleep(5)
    main.stop()

