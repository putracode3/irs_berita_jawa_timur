from django.shortcuts import render, get_object_or_404
from .models import Post
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def post_list(request):
  # postlist = Post.objects.filter(draft=False)
  # return render(request, 'post_list.html', {'postlist': postlist})

  queryset_list = Post.objects.all().order_by('-timestamp')  # .order_by("-timestamp")

  query = request.GET.get("q")
  paginator = Paginator(queryset_list, 1)  # Show 4 contacts per page
  page_request_var = "page"
  page = request.GET.get(page_request_var)
  try:
    queryset = paginator.page(page)
  except PageNotAnInteger:
    # If page is not an integer, deliver first page.
    queryset = paginator.page(1)
  except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
    queryset = paginator.page(paginator.num_pages)

  context = {
    'object_list': queryset,
    'title': 'List',
    'page_request_var': page_request_var,
  }

  return render(request, 'post_list.html', context)

def post_detail(request, slug):
  post = get_object_or_404(Post, slug=slug, draft=False)
  return render(request, 'post_detail.html', {'post':post})
