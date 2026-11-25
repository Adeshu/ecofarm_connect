# Quick Installation Guide

## Step 1: Copy Files
Extract and copy all files maintaining directory structure to your Django project.

## Step 2: Update Settings
```python
INSTALLED_APPS = [
    # ... existing apps
    'accounts',
    'core', 
    'quests',
    'farms',
    'gamification',
    'courses',
]

AUTH_USER_MODEL = 'accounts.User'
```

## Step 3: Migrate Database
```bash
python manage.py makemigrations accounts quests farms gamification courses core
python manage.py migrate
```

## Step 4: Create Superuser
```bash
python manage.py createsuperuser
```

## Step 5: Load Sample Data
```bash
python manage.py shell
exec(open('complete_sample_data.py').read())
exit()
```

## Step 6: Run Server
```bash
python manage.py runserver
```

## Step 7: Test Login
- URL: http://127.0.0.1:8000/
- Test user: 9876543210 / farming123

## Ready! 🎉

Your complete sustainable farming platform is now running with:
- ✅ User authentication
- ✅ Quest system
- ✅ Farm management
- ✅ Gamification (points, badges, leaderboard)
- ✅ Course system
- ✅ Complete admin panel
- ✅ Sample data loaded

Visit `/dashboard/` after login to see all features in action!
