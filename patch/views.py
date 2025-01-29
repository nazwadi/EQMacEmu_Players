from django.shortcuts import render
from django.db import connection
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re
from django.contrib import messages
from django.db.models.functions import TruncMonth

from .models import PatchMessage
from .models import Comment
from datetime import datetime
from .forms import CommentForm


def highlight_text(text, search_terms):
    """Safely highlight search terms in text."""
    if not text or not search_terms:
        return text

    # Escape HTML first
    text = escape(text)

    # Split search query into terms and remove empty strings
    terms = [term.strip() for term in search_terms.split() if term.strip()]

    # Create a regular expression pattern that matches any of the terms (case insensitive)
    pattern = '|'.join(map(re.escape, terms))
    if pattern:
        # Wrap matched terms with highlight span
        highlighted = re.sub(
            f'({pattern})',
            r'<span class="search-highlight">\1</span>',
            text,
            flags=re.IGNORECASE
        )
        return mark_safe(highlighted)

    return text


def process_search_results(results, search_query):
    """Process and highlight search results."""
    processed_results = []

    for result in results:
        # Create a new dict with highlighted content
        processed_result = dict(result)

        # Highlight title and content
        processed_result['title_highlighted'] = highlight_text(
            result['title'],
            search_query
        )

        if result['body_plaintext']:
            # Get context around the first match in the content
            content = result['body_plaintext']
            terms = search_query.split()

            # Find the first occurrence of any search term
            first_match_pos = -1
            for term in terms:
                pos = content.lower().find(term.lower())
                if pos != -1 and (first_match_pos == -1 or pos < first_match_pos):
                    first_match_pos = pos

            # Extract context around the match
            if first_match_pos != -1:
                start = max(0, first_match_pos - 100)
                end = min(len(content), first_match_pos + 200)

                # Adjust to word boundaries
                if start > 0:
                    start = content.find(' ', start) + 1
                if end < len(content):
                    end = content.rfind(' ', 0, end)

                context = content[start:end]
                if start > 0:
                    context = '... ' + context
                if end < len(content):
                    context = context + ' ...'
            else:
                # If no match found, use the beginning of the content
                context = content[:300]
                if len(content) > 300:
                    context = context + ' ...'

            processed_result['content_preview'] = highlight_text(
                context,
                search_query
            )

        processed_results.append(processed_result)

    return processed_results

# Create your views here.
def index(request):
    """
    Show patch index

    Defines view for https://url.tld/patch/

    :param request:
    :return: HttpResponse
    """
    search_query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    patch_messages = []

    # Convert dates to proper format if provided
    date_filter = ""
    date_params = []
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            date_filter += " AND patch_date >= %s"
            date_params.append(start_date)
        except ValueError:
            start_date = ''

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            date_filter += " AND patch_date <= %s"
            date_params.append(end_date)
        except ValueError:
            end_date = ''

    if search_query or start_date or end_date:
        with connection.cursor() as cursor:
            with connection.cursor() as cursor:
                base_query = """
                    SELECT id, title, body_plaintext, patch_date, patch_year, 
                           patch_number_this_date, slug
                """

                if search_query:
                    base_query += """,
                        MATCH(title, body_plaintext) AGAINST(%s IN NATURAL LANGUAGE MODE) AS relevance
                    FROM patch_patchmessage
                    WHERE MATCH(title, body_plaintext) AGAINST(%s IN NATURAL LANGUAGE MODE)
                    """
                    params = [search_query, search_query] + date_params
                else:
                    base_query += """
                    FROM patch_patchmessage
                    WHERE 1=1
                    """
                    params = date_params

                final_query = base_query + date_filter + """
                    ORDER BY patch_year DESC, patch_date DESC, patch_number_this_date ASC
                """

                cursor.execute(final_query, params)

                columns = [col[0] for col in cursor.description]

                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

                # Process and highlight search results
                if search_query:
                    patch_messages = process_search_results(results, search_query)
                else:
                    patch_messages = results
    else:
        patch_messages = PatchMessage.objects.all().order_by(
            'patch_year', 'patch_date', 'patch_number_this_date'
        )

    return render(request=request,
                  context={
                      "patch_messages": patch_messages,
                      'search_query': search_query,
                      'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else '',
                      'end_date': end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else ''
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
