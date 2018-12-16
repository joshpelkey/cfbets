from django.contrib import admin
from squares.models import SquaresProposed, SquaresAccepted

# Register your models here.
admin.site.register(SquaresProposed)
admin.site.register(SquaresAccepted)
