import csv
import json
from collections import OrderedDict
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.db import connection
from django.db.models import Q
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re
from itertools import groupby
from django.db.models import Count
from django.contrib import messages
from django.db.models.functions import TruncMonth

from .models import PatchMessage, PatchTag, EXPANSION_CHOICES
from .models import Comment
from datetime import datetime
from .forms import CommentForm

EXPANSION_ORDER = [exp for exp, _ in EXPANSION_CHOICES]


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
    tag_filter = request.GET.get('tag', '')
    patch_messages = []

    all_tags = PatchTag.objects.order_by('name')
    active_tag = tag_filter if tag_filter else ''

    if search_query or start_date or end_date:
        # Handle search case
        date_filter = ""
        date_params = []

        # Process start date
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

        with connection.cursor() as cursor:
            base_query = """
                    SELECT id, title, body_plaintext, patch_date, patch_year,
                           patch_number_this_date, slug, patch_type, expansion
                """

            if search_query:
                base_query += """,
                        MATCH(title, body_plaintext, body_markdown) AGAINST(%s IN NATURAL LANGUAGE MODE) AS relevance
                    FROM patch_patchmessage
                    WHERE MATCH(title, body_plaintext, body_markdown) AGAINST(%s IN NATURAL LANGUAGE MODE)
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

            # Apply tag filter in Python if set (raw SQL path)
            if tag_filter:
                tagged_ids = set(
                    PatchMessage.objects.filter(tags__slug=tag_filter).values_list('id', flat=True)
                )
                results = [r for r in results if r['id'] in tagged_ids]

            # Process and highlight search results if there's a search query
            if search_query:
                patch_messages = process_search_results(results, search_query)
            else:
                patch_messages = results
        return render(request, 'patch/index.html', {
            'patch_messages': patch_messages,
            'search_query': search_query,
            'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else '',
            'end_date': end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else '',
            'is_search': True,
            'all_tags': all_tags,
            'active_tag': active_tag,
        })
    else:
        # Get patches grouped by year
        patches_qs = (
            PatchMessage.objects
            .order_by('-patch_year', '-patch_date', '-patch_number_this_date')
        )
        if tag_filter:
            patches_qs = patches_qs.filter(tags__slug=tag_filter)

        patches_by_year = patches_qs.values('patch_year', 'title', 'slug', 'patch_date', 'body_plaintext')

        # Group patches by year and count patches per year
        years_data = (
            patches_qs
            .values('patch_year')
            .annotate(count=Count('id'))
            .order_by('-patch_year')
        )

        # Expansion-grouped data
        patches_for_expansion = (
            patches_qs
            .order_by('patch_date', 'patch_number_this_date')
            .values('expansion', 'title', 'slug', 'patch_date')
        )

        expansion_display = dict(EXPANSION_CHOICES)
        patches_by_expansion_raw = OrderedDict()
        for patch in patches_for_expansion:
            exp = patch['expansion'] or 'unknown'
            if exp not in patches_by_expansion_raw:
                patches_by_expansion_raw[exp] = []
            patches_by_expansion_raw[exp].append(patch)

        patches_by_expansion = [
            {
                'key': exp,
                'display': expansion_display.get(exp, exp),
                'patches': patches_by_expansion_raw[exp],
                'count': len(patches_by_expansion_raw[exp]),
            }
            for exp in EXPANSION_ORDER
            if exp in patches_by_expansion_raw
        ]

        # Return browse template
        return render(request, 'patch/index.html', {
            'patches_by_year': patches_by_year,
            'years_data': years_data,
            'patches_by_expansion': patches_by_expansion,
            'is_search': False,
            'all_tags': all_tags,
            'active_tag': active_tag,
        })


def view_patch_message(request, slug: str):
    """
    Show patch message

    Defines view for https://url.tld/patch/view/<int:pk>

    :param request:
    :param slug: the slug for the patch message
    :return: HttpResponse
    """
    patch_message = PatchMessage.objects.get(slug=slug)
    next_patch = PatchMessage.objects.filter(
        Q(patch_date=patch_message.patch_date, patch_number_this_date__gt=patch_message.patch_number_this_date) |
        Q(patch_date__gt=patch_message.patch_date)
    ).order_by("patch_date", "patch_number_this_date").first()
    prev_patch = PatchMessage.objects.filter(
        Q(patch_date=patch_message.patch_date, patch_number_this_date__lt=patch_message.patch_number_this_date) |
        Q(patch_date__lt=patch_message.patch_date)
    ).order_by("-patch_date", "-patch_number_this_date").first()
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
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a comment.")
            comment_form = CommentForm()
        else:
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.patch_message = patch_message
                new_comment.username = request.user
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
                      "current_month": patch_message.patch_date.strftime('%B'),
                      "default_tab": "markdown" if patch_message.markdown_edited else "plaintext",
                      "comments": comments,
                      "new_comment": new_comment,
                      "comment_form": comment_form,
                  },
                  template_name="patch/view_patch_message.html")


def patch_raw(request, slug: str):
    """Return the plain-text body as a downloadable .txt file."""
    patch_message = PatchMessage.objects.get(slug=slug)
    response = HttpResponse(
        patch_message.body_plaintext or '',
        content_type='text/plain; charset=utf-8',
    )
    response['Content-Disposition'] = f'attachment; filename="{slug}.txt"'
    return response


def export_json(request):
    """Stream the full archive as a JSON array."""
    patches = (
        PatchMessage.objects
        .order_by('patch_date', 'patch_number_this_date')
        .prefetch_related('tags')
    )

    def rows():
        yield '[\n'
        for i, pm in enumerate(patches):
            record = {
                'title': pm.title,
                'slug': pm.slug,
                'patch_date': pm.patch_date.isoformat() if pm.patch_date else None,
                'patch_year': pm.patch_year,
                'patch_type': pm.patch_type,
                'expansion': pm.expansion,
                'tags': [t.slug for t in pm.tags.all()],
                'body_plaintext': pm.body_plaintext or '',
                'body_markdown': pm.body_markdown or '',
                'source_notes': pm.source_notes or '',
            }
            if i > 0:
                yield ',\n'
            yield json.dumps(record, ensure_ascii=False)
        yield '\n]'

    response = StreamingHttpResponse(rows(), content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="everquest-patches-1999-2010.json"'
    return response


class _Echo:
    """Minimal file-like object for csv.writer in a streaming response."""
    def write(self, value):
        return value


def export_csv(request):
    """Stream the full archive as a CSV file."""
    writer = csv.writer(_Echo())

    def rows():
        yield writer.writerow([
            'title', 'slug', 'patch_date', 'patch_year',
            'patch_type', 'expansion', 'tags', 'body_plaintext',
        ])
        qs = (
            PatchMessage.objects
            .order_by('patch_date', 'patch_number_this_date')
            .prefetch_related('tags')
        )
        for pm in qs:
            yield writer.writerow([
                pm.title,
                pm.slug,
                pm.patch_date.isoformat() if pm.patch_date else '',
                pm.patch_year,
                pm.patch_type,
                pm.expansion or '',
                '|'.join(t.slug for t in pm.tags.all()),
                pm.body_plaintext or '',
            ])

    response = StreamingHttpResponse(
        (row for row in rows()),
        content_type='text/csv; charset=utf-8',
    )
    response['Content-Disposition'] = 'attachment; filename="everquest-patches-1999-2010.csv"'
    return response
