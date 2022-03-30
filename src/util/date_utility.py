from datetime import datetime


class DateUtility:


    @staticmethod
    def get_current_time():
        return datetime.now()


    @staticmethod
    def get_current_string_time(format="%Y%m%d%H%M%S"):
        return DateUtility.get_current_time().strftime(format)


    @staticmethod
    def get_current_timestamp():
        return datetime.timestamp(DateUtility.get_current_time())

