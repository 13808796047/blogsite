import markdown
from django.shortcuts import render, get_object_or_404
from comments.forms import CommentForm
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.db.models import Q


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    # 指定paginate_by属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = settings.PAGE_NUM

    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过render函数的context参数传递一个字典实现的，
        例如 render(request,'blog/index.html',context={'posts':posts}),
        在类视图中，这个需要传递的模板变量字典是通过get_context_data获得的
        所以我们复写该方法，以便我们能够自已再插入一些我们自定义的模板变量进去
        :param kwargs:
        :return:
        """
        # 首先获得父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)
        # 父类生成的字典已有paginator,page_obj,ispaginated这本个模板变量
        # paginator是Paginator的一个实例
        # page_obj是Page的一个实例
        # is_paginated是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页10个数据，而本身只有5个数据，其实就用不着分页，此时is_paginated=False
        # 关于什么是 Paginator，Page 类在 Django Pagination 简单分页：http://zmrenwu.com/post/34/ 中已有详细说明。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        # 调用自己写的pagination_data方法获得显示分页导航条需要的数据，见下方
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        # 将分页导航条的模板变量更新到context中，注意pagination_data方法返回的也是一个字典。
        context.update(pagination_data)
        # 将更新后的context返回，以便ListView使用这个字典中的模板变量去渲染模板
        # 注意此时context字典中已有了显示分页导航条所需的数据
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}
        # # 当前页左边连续的页码号，初始值为空
        # left = []
        # # 当前页右边连续的页码号，初始值为空
        # right = []
        # # 标示第1页页码后是琐需要显示省略号
        # left_has_more = False
        # # 标示最后一页页码前是否需要显示省略号
        # right_has_more = False
        # # 标示是否需要显示第1页的页码号
        # # 因为如果当前页左路边的连续页码号中已经含有第1页的页码号，此时就无需再显示第1页的页码号，
        # # 基它情况下第一页的页码是始终需要显示的
        # first = False
        # # 标示是否需要显示最后一页的页码号
        # last = False
        # 获得用户当前请求的页码号
        page_number = page.number
        # 获得分页后的总页数
        # 获得整个分页页码列表，比如分了四页，那么就是[1,2,3,4]

        page_range = [x for x in range(int(page_number - 2), int(page_number) + 3) if 0 < x <= paginator.num_pages]
        # 加入省略页码
        if page_range[0] - 1 >= 2:
            page_range.insert(0, '...')
        if paginator.num_pages - page_range[-1] >= 2:
            page_range.append('...')
        # 加上首页，尾页
        if page_range[0] != 1:
            page_range.insert(0, 1)
        if page_range[-1] != paginator.num_pages:
            page_range.append(paginator.num_pages)
        data = {
            'page_range': page_range
        }
        #        if page_number == 1:
        #            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此left=[]
        #            # 此时只要获取当前页右边的连续页码号
        #            # 比如分页页码列表是[1,2,3,4],那么获得的就是right=[2,3]
        #            # 注意这里只获得了当前页码后连续两个页码，你可以更改这个数字以获取更多页码
        #            right = page_range[page_number:page_number + 2]
        #            # 如果最右边的页码号比最后一页的页码号减1还要小，
        #            # 说明最右边的页码号和最后一页的页码号之间还有其它页码因此需要显示省略号，通过right_has_more来指示
        #            if right[-1] < total_pages - 1:
        #                right_has_more = True
        #            # 如果最右边的页码号比最后一页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
        #            # 所以需要显示最后一页的页码号，通过last来指示
        #            if right[-1] < total_pages:
        #                last = True
        #        elif page_number == total_pages:
        #            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此right=[]
        #            # 此时只要获取当前页左边的连续页码号
        #            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
        #            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码
        #            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
        # # 如果最左边的页码号比第 2 页页码号还大，
        #            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
        #            if left[0] > 2:
        #                left_has_more = True
        #
        #            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
        #            # 所以需要显示第一页的页码号，通过 first 来指示
        #            if left[0] > 1:
        #                first = True
        #        else:
        #            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
        #            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
        #            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
        #            right = page_range[page_number:page_number + 2]
        #
        #            # 是否需要显示最后一页和最后一页前的省略号
        #            if right[-1] < total_pages - 1:
        #                right_has_more = True
        #            if right[-1] < total_pages:
        #                last = True
        #
        #            # 是否需要显示第 1 页和第 1 页后的省略号
        #            if left[0] > 2:
        #                left_has_more = True
        #            if left[0] > 1:
        #                first = True
        #
        #        data = {
        #            'left': left,
        #            'right': right,
        #            'left_has_more': left_has_more,
        #            'right_has_more': right_has_more,
        #            'first': first,
        #            'last': last,
        #        }

        return data


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
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify)
        ])
        post.body = md.convert(post.body)
        # 插入侧边文章目录
        post.toc = md.toc
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


# 标签云
class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


# 搜索
def search(request):
    q = request.GET.get('q')
    error_msg = ''
    if not q:
        error_msg = '请输入关键词'
        return render(request, 'blog/index.html', {'error_msg': error_msg})
    posts = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'error_msg': error_msg, 'posts': posts})
