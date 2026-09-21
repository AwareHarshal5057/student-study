import re
import requests
import urllib.parse
import urllib.request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import generic
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_protect

import urllib.request
import json
import ssl
import wikipedia
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required 

def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)

        if form.is_valid():
            note = Notes(
                user=request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description']
            )
            note.save()
            messages.success(
                request, f"Notes Added From {request.user.username} Successfully")
            return redirect('notes')

    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {
        'notes': notes,
        'form': form
    }
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, pk):
    note = Notes.objects.get(id=pk, user=request.user)
    note.delete()
    messages.success(request, "Note deleted successfully")
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes
    template_name = 'dashboard/notes_detail.html'
    context_object_name = 'note'

@login_required
def homework(request):
    if request.method == "POST":

        form = HomeworkForm(request.POST)

        if form.is_valid():

            homework = form.save(commit=False)

            homework.user = request.user

            homework.save()

            messages.success(

                request, f'Homework added from {request.user.username}!!')

            return redirect('homework')

    else:

        form = HomeworkForm()

    homeworks = Homework.objects.filter(user=request.user)

    if len(homeworks) == 0:

        homework_done = True

    else:

        homework_done = False

    context = {

        'homeworks': homeworks,

        'homework_done': homework_done,

        'form': form

    }

    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delet_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text')

        result_list = []

        if text:
            try:
                search_query = urllib.parse.quote(text)
                url = f"https://www.youtube.com/results?search_query={search_query}"

                req = urllib.request.Request(
                    url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read().decode('utf-8')

                video_ids = re.findall(r"watch\?v=(\S{11})", html)

                seen = set()
                unique_ids = [v for v in video_ids if not (
                    v in seen or seen.add(v))]

                for video_id in unique_ids[:10]:
                    result_dict = {
                        'input': text,
                        'title': f"YouTube Video ({video_id})",
                        'duration': "",
                        'thumbnails': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                        'channel': "YouTube Channel",
                        'link': f"https://www.youtube.com/watch?v={video_id}",
                        'views': "",
                        'published': "",
                        'description': "Click to watch video on YouTube"
                    }
                    result_list.append(result_dict)

            except Exception as e:
                print(f"Error fetching videos: {e}")

        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/youtube.html', context)

    else:
        form = DashboardForm()

    context = {
        'form': form
    }
    return render(request, 'dashboard/youtube.html', context)

@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)

        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                finished = True if finished == 'on' else False
            except:
                finished = False

            Todo.objects.create(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )

            messages.success(
                request,
                f"Todo Added for {request.user.username}"
            )

            return redirect('todo')

    form = TodoForm()

    todos = Todo.objects.filter(user=request.user)

    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        'todos': todos,
        'form': form,
        'todos_done': todos_done,
    }

    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)

    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True

    todo.save()

    return redirect('todo')

@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')



def books(request):
    result_list = []
    error = ""

    if request.method == "POST":

        form = DashboardForm(request.POST)
        text = request.POST.get("text")

        if text:

            try:

                url = "https://openlibrary.org/search.json"

                params = {
                    "q": text,
                    "limit": 10
                }

                response = requests.get(
                    url,
                    params=params,
                    timeout=10
                )

                response.raise_for_status()

                data = response.json()

                for item in data.get("docs", []):

                    cover_id = item.get("cover_i")

                    thumbnail = ""

                    if cover_id:
                        thumbnail = (
                            f"https://covers.openlibrary.org/b/id/"
                            f"{cover_id}-M.jpg"
                        )

                    result_list.append({

                        "title": item.get(
                            "title",
                            "No title"
                        ),

                        "author": ", ".join(
                            item.get(
                                "author_name",
                                []
                            )
                        ),

                        "year": item.get(
                            "first_publish_year",
                            ""
                        ),

                        "thumbnail": thumbnail,

                        "book_url": (
                            f"https://openlibrary.org"
                            f"{item.get('key', '')}"
                        ),
                    })

            except requests.RequestException as e:

                error = str(e)

    else:

        form = DashboardForm()

    return render(
        request,
        "dashboard/books.html",
        {
            "form": form,
            "results": result_list,
            "error": error
        }
    )


def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        
        # Checking all possible form field names
        text = (
            request.POST.get('text') or 
            request.POST.get('input') or 
            request.POST.get('search') or 
            ''
        ).strip()

        if text:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{text}"

            try:
                r = requests.get(url, timeout=5)

                if r.status_code == 200:
                    answer = r.json()
                    entry = answer[0]

                    # 1. Phonetics
                    phonetics = entry.get('phonetic', '')
                    if not phonetics:
                        for item in entry.get('phonetics', []):
                            if item.get('text'):
                                phonetics = item['text']
                                break

                    # 2. Audio Fetching + Google TTS Fallback (Always Works)
                    audio = ""
                    for item in entry.get('phonetics', []):
                        audio_src = item.get('audio', '')
                        if audio_src:
                            if audio_src.startswith('//'):
                                audio = f"https:{audio_src}"
                            else:
                                audio = audio_src
                            break

                    # Fallback audio if API provides empty string
                    if not audio:
                        audio = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=en&client=tw-ob"

                    # 3. Definition
                    definition = ""
                    meanings = entry.get('meanings', [])
                    if meanings and meanings[0].get('definitions'):
                        definition = meanings[0]['definitions'][0].get('definition', '')

                    # 4. Example
                    example = ""
                    for meaning in meanings:
                        for def_item in meaning.get('definitions', []):
                            if def_item.get('example'):
                                example = def_item['example']
                                break
                        if example:
                            break

                    # 5. Synonyms
                    synonyms = []
                    for meaning in meanings:
                        synonyms.extend(meaning.get('synonyms', []))
                        for def_item in meaning.get('definitions', []):
                            synonyms.extend(def_item.get('synonyms', []))

                    synonyms = list(dict.fromkeys(synonyms))

                    context = {
                        'form': form,
                        'input': text,
                        'phonetics': phonetics,
                        'audio': audio,
                        'definition': definition,
                        'example': example,
                        'synonyms': synonyms
                    }
                    return render(request, 'dashboard/dictionary.html', context)

                else:
                    context = {
                        'form': form,
                        'error': f'Word "{text}" not found in dictionary.'
                    }
                    return render(request, 'dashboard/dictionary.html', context)

            except requests.RequestException:
                context = {
                    'form': form,
                    'error': 'Network connection issue.'
                }
                return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()

    return render(request, 'dashboard/dictionary.html', {'form': form})

def wiki(request):
    form = DashboardForm()
    context = {
        'form': form,
        'title': '',
        'link': '',
        'details': '',
        'error': ''
    }
    if request.method == 'POST':
        form = DashboardForm(request.POST)

        text = request.POST.get('text', '').strip()
        print("SEARCH TEXT:", text)

        if text:
            try:
                # Wikipedia Search API
                search_url = "https://en.wikipedia.org/w/api.php"

                params = {
                    'action': 'query',
                    'list': 'search',
                    'srsearch': text,
                    'format': 'json',
                    'utf8': 1
                }

                response = requests.get(
                    search_url,
                    params=params,
                    headers={
                        'User-Agent': 'StudentStudyPortal/1.0'
                    },
                    timeout=10
                )

                print("STATUS CODE:", response.status_code)
                print("RESPONSE:", response.text[:300])

                response.raise_for_status()

                data = response.json()

                search_results = data.get('query', {}).get('search', [])

                if search_results:
                    page_title = search_results[0]['title']

                    # Get summary of selected page
                    summary_url = (
                        "https://en.wikipedia.org/api/rest_v1/page/summary/"
                        + requests.utils.quote(page_title)
                    )

                    summary_response = requests.get(
                        summary_url,
                        headers={
                            'User-Agent': 'StudentStudyPortal/1.0'
                        },
                        timeout=10
                    )

                    print("SUMMARY STATUS:", summary_response.status_code)

                    summary_response.raise_for_status()

                    summary_data = summary_response.json()

                    context['title'] = summary_data.get(
                        'title',
                        page_title
                    )

                    context['details'] = summary_data.get(
                        'extract',
                        'No summary found.'
                    )

                    context['link'] = (
                        summary_data.get('content_urls', {})
                        .get('desktop', {})
                        .get('page', '')
                    )

                else:
                    context['error'] = (
                        f"No Wikipedia result found for '{text}'."
                    )

            except requests.exceptions.RequestException as e:
                print("WIKI REQUEST ERROR:", e)
                context['error'] = (
                    "Unable to connect to Wikipedia. Please try again."
                )

            except ValueError as e:
                print("WIKI JSON ERROR:", e)
                context['error'] = (
                    "Wikipedia returned an invalid response."
                )

            except Exception as e:
                print("WIKI ERROR:", e)
                context['error'] = (
                    "Something went wrong while searching Wikipedia."
                )

        else:
            context['error'] = "Please enter something to search."

        context['form'] = form

    return render(request, 'dashboard/wiki.html', context)

def conversion(request):

    form = ConversionForm()
    context = {
        'form': form,
        'input': False,
    }

    if request.method == "POST":

        form = ConversionForm(request.POST)

        if form.is_valid():

            measurement = request.POST.get('measurement')

            if measurement == 'length':

                measurement_form = ConversionLengthForm()

                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                }

                if 'input' in request.POST:

                    first = request.POST.get('measure1')
                    second = request.POST.get('measure2')
                    input_value = request.POST.get('input')

                    answer = ''

                    if input_value and int(input_value) >= 0:

                        if first == 'yard' and second == 'foot':
                            answer = f'{input_value} yard = {int(input_value) * 3} foot'

                        elif first == 'foot' and second == 'yard':
                            answer = f'{input_value} foot = {int(input_value) / 3} yard'

                    context = {
                        'form': form,
                        'm_form': measurement_form,
                        'input': True,
                        'answer': answer,
                    }

            elif measurement == 'mass':

                measurement_form = ConversionMassForm()

                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                }

                if 'input' in request.POST:

                    first = request.POST.get('measure1')
                    second = request.POST.get('measure2')
                    input_value = request.POST.get('input')

                    answer = ''

                    if input_value and int(input_value) >= 0:

                        if first == 'pound' and second == 'kilogram':
                            answer = f'{input_value} pound = {int(input_value) * 0.453592} kilogram'

                        elif first == 'kilogram' and second == 'pound':
                            answer = f'{input_value} kilogram = {int(input_value) * 2.20462} pound'

                    context = {
                        'form': form,
                        'm_form': measurement_form,
                        'input': True,
                        'answer': answer,
                    }

    return render(request, 'dashboard/conversion.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username} !! ")
            return redirect("login")
    else:        
        form = UserRegistrationForm()
    context = {
           'form' : form
        }
    return render(request,'dashboard/register.html',context )

@login_required
def profile(request):

    homeworks = Homework.objects.filter(
        user=request.user
    )

    todos = Todo.objects.filter(
        user=request.user
    )

    context = {
        'homeworks': homeworks,
        'todos': todos,
    }

    return render(request, 'dashboard/profile.html', context)


def logout_user(request):
    logout(request)
    return render(request, 'dashboard/logout.html')