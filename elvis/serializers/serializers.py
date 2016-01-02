from rest_framework import serializers
from django.contrib.auth.models import User
from elvis.models.attachment import Attachment
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.collection import Collection
from elvis.models.genre import Genre
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.language import Language
from elvis.models.location import Location
from elvis.models.source import Source
from elvis.models.tag import Tag
from django.core.cache import cache

"""This file contains interdependent serializers which are combined
in order to form function specific serialization. The intent is
to standardize serialization across the project, which will be
hugely useful in terms of maintainability, clarity, and performance.
The serializers are named using the following pattern:

[Model][Variable]Serializer
    -The [Model] is the model this class can serialize
    -The [Variable] is the extent of information to be serialized,
     which include:
        -Min: Only serialize a url, an id, and a human readable title
        -Embed: Serialize links to child models and attachments.
         Primarily intended for use by other serializers.
        -List: Serialize metadata which is useful for sorting
         lists of this model. Include only basic information
         about child models.
        -Full: Serialize all metadata. Intended for detail views.
        This level is NOT cached, as the bulk of its information is built
        up from the smaller and cached serializers."""


class CachedMinHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """The smallest cached serializer, for requests at the MIN level. Will not
    only check for MIN representations in cache, but also EMB and LIST, as
    MIN is a subset of these levels and can be constructed from them."""
    def to_representation(self, instance):
        str_uuid = str(instance.uuid)
        min_check = cache.get("MIN-" + str_uuid)
        if min_check:
            return min_check

        emb_check = cache.get("EMB-" + str_uuid)
        if emb_check:
            min = {k: v for k, v in emb_check.items() if k in self.fields.keys()}
            cache.set("MIN-" + str_uuid, min, timeout=None)
            return min

        list_check = cache.get("LIST-" + str_uuid)
        if list_check:
            min = {k: v for k, v in list_check.items() if k in self.fields.keys()}
            cache.set("MIN-" + str_uuid, min, timeout=None)
            return min

        result = super().to_representation(instance)
        cache.set("MIN-" + str_uuid, result, timeout=None)
        return result


class CachedMinModelSerializer(serializers.ModelSerializer):
    """Same as above, only for those models without associated views."""
    def to_representation(self, instance):
        str_uuid = str(instance.uuid)
        cache_check = cache.get("MIN-" + str_uuid)
        if cache_check:
            return cache_check
        result = super().to_representation(instance)
        cache.set("MIN-" + str_uuid, result, timeout=None)
        return result


class CachedListHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """A cached serializer for the LIST level of serialization"""
    def to_representation(self, instance):
        str_uuid = str(instance.uuid)
        cache_check = cache.get("LIST-" + str_uuid)
        if cache_check:
            return cache_check
        result = super().to_representation(instance)
        cache.set("LIST-" + str_uuid, result, timeout=None)
        return result


class CachedEmbedHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """A cached serializer for the EMB level of serialization"""
    def to_representation(self, instance):
        str_uuid = str(instance.uuid)
        cache_check = cache.get("EMB-" + str_uuid)
        if cache_check:
            return cache_check
        result = super().to_representation(instance)
        cache.set("EMB-" + str_uuid, result, timeout=None)
        return result


class AttachmentMinSerializer(CachedMinHyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "url")


class ComposerMinSerializer(CachedMinHyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('title', 'url', 'id')


class PieceMinSerializer(CachedMinHyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ('title', 'url', 'id')


class MovementMinSerializer(CachedMinHyperlinkedModelSerializer):
    class Meta:
        model = Movement
        fields = ('title', 'url', 'id')


class CollectionMinSerializer(CachedMinHyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ('title', 'url', 'id', 'public')


class UserMinSerializer(CachedMinHyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'username', 'id')


class GenreMinSerializer(CachedMinModelSerializer):
    class Meta:
        model = Genre
        fields = ('title', 'id')


class InstrumentVoiceMinSerializer(CachedMinModelSerializer):
    class Meta:
        model = InstrumentVoice
        fields = ('title', 'id')


class LanguageMinSerializer(CachedMinModelSerializer):
    class Meta:
        model = Language
        fields = ('title', 'id')


class LocationMinSerializer(CachedMinModelSerializer):
    class Meta:
        model = Location
        fields = ('title', 'id')


class SourceMinSerializer(CachedMinModelSerializer):
    class Meta:
        model = Source
        fields = ('title', 'id')


class TagMinSerializer(CachedMinModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', 'id')


class AttachmentEmbedSerializer(CachedEmbedHyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "file_name", "extension", "url", "source")


class MovementEmbedSerializer(CachedEmbedHyperlinkedModelSerializer):
    composition_end_date = serializers.IntegerField()
    attachments = AttachmentMinSerializer(many=True)
    piece = PieceMinSerializer()

    class Meta:
        model = Movement
        fields = ('title', 'url', 'id', 'attachments', 'composition_end_date',
                  'piece')


class PieceEmbedSerializer(CachedEmbedHyperlinkedModelSerializer):
    composer = ComposerMinSerializer()
    attachments = AttachmentMinSerializer(many=True)
    movements = MovementEmbedSerializer(many=True)

    class Meta:
        model = Piece
        fields = ('title', 'url', 'id', 'composer', 'movements',
                  'movement_count', 'composition_end_date', 'attachments')


class PieceListSerializer(CachedListHyperlinkedModelSerializer):
    composer = ComposerMinSerializer()
    movement_count = serializers.ReadOnlyField()

    class Meta:
        model = Piece
        fields = ('title', 'url', 'id', 'composer',
                  'movement_count', 'composition_end_date')


class MovementListSerializer(CachedListHyperlinkedModelSerializer):
    composer = ComposerMinSerializer()

    class Meta:
        model = Movement
        fields = ('title', 'url', 'id', 'composer', 'composition_end_date')


class ComposerListSerializer(CachedListHyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('name', 'url', 'id', 'birth_date', 'death_date',
                  'piece_count', 'movement_count')


class CollectionListSerializer(CachedListHyperlinkedModelSerializer):
    creator = serializers.ReadOnlyField(source="creator.username")

    class Meta:
        model = Collection
        fields = ('title', 'url', 'id', 'piece_count', 'movement_count', 'creator')


class AttachmentFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "extension", "id", 'source', "url", "created",
                  "updated", "uploader", "attachment")


class ComposerFullSerializer(serializers.HyperlinkedModelSerializer):
    pieces = PieceListSerializer(many=True)
    free_movements = MovementEmbedSerializer(many=True)

    class Meta:
        model = Composer


class CollectionFullSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    creator = serializers.CharField(source='creator.username')
    pieces = PieceEmbedSerializer(many=True)
    movements = MovementEmbedSerializer(many=True)

    def update(self, instance, validated_data):
        if 'public' in validated_data:
            instance.public = validated_data.get('public')
        instance.save()
        return instance

    class Meta:
        model = Collection


class MovementFullSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    composer = ComposerMinSerializer()
    tags = TagMinSerializer(many=True)
    genres = GenreMinSerializer(many=True)
    instruments_voices = InstrumentVoiceMinSerializer(many=True)
    languages = LanguageMinSerializer(many=True)
    locations = LocationMinSerializer(many=True)
    sources = SourceMinSerializer(many=True)
    collections = CollectionMinSerializer(many=True)
    attachments = AttachmentEmbedSerializer(many=True)
    creator = serializers.CharField(source='creator.username')

    class Meta:
        model = Movement


class PieceFullSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    composer = ComposerMinSerializer()
    tags = TagMinSerializer(many=True)
    genres = GenreMinSerializer(many=True)
    instruments_voices = InstrumentVoiceMinSerializer(many=True)
    languages = LanguageMinSerializer(many=True)
    locations = LocationMinSerializer(many=True)
    sources = SourceMinSerializer(many=True)
    collections = CollectionMinSerializer(many=True)
    attachments = AttachmentEmbedSerializer(many=True)
    creator = serializers.CharField(source='creator.username')
    movements = MovementFullSerializer(many=True)

    class Meta:
        model = Piece


class UserFullSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField()
    pieces = PieceListSerializer(many=True)
    movements = MovementListSerializer(many=True)

    class Meta:
        model = User

    def get_full_name(self, obj):
        if not obj.last_name:
            return "{0}".format(obj.username)
        else:
            return "{0} {1}".format(obj.first_name, obj.last_name)