from django.urls import path
from .views import MyappView

urlpatterns = [
    # Define paths for your app here
    path("remark/",MyappView.as_view(),name="myapp")
]
