from database import Database

class SpectrumDB:

    @staticmethod
    def Add(h):
        conn = Database.GetConnection()

        cur = conn.cursor()
        cur.execute("INSERT IGNORE INTO spectrum SET hash=%s", (h,))
        conn.commit()

        cur.execute("SELECT id FROM spectrum WHERE hash=%s", (h,))
        spectrumId = cur.fetchone()[0]
        conn.close()

        return spectrumId
