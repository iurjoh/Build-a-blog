from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Post, Contact
from .forms import CommentForm, PostForm, ContactForm
from django.utils.text import slugify


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("created_on")
    template_name = "index.html"
    paginate_by = 6


class PostDetail(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )


class PostLike(View):

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class PostShare(View):

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.shares.filter(id=request.user.id).exists():
            post.shares.remove(request.user)
        else:
            post.shares.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))

class PostEdit(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        form = PostForm(instance=post)
        return render(request, "post_edit.html", {"post": post, "form": form})

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # Check if the featured_image field has a new value
            if 'featured_image' in request.FILES:
                post.featured_image = request.FILES['featured_image']
            form.save()
            messages.success(request, "Post edited successfully.")
        else:
            messages.error(request, "Error editing post.")

        return redirect("post_detail", slug=slug)


class PostDelete(View):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('home')


class PostCreate(View):
    def get(self, request, *args, **kwargs):
        form = PostForm(user=request.user)  # Pass the user to the form
        return render(request, "post_create.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES, user=request.user)  # Pass the user to the form
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)  # Generate the slug based on the title
            post.status = 1  # Set status to Published

            post.save()
            messages.success(request, "Post created successfully.")
            return redirect(reverse('post_detail', args=[post.slug]))
        else:
            messages.error(request, "Error creating post.")

        return render(request, "post_create.html", {"form": form})


class PostContact(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'post_contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            # Save form data as a Contact instance
            contact = form.save()  # The name field will be pre-filled with the logged-in user's name

            # Perform other actions (e.g., sending email)

            messages.success(request, 'Your message has been sent successfully.')
            return redirect('home')

        return redirect('home')
