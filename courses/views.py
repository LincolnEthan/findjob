from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.core.cache import cache
from django.db.models import Count
from django.apps import apps
from django.forms import modelform_factory
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
from pagedown.widgets import PagedownWidget

from .models import Course,Subject,Module,Content
from .mixviews import OwnerCourseMixin,OwnerCourseEdiMixin
from .forms import ModuleFormSet

class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
       
        all_courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = 'subject_{}_courses'.format(subject.id)
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses})

class CourseDetailView(DetailView):
    model=Course
    
    template_name='courses/course/detail.html'
    def get_context_data(self,**kwargs):
        context= super(CourseDetailView,self).get_context_data(**kwargs)
        course=self.get_object()
        if 'module_id' in self.kwargs:
            context['module']=course.modules.get(id=self.kwargs['module_id'])
        else:
            context['module']=course.modules.all()[0]
        return context    
    
    
    
    
    
    
################################################################################## 
    
class ManageCourseListView(OwnerCourseMixin,ListView):
    template_name = 'courses/manage/course/list.html'
    
class CourseCreateView(PermissionRequiredMixin,OwnerCourseEdiMixin,CreateView):
    permission_required='courses.add_course'
    
class CourseUpdateView(PermissionRequiredMixin,OwnerCourseEdiMixin,UpdateView):
    permission_required='courses.change_course'

class CourseDeleteView(PermissionRequiredMixin,OwnerCourseEdiMixin,DeleteView):
    permission_required='courses.delete_course'
    template_name='courses/manage/course/delete.html'
    success_url =reverse_lazy('courses:manage_course_list')

class CourseModuleUpdateView(TemplateResponseMixin,View):
    template_name= 'courses/manage/module/formset.html'
    course = None
    def get_formset(self,data=None):
        return ModuleFormSet(instance=self.course,data=data)
    
    def dispatch(self, request,pk):
        self.course=get_object_or_404(Course,id=pk,owner=request.user)
        return super(CourseModuleUpdateView,self).dispatch(request,pk)
    
    def get(self,request,*args,**kwargs):
        formset=self.get_formset()
        return self.render_to_response({'course':self.course,'formset':formset})
    
    
    def post(self,request,*args,**kwargs):
        formset= self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list')
        
        return self.render_to_response({'course':self.course,'formset':formset})
    

class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model,
               exclude=['owner', 'order', 'created', 'updated'],widgets={'content':PagedownWidget})
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView,
                     self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('courses:module_content_list', self.module.id)

        return self.render_to_response({'form': form,
                                        'object': self.obj})
class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('courses:module_content_list', module.id)
    
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)

        return self.render_to_response({'module': module})

@csrf_exempt
def content_order(request):
    if request.method=="POST":
        request_json=json.loads(request.body)
        for id, order in request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)
        return JsonResponse({'saved': 'OK'})       

@csrf_exempt
def module_order(request):
    if request.method=="POST":
        request_json=json.loads(request.body)
        for id, order in request_json.items():
            Module.objects.filter(id=id,
                                   course__owner=request.user).update(order=order)
        return JsonResponse({'saved': 'OK'})        
        
        