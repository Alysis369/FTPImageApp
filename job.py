from dataclasses import dataclass


@dataclass
class Job:
    DB_TABLE = {
        "Nintendo": "ENG.NintendoProcessRecords",
        "SquareEnix": "ENG.SquareProcessRecords"
    }
    DB_TABLE_SHORT = {
        "Nintendo": "npr",
        "SquareEnix": "spr"
    }

    start_date: str
    end_date: str
    line: str
    eq: str
    eq_num: str
    home_dir: str
    camera: str
    inspection: str
    quality: str
    reject: str

    @property
    def ptdb_table(self):
        return Job.DB_TABLE[self.line]

    @property
    def ptdb_table_short(self):
        return Job.DB_TABLE_SHORT[self.line]
