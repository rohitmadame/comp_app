from django.shortcuts import render, redirect, get_object_or_404  # Moved get_object_or_404 here
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Complaint, ComplaintImage
from django.views.decorators.http import require_http_methods, require_POST  # Added require_POST
from django.http import JsonResponse, HttpResponse

def home(request):
    return HttpResponse("Hello, World!")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        return render(request, 'user_login.html', {'error': 'Invalid credentials'})
    return render(request, 'user_login.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'user_register.html', {'error': 'Username exists'})
        User.objects.create_user(username=username, password=password)
        return redirect('user_login')
    return render(request, 'user_register.html')

@login_required
def user_dashboard(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'user_dashboard.html', {'complaints': complaints})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    
    complaints = Complaint.objects.select_related('user').all().order_by('-created_at')
    status_counts = {
        'pending': Complaint.objects.filter(status='pending').count(),
        'in_progress': Complaint.objects.filter(status='in_progress').count(),
        'resolved': Complaint.objects.filter(status='resolved').count(),
    }
    
    return render(request, 'admin_dashboard.html', {
        'complaints': complaints,
        'status_counts': status_counts,
        'total_complaints': sum(status_counts.values())
    })

@login_required
def add_complaint(request):
    if request.method == 'POST':
        complaint = Complaint.objects.create(
            user=request.user,
            complaint_type=request.POST.get('complaint_type'),
            city=request.POST.get('city'),
            ward_number=request.POST.get('ward_number'),
            description=request.POST.get('description')
        )
        for file in request.FILES.getlist('images'):
            ComplaintImage.objects.create(complaint=complaint, image=file)
        return redirect('user_dashboard')
    return render(request, 'add_complaint.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        return render(request, 'admin_login.html', {'error': 'Invalid admin credentials'})
    return render(request, 'admin_login.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
def complaint_detail(request, complaint_id):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    
    complaint = get_object_or_404(Complaint, id=complaint_id)
    return render(request, 'complaint_detail.html', {
        'complaint': complaint,
        'images': complaint.images.all()
    })

@login_required
@require_POST  # Now properly imported
def update_status(request, complaint_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        new_status = request.POST.get('status')
        
        if new_status not in dict(Complaint.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
            
        complaint.status = new_status
        complaint.save()
        
        return JsonResponse({
            'success': True,
            'new_status': complaint.get_status_display(),
            'status_class': {
                'pending': 'bg-warning',
                'in_progress': 'bg-primary',
                'resolved': 'bg-success'
            }[new_status]
        })
        
    except Complaint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Complaint not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)