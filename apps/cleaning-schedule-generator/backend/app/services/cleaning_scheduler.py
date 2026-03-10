from collections import defaultdict
from datetime import timedelta

from app.schemas.schedule import CleanerInput, ScheduleTask, UnscheduledTask


def generate_schedule(
    bookings,
    cleaners: list[CleanerInput],
    cleaning_duration_minutes: int,
    fallback_window_hours: int,
) -> tuple[list[ScheduleTask], list[UnscheduledTask]]:
    tasks: list[ScheduleTask] = []
    unscheduled: list[UnscheduledTask] = []
    cleaner_assignments = defaultdict(int)
    cleaner_busy: dict[str, list[tuple]] = defaultdict(list)

    grouped_by_property = defaultdict(list)
    for booking in bookings:
        grouped_by_property[booking.property_id].append(booking)

    ordered_bookings = []
    for property_bookings in grouped_by_property.values():
        property_bookings.sort(key=lambda booking: booking.check_out)
        ordered_bookings.extend(property_bookings)

    ordered_bookings.sort(key=lambda booking: booking.check_out)

    for booking in ordered_bookings:
        same_property_bookings = grouped_by_property[booking.property_id]
        current_index = same_property_bookings.index(booking)
        next_booking = (
            same_property_bookings[current_index + 1]
            if current_index + 1 < len(same_property_bookings)
            else None
        )

        earliest_start = booking.check_out
        latest_end = (
            next_booking.check_in
            if next_booking
            else booking.check_out + timedelta(hours=fallback_window_hours)
        )

        chosen_slot = None
        chosen_cleaner = None

        for cleaner in sorted(cleaners, key=lambda item: cleaner_assignments[item.cleaner_id]):
            for window in cleaner.availability:
                candidate_start = max(earliest_start, window.start)
                candidate_end = candidate_start + timedelta(minutes=cleaning_duration_minutes)

                if candidate_end > window.end or candidate_end > latest_end:
                    continue

                overlaps_existing = any(
                    not (candidate_end <= busy_start or candidate_start >= busy_end)
                    for busy_start, busy_end in cleaner_busy[cleaner.cleaner_id]
                )
                if overlaps_existing:
                    continue

                chosen_slot = (candidate_start, candidate_end)
                chosen_cleaner = cleaner
                break

            if chosen_cleaner:
                break

        if not chosen_slot or not chosen_cleaner:
            unscheduled.append(
                UnscheduledTask(
                    booking_id=booking.booking_id,
                    property_id=booking.property_id,
                    reason="No feasible cleaner/time slot between reservations",
                )
            )
            continue

        cleaner_busy[chosen_cleaner.cleaner_id].append(chosen_slot)
        cleaner_assignments[chosen_cleaner.cleaner_id] += 1

        tasks.append(
            ScheduleTask(
                booking_id=booking.booking_id,
                property_id=booking.property_id,
                cleaner_id=chosen_cleaner.cleaner_id,
                cleaner_name=chosen_cleaner.name,
                start=chosen_slot[0],
                end=chosen_slot[1],
            )
        )

    return tasks, unscheduled
