from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Course
from django.core.urlresolvers import reverse_lazy
class OwnerMixin(object):

    def get_queryset(self):
        qs=super(OwnerMixin,self).get_queryset()
        return qs.filter(owner=self.request.user)
    
class OwnerEditMixin(object):

    def form_valid(self,form):
        form.instance.owner =self.request.user
        return super(OwnerEditMixin,self).form_valid(form)

class OwnerCourseMixin(OwnerMixin,LoginRequiredMixin):
    model=Course

class OwnerCourseEdiMixin(OwnerCourseMixin,OwnerEditMixin):
    fields =['subject','title','slug','overview']
    success_url =reverse_lazy('courses:manage_course_list')
    template_name='courses/manage/course/form.html'