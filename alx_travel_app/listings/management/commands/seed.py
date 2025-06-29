from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
from faker import Faker
import random
from datetime import timedelta

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with fake Listings, Bookings, and Reviews.'

    def handle(self, *args, **kwargs):
        NUM_USERS = 10
        NUM_LISTINGS = 200
        NUM_BOOKINGS = 50
        REVIEW_CHANCE = 0.5  # 50% chance of leaving a review for confirmed bookings

        self.stdout.write(self.style.WARNING('🔄 Clearing existing data...'))
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.WARNING('👤 Seeding users...'))
        users = [
            User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='test1234'
            )
            for _ in range(NUM_USERS)
        ]

        self.stdout.write(self.style.WARNING('🏘️ Seeding listings...'))
        listings = [
            Listing.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                price_per_night=round(random.uniform(30, 500), 2),
                host=random.choice(users)
            )
            for _ in range(NUM_LISTINGS)
        ]

        self.stdout.write(self.style.WARNING('📅 Seeding bookings...'))
        bookings = []
        for _ in range(NUM_BOOKINGS):
            user = random.choice(users)
            listing = random.choice(listings)

            # Ensure user isn't booking their own listing
            while listing.host == user:
                listing = random.choice(listings)

            check_in = fake.date_between(start_date='-6M', end_date='today')
            check_out = check_in + timedelta(days=random.randint(1, 7))

            booking = Booking.objects.create(
                user=user,
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                guests=random.randint(1, 4),
                booking_status=random.choice(['pending', 'confirmed', 'cancelled'])
            )
            bookings.append(booking)

        self.stdout.write(self.style.WARNING('📝 Seeding reviews (only confirmed bookings)...'))
        review_count = 0
        for booking in bookings:
            if booking.booking_status == 'confirmed' and random.random() < REVIEW_CHANCE:
                # Ensure one review per user-listing pair
                if not Review.objects.filter(user=booking.user, listing=booking.listing).exists():
                    Review.objects.create(
                        user=booking.user,
                        listing=booking.listing,
                        rating=random.randint(1, 5),
                        comment=fake.sentence(nb_words=12)
                    )
                    review_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded:\n'
            f'👤 Users: {NUM_USERS}\n'
            f'🏘️ Listings: {NUM_LISTINGS}\n'
            f'📅 Bookings: {NUM_BOOKINGS}\n'
            f'📝 Reviews: {review_count}'
        ))
