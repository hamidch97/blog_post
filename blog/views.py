from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector , SearchQuery , SearchRank
from blog.forms import EmailPostForm, CommentForm , SearchForm
from blog.models import Posts, Comment


def post_list(request, tag_slug=None):
    post_list = Posts.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    try:
        post = paginator.page(page_number)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)

    return render(request, 'blogs/post_list.html', {'post': post, 'tag': tag})


def detail_post(request, year, month, day, post):
    post = get_object_or_404(Posts, status=Posts.Status.PUBLISHED,
                             slug=post, publish__year=year, 
                             publish__month=month, 
                             publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()

    # similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Posts.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blogs/detail_post.html', {
                                                        'post': post, 
                                                        'comments': comments, 
                                                        'form': form, 
                                                        'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Posts, id=post_id, status=Posts.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read"\
                f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
                      f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'hamid.chayeb97@gmail.com', [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blogs/email/share.html', {'post': post,
                                                        'form': form,
                                                        'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Posts, id=post_id, status=Posts.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blogs/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_victor = SearchVector('title','body')
            search_query = SearchQuery(query)
            results = Posts.published.annotate(
                search = search_victor , rank=SearchRank(search_victor,search_query)
            ).filter(search=search_query).order_by('-rank')
    return render(request ,'blogs/search.html',{'form':form,'query':query, 'results':results} )