from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from .forms import QuestionCreateForm
from .models import *


@login_required
def create_edit_question(request, id=None):

    user = request.user

    if id:
        obj = get_object_or_404(Question, id=id)
        if obj.author != user:
            return HttpResponseForbidden()
    else:
        obj = Question(author=user)

    if request.POST:
        form = QuestionCreateForm(request.POST, instance=obj)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.author_id = user.id
            obj.save()

            form.save_m2m()  # save tags into db

            messages.success(
                request, 'Your Question Has Been Submitted Successfully', extra_tags='alert alert-success')

            return redirect(to='question:question-detail')

        else:
            messages.error(request, 'Errors occurred',
                           extra_tags='alert alert-danger')
    else:
        form = QuestionCreateForm(instance=obj)

    context = {
        'form': form,
    }

    template_name = 'pages/question_create.html'

    return render(request, template_name, context=context)


def question_list_view(request):
    all_questions = Question.objects.all().order_by('-id')
    paginator = Paginator(all_questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template_name = "pages/question_list.html"
    context = {
        'questions': page_obj,
    }
    return render(request, template_name, context)


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'pages/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(**kwargs)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        question = Question.objects.get(slug=slug)
        question_like = QuestionLike.objects.filter(question=question).count()
        context["question_like"] = question_like
        return context


def save_question_like(request):
    if request.method == 'POST':
        questionid = request.POST['questionId']
        question = Question.objects.get(pk=questionid)
        user = request.user
        check = QuestionLike.objects.filter(
            question=question, user=user).count()
        if check > 0:
            return JsonResponse({'bool': False})
        else:
            QuestionLike.objects.create(
                question=question,
                user=user
            )
            return JsonResponse({'bool': True})
