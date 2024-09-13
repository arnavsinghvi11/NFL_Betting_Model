import datetime
from datetime import datetime
from datetime import timedelta
import pytz
from pytz import timezone

class Date:
    def date_formatting(self, days):
        #returns formatted version of date inputted to include month, date, year, current time
        date_format='%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        if days > 0: 
            correct_date = date.astimezone(timezone('US/Pacific')) + timedelta(days = days)
        elif days < 0:
            correct_date = date.astimezone(timezone('US/Pacific')) - timedelta(days = -days)
        else:
            correct_date = date.astimezone(timezone('US/Pacific'))
        return correct_date.strftime(date_format)

    def date_month_day(self, days):
        #returns inputted date's month and day
        date_formatted = self.date_formatting(days)
        date_formatted = date_formatted.split('/')[0] + '/' + date_formatted.split('/')[1]
        return date_formatted.split('/')[0].lstrip('0'), date_formatted.split('/')[1].lstrip('0')

    def date_converter(self, col):
        #returns formatted version of date to maintain recency of dates based on NFL Schedule
        #Since the season starts in September, 9 is the earliest number.
        #Each "single-digit" month is then compounded with a multiplier to be the most recent 
        #when sorted in descending order
        if int(col.split('-')[0]) < 9:
            multipler = 1
            if int(col.split('-')[0]) == 2:
                multipler = 10
            if int(col.split('-')[0]) == 3:
                multipler = 100
            if int(col.split('-')[0]) == 4:
                multipler = 1000
            if int(col.split('-')[0]) == 5:
                multipler = 10000
            if int(col.split('-')[0]) == 6:
                multipler = 100000
            if int(col.split('-')[0]) == 7:
                multipler = 1000000
            col = str(int(col.split('-')[0]) * 10000 * multipler)+ col.split('-')[1]
        else:
            if int(col.split('-')[1]) < 9: 
                col = col.split('-')[0] + '0' + col.split('-')[1]
            else:
                col = col.split('-')[0] + col.split('-')[1]
        return int(col)
    
    def date_converter2(self, date):
        month, day, year = date.split('/')
        if int(month) > 9:
            day = day.zfill(2)
        else:
            day = str(int(day))
        return str(int(month)), day
    
    def get_date_counter2(self, date_counter, month, month_ends):
        if date_counter == 1:
            if month == 10:
                return month_ends[9]
            elif month == 11:
                return month_ends[10]
            elif month == 12:
                return month_ends[11]
            elif month == 1:
                return month_ends[12]
            else:
                return month_ends[month - 1]
        else:
            if date_counter - 1 < 9:
                if month == 9:
                    return int(str(9) + str(date_counter - 1))
                elif month == 10:
                    return int(str(100) + str(date_counter - 1))
                elif month == 11:
                    return int(str(110) + str(date_counter - 1))
                elif month == 12:
                    return int(str(120) + str(date_counter - 1))
                else:
                    if date_counter - 1 == 9:
                        return int(str(month) + ('0' * (5 + (month - 1))) + str(date_counter - 1))
                    else:
                        return int(str(month) + ('0' * (4 + (month - 1))) + str(date_counter - 1))
            else:
                if month == 9:
                    return int(str(9) + str(date_counter - 1))
                elif month == 10:
                    return int(str(10) + str(date_counter - 1))
                elif month == 11:
                    return int(str(11) + str(date_counter - 1))
                elif month == 12:
                    return int(str(12) + str(date_counter - 1))
                else:
                    return int(str(month) + ('0' * (4 + (month - 1))) + str(date_counter - 1))
