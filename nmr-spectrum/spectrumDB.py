from database import Database

class SpectrumDB:

    @staticmethod
    def Create(h):
        conn = Database.GetConnection()

        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO spectrum SET spectrum=%s", (h,))
            conn.commit()

            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM spectrum WHERE spectrum=%s ORDER BY date DESC LIMIT 1", (h,))
                return int(cursor.fetchone()[0])
        finally:
            conn.close()

    @staticmethod
    def AddPeaks(spectrumId, peaks):
        conn = Database.GetConnection()

        try:
            with conn.cursor() as cursor:
                cursor.executemany("INSERT IGNORE INTO peaks SET peak=%s, class=%s, spectrum_id=%s", [(round(peak, 5), c, spectrumId) for (peak, c) in peaks])
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def RemovePeaks(spectrumId, peaks):
        conn = Database.GetConnection()

        try:
            with conn.cursor() as cursor:
                cursor.executemany("DELETE FROM peaks WHERE peak=%s AND class=%s AND spectrum_id=%s", [(round(peak, 5), c, spectrumId) for (peak, c) in peaks])
            conn.commit()
        finally:
            conn.close()
