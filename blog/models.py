import markdown
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import strip_tags


class Category(models.Model):
    """
    Django 要求模型必须继承models.Model类
    Category只需要一个简单的分类名name就可以了
    CharField 指定了分类名name的数据类型，CharField是字符型
    CharField的max_length参数指定基最大长度，超过这个长度的分类名就不能被存入数据库
    当然Django还为我们提供了多种其它的数据类型，如日期类型DateTimeField、整数类型IntegerField等等
    Django 内置的全部类型可查看文档：
    https://docs.djangoproject.com/en/1.10/ref/models/fields/#field-types
    """
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    标签Tag也比较简单，和Category一样
    再次强调一定要继承models.Model
    """
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    文章的数据库表稍微复杂一点，主要是涉及的字段更多
    """
    # 文章标题
    title = models.CharField(max_length=128)
    # 文章正文，我们使用TextField
    # 存储比较短的字符串可以使用CharField，但对于文章的正文来说可能会是一大段文本，因此使用TextField来存储大段文本
    body = models.TextField()
    # 这两个列分别表示文章的创建时间和最后一次修改时间，存储时间的字段用DateTimeField类型
    created_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    # 文章摘要，可以没有文章摘要，但默认情况下CharField要求我们必须存入数据，否则就会报错
    # 指定CharField的blank=True参数后就可以允许空值了
    excerpt = models.CharField(max_length=200, blank=True)
    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同
    # 我们规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是ForeignKey，即一对多的关联关系
    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以我们使作ManyToManyField，表明这是多对多的关联关系
    # 同时我们规定文章可以没有标签，因此为标签tags指定了blank=True.
    # 如果你对 ForeignKey、ManyToManyField 不了解，请看教程中的解释，亦可参考官方文档：
    # https://docs.djangoproject.com/en/1.10/topics/db/models/#relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    # 文章作者，这里User是从django.contrib.auth.models导入的。
    # django.contrib.auth是Django内置的应用，专门用于处理网站用户的注册，登录等流程，User是Django为我们已经写好的用户模型
    # 这里我们通过ForeignKey把文章和User关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个用者可能会写多篇文章，因此这是一对多的关联关系，和Category类似。
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 新增views字段用于记录阅读量
    views = models.PositiveIntegerField(default=0)

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    # 文章摘要
    def save(self,*args, **kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个Markdown类，用于渲染body的文本
            md = markdown.Markdown(
                extensions=[
                    'markdown.extensions.extra',
                    'markdown.extensions.codehilite',
                ]
            )
            # 先将Markdown文本渲染成HTML文本
            # strip_tags去掉Html文本的全部HTML标签
            # 从文本摘取前54个字符赋给excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]
        # 调用父类的save方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_time']
