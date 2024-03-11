from sqlalchemy import create_engine, engine as sa_engine, text
import pandas as pd
from ftplib import FTP


class ftp_app_model:
    PT_DB = 'root:password@localhost:3306/eng'
    IMG_DB = 'root:password@localhost:3307/eng'
    IMG_FTP = {'server': 'localhost',
               'user': 'user',
               'password': 'pass'}

    def __init__(self, pt_db=PT_DB, img_db=IMG_DB, img_ftp=IMG_FTP):
        self.ptdb = self.db_init(pt_db)
        self.imgdb = self.db_init(img_db)
        self.imgftp = self.ftp_init(img_ftp)

    @staticmethod
    def _sql_query_decorator(func):
        def wrapper(self, **kwargs):
            with self.ptdb.connect() as conn, conn.begin():
                val = func(self, conn, **kwargs)
            return val

        return wrapper

    def db_init(self, creds: str) -> sa_engine:
        engine = create_engine(f"mysql+pymysql://{creds}")
        self.db_isalive(engine)  # check if conn is valid
        return engine

    def db_isalive(self, engine: sa_engine):
        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT 1"))
            except Exception as e:
                print(f'Connection error: {e}')

    def ftp_init(self, creds: dict) -> FTP:
        ftp = FTP(creds['server'], creds['user'], creds['password'])
        self.ftp_isalive(ftp)  # check if conn is valid
        return ftp

    def ftp_isalive(self, ftp: FTP):
        try:
            ftp.voidcmd("NOOP")
        except Exception as e:
            print(f'Connection failed: {e}')

    @property
    def line_list(self) -> list:
        with self.ptdb.connect() as conn, conn.begin():
            data = pd.read_sql_query("SELECT DISTINCT Line FROM ENG.Station s", conn)
        return list(data['Line'])

    @_sql_query_decorator
    def get_station_list(self, conn: sa_engine, **kwargs) -> list:
        line = kwargs['line']
        data = pd.read_sql_query(
            "SELECT StationNames FROM ENG.Station s "
            f"WHERE Line = '{line}'",
            conn)

        return list(data['StationNames'])

    @_sql_query_decorator
    def get_eq_num(self, conn: sa_engine, **kwargs) -> str:
        eq_name = kwargs['eq_name']
        data = pd.read_sql_query(
            "SELECT StationNum FROM ENG.Station s "
            f"WHERE StationNames  = '{eq_name}'",
            conn
        )
        return str(data['StationNum'][0])

    @_sql_query_decorator
    def get_reject_list(self, conn: sa_engine, **kwargs) -> list:
        eq_num = kwargs['eq_num']

        data = pd.read_sql_query(
            "SELECT RejectName FROM ENG.RejectType rt "
                "JOIN ENG.Station s ON rt.StationID = s.StationID " 
                f"WHERE StationNum  = '{eq_num}'",
            conn)

        return list(data['RejectName'])