import os
from sqlalchemy import create_engine, engine as sa_engine, text
import pandas as pd
from ftplib import FTP
import threading


class FtpAppModel:
    VERSION = 0.0
    PT_DB = 'root:password@localhost:3306/eng'
    IMG_DB = 'root:password@localhost:3307/eng'
    IMG_FTP = {'server': 'localhost',
               'user': 'user',
               'password': 'pass'}

    def __init__(self, pt_db=PT_DB, img_db=IMG_DB, img_ftp=IMG_FTP):
        self.ptdb = self._db_init(pt_db)
        self.imgdb = self._db_init(img_db)
        self._ftp_init(img_ftp)  # make sure connection is alive

    @staticmethod
    def _ptdb_query_decorator(func):
        def wrapper(self, **kwargs):
            with self.ptdb.connect() as conn, conn.begin():
                val = func(self, conn, **kwargs)
            return val

        return wrapper

    @staticmethod
    def _imgdb_query_decorator(func):
        def wrapper(self, **kwargs):
            with self.imgdb.connect() as conn, conn.begin():
                val = func(self, conn, **kwargs)
            return val

        return wrapper

    def _db_init(self, creds: str) -> sa_engine:
        try:
            engine = create_engine(f"mysql+pymysql://{creds}")
            self._db_isalive(engine)  # check if conn is valid
            return engine
        except Exception as e:
            raise ConnectionError(f'SQL DB Connection Error: {e}')

    def _db_isalive(self, engine: sa_engine):
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def _ftp_init(self, creds: dict) -> FTP:
        try:
            ftp = FTP(creds['server'], creds['user'], creds['password'], timeout=3)
            ftp.set_pasv(True)
            self._ftp_isalive(ftp)  # check if conn is valid
            return ftp
        except Exception as e:
            raise ConnectionError(f'FTP Connection Error: {e}')

    def _ftp_isalive(self, ftp: FTP):
        ftp.voidcmd("NOOP")

    @property
    def line_list(self) -> list:
        with self.ptdb.connect() as conn, conn.begin():
            data = pd.read_sql_query("SELECT DISTINCT Line FROM ENG.Station s", conn)
        return list(data['Line'])

    @_ptdb_query_decorator
    def get_station_list(self, conn: sa_engine, **kwargs) -> list:
        line = kwargs['line']
        data = pd.read_sql_query(
            "SELECT StationNames FROM ENG.Station s "
            f"WHERE Line = '{line}'",
            conn)
        return list(data['StationNames'])

    @_ptdb_query_decorator
    def get_eq_num(self, conn: sa_engine, **kwargs) -> str:
        eq_name = kwargs['eq_name']
        data = pd.read_sql_query(
            "SELECT StationNum FROM ENG.Station s "
            f"WHERE StationNames  = '{eq_name}'",
            conn
        )
        return str(data['StationNum'][0])

    @_ptdb_query_decorator
    def get_reject_list(self, conn: sa_engine, **kwargs) -> list:
        eq_num = kwargs['eq_num']

        data = pd.read_sql_query(
            "SELECT RejectName FROM ENG.RejectType rt "
            "JOIN ENG.Station s ON rt.StationID = s.StationID "
            f"WHERE StationNum  = '{eq_num}'",
            conn)

        return list(data['RejectName'])

    @_ptdb_query_decorator
    def run_ptdb_query(self, conn: sa_engine, **kwargs) -> pd.DataFrame:
        query = kwargs['query']

        data = pd.read_sql_query(query, conn)

        return data

    @_imgdb_query_decorator
    def run_imgdb_query(self, conn: sa_engine, **kwargs) -> pd.DataFrame:
        query = kwargs['query']

        data = pd.read_sql_query(query, conn)

        return data

    def download_ftp_image(self, homepath: str, imgpath: str):
        filepath = imgpath.split('/')
        img = filepath.pop()
        imgpath = '/'.join(filepath)

        # spawn new ftp connection
        ftp = self._ftp_init(self.IMG_FTP)
        # change dir
        ftp.cwd(imgpath)

        # transfer images
        with open('/'.join([homepath, img]), "wb") as file:
            try:
                ftp.retrbinary(f"RETR {img}", file.write)
                ftp.quit()
            except Exception as e:
                print(f'{img}: {e}')
                file.close()
                os.remove('/'.join([homepath, img]))  # delete broken image
                ftp.quit()
                return "FAIL"
        return "SUCCESS"
