from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse
from .models import Message,Riddle
from .form import MessageForm,RiddleForm



# display form to decide the message 
def index(request):
    if request.method=='POST':
        form=MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Riddle_Generator')
    else:
        form=MessageForm()
    return render(request,'Message.html',{'form':form})
    
    
    

def Riddle_Generator(request):
    # get latest message
    message_obj = Message.objects.last()

    # safety check (optional but good)
    if not message_obj:
        return redirect('confirm_link')

    message_text = message_obj.message
    word_count = len(message_text.split())

    # track which riddle we're currently filling
    if 'riddle_form_index' not in request.session:
        request.session['riddle_form_index'] = 1  # 1-based index

    current_index = request.session['riddle_form_index']

    # finished creating all riddles
    if current_index > word_count:
        del request.session['riddle_form_index']
        return redirect('confirm_link')

    if request.method == 'POST':
        form = RiddleForm(request.POST)
        if form.is_valid():
            riddle_instance = form.save(commit=False)

            # set required fields
            riddle_instance.word_index = str(current_index)
            riddle_instance.riddle_id = message_obj  # ✅ ForeignKey linked

            riddle_instance.save()

            request.session['riddle_form_index'] = current_index + 1
            return redirect('Riddle_Generator')
    else:
        form = RiddleForm()

    return render(request, 'Riddles.html', {
        'form': form,
        'current_index': current_index,
        'total': word_count,
    })




# this display riddle to answer
def confirm_view(request, uuid):
    message = Message.objects.last()
    message_words = message.message.split()
    riddles = list(message.riddles.all())

    if 'riddle_index' not in request.session:
        request.session['riddle_index'] = 0

    if 'wrong_attempts' not in request.session:
        request.session['wrong_attempts'] = 0

    index = request.session['riddle_index']

    # ✅ all riddles done
    if index >= len(riddles):
        request.session.pop('riddle_index', None)
        request.session.pop('wrong_attempts', None)
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
            request.session['riddle_index'] += 1
            request.session['wrong_attempts'] = 0  # 🔥 reset on correct
            return redirect(request.path)
        else:
            request.session['wrong_attempts'] += 1
            error = "Wrong answer, try again!"

    # ✅ show hint after 3 wrong attempts
    if request.session['wrong_attempts'] >= 3:
        hint = current_riddle.hint

    revealed_words = message_words[:index]

    return render(request, 'Reveal.html', {
        'riddle': current_riddle,
        'error': error,
        'revealed_words': revealed_words,
        'hint': hint
    })

 


# confirm link
def confirm_link(request):
    message_class = Message.objects.first()
    uuid = message_class.uuid

    link = request.build_absolute_uri(
        reverse('confirm', args=[uuid])
    )

    return render(request, 'confirm_link.html', {'link': link})