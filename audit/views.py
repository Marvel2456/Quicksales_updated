from django.shortcuts import render
from .models import History
from django.core.paginator import Paginator

# Create your views here.

def historyPage(request):
    history = History.objects.all()
    # paginator = Paginator(History.objects.all(), 20)
    # page = request.GET.get('page')
    # history_page = paginator.get_page(page)
    # nums = "a" *history_page.paginator.num_pages
    
    context = {
        'history': history,
        # 'history_page': history_page,
        # 'nums': nums,
    }
    
    return render(request, 'history/his.html', context)