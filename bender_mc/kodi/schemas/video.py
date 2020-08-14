"""
    kodi_api.schemas
    ~~~~~~~~~~~~~~~~

    Schemas for the Kodi (v19) video database.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
from drowsy.convert import CamelModelResourceConverter
from drowsy.schema import ModelResourceSchema
from bender_mc.kodi.models.video import (
    Actor, Art, Bookmark, Country, Episode, EpisodeView, File, Genre,
    Movie, MovieView, MusicVideo, MusicVideoView, Path, Rating, Season,
    SeasonView, Set, Setting, Studio, Tag, TvShow, TvShowView, TvShowCount,
    TvShowLinkPathMinView, Uniqueid, Version
)


class ActorSchema(ModelResourceSchema):
    class Meta:
        model = Actor
        model_converter = CamelModelResourceConverter


class ArtSchema(ModelResourceSchema):
    class Meta:
        model = Art
        model_converter = CamelModelResourceConverter


class BookmarkSchema(ModelResourceSchema):
    class Meta:
        model = Bookmark
        model_converter = CamelModelResourceConverter


class CountrySchema(ModelResourceSchema):
    class Meta:
        model = Country
        model_converter = CamelModelResourceConverter


class EpisodeSchema(ModelResourceSchema):
    class Meta:
        model = Episode
        model_converter = CamelModelResourceConverter


class EpisodeViewSchema(ModelResourceSchema):
    class Meta:
        model = EpisodeView
        model_converter = CamelModelResourceConverter


class FileSchema(ModelResourceSchema):
    class Meta:
        model = File
        model_converter = CamelModelResourceConverter


class GenreSchema(ModelResourceSchema):
    class Meta:
        model = Genre
        model_converter = CamelModelResourceConverter


class MovieSchema(ModelResourceSchema):
    class Meta:
        model = Movie
        model_converter = CamelModelResourceConverter


class MovieViewSchema(ModelResourceSchema):
    class Meta:
        model = MovieView
        model_converter = CamelModelResourceConverter


class MusicVideoSchema(ModelResourceSchema):
    class Meta:
        model = MusicVideo
        model_converter = CamelModelResourceConverter


class MusicVideoViewSchema(ModelResourceSchema):
    class Meta:
        model = MusicVideoView
        model_converter = CamelModelResourceConverter


class PathSchema(ModelResourceSchema):
    class Meta:
        model = Path
        model_converter = CamelModelResourceConverter


class RatingSchema(ModelResourceSchema):
    class Meta:
        model = Rating
        model_converter = CamelModelResourceConverter


class SeasonSchema(ModelResourceSchema):
    class Meta:
        model = Season
        model_converter = CamelModelResourceConverter


class SeasonViewSchema(ModelResourceSchema):
    class Meta:
        model = SeasonView
        model_converter = CamelModelResourceConverter


class SetSchema(ModelResourceSchema):
    class Meta:
        model = Set
        model_converter = CamelModelResourceConverter


class SettingSchema(ModelResourceSchema):
    class Meta:
        model = Setting
        model_converter = CamelModelResourceConverter


class StudioSchema(ModelResourceSchema):
    class Meta:
        model = Studio
        model_converter = CamelModelResourceConverter


class TagSchema(ModelResourceSchema):
    class Meta:
        model = Tag
        model_converter = CamelModelResourceConverter


class TvShowSchema(ModelResourceSchema):
    class Meta:
        model = TvShow
        model_converter = CamelModelResourceConverter


class TvShowCountSchema(ModelResourceSchema):
    class Meta:
        model = TvShowCount
        model_converter = CamelModelResourceConverter


class TvShowViewSchema(ModelResourceSchema):
    class Meta:
        model = TvShowView
        model_converter = CamelModelResourceConverter


class TvShowLinkPathMinViewSchema(ModelResourceSchema):
    class Meta:
        model = TvShowLinkPathMinView
        model_converter = CamelModelResourceConverter


class UniqueidSchema(ModelResourceSchema):
    class Meta:
        model = Uniqueid
        model_converter = CamelModelResourceConverter


class VersionSchema(ModelResourceSchema):
    class Meta:
        model = Version
        model_converter = CamelModelResourceConverter
