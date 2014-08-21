from rest_framework import serializers
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.attachment import Attachment
from elvis.models.corpus import Corpus
from elvis.models.collection import Collection
from elvis.models.movement import Movement
from django.contrib.auth.models import User

import os
from django.conf import settings

class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('url', "name")

class TagPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ("url", "name")

class AttachmentPieceSerializer(serializers.HyperlinkedModelSerializer):
    # LM: Must add this to serializers explicitly, otherwise will raise KeyError because file_name isn't *really* a field
    file_name = serializers.Field()
    attachment = serializers.SerializerMethodField("retrieve_attachment")

    class Meta:
        model = Attachment
        fields = ("file_name", "id", "attachment")

    def retrieve_attachment(self, obj):
        request = self.context.get('request', None)
        if not request.user.is_authenticated():
            return ""
        path = os.path.relpath(obj.attachment.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url

class CorpusPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Corpus
        fields = ("url", "title")

class CollectionPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ("url", "title")

class UserPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', "last_name")

class MovementPieceSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field('pk')
    class Meta:
        model = Movement
        fields = ('url', 'title', 'item_id')

class PieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerPieceSerializer()
    tags = TagPieceSerializer()
    attachments = AttachmentPieceSerializer()
    corpus = CorpusPieceSerializer()
    collections = CollectionPieceSerializer()
    uploader = UserPieceSerializer()
    movements = MovementPieceSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece
