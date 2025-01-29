from django.shortcuts import render
from django.contrib import messages
from django.db.models.functions import TruncMonth

from patch.models import PatchMessage
from patch.models import Comment
from .forms import CommentForm

# Create your views here.
def index(request):
    """
    Show patch index

    Defines view for https://url.tld/patch/

    :param request:
    :return: HttpResponse
    """
    patch_messages = PatchMessage.objects.all()

    return render(request=request,
                  context={
                      "patch_messages": patch_messages,
                  },
                  template_name="patch/index.html")

def view_patch_message(request, slug: str):
    """
    Show patch message

    Defines view for https://url.tld/patch/view/<int:pk>

    :param request:
    :param slug: the slug for the patch message
    :return: HttpResponse
    """
    patch_message = PatchMessage.objects.get(slug=slug)
    next_patch = PatchMessage.objects.filter(patch_date__gt=patch_message.patch_date).order_by("patch_date").first()
    prev_patch = PatchMessage.objects.filter(patch_date__lt=patch_message.patch_date).order_by("-patch_date").first()
    comments = Comment.objects.filter(patch_message=patch_message).filter(active=True)

    patches_this_year = PatchMessage.objects.filter(patch_year=patch_message.patch_year)
    patches_by_month = patches_this_year.annotate(month=TruncMonth('patch_date')).order_by("month")
    patches_by_month_dict = {}
    for patch in patches_by_month:
        month_key = patch.month.strftime('%B')  # For example, 'January 2025'
        if month_key not in patches_by_month_dict:
            patches_by_month_dict[month_key] = []
        patches_by_month_dict[month_key].append(patch)

    new_comment = None  # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.patch_message = patch_message

            new_comment.username = request.user

            # Save the comment to the database
            new_comment.save()
            messages.success(request, "Success! Your comment is awaiting moderation.")
        else:
            messages.error(request, "Your comment did not submit successfully.")
    else:
        comment_form = CommentForm()

    return render(request=request,
                  context={
                      "patch_message": patch_message,
                      "next_patch": next_patch,
                      "prev_patch": prev_patch,
                      "patches_by_month": patches_by_month_dict,
                      "comments": comments,
                      "new_comment": new_comment,
                      "comment_form": comment_form,
                  },
                  template_name="patch/view_patch_message.html")
