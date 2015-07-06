from rest_framework import serializers
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.genre import Genre
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.language import Language
from elvis.models.location import Location
from elvis.models.source import Source
from elvis.models.attachment import Attachment
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


class GenrePieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = ("name",)


class InstrumentVoicePieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstrumentVoice
        fields = ("name",)


class LanguagePieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = ("name",)


class LocationPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ("name",)


class SourcePieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Source
        fields = ("name",)


class AttachmentPieceSerializer(serializers.HyperlinkedModelSerializer):
    # LM: Must add this to serializers explicitly, otherwise will raise KeyError because file_name isn't *really* a field
    file_name = serializers.ReadOnlyField()
    attachment = serializers.SerializerMethodField("retrieve_attachment")
    source = serializers.CharField()

    class Meta:
        model = Attachment
        fields = ("file_name", "id", "source", "attachment")

    def retrieve_attachment(self, obj):
        request = self.context.get('request', None)
        if not request.user.is_authenticated():
            return ""
        path = os.path.relpath(obj.attachment.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url


class UserPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', "last_name")


class MovementPieceSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class PieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerPieceSerializer()
    tags = TagPieceSerializer(many=True)
    genres = GenrePieceSerializer(many=True)
    date_of_composition = serializers.DateField(format=None)
    date_of_composition2 = serializers.DateField(format=None)
    instruments_voices = InstrumentVoicePieceSerializer(many=True)
    languages = LanguagePieceSerializer(many=True)
    locations = LocationPieceSerializer(many=True)
    sources = SourcePieceSerializer(many=True)
    attachments = AttachmentPieceSerializer(many=True)
    comment = serializers.CharField()
    uploader = UserPieceSerializer()
    movements = MovementPieceSerializer(many=True)
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Piece
