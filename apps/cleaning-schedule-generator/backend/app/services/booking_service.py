from app.schemas.schedule import BookingInput


def normalize_bookings(bookings: list[BookingInput]) -> list[BookingInput]:
    return sorted(bookings, key=lambda booking: (booking.property_id, booking.check_out, booking.check_in))
