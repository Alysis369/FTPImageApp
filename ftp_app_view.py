import queue

import customtkinter as ctk
from tkinter import filedialog
import datetime
import time
import threading


class ftp_app_view(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800*600")
        self.title("FTP Image Pull App")
        self.grid_columnconfigure((0, 1), weight=0)
        self.grid_rowconfigure((0), weight=0)

        # attributes
        # TODO: Move app model props to another class
        self.start_dt = ctk.StringVar(value=str(datetime.datetime.now()))
        self.end_dt = ctk.StringVar(value=str(datetime.datetime.now()))
        self.line = ctk.StringVar()
        self.eq = ctk.StringVar()
        self.eq_num = ctk.StringVar()
        self.home_dir = ctk.StringVar()
        self.camera = ctk.StringVar()
        self.inspection = ctk.StringVar()
        self.quality = ctk.StringVar()
        self.reject = ctk.StringVar()
        self.progress_queue = queue.Queue()

        # in-app attributes
        self.progress = ctk.DoubleVar(value=0.0)
        self.status = ctk.StringVar()


        # add attribute traces
        self.eq.trace_add('write', self._trace_eq_write)

        # pack frames
        self._pack_frames()

    def _trace_eq_write(self, *args):
        # TODO: replace eq_num_dict with DB
        eq_num_dict = {'': '', 'Mario': 'Red hair dude', 'Luigi': 'Green hair bro'}
        self.eq_num.set(eq_num_dict[self.eq.get()])

    def _pack_frames(self):
        self._create_datetime_frame().grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nsew')
        self._create_line_frame().grid(row=0, column=1, padx=10, pady=(10, 5), sticky='nsew')
        self._create_eq_frame().grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        self._create_directory_frame().grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        self._create_imgpull_tabview().grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 5), sticky='nsew')
        self._create_submit_frame().grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 5), sticky='nsew')

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
        # TODO: pull line data from DB
        line_data = ['Nintendo', 'SquareEnix']

        frame = ctk.CTkFrame(master=self)

        for line in line_data:
            radio_button = ctk.CTkRadioButton(master=frame, variable=self.line, value=line, text=line)
            radio_button.pack(padx=10, pady=10, fill='x')

        return frame

    def _create_eq_frame(self) -> ctk.CTkFrame:
        # TODO: pull eq data from DB
        eq_data = ['Mario', 'Luigi']

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
        tab_vv = tabview.add('VV')

        self._create_gd_frame(tab_gd).pack(side='left', fill='x')
        self._create_bd_frame(tab_bd).pack(side='left', fill='x')

        return tabview

    # noinspection PyTypeChecker
    def _create_gd_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)

        self._create_cam_frame(master=frame).grid(row=0, column=0, padx=5, pady=(0,5))
        self._create_insp_frame(master=frame).grid(row=0, column=1, padx=5, pady=(0,5))

        return frame

    def _create_bd_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)

        self._create_cam_frame(master=frame).grid(row=0, column=0, padx=5, pady=(0,5))
        self._create_insp_frame(master=frame).grid(row=0, column=1, padx=5, pady=(0,5))
        self._create_reject_frame(master=frame).grid(row=1, column=0, columnspan=2, padx=5, sticky='ew')
        return frame

    # noinspection PyTypeChecker
    def _create_cam_frame(self, master=None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(master if master else self)
        self.__cam_rb_select = ctk.StringVar(value='Any')

        cam_label = ctk.CTkLabel(frame, text='Camera: ')
        cam_rb_any = ctk.CTkRadioButton(frame, variable=self.__cam_rb_select, text='Any', value='Any')
        cam_rb_spec = ctk.CTkRadioButton(frame, variable=self.__cam_rb_select, text='Specific (ex. C4)', value='Specific')
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
        # TODO: pull eq data from DB
        reject_data = ['', 'Hat', 'Mustache', 'Clothes']

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

    def _create_submit_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self)

        submit_button = ctk.CTkButton(frame, width=10, text='Run', command=lambda: self.__run_main_thread(submit_button))
        status_label = ctk.CTkLabel(frame, width=400, textvariable=self.status)
        progress_pb = ctk.CTkProgressBar(frame, variable=self.progress)

        submit_button.grid(row=0, column=0, padx=5, pady=5)
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
        self.__cam_rb_select.set('Any')
        self.__insp_rb_select.set('Any')

    def __run_main_thread(self, run_button):
        # print(f'start_dt: {self.start_dt.get()}\n'
        #       f'end_dt: ')
        # self.start_dt = ctk.StringVar(value=str(datetime.datetime.now()))
        # self.end_dt = ctk.StringVar(value=str(datetime.datetime.now()))
        # self.line = ctk.StringVar()
        # self.eq = ctk.StringVar()
        # self.eq_num = ctk.StringVar()
        # self.home_dir = ctk.StringVar()
        # self.camera = ctk.StringVar()
        # self.inspection = ctk.StringVar()
        # self.quality = ctk.StringVar()
        # self.reject = ctk.StringVar()

        run_button.configure(state='disabled')
        self.status.set('verrrrrrryyyyyyyyyyyyyyLOOOOOOONGGGGTEEEEEXXXTTTT')
        # self.progress_thread = threading.Thread(target=self.__run_main)
        # self.progress_thread.start()

        # if self.thread.is_alive():
        #     self.after(100, self.periodiccall)

        # run_button.configure(state='enabled')

    # def __check_progress_queue(self):
    # def __run_main(self):
    #     # run the main function here
    #     self.thread = StatusThreadClient(self.progress_queue)
    #     self.thread.start()