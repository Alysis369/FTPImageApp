from ftp_app_view import FtpAppView
from ftp_app_controller import FtpAppController
from ftp_app_model import FtpAppModel
import queue
import threading
import traceback as tb
from CTkMessagebox import CTkMessagebox

class Main:
    VERSION = 0.0
    VIEW = FtpAppView
    CONTROLLER = FtpAppController
    MODEL = FtpAppModel

    def __init__(self, n_worker: int = 5):
        print('Setting up...')
        # setup queues
        self._sentinel = object()
        self.status_q = queue.Queue()
        self.job_q = queue.Queue()
        self.img_q = queue.Queue()

        # setup threads
        self.job_producer_thread = threading.Thread(target=self._job_producer_main,
                                                    args=(self.status_q, self.job_q, self.img_q))
        self.img_worker_pool = []
        self._spawn_worker_pool(n_worker)  # spawn workers

        # setup controller and view
        self.controller = self.CONTROLLER(self.MODEL)
        self.view = self.VIEW(self.status_q, self.job_q, self.controller)

    def startup(self):
        """ Startup threads and app """
        print("Starting up...")

        # start threads
        try:
            # start thread
            if not self.job_producer_thread.is_alive():
                self.job_producer_thread.start()
            for worker in self.img_worker_pool:
                if worker.is_alive():
                    continue
                worker.start()

            # start controller
            self.controller.start()

            # start app
            self.view.start()
            self.view.mainloop()
        except Exception as e:
            # create warning box
            print(''.join(tb.format_exception(None, e, e.__traceback__)))
            msg = CTkMessagebox(title='App load failed', message=str(e), icon="cancel",
                                option_1='Retry', option_2='Cancel')

            if msg.get() == 'Retry':
                self.startup()
            else:
                self.shutdown()

    def shutdown(self):
        """ Shutdown app and clear threads """
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

        # confirm app death
        self.view.shutdown_thread()

    def _spawn_worker_pool(self, n_worker: int):
        for _ in range(n_worker):
            thread = threading.Thread(target=self._img_worker_main, args=(self.status_q, self.img_q))
            self.img_worker_pool.append(thread)

    def _job_producer_main(self, status_q: queue.Queue, job_q: queue.Queue, img_q: queue.Queue):
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
            except ConnectionError:
                status_q.put(
                    {'status': f'DB connection TIMEOUT by {threading.current_thread().name}', 'fault': True})
                img_q.put({'sentinel': job['sentinel']})
            except AttributeError:
                status_q.put({'status': f'HOMEPATH invalid by {threading.current_thread().name}', 'fault': True})
                img_q.put({'sentinel': job['sentinel']})

    def _img_worker_main(self, status_q: queue.Queue, img_q: queue.Queue):
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
                status_q.put({'status': f'{img["imgpath"]} {status} by {threading.current_thread().name}'})
                img_q.task_done()

            except queue.Empty:
                continue

            except ConnectionError:
                status_q.put(
                    {'status': f'FTP connection TIMEOUT by {threading.current_thread().name}', 'fault': True})
                img_q.task_done()


if __name__ == "__main__":
    main = Main()
    main.startup()  # start the threads and app
    main.shutdown()  # shutdown the app
