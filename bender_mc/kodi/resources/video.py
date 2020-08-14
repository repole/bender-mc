"""
    bender_mc.kodi.resources.video
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Resources for the Kodi (v19) video database API.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
from drowsy.resource import ModelResource
from bender_mc.kodi.schemas.video import (
    ActorSchema, ArtSchema, BookmarkSchema, CountrySchema, EpisodeSchema,
    EpisodeViewSchema, FileSchema, GenreSchema, MovieSchema, MovieViewSchema,
    MusicVideoSchema, MusicVideoViewSchema, PathSchema, RatingSchema,
    SeasonSchema, SeasonViewSchema, SetSchema, SettingSchema, StudioSchema,
    TagSchema, TvShowSchema, TvShowCountSchema, TvShowLinkPathMinViewSchema,
    TvShowViewSchema, UniqueidSchema, VersionSchema
)


class ActorResource(ModelResource):
    class Meta:
        schema_cls = ActorSchema


class ArtResource(ModelResource):
    class Meta:
        schema_cls = ArtSchema


class BookmarkResource(ModelResource):
    class Meta:
        schema_cls = BookmarkSchema


class CountryResource(ModelResource):
    class Meta:
        schema_cls = CountrySchema


class EpisodeResource(ModelResource):
    class Meta:
        schema_cls = EpisodeSchema


class EpisodeViewResource(ModelResource):
    class Meta:
        schema_cls = EpisodeViewSchema


class FileResource(ModelResource):
    class Meta:
        schema_cls = FileSchema


class GenreResource(ModelResource):
    class Meta:
        schema_cls = GenreSchema


class MovieResource(ModelResource):
    class Meta:
        schema_cls = MovieSchema


class MovieViewResource(ModelResource):
    class Meta:
        schema_cls = MovieViewSchema


class MusicVideoResource(ModelResource):
    class Meta:
        schema_cls = MusicVideoSchema


class MusicVideoViewResource(ModelResource):
    class Meta:
        schema_cls = MusicVideoViewSchema


class PathResource(ModelResource):
    class Meta:
        schema_cls = PathSchema


class RatingResource(ModelResource):
    class Meta:
        schema_cls = RatingSchema


class SeasonResource(ModelResource):
    class Meta:
        schema_cls = SeasonSchema


class SeasonViewResource(ModelResource):
    class Meta:
        schema_cls = SeasonViewSchema


class SetResource(ModelResource):
    class Meta:
        schema_cls = SetSchema


class SettingResource(ModelResource):
    class Meta:
        schema_cls = SettingSchema


class StudioResource(ModelResource):
    class Meta:
        schema_cls = StudioSchema


class TagResource(ModelResource):
    class Meta:
        schema_cls = TagSchema


class TvShowResource(ModelResource):
    class Meta:
        schema_cls = TvShowSchema


class TvShowCountResource(ModelResource):
    class Meta:
        schema_cls = TvShowCountSchema


class TvShowViewResource(ModelResource):
    class Meta:
        schema_cls = TvShowViewSchema


class TvShowLinkPathMinViewResource(ModelResource):
    class Meta:
        schema_cls = TvShowLinkPathMinViewSchema


class UniqueidResource(ModelResource):
    class Meta:
        schema_cls = UniqueidSchema


class VersionResource(ModelResource):
    class Meta:
        schema_cls = VersionSchema
