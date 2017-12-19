import calendar
import datetime


def omloop_in_year(year):
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, 2)
    return [day for week in monthcal for day in week if \
            day.weekday() == calendar.SATURDAY and \
            day.month == 2][3]


def omloop_next():
    omloop_year_this = omloop_in_year(datetime.datetime.now().year)
    omloop_year_next = omloop_in_year(datetime.datetime.now().year + 1)
    today = datetime.date.today()

    if omloop_year_this < today:
        omloop = omloop_year_next
    elif omloop_year_this > today:
        omloop = omloop_year_this
    else:
        print(False)
        omloop = False

    return omloop


def omloop():
    omloop = omloop_next()

    if isinstance(omloop, datetime.date):
        return "Omloop Het Nieuwsblad is in {} days!".format((omloop - datetime.date.today()).days)
    else:
        return "Omloop Het Nieuwsblad is today!"


def main():
    print(omloop())


if __name__ == "__main__":
    main()
