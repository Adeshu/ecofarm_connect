import uuid
from gamification.models import Badge

def create_25_milestone_badges():
    badges = [
        # Quest Completion badges
        {'name': 'Quest Beginner', 'description': 'Complete your first quest.', 'icon': 'fas fa-flag', 'category': 'milestone', 'type': 'quest', 'points_required': 10, 'rarity': 'common', 'quest_id': 'quest_1'},
        {'name': 'Quest Explorer', 'description': 'Complete 5 quests.', 'icon': 'fas fa-map-marker-alt', 'category': 'milestone', 'type': 'quest', 'points_required': 50, 'rarity': 'uncommon', 'quest_id': 'quest_5'},
        {'name': 'Quest Conqueror', 'description': 'Complete 10 quests.', 'icon': 'fas fa-trophy', 'category': 'milestone', 'type': 'quest', 'points_required': 100, 'rarity': 'rare', 'quest_id': 'quest_10'},
        # Add more quest badges incrementally
        {'name': 'River Restoration Champion', 'description': 'Complete the River Restoration quest.', 'icon': 'fas fa-water', 'category': 'milestone', 'type': 'quest', 'points_required': 30, 'rarity': 'common', 'quest_id': 'river_restoration'},
        {'name': 'Soil Scientist', 'description': 'Complete the Soil Health Assessment quest.', 'icon': 'fas fa-leaf', 'category': 'milestone', 'type': 'quest', 'points_required': 40, 'rarity': 'uncommon', 'quest_id': 'soil_health_assessment'},
        {'name': 'Pest Control Expert', 'description': 'Complete the Integrated Pest Management quest.', 'icon': 'fas fa-bug', 'category': 'milestone', 'type': 'quest', 'points_required': 60, 'rarity': 'rare', 'quest_id': 'ipm'},

        # Course Completion badges
        {'name': 'Course Novice', 'description': 'Complete your first course.', 'icon': 'fas fa-book-open', 'category': 'milestone', 'type': 'course', 'points_required': 15, 'rarity': 'common', 'course_id': 'course_1'},
        {'name': 'Course Graduate', 'description': 'Complete 3 courses.', 'icon': 'fas fa-graduation-cap', 'category': 'milestone', 'type': 'course', 'points_required': 70, 'rarity': 'uncommon', 'course_id': 'course_3'},
        {'name': 'Course Master', 'description': 'Complete 5 courses.', 'icon': 'fas fa-award', 'category': 'milestone', 'type': 'course', 'points_required': 120, 'rarity': 'rare', 'course_id': 'course_5'},
        {'name': 'Organic Farming Expert', 'description': 'Complete Organic Farming course.', 'icon': 'fas fa-seedling', 'category': 'milestone', 'type': 'course', 'points_required': 50, 'rarity': 'uncommon', 'course_id': 'organic_farming'},
        {'name': 'Water Management Guru', 'description': 'Complete Water Management course.', 'icon': 'fas fa-water', 'category': 'milestone', 'type': 'course', 'points_required': 55, 'rarity': 'uncommon', 'course_id': 'water_management'},
        {'name': 'Sustainable Practices Leader', 'description': 'Complete Sustainable Practices course.', 'icon': 'fas fa-recycle', 'category': 'milestone', 'type': 'course', 'points_required': 70, 'rarity': 'rare', 'course_id': 'sustainable_practices'},

        # Mastery badges (perfect score)
        {'name': 'Master of Soil Health', 'description': 'Perfect score in Soil Health course.', 'icon': 'fas fa-medal', 'category': 'achievement', 'type': 'mastery', 'points_required': 100, 'rarity': 'epic', 'course_id': 'soil_health'},
        {'name': 'Master of Pest Management', 'description': 'Perfect score in Pest Management course.', 'icon': 'fas fa-bug', 'category': 'achievement', 'type': 'mastery', 'points_required': 110, 'rarity': 'epic', 'course_id': 'pest_management'},
        {'name': 'Master of Crop Rotation', 'description': 'Perfect score in Crop Rotation course.', 'icon': 'fas fa-seedling', 'category': 'achievement', 'type': 'mastery', 'points_required': 120, 'rarity': 'epic', 'course_id': 'crop_rotation'},

        # Learning streak badges
        {'name': 'Learning Streak 3 Days', 'description': '3 days learning streak.', 'icon': 'fas fa-fire', 'category': 'achievement', 'type': 'streak', 'points_required': 20, 'rarity': 'common', 'streak_days': 3},
        {'name': 'Learning Streak 7 Days', 'description': '7 days learning streak.', 'icon': 'fas fa-fire', 'category': 'achievement', 'type': 'streak', 'points_required': 40, 'rarity': 'uncommon', 'streak_days': 7},
        {'name': 'Learning Streak 14 Days', 'description': '14 days learning streak.', 'icon': 'fas fa-fire', 'category': 'achievement', 'type': 'streak', 'points_required': 70, 'rarity': 'rare', 'streak_days': 14},
        {'name': 'Learning Streak 30 Days', 'description': '30 days learning streak.', 'icon': 'fas fa-fire', 'category': 'achievement', 'type': 'streak', 'points_required': 120, 'rarity': 'epic', 'streak_days': 30},
        {'name': 'Learning Streak 60 Days', 'description': '60 days learning streak.', 'icon': 'fas fa-fire', 'category': 'achievement', 'type': 'streak', 'points_required': 160, 'rarity': 'legendary', 'streak_days': 60},

        # General achievement badges
        {'name': 'Eco Warrior', 'description': 'Contribute 10 community posts.', 'icon': 'fas fa-leaf', 'category': 'achievement', 'type': 'special', 'points_required': 50, 'rarity': 'uncommon'},
        {'name': 'Farm Innovator', 'description': 'Implement 5 sustainable farming techniques.', 'icon': 'fas fa-lightbulb', 'category': 'achievement', 'type': 'special', 'points_required': 60, 'rarity': 'rare'},
        {'name': 'Data Master', 'description': 'Complete 10 data collection activities.', 'icon': 'fas fa-chart-bar', 'category': 'achievement', 'type': 'special', 'points_required': 70, 'rarity': 'rare'},
        {'name': 'Green Leader', 'description': 'Lead a community event.', 'icon': 'fas fa-users', 'category': 'achievement', 'type': 'special', 'points_required': 80, 'rarity': 'epic'},
        {'name': 'Climate Champion', 'description': 'Reduce carbon footprint by 10% on farm.', 'icon': 'fas fa-globe', 'category': 'achievement', 'type': 'special', 'points_required': 90, 'rarity': 'epic'},
    ]

    import uuid
    from gamification.models import Badge

    for data in badges:
        Badge.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['description'],
                'icon': data['icon'],
                'color': data.get('color', '#20c997'),
                'points_required': data['points_required'],
                'category': data['category'],
                'type': data['type'],
                'quest_id': data.get('quest_id', None),
                'course_id': data.get('course_id', None),
                'streak_days': data.get('streak_days', None),
                'rarity': data['rarity'],
                'is_active': True
            }
        )
    print("25 milestone badges created successfully.")
