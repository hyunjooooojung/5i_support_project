import support_data
from support_data.machine import transform_image
from support_data.machine import rectangle_image
from .models  import Support
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F

# Create your views here.
def home(request):
    user = request.user.is_authenticated
    if user:
        # my_images = Support.objects.all().order_by('-id')
        my_images = Support.objects.filter(input_num=F("people_num"))
        return render(request, 'support_data/home.html', {'my_images':my_images})
    else:
        return redirect('/login')
     

def upload(request):
    if request.method == 'GET':
        return render(request, 'support_data/upload.html')
    if request.method == 'POST':
        image = request.FILES.get('image','')
        write_image = request.FILES.get('image','')
        team_name = request.user
        input_num = request.POST.get('input_num','')
        my_image = Support.objects.create(image=image,write_image=write_image, team_name=team_name,input_num=input_num)
        my_image.save()
        # 머신러닝 코드 불러오기
        my_image.people_num = transform_image(my_image.image.url)
        rectangle_image(my_image.image.url,my_image.write_image.url)
        my_image.save()
        if int(input_num) == my_image.people_num:
            return redirect(f'/result/{my_image.id}/')
        else:
            
            return redirect(f'/error/{my_image.id}/',{'error':'인원 수가 일치하지 않습니다'})

def error(request, id):
    if request.method == 'GET':
        my_image = Support.objects.get(id=id)
        return render(request, 'support_data/error.html', {'my_image':my_image})


def result(request, id):
    if request.method == 'GET':
        # 업로드 페이지에서 저장한 내용들을 모두 받아와준다.
        my_image = Support.objects.get(id=id)
        return render(request, 'support_data/result.html', {'my_image':my_image})
    
    
def my_result(request): 
    if request.method == 'GET':
        all_image = Support.objects.all()
        my_image = all_image.filter(team_name=request.user)
        # 일치하는 이미지만 보여주는 코드
        true_image = my_image.filter(input_num=F("people_num"))
        # 오류난 이미지만 보여주는 코드
        false_image = my_image.exclude(input_num=F("people_num"))
    return render(request, 'support_data/my_result.html', {'my_image':my_image, 'true_image':true_image, 'false_image':false_image})


def team_result(request):
    if request.method == 'GET':
        all_image = Support.objects.all()
        my_image = all_image.filter(team_name__team_name=request.user.team_name)
        true_image = my_image.filter(input_num=F("people_num"))
    return render(request, 'support_data/team_result.html', {'my_image':my_image, 'true_image':true_image})
    
    
@login_required    
def approval_list(request):
    if request.method == 'GET':
        approval_list = Support.objects.all()
        return render(request, 'support_data/approval.html', {'approval_list': approval_list})

@login_required
def approval(request, id):
    me = request.user
    click_approval = Support.objects.get(id=id)
    click_approval.is_approval=not click_approval.is_approval
    click_approval.save()
    return redirect('/approval')

@login_required    
def objection_list(request):
    if request.method == 'GET':
        objection_list = Support.objects.all()
        return render(request, 'support_data/objection_list.html', {'objection_list': objection_list})
    
def objection(request):
    if request.method == 'GET':
        return render (request, 'support_data/objection.html')

    elif request.method == 'POST':
        team_name = request.user
        content = request.POST.get("content")
        #image = request.FILES.get("image")
        Support.objects.create(content=content, team_name=team_name)
        return redirect('/')   


def delete_image(request,id):
    my_image = Support.objects.get(id=id)
    my_image.delete()
    return redirect('/')

def my_objection(request, id):
    if request.method == 'GET':
        my_image = Support.objects.get(id=id)
        return render(request, 'support_data/my_objection.html', {'my_image':my_image})        