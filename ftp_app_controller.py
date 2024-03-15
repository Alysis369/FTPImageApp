from job import Job


class FtpAppController:
    VERSION = 0.0

    def __init__(self, model):
        self.model = model

    def start(self):
        """ Start the controller """
        self.model = self.model()

    def img_list_producer(self, job: Job) -> list:
        """
        run DB calls and produce list of images to download
        :param job:
        :return target_imgpath_list:
        """
        print(f'executing job {repr(job)}')

        # Execute db calls
        ptdb_query = FtpAppController.generate_ptdb_query(job)
        imgdb_query = FtpAppController.generate_imgdb_query(job)
        ptdb_results = self.model.run_ptdb_query(query=ptdb_query)
        imgdb_results = self.model.run_imgdb_query(query=imgdb_query)

        # combine files together
        txid_list = list(ptdb_results['Txid'])
        imgpath_list = list(imgdb_results['ImgPath'])

        # compare the two different files
        target_imgpath_list = []

        for imgpath in imgpath_list:
            for txid in txid_list:
                if txid in imgpath:
                    target_imgpath_list.append(imgpath)
                    break

        return target_imgpath_list

    @staticmethod
    def generate_ptdb_query(job: Job) -> str:
        """
        Generate ptdb query str
        :param job:
        :return query: str
        """
        query = f"SELECT Txid FROM {job.ptdb_table} {job.ptdb_table_short} " + \
                f"LEFT JOIN ENG.Station s ON {job.ptdb_table_short}.StationID = s.StationID " + \
                f"LEFT JOIN ENG.RejectType rt on {job.ptdb_table_short}.RejectID  = rt.RejectID " + \
                f"WHERE StationNum  = '{job.eq_num}' " + \
                f"AND CreatedDateTime BETWEEN '{job.start_date}' AND '{job.end_date}' "

        if job.quality == 'Gd':
            query += f'AND {job.ptdb_table_short}.RejectID IS NULL '
        elif job.quality == 'Bd':
            query += f'AND {job.ptdb_table_short}.RejectID IS NOT NULL '

        if job.reject:
            query += f"AND RejectName = '{job.reject}' "

        return query

    @staticmethod
    def generate_imgdb_query(job: Job) -> str:
        """
        Generate imgdb query str
        :param job:
        :return query: str
        """
        query = f"SELECT ImgPath FROM ENG.ImgFile if2 " + \
                f"WHERE ImgPath LIKE '%%{job.eq}%%{job.camera}%%{job.inspection}%%' " + \
                f"AND CreatedDateTime BETWEEN '{job.start_date}' AND '{job.end_date}' "

        return query
