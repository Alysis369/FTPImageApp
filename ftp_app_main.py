from ftp_app_view import ftp_app_view
from ftp_app_controller import ftp_app_controller
from ftp_app_model import ftp_app_model
import queue
import threading
import time


class main:
    VIEW = ftp_app_view
    CONTROLLER = ftp_app_controller
    MODEL = ftp_app_model

    def __init__(self, n_worker=5):
        print('Setting up...')
        # setup controller
        self.controller = self.CONTROLLER(self.MODEL)

        # setup queues
        self._sentinel = object()
        self.status_q = queue.Queue()
        self.job_q = queue.Queue()
        self.img_q = queue.Queue()

        # setup threads
        self.job_producer_thread = threading.Thread(target=self.job_producer_main,
                                                    args=(self.status_q, self.job_q, self.img_q))
        self.img_worker_pool = []
        self.spawn_worker_pool(n_worker)  # spawn workers

    def startup(self):
        """ Startup threads and app """
        print("Starting up...")

        # start threads
        try:
            self.job_producer_thread.start()
            for worker in self.img_worker_pool:
                worker.start()

            # start app
            app = self.VIEW(self.status_q, self.job_q, self.controller)
            app.mainloop()
        except Exception as e:
            print(f'App load failed: {e}')
            self.shutdown()

    def shutdown(self):
        print("Shutting down...")
        # flush queue
        for q in (self.job_q, self.img_q):
            with q.mutex:
                q.queue.clear()

        # sending sentinels
        self.job_q.put(self._sentinel)
        self.img_q.put(self._sentinel)
        self.img_q.task_done()

        self.job_producer_thread.join()
        for worker in self.img_worker_pool:
            worker.join()

    def spawn_worker_pool(self, n_worker):
        for _ in range(n_worker):
            thread = threading.Thread(target=self.img_worker_main, args=(self.status_q, self.img_q))
            self.img_worker_pool.append(thread)

    def job_producer_main(self, status_q, job_q, img_q):
        """ main for job producer """

        while True:
            try:
                job = job_q.get(timeout=0.1)
                if job is self._sentinel:  # check for sentinel
                    break

                # main
                imgpath_list = self.controller.img_list_producer(job['job'])

                status_q.put({'status': f"identified {len(imgpath_list)} images..", 'job_size': len(imgpath_list)})

                # process image_list, put in img_q
                for img in imgpath_list:
                    img_q.put({'imgpath': img, 'homepath': job['job'].home_dir})

                # indicate that all images in the job has been sent
                img_q.put({'sentinel': job['sentinel']})

            except queue.Empty:
                continue

    def img_worker_main(self, status_q, img_q):
        """ main job for img worker """

        while True:
            try:
                img = img_q.get(timeout=0.1)
                if img is self._sentinel:
                    img_q.put(self._sentinel)
                    img_q.task_done()  # to prevent collision with actual tasks
                    break

                if 'sentinel' in img:
                    # means end of queue, wait for all threads to finish
                    img_q.task_done()
                    img_q.join()

                    status_q.put(img['sentinel'])
                    continue

                # main
                status = self.controller.model.download_ftp_image(homepath=img['homepath'], imgpath=img['imgpath'])
                print(f'{img["imgpath"]} {status} by {threading.current_thread().name}')
                status_q.put({'status': f'{img["imgpath"]} {status} by {threading.current_thread().name}'})
                img_q.task_done()

            except queue.Empty:
                continue


if __name__ == "__main__":
    main = main()
    main.startup()  # start the threads and app
    main.shutdown()  # shutdown the app

    for thread_name in threading.enumerate():
        print(thread_name.name)
