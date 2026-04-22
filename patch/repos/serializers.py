from rest_framework import serializers
from .models import Repo, RepoAnalytic


class RepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repo
        fields = '__all__'
        read_only_fields = ['last_check_date', 'last_import_date']
        extra_kwargs = {
            'token': {'write_only': True},
        }


class RepoAnalyticSerializer(serializers.ModelSerializer):
    repo_name = serializers.CharField(source='repo.name', read_only=True)

    class Meta:
        model = RepoAnalytic
        fields = '__all__'
        extra_fields = ['repo_name']
