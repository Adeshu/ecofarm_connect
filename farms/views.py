from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Farm, Crop, FarmActivity
from .forms import FarmForm, CropForm, FarmActivityForm
from gamification.models import Achievement, PointsHistory


@login_required
def farm_list(request):
    farms = Farm.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'farms/farm_list.html', {'farms': farms})


@login_required
def farm_detail(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id)
    crops = farm.crops.all().order_by('-created_at')
    activities = farm.activities.all().order_by('-date_performed')[:10]

    total_crops = crops.count()
    active_crops = crops.filter(status__in=['planted', 'growing', 'flowering']).count()
    harvested_crops = crops.filter(status='harvested').count()
    total_area = crops.aggregate(total=Sum('area_planted'))['total'] or 0

    context = {
        'farm': farm,
        'crops': crops,
        'activities': activities,
        'total_crops': total_crops,
        'active_crops': active_crops,
        'harvested_crops': harvested_crops,
        'total_area': total_area,
    }
    return render(request, 'farms/farm_detail.html', context)


@login_required
def farm_create(request):
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()

            request.user.total_points += 25
            request.user.update_level()
            request.user.save()

            Achievement.objects.create(
                user=request.user,
                title=f'New Farm Created: {farm.name}',
                description=f'Successfully registered the farm "{farm.name}"',
                points_earned=25,
                related_object_id=str(farm.id),
                related_object_type='farm'
            )

            PointsHistory.objects.create(
                user=request.user,
                points_change=25,
                point_type='farm_activity',
                description=f'Created farm: {farm.name}',
                related_object_id=str(farm.id),
                related_object_type='farm'
            )

            messages.success(request, f'Farm "{farm.name}" created successfully! You earned 25 points!')
            return redirect('farms:farm_detail', farm_id=farm.id)
    else:
        form = FarmForm()
    return render(request, 'farms/farm_form.html', {'form': form, 'title': 'Create New Farm'})


@login_required
def farm_edit(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Farm updated successfully!')
            return redirect('farms:farm_detail', farm_id=farm.id)
    else:
        form = FarmForm(instance=farm)
    return render(request, 'farms/farm_form.html', {'form': form, 'farm': farm, 'title': 'Edit Farm'})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Farm, Crop
from .forms import CropForm
from gamification.models import PointsHistory

@login_required
def crop_create(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)

    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.farm = farm  # link crop to farm
            crop.save()

            # update user points and achievements
            request.user.total_points += 15
            request.user.update_level()
            request.user.save()

            PointsHistory.objects.create(
                user=request.user,
                points_change=15,
                point_type='farm_activity',
                description=f'Added crop: {crop.name} to {farm.name}',
                related_object_id=str(crop.id),
                related_object_type='crop'
            )

            messages.success(request, f'Crop "{crop.name}" added successfully! You earned 15 points!')
            return redirect('farms:farm_detail', farm_id=farm.id)

        else:
            messages.error(request, "Please correct the errors below.")
            # Optionally log errors for debugging
            print("Crop Form Errors:", form.errors)
    else:
        form = CropForm()

    context = {
        'form': form,
        'farm': farm,
        'title': f'Add Crop to {farm.name}'
    }
    return render(request, 'farms/crop_form.html', context)


@login_required
def crop_edit(request, farm_id, crop_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    crop = get_object_or_404(Crop, id=crop_id, farm=farm)
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Crop updated successfully!')
            return redirect('farms:farm_detail', farm_id=farm.id)
    else:
        form = CropForm(instance=crop)
    return render(request, 'farms/crop_form.html', {'form': form, 'farm': farm, 'crop': crop, 'title': f'Edit {crop.name}'})


@login_required
def activity_create(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id, owner=request.user)
    if request.method == 'POST':
        form = FarmActivityForm(request.POST, farm=farm)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.farm = farm
            activity.save()

            request.user.total_points += 10
            request.user.update_level()
            request.user.save()

            PointsHistory.objects.create(
                user=request.user,
                points_change=10,
                point_type='farm_activity',
                description=f'Logged activity: {activity.get_activity_type_display()}',
                related_object_id=str(activity.id),
                related_object_type='farm_activity'
            )

            messages.success(request, 'Activity logged successfully! You earned 10 points!')
            return redirect('farms:farm_detail', farm_id=farm.id)
    else:
        form = FarmActivityForm(farm=farm)
    return render(request, 'farms/activity_form.html', {'form': form, 'farm': farm, 'title': f'Log Activity for {farm.name}'})


def public_farms(request):
    farms = Farm.objects.all().select_related('owner').order_by('-created_at')

    search = request.GET.get('search')
    if search:
        farms = farms.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search) |
            Q(owner__first_name__icontains=search) |
            Q(owner__last_name__icontains=search)
        )

    state = request.GET.get('state')
    if state:
        farms = farms.filter(location__icontains=state)  # Filtering approximate by location field

    farm_type = request.GET.get('farm_type')
    if farm_type:
        farms = farms.filter(farm_type=farm_type)

    paginator = Paginator(farms, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'farms': page_obj,
        'search_query': search,
        'current_state': state,
        'current_type': farm_type,
    }
    return render(request, 'farms/public_farms.html', context)
