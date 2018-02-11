from database import Database

class SpectrumDB:

    @staticmethod
    def Add(h):
        conn = Database.GetConnection()

        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT IGNORE INTO spectrum SET hash=%s", (h,))
            conn.commit()

            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM spectrum WHERE hash=%s", (h,))
                return cursor.fetchone()[0]
        finally:
            conn.close()
