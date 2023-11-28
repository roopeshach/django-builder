from django.urls import path
from . import views
urlpatterns = [
    path('schema', views.model_schema_view, name="schema"),
    path('save-schema/', views.save_model_schema, name='save_model_schema'),
]
