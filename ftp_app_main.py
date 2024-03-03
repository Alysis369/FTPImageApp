from ftp_app_view import ftp_app_view
import queue
import threading
import time

def main():
    for i in range(5):
        time.sleep(1)
        print(i)

if __name__ == "__main__":

    app = ftp_app_view(queue.Queue(), queue.Queue())
    test = threading.Thread(target=main)

    test.start()
    print('im here 1')
    app.mainloop()
    print('im here 2')
    test.join()
    print('im here 3')

