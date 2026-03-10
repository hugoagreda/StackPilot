from app.schemas.schedule import ScheduleTask


def render_ics(tasks: list[ScheduleTask]) -> str:
    header = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//StackPilot//Cleaning Schedule Generator//EN",
    ]
    body = []

    for task in tasks:
        start = task.start.strftime("%Y%m%dT%H%M%S")
        end = task.end.strftime("%Y%m%dT%H%M%S")
        body.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{task.booking_id}-{task.cleaner_id}",
                f"SUMMARY:Cleaning {task.property_id}",
                f"DESCRIPTION:Booking {task.booking_id} assigned to {task.cleaner_name}",
                f"DTSTART:{start}",
                f"DTEND:{end}",
                "END:VEVENT",
            ]
        )

    footer = ["END:VCALENDAR"]
    return "\r\n".join(header + body + footer) + "\r\n"
