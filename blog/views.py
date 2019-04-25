import markdown
from django.shortcuts import render, get_object_or_404
from comments.forms import CommentForm
from .models import Post, Category


def index(request):
    posts = Post.objects.all()
    return render(request, 'blog/index.html', {'posts': posts})


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 阅读量+1
    post.increase_views()
    # 记得在顶部引入markdown模块
    post.body = markdown.markdown(post.body, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc'
    ])
    form = CommentForm()
    # 获取这篇post下的全部评论
    comment_list = post.comment_set.all()

    return render(request, 'blog/detail.html', {'post': post, 'form': form, 'comment_list': comment_list})


# 日期分类归档
def archives(request, year, month):
    posts = Post.objects.filter(
        created_time__year=year,
        created_time__month=month,
    )
    return render(request, 'blog/index.html', {'posts': posts})


# 分类查找
def category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = Post.objects.filter(category=category)
    return render(request, 'blog/index.html', {'posts': posts})
