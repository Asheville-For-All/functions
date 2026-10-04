#https://pypi.org/project/calendar-link/

from calendar_link import CalendarEvent, CalendarGenerator

## SAMPLE DICT
event_data = {
    "title": "Asheville For All Monthly Meetup",
    "start_time": "2026-10-22T18:00:00",
    "end_time": "2026-10-22T20:00:00",
    "location": "Hi-Wire Brewing - River Arts District, 284 Lyman St., Asheville NC 28801",
    "timezone": "America/New_York"
}

def get_calendar_links(cal_info_dict: dict):

    event = CalendarEvent.from_dict(cal_info_dict)

    generator = CalendarGenerator()

    links = generator.generate_all_links(event)

    for service, link in links.items():
        print(f"{service}: {link}")

    del links["ics"] ##the ICS link isn't usable in emails

    return links

## keys are in lower case, so may want to upper case them.