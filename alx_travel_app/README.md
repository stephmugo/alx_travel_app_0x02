# 🏡 Django Listings & Bookings API

This Django REST API provides functionality for managing rental listings, bookings, and reviews. It supports user authentication and enforces access control to ensure that users only manage their own data.

## 🚀 Features

- Full CRUD support for:
  - Listings (rental properties)
  - Bookings (with date range, guest count, and status)
  - Reviews (one per user per listing)
- Automatically assigns:
  - `host` to listing creators
  - `user` to booking creators
- Access control using Django REST Framework permissions
- Supports seeding with Faker data via custom Django command
- Uses `ModelViewSet` for efficient endpoint management


---

## 🧠 Models Overview

### `Listing`
- Fields: `title`, `description`, `location`, `price_per_night`, `host`, `created_at`

### `Booking`
- Fields: `user`, `listing`, `check_in`, `check_out`, `guests`, `booking_status`, `created_at`
- Method: `total_price()`: Calculates nights \* price per night

### `Review`
- Fields: `user`, `listing`, `rating`, `comment`, `created_at`
- Constraints: Only 1 review per user-listing combination

---

## 🔧 API Endpoints

| Resource    | Endpoint                     | Method | Description                              | Auth Required |
|-------------|------------------------------|--------|------------------------------------------|---------------|
| Listings    | `/listings/`                 | GET    | List all listings                        | No            |
|             | `/listings/`                 | POST   | Create a new listing                     | ✅ Yes        |
|             | `/listings/<id>/`            | GET    | Retrieve a listing                       | No            |
|             | `/listings/<id>/`            | PUT    | Update a listing                         | ✅ Yes        |
|             | `/listings/<id>/`            | DELETE | Delete a listing                         | ✅ Yes        |
| Bookings    | `/bookings/`                 | GET    | List user bookings                       | ✅ Yes        |
|             | `/bookings/`                 | POST   | Create a new booking                     | ✅ Yes        |
|             | `/bookings/<id>/`            | PUT    | Update a booking                         | ✅ Yes        |
|             | `/bookings/<id>/`            | DELETE | Delete a booking                         | ✅ Yes        |

---

## 📜 Serializers

### `ListingSerializer`
- Excludes `host`, `created_at` from being editable

### `BookingSerializer`
- Adds computed `total_price` using `get_total_price()`
- Read-only fields: `user`, `created_at`, `total_price`

---

## 👨‍💻 Views Summary

### `ListingViewSet`
- Lists and manages all listings
- Uses `ModelViewSet` with a full queryset

### `BookingViewSet`
- Filters bookings by current user
- Read/write access is scoped per user
- Supports `total_price` calculation

---

## 🧪 Seed Command

Command path: `listings/management/commands/seed_data.py`

### Seed Logic:
- Deletes existing data (non-superusers)
- Creates 10 users, 200 listings, 50 bookings
- Randomly adds reviews for confirmed bookings


