import datetime


def omloop():
    day_omloop = datetime.date(2018, 2, 24)

    return "Omloop Het Nieuwsblad is in {} days!".format((day_omloop - datetime.date.today()).days)
