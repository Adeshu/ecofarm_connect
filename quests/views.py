from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from .models import QuestCategory, Quest, QuestCompletion, QuestStep, QuestStepCompletion
from .forms import QuestStepCompletionForm
from gamification.models import Achievement, PointsHistory, UserBadge, Badge
def _finalize_quest_completion(request, completion):
    """Finalize quest completion and handle rewards."""
    if completion.is_completed:
        return None

    quest = completion.quest

    completion.is_completed = True
    completion.completed_at = timezone.now()
    completion.points_earned = quest.points_reward
    completion.save()

    request.user.total_points += quest.points_reward
    request.user.update_level()
    request.user.save()

    Achievement.objects.create(
        user=request.user,
        title=f'Quest Completed: {quest.title}',
        description=f'Successfully completed the quest "{quest.title}"',
        points_earned=quest.points_reward,
        related_object_id=str(quest.id),
        related_object_type='quest'
    )

    PointsHistory.objects.create(
        user=request.user,
        points_change=quest.points_reward,
        point_type='quest_completion',
        description=f'Completed quest: {quest.title}',
        related_object_id=str(quest.id),
        related_object_type='quest'
    )

    badges = Badge.objects.filter(
        points_required__lte=request.user.total_points,
        is_active=True
    ).exclude(user_badges__user=request.user)

    new_badges = []
    for badge in badges:
        user_badge, badge_created = UserBadge.objects.get_or_create(user=request.user, badge=badge)
        if badge_created:
            new_badges.append(badge.name)

    return {
        'points_earned': quest.points_reward,
        'total_points': request.user.total_points,
        'level': request.user.level,
        'new_badges': new_badges,
    }


def quest_list(request):
    """List all active quests"""
    quests = Quest.objects.filter(is_active=True, status='active').select_related('category')
    categories = QuestCategory.objects.all()

    # Get user's completed quests
    completed_quest_ids = []
    if request.user.is_authenticated:
        completed_quest_ids = QuestCompletion.objects.filter(
            user=request.user, is_completed=True
        ).values_list('quest_id', flat=True)

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        quests = quests.filter(category_id=category_id)

    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        quests = quests.filter(difficulty=difficulty)

    # Search
    search = request.GET.get('search')
    if search:
        quests = quests.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Pagination
    paginator = Paginator(quests, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_difficulty': difficulty,
        'search_query': search,
        'difficulty_choices': Quest.DIFFICULTY_CHOICES,
        'completed_quest_ids': completed_quest_ids,
    }
    return render(request, 'quests/quest_list.html', context)


def quest_detail(request, quest_id):
    """Quest detail view with step progress tracking"""
    quest = get_object_or_404(Quest, id=quest_id, is_active=True, status='active')
    steps = quest.steps.all().order_by('order')

    completion = None
    is_completed = False
    user_step_completions = {}
    progress_percentage = 0

    if request.user.is_authenticated:
        try:
            completion = QuestCompletion.objects.get(user=request.user, quest=quest)
            is_completed = completion.is_completed
            
            # Get user's step completions
            step_completions = QuestStepCompletion.objects.filter(completion=completion).select_related('step')
            user_step_completions = {sc.step_id: sc for sc in step_completions}
            
            # Calculate progress percentage
            total_steps = steps.count()
            completed_steps = len(user_step_completions)
            if total_steps > 0:
                progress_percentage = int((completed_steps / total_steps) * 100)
            
            # Safety check: If all steps are completed but quest isn't marked complete, finalize it
            if not is_completed and total_steps > 0 and completed_steps == total_steps:
                _finalize_quest_completion(request, completion)
                completion.refresh_from_db()
                is_completed = completion.is_completed
                
        except QuestCompletion.DoesNotExist:
            completion = None

    context = {
        'quest': quest,
        'steps': steps,
        'user_step_completions': user_step_completions,
        'completion': completion,
        'is_completed': is_completed,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'quests/quest_detail.html', context)


@login_required
def complete_quest_step(request, quest_id, step_id):
    """Complete an individual quest step"""
    completion, _ = QuestCompletion.objects.get_or_create(user=request.user, quest_id=quest_id)
    step = get_object_or_404(QuestStep, id=step_id, quest_id=quest_id)

    # Check if already completed
    try:
        step_completion = QuestStepCompletion.objects.get(completion=completion, step=step)
        messages.info(request, "Step already completed.")
        return redirect('quests:quest_detail', quest_id=quest_id)
    except QuestStepCompletion.DoesNotExist:
        step_completion = None

    if request.method == 'POST':
        form = QuestStepCompletionForm(request.POST, request.FILES)
        if form.is_valid():
            new_completion = form.save(commit=False)
            new_completion.completion = completion
            new_completion.step = step
            new_completion.save()

            total_steps = step.quest.steps.count()
            completed_steps = QuestStepCompletion.objects.filter(completion=completion).count()

            if total_steps and completed_steps == total_steps:
                # Refresh completion object to ensure we have latest state
                completion.refresh_from_db()
                finalize_result = _finalize_quest_completion(request, completion)
                success_message = f'Step "{step.title}" marked completed.'
                if finalize_result is not None:
                    success_message = (
                        f'Quest "{step.quest.title}" completed! You earned {step.quest.points_reward} points.'
                    )
                    new_badges = finalize_result.get('new_badges')
                    if new_badges:
                        success_message += f' New badges earned: {", ".join(new_badges)}.'
                    # Refresh completion after finalizing to get updated state
                    completion.refresh_from_db()
                messages.success(request, success_message)
            else:
                messages.success(request, f'Step "{step.title}" marked completed.')
            return redirect('quests:quest_detail', quest_id=quest_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = QuestStepCompletionForm()

    context = {
        'form': form,
        'step': step,
        'quest_id': quest_id,
    }
    return render(request, 'quests/step_complete_form.html', context)


@login_required
def complete_quest(request, quest_id):
    """Complete an entire quest"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    quest = get_object_or_404(Quest, id=quest_id, is_active=True, status='active')

    # Get or create completion
    completion, created = QuestCompletion.objects.get_or_create(
        user=request.user,
        quest=quest,
        defaults={'points_earned': quest.points_reward}
    )

    if completion.is_completed:
        return JsonResponse({'error': 'Quest already completed'}, status=400)

    finalize_result = _finalize_quest_completion(request, completion)

    if finalize_result is None:
        return JsonResponse({'error': 'Quest already completed'}, status=400)

    response_data = {
        'success': True,
        'points_earned': finalize_result['points_earned'],
        'total_points': finalize_result['total_points'],
        'level': finalize_result['level'],
        'message': f'Quest completed! You earned {quest.points_reward} points!'
    }

    new_badges = finalize_result.get('new_badges')
    if new_badges:
        response_data['new_badges'] = new_badges
        response_data['message'] += f' New badges earned: {", ".join(new_badges)}'

    return JsonResponse(response_data)


@login_required
def my_quests(request):
    """User's quest completions"""
    completions = QuestCompletion.objects.filter(user=request.user).select_related('quest')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'completed':
        completions = completions.filter(is_completed=True)
    elif status_filter == 'in_progress':
        completions = completions.filter(is_completed=False)

    context = {
        'completions': completions,
        'current_status': status_filter,
    }
    return render(request, 'quests/my_quests.html', context)
