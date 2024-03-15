import threading
import customtkinter as ctk
from tkinter import filedialog
import datetime
import queue
from job import Job


class FtpAppView(ctk.CTk):
    def __init__(self, status_queue, job_queue, controller):
        super().__init__()
        self.geometry("800*600")
        self.title("FTP Image Pull App")
        self.grid_columnconfigure((0, 1), weight=0)
        self.grid_rowconfigure(0, weight=0)

        # model
        self.controller = controller

        # attributes
        self.start_dt = ctk.StringVar(value=str(datetime.datetime.now()))
        self.end_dt = ctk.StringVar(value=str(datetime.datetime.now()))
        self.line = ctk.StringVar()
        self.eq = ctk.StringVar()
        self.eq_num = ctk.StringVar()
        self.home_dir = ctk.StringVar()
        self.camera = ctk.StringVar()
        self.inspection = ctk.StringVar()
        self.quality = ctk.StringVar(value=str('Gd'))
        self.reject = ctk.StringVar()

        # threading queues
        self.status_q = status_queue
        self.job_q = job_queue

        # threads
        self._sentinel = object()
        self._job_sentinel = None
        self.status_thread = threading.Thread(target=self.__status_thread_main)

        # in-app attributes
        self.progress = ctk.DoubleVar(value=0.0)
        self.curr_job_size, self.curr_completed_job, self.curr_fault_job = 1, 0, 0
        self.status = ctk.StringVar()

        # add attribute traces
        self.line.trace_add('write', self._trace_line_write)
        self.eq.trace_add('write', self._trace_eq_write)
        self.protocol("WM_DELETE_WINDOW", self.shutdown)

    @property
    def model(self):
        return self.controller.model

    def start(self):
        # pack frames
        self._start_threads()
        self._pack_frames()

    def shutdown(self):
        # kill App
        self.destroy()

    def shutdown_thread(self):
        # clear queue
        with self.status_q.mutex:
            self.status_q.queue.clear()

        # send sentinels to threads
        self.status_q.put(self._sentinel)

        # wait on thread death
        self.status_thread.join()

    def _trace_line_write(self, *args):
        eq_list = self.model.get_station_list(line=self.line.get())

        self.eq.set('')
        self.eq_num.set('')
        self.reject.set('')
        self.eq_frame.children['!ctkoptionmenu'].configure(values=eq_list)

    def _trace_eq_write(self, *args):
        if self.eq.get():
            self.eq_num.set(self.model.get_eq_num(eq_name=self.eq.get()))

            # update reject list
            rej_list = self.model.get_reject_list(eq_num=self.eq_num.get())
            self.reject.set('')
            self._reject_frame.children['!ctkoptionmenu'].configure(values=rej_list)

    def _start_threads(self):
        if not self.status_thread.is_alive():
            self.status_thread.start()

    def _pack_frames(self):
        self.datetime_frame = self._create_datetime_frame()
        self.line_frame = self._create_line_frame()
        self.eq_frame = self._create_eq_frame()
        self.directory_frame = self._create_directory_frame()
        self.imgpull_tabview = self._create_imgpull_tabview()
        self.submit_frame = self._create_submit_frame()

        self.datetime_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nsew')
        self.line_frame.grid(row=0, column=1, padx=10, pady=(10, 5), sticky='nsew')
        self.eq_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        self.directory_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        self.imgpull_tabview.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 5), sticky='nsew')
        self.submit_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 5), sticky='nsew')

    def _create_datetime_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master=self)

        dt_start_label = ctk.CTkLabel(master=frame, text='Start Date: ')
        dt_end_label = ctk.CTkLabel(master=frame, text='End Date: ')
        dt_start_entry = ctk.CTkEntry(master=frame, placeholder_text='start_date', textvariable=self.start_dt)
        dt_end_entry = ctk.CTkEntry(master=frame, placeholder_text='end_date', textvariable=self.end_dt)

        dt_start_label.grid(row=0, column=0, padx=10, pady=10)
        dt_end_label.grid(row=1, column=0, padx=10, pady=10)
        dt_start_entry.grid(row=0, column=1, padx=10, pady=10)
        dt_end_entry.grid(row=1, column=1, padx=10, pady=10)

        return frame

    def _create_line_frame(self) -> ctk.CTkFrame:
        line_data = self.model.line_list
        frame = ctk.CTkFrame(master=self)

        for line in line_data:
            radio_button = ctk.CTkRadioButton(master=frame, variable=self.line, value=line, text=line)
            radio_button.pack(padx=10, pady=10, fill='x')

        return frame

    def _create_eq_frame(self) -> ctk.CTkFrame:
        eq_data = []

        frame = ctk.CTkFrame(master=self)

        eq_label = ctk.CTkLabel(frame, text='Equipment: ')
        eq_om = ctk.CTkOptionMenu(frame, dynamic_resizing=False, variable=self.eq, values=eq_data)
        eq_num_label = ctk.CTkLabel(frame, textvariable=self.eq_num)

        eq_label.pack(side='left', padx=10, pady=10)
        eq_om.pack(side='left', padx=10, pady=10, fill='x')
        eq_num_label.pack(side='left', padx=10, pady=10)

        return frame

    def _create_directory_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master=self)

        dir_button = ctk.CTkButton(frame, text='Select home directory', command=self.__select_home_dir)
        dir_label = ctk.CTkLabel(frame, textvariable=self.home_dir)

        dir_button.pack(side='left', padx='10', pady='10')
        dir_label.pack(side='left', padx='10', pady='10')

        return frame

    def _create_imgpull_tabview(self) -> ctk.CTkTabview:
        tabview = ctk.CTkTabview(self, anchor='nw', height=100)
        tabview.configure(command=lambda tv=tabview: self.__tabview_change(tv))
        tab_gd = tabview.add('Gd')
        tab_bd = tabview.add('Bd')

        self.tv_gd_frame = self._create_gd_frame(tab_gd)
        self.tv_bd_frame = self._create_bd_frame(tab_bd)

        self.tv_gd_frame.pack(side='left', fill='x')
        self.tv_bd_frame.pack(side='left', fill='x')

        return tabview

    # noinspection PyTypeChecker
    def _create_gd_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)

        self._create_cam_frame(master=frame).grid(row=0, column=0, padx=5, pady=(0, 5))
        self._create_insp_frame(master=frame).grid(row=0, column=1, padx=5, pady=(0, 5))

        return frame

    def _create_bd_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)

        self._create_cam_frame(master=frame).grid(row=0, column=0, padx=5, pady=(0, 5))
        self._create_insp_frame(master=frame).grid(row=0, column=1, padx=5, pady=(0, 5))

        self._reject_frame = self._create_reject_frame(master=frame)
        self._reject_frame.grid(row=1, column=0, columnspan=2, padx=5, sticky='ew')
        return frame

    # noinspection PyTypeChecker
    def _create_cam_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)
        self.__cam_rb_select = ctk.StringVar(value='Any')

        cam_label = ctk.CTkLabel(frame, text='Camera: ')
        cam_rb_any = ctk.CTkRadioButton(frame, variable=self.__cam_rb_select, text='Any', value='Any')
        cam_rb_spec = ctk.CTkRadioButton(frame, variable=self.__cam_rb_select, text='Specific (ex. C4)',
                                         value='Specific')
        cam_entry = ctk.CTkEntry(master=frame, textvariable=self.camera, state="disabled", fg_color='grey')

        # add trace
        self.__cam_rb_select.trace_add('write',
                                       lambda *args, select_var=self.__cam_rb_select,
                                              entry_var=cam_entry: self.__trace_cam_rb_write(*args, select_var,
                                                                                             entry_var))

        cam_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        cam_rb_any.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        cam_rb_spec.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        cam_entry.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        return frame

    # noinspection PyTypeChecker
    def _create_insp_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)
        self.__insp_rb_select = ctk.StringVar(value='Any')

        insp_label = ctk.CTkLabel(frame, text='Inspection: ')
        insp_rb_any = ctk.CTkRadioButton(frame, variable=self.__insp_rb_select, text='Any', value='Any')
        insp_rb_spec = ctk.CTkRadioButton(frame, variable=self.__insp_rb_select, text='Specific (ex. I10)',
                                          value='Specific')
        insp_entry = ctk.CTkEntry(master=frame, textvariable=self.inspection, state="disabled", fg_color='grey')

        # add trace
        self.__insp_rb_select.trace_add('write',
                                        lambda *args, select_var=self.__insp_rb_select,
                                               entry_var=insp_entry: self.__trace_insp_rb_write(
                                            *args, select_var, entry_var))

        insp_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        insp_rb_any.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        insp_rb_spec.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        insp_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        return frame

    def _create_reject_frame(self, master=None) -> ctk.CTkFrame:
        reject_data = []

        frame = ctk.CTkFrame(master if master else self)

        rej_label = ctk.CTkLabel(frame, text='Reject: ')
        rej_om = ctk.CTkOptionMenu(frame, dynamic_resizing=False, variable=self.reject, values=reject_data)
        rej_name_label = ctk.CTkLabel(frame, textvariable=self.reject)

        rej_label.pack(side='left', padx=10, pady=10)
        rej_om.pack(side='left', padx=10, pady=10, fill='x')
        rej_name_label.pack(side='bottom', padx=10, pady=10)

        return frame

    def _create_vv_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)

        return frame

    def _create_submit_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self, width=460, height=60)
        frame.grid_propagate(False)

        self.submit_button = ctk.CTkButton(frame, width=10, text='Run', command=self.__run_job)
        status_label = ctk.CTkLabel(frame, width=400, textvariable=self.status)
        progress_pb = ctk.CTkProgressBar(frame, variable=self.progress)

        self.submit_button.grid(row=0, column=0, padx=5, pady=5)
        status_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        progress_pb.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        return frame

    def __select_home_dir(self, *args):
        self.home_dir.set(filedialog.askdirectory())

    def __trace_cam_rb_write(self, var, index, mode, select, entry):
        sel = select.get()
        if sel == 'Any':
            entry.configure(state="disabled", fg_color='grey')
            self.camera.set('')
        elif sel == 'Specific':
            entry.configure(state="normal", fg_color=['#F9F9FA', '#343638'])

    def __trace_insp_rb_write(self, var, index, mode, select, entry):
        sel = select.get()
        if sel == 'Any':
            entry.configure(state="disabled", fg_color='grey')
            self.inspection.set('')
        elif sel == 'Specific':
            entry.configure(state="normal", fg_color=['#F9F9FA', '#343638'])

    def __tabview_change(self, tabview):
        self.quality.set(tabview.get())
        self.camera.set('')
        self.inspection.set('')
        self.reject.set('')
        self.__cam_rb_select.set('Any')
        self.__insp_rb_select.set('Any')

    def __run_job(self):
        self.submit_button.configure(state='disabled')  # disable button

        # create and put job
        self._job_sentinel = object()
        job = Job(
            start_date=self.start_dt.get(),
            end_date=self.end_dt.get(),
            line=self.line.get(),
            eq=self.eq.get(),
            eq_num=self.eq_num.get(),
            home_dir=self.home_dir.get(),
            camera=self.camera.get(),
            inspection=self.inspection.get(),
            quality=self.quality.get(),
            reject=self.reject.get()
        )

        # self.status_queue.put(('Starting first job!',))
        self.progress.set(0.0)
        self.job_q.put({'job': job, 'sentinel': self._job_sentinel})

    def __status_thread_main(self):
        # poll status_q
        while True:
            try:
                status = self.status_q.get(timeout=0.1)
                if status is self._job_sentinel:
                    # A job is completed
                    self._job_sentinel = None

                    job_summary_status = f'Completed! Transferred {self.curr_job_size - self.curr_fault_job} images. '
                    job_summary_status += f'{self.curr_fault_job} fault occurred.' if self.curr_fault_job else ''

                    status = {'status': job_summary_status}
                    self.curr_job_size, self.curr_completed_job, self.curr_fault_job = 1, 0, 0
                    self.submit_button.configure(state='normal')

                if status is self._sentinel:
                    # kill thread
                    break

                # progress bar logic
                if 'job_size' in status:
                    # update job size
                    self.curr_job_size = status['job_size']
                    continue
                # time out logic
                if 'fault' in status:
                    # add to timeout counter
                    self.curr_fault_job += 1
                    continue

                self.curr_completed_job += 1
                self.progress.set(int(self.curr_completed_job) / int(self.curr_job_size))
                self.status.set(status['status'])

            except queue.Empty:
                continue
