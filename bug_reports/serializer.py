from rest_framework import serializers
from .models import BugReport

class BugReportSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = BugReport
        fields = '__all__'

