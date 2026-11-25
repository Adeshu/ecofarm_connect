"""
create_sample_data_final.py
Run with:  python manage.py shell < create_sample_data_final.py
"""

import uuid
import random
from datetime import datetime
from django.utils.text import slugify

from django.utils import timezone

from accounts.models import User
from courses.models import Course, CourseCategory
from farms.models import Farm
from gamification.models import Badge

print("Creating extensive sample data…")

# -------------------- USERS -------------------- #
users_data = [
    # phone, first, last, state, district, village, points, level, joined
    ("1234567890", "Alice",    "Smith",      "California",   "District A",  "Village X",  1200, 5, "2025-09-26"),
    ("1234567891", "Bob",      "Johnson",    "Texas",        "District B",  "Village Y",   950, 4, "2025-09-20"),
    ("1234567892", "Carol",    "Williams",   "Florida",      "District C",  "Village Z",   700, 3, "2025-09-18"),
    ("1234567893", "David",    "Brown",      "Nevada",       "District D",  "Village W",   450, 2, "2025-09-15"),
    ("1234567894", "Eva",      "Davis",      "Oregon",       "District E",  "Village V",   800, 4, "2025-09-12"),
    ("1234567895", "Frank",    "Miller",     "Washington",   "District F",  "Village U",   650, 3, "2025-09-10"),
    ("1234567896", "Grace",    "Wilson",     "Colorado",     "District G",  "Village T",  1100, 5, "2025-09-08"),
    ("1234567897", "Henry",    "Moore",      "Arizona",      "District H",  "Village S",   520, 2, "2025-09-05"),
    ("1234567898", "Ivy",      "Taylor",     "Montana",      "District I",  "Village R",   370, 2, "2025-09-03"),
    ("1234567899", "Jack",     "Anderson",   "Idaho",        "District J",  "Village Q",   890, 4, "2025-09-01"),
    ("1234567800", "Kate",     "Thomas",     "Utah",         "District K",  "Village P",  1350, 5, "2025-08-28"),
    ("1234567801", "Luke",     "Jackson",    "New Mexico",   "District L",  "Village O",   280, 1, "2025-08-25"),
    ("1234567802", "Maya",     "White",      "Wyoming",      "District M",  "Village N",   740, 3, "2025-08-22"),
]

created_users = []
for phone, first, last, state, district, village, pts, lvl, joined in users_data:
    user, created = User.objects.get_or_create(
        phone=phone,
        defaults={
            "first_name": first,
            "last_name": last,
            "state": state,
            "district": district,
            "village": village,
            "total_points": pts,
            "level": lvl,
            "date_joined": timezone.make_aware(datetime.fromisoformat(joined)),
            "is_verified": True,
            "is_active": True,
        },
    )
    if created:
        user.set_password("password123")
        user.save()
        print(f"  ✔ Created user: {first} {last}")
    else:
        print(f"  • User already exists: {first} {last}")
    created_users.append(user)

# -------------------- COURSE CATEGORIES -------------------- #
categories_data = [
    ("Sustainable Farming", "Basic sustainable farming techniques"),
    ("Crop Management", "Advanced crop management strategies"),
    ("Soil & Water", "Soil health and water conservation"),
    ("Technology", "Modern farming technology and tools"),
    ("Business", "Farm business and marketing"),
]

created_categories = []
for name, desc in categories_data:
    try:
        category, created = CourseCategory.objects.get_or_create(
            name=name, 
            defaults={"description": desc}
        )
        print(f"  {'✔' if created else '•'} Category: {name}")
        created_categories.append(category)
    except Exception as e:
        print(f"  ✗ Error creating category '{name}': {e}")

# -------------------- COURSES -------------------- #
courses_data = [
    ("Organic Farming Basics", "Learn the fundamentals of organic farming techniques."),
    ("Advanced Water Conservation", "Explore advanced methods of water conservation in agriculture."),
    ("Soil Health Management", "Understand soil composition and health improvement strategies."),
    ("Integrated Pest Management", "Sustainable approaches to managing agricultural pests."),
    ("Crop Rotation Techniques", "Maximize soil fertility through strategic crop rotation."),
    ("Sustainable Livestock Management", "Best practices for raising healthy animals sustainably."),
    ("Greenhouse Management", "Optimize controlled environment agriculture techniques."),
    ("Permaculture Design Principles", "Create sustainable agricultural ecosystems."),
    ("Composting and Fertilization", "Natural methods to enrich soil fertility."),
    ("Seed Saving and Plant Breeding", "Preserve genetic diversity and improve crop varieties."),
    ("Farm Business Management", "Financial planning and marketing for sustainable farms."),
    ("Climate-Smart Agriculture", "Adapt farming practices to climate change challenges."),
    ("Organic Certification Process", "Navigate the requirements for organic certification."),
    ("Renewable Energy on Farms", "Implement solar, wind, and biogas systems on farms."),
    ("Food Safety and Processing", "Ensure safe handling from farm to table."),
]
print("\nCreating courses with detailed debug info...")

for title, desc in courses_data:
    try:
        if created_categories and created_users:
            category = random.choice(created_categories)
            created_by = random.choice(created_users)
            slug = slugify(title)
            course = None
            try:
                course = Course.objects.get(slug=slug)
                print(f"  • Course already exists (slug): {course.title}")
            except Course.DoesNotExist:
                course = Course.objects.create(
                    title=title,
                    description=desc,
                    category=category,
                    duration_hours=random.randint(10, 40),
                    created_by=created_by,
                    slug=slug,
                )
                print(f"  ✔ Created course: {title}")
        else:
            print(f"  ✗ Skipping course '{title}': No categories/users available")
    except Exception as e:
        print(f"  ✗ Error creating course '{title}': {e}")

# -------------------- BADGES -------------------- #
badges_data = [
    ("Green Novice", "Started your sustainable farming journey", "fas fa-seedling", 0),
    ("Water Guardian", "Completed water conservation training", "fas fa-tint", 100),
    ("Soil Scientist", "Mastered soil health management", "fas fa-microscope", 200),
    ("Pest Control Expert", "Learned integrated pest management", "fas fa-bug", 300),
    ("Crop Rotation Master", "Implemented advanced rotation strategies", "fas fa-sync-alt", 400),
    ("Organic Champion", "Achieved organic certification knowledge", "fas fa-leaf", 500),
    ("Climate Warrior", "Adapted to climate-smart practices", "fas fa-globe-americas", 600),
    ("Energy Saver", "Implemented renewable energy solutions", "fas fa-solar-panel", 700),
    ("Business Guru", "Mastered farm business management", "fas fa-chart-line", 800),
    ("Food Safety Expert", "Ensured safe food handling practices", "fas fa-shield-alt", 900),
    ("Innovation Leader", "Pioneered new farming technologies", "fas fa-lightbulb", 1000),
    ("Sustainable Legend", "Achieved mastery in all areas", "fas fa-crown", 1500),
]

for name, desc, icon, points in badges_data:
    try:
        badge, created = Badge.objects.get_or_create(
            name=name,
            defaults={
                "description": desc,
                "icon": icon,
                "points_required": points,
                "is_active": True,
            }
        )
        print(f"  {'✔' if created else '•'} Badge: {name}")
    except Exception as e:
        print(f"  ✗ Error creating badge '{name}': {e}")

# -------------------- FARMS -------------------- #
farms_data = [
    ("Green Valley Organic",      "Valley Town",     "Community farm focusing on sustainable practices."),
    ("Sunny Meadows Organic",     "Meadow City",     "Diversified farm growing organic produce."),
    ("Eco Springs Farm",          "Springfield",     "Utilizes eco-friendly methods for sustainable farming."),
    ("Desert Bloom Farm",         "Desert Ridge",    "Growing crops adapted to arid environments."),
    ("Oregon Hills Farm",         "Hilltop",         "Focusing on organic vegetables and fruits."),
    ("Mountain View Ranch",       "High Ridge",      "High-altitude sustainable farming operations."),
    ("Prairie Wind Farm",         "Windy Plains",    "Large-scale organic grain and vegetable production."),
    ("Riverside Organic Gardens", "River Bend",      "Water-efficient farming along the river."),
    ("Sunset Acres",              "Golden Valley",   "Family farm specializing in heirloom varieties."),
    ("Arctic Green Farm",         "Frozen Lake",     "Cold-climate farming innovations."),
    ("Tropical Paradise Farm",    "Coconut Grove",   "Year-round tropical crop production."),
    ("Maple Ridge Farm",          "Sugar Hill",      "Sustainable maple syrup and vegetable production."),
    ("Coastal Breeze Farm",       "Seashore",        "Salt-tolerant crops and aquaponics."),
    ("Pine Forest Farm",          "Evergreen Valley", "Forest farming and mushroom cultivation."),
    ("Heritage Seed Farm",        "Old Town",        "Preserving heirloom seed varieties."),
    ("Innovation Hub Farm",       "Tech Valley",     "Smart farming technology showcase."),
    ("Community Cooperative",     "Unity Square",    "Shared farming resources and knowledge."),
    ("Butterfly Meadow Farm",     "Flower Fields",   "Pollinator-friendly farming practices."),
    ("Windmill Farm",             "Breezy Heights",  "Wind-powered sustainable agriculture."),
    ("Solar Fields Farm",         "Sunny Acres",     "Solar-powered greenhouse operations."),
]

for i, (name, location, desc) in enumerate(farms_data):
    try:
        owner = created_users[i % len(created_users)]
        farm, created = Farm.objects.get_or_create(
            name=name,
            defaults={
                "location": location,
                "description": desc,
                "owner": owner,
                "created_at": timezone.now(),
            },
        )
        print(f"  {'✔' if created else '•'} Farm: {name} (Owner: {owner.get_full_name()})")
    except Exception as e:
        print(f"  ✗ Error creating farm '{name}': {e}")

print("\nSample data creation complete!")
print(f"Created: {len(users_data)} users, {len(courses_data)} courses, {len(badges_data)} badges, {len(farms_data)} farms")
