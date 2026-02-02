from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from .models import Message, Riddle
from .form import MessageForm, RiddleForm


# Display form to create a new message
def index(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Riddle_Generator')
    else:
        form = MessageForm()
    return render(request, 'Message.html', {'form': form})


# Generate riddles for each word in the message
def Riddle_Generator(request):
    # Get latest message
    message_obj = Message.objects.last()

    if not message_obj:
        return redirect('confirm_link')

    message_text = message_obj.message
    word_count = len(message_text.split())
    message_uuid = str(message_obj.uuid)

    # Session key scoped to this message
    riddle_form_index_key = f"riddle_form_index_{message_uuid}"

    # Track which riddle we're currently filling
    if riddle_form_index_key not in request.session:
        request.session[riddle_form_index_key] = 1  # 1-based index

    current_index = request.session[riddle_form_index_key]

    # Finished creating all riddles
    if current_index > word_count:
        request.session.pop(riddle_form_index_key, None)
        return redirect('confirm_link')

    if request.method == 'POST':
        form = RiddleForm(request.POST)
        if form.is_valid():
            riddle_instance = form.save(commit=False)
            riddle_instance.word_index = str(current_index)
            riddle_instance.riddle_id = message_obj  # link ForeignKey
            riddle_instance.save()
            request.session[riddle_form_index_key] = current_index + 1
            return redirect('Riddle_Generator')
    else:
        form = RiddleForm()

    return render(request, 'Riddles.html', {
        'form': form,
        'current_index': current_index,
        'total': word_count,
    })


# Display riddles to answer and handle hints
def confirm_view(request, uuid):
    message = Message.objects.get(uuid=uuid)
    message_words = message.message.split()
    riddles = list(message.riddles.all())

    # Scoped session keys per message
    riddle_index_key = f"riddle_index_{uuid}"
    wrong_attempts_key = f"wrong_attempts_{uuid}"

    if riddle_index_key not in request.session:
        request.session[riddle_index_key] = 0
    if wrong_attempts_key not in request.session:
        request.session[wrong_attempts_key] = 0

    index = request.session[riddle_index_key]

    # All riddles done
    if index >= len(riddles):
        request.session.pop(riddle_index_key, None)
        request.session.pop(wrong_attempts_key, None)
        return render(request, 'completed.html', {
            'full_message': message.message
        })

    current_riddle = riddles[index]
    error = None
    hint = None

    if request.method == "POST":
        user_answer = request.POST.get("answer", "").strip().lower()
        correct_answer = current_riddle.answer.strip().lower()

        if user_answer == correct_answer:
            request.session[riddle_index_key] += 1
            request.session[wrong_attempts_key] = 0
            return redirect(request.path)
        else:
            request.session[wrong_attempts_key] += 1
            error = "Wrong answer, try again!"

    # Show hint after 3 wrong attempts
    if request.session[wrong_attempts_key] >= 3:
        hint = current_riddle.hint

    revealed_words = message_words[:index]

    return render(request, 'Reveal.html', {
        'riddle': current_riddle,
        'error': error,
        'revealed_words': revealed_words,
        'hint': hint
    })


# Generate and display the confirmation link
def confirm_link(request):
    message_class = Message.objects.first()
    if not message_class:
        return HttpResponse("No message exists yet.")

    uuid = message_class.uuid

    link = request.build_absolute_uri(
        reverse('confirm', args=[uuid])
    )

    return render(request, 'confirm_link.html', {'link': link})
