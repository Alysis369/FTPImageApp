from ftp_app_view import ftp_app_view
from ftp_app_controller import ftp_app_controller
import queue
import threading
import time


class main:
    VIEW = ftp_app_view
    CONTROLLER = ftp_app_controller

    def __init__(self):
        print('Setting up...')
        # setup queues
        self._sentinel = object()
        self.status_q = queue.Queue()
        self.job_q = queue.Queue()
        self.img_q = queue.Queue()

        # setup threads
        self.job_producer_thread = threading.Thread(target=self.job_producer_main, args=(self.status_q, self.job_q))

    def startup(self):
        """ Startup threads and app """
        print("Starting up...")
        # start threads
        self.job_producer_thread.start()

        # start app
        app = self.VIEW(self.status_q, self.job_q)
        app.mainloop()

    def shutdown(self):
        print("Shutting down...")
        # sending sentinels
        self.job_q.put(self._sentinel)

        self.job_producer_thread.join()

    def job_producer_main(self, status_q, job_q):
        """ main for job producer """

        while True:
            try:
                job = job_q.get(timeout=0.1)
                if job is self._sentinel:  # check for sentinel
                    break

                # main
                img_list = self.CONTROLLER.img_list_producer(job['job'])

                # process image_list
                for img in img_list:
                    status_q.put(f'Processed image {img}.. ')
                    time.sleep(0.5)

                status_q.put(job['sentinel'])

            except queue.Empty:
                continue


if __name__ == "__main__":
    main = main()
    main.startup()  # start the threads and app
    main.shutdown()  # shutdown the app

    for thread in threading.enumerate():
        print(thread.name)
