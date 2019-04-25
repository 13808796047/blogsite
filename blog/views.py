import markdown
from django.shortcuts import render, get_object_or_404
from comments.forms import CommentForm
from .models import Post, Category
from django.views.generic import ListView, DetailView


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'


# def index(request):
#     posts = Post.objects.all()
#     return render(request, 'blog/index.html', {'posts': posts})


# def detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     # 阅读量+1
#     post.increase_views()
#     # 记得在顶部引入markdown模块
#     post.body = markdown.markdown(post.body, extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         'markdown.extensions.toc'
#     ])
#     form = CommentForm()
#     # 获取这篇post下的全部评论
#     comment_list = post.comment_set.all()
#
#     return render(request, 'blog/detail.html', {'post': post, 'form': form, 'comment_list': comment_list})

# 类视图
class PostDetailView(DetailView):
    # 这些含义和ListView是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写get方法的目的是因为每当文章被访问一次，就得将文章的阅读量加1
        # get方法返回的是一个HttpResponse实例
        # 之所以需要先调用父类的get方法，是因为只有当get方法被调用后，
        # 才有self.object属性，其值为Post模型实例，即被访问的文章post
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        # 将文章阅读量+1
        # 注意self.object的值就是被访问的文章post
        self.object.increase_views()
        # 视图必须返回一个HttpResponse对象
        return response

    def get_object(self, queryset=None):
        # 覆写get_object方法的目的是因为需要对post的body值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
        return post

    def get_context_data(self, **kwargs):
        # 覆写get_context_data的目的是因为除了将post传递给模板外(DetailView已经帮我们完成)
        # 还要把评论表单、post下的评论列表传递给模板
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


# 日期分类归档
# def archives(request, year, month):
#     posts = Post.objects.filter(
#         created_time__year=year,
#         created_time__month=month,
#     )
#     return render(request, 'blog/index.html', {'posts': posts})
# 类视图
class ArchivesView(IndexView):
    def get_queryset(self):
        return super(ArchivesView, self).get_queryset().filter(
            created_time__year=self.kwargs.get('year'),
            created_time__month=self.kwargs.get('month'),
        )


# 分类查找
# def category(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     posts = Post.objects.filter(category=category)
#     return render(request, 'blog/index.html', {'posts': posts})
# 类视图
class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)
