"""
    bender_mc.kodi.models.video
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SQLAlchemy models for the Kodi (v19) video database
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
from sqlalchemy import Boolean, Column, Float, Index, Integer, String, Table, Text, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, foreign, relationship


Base = declarative_base()
metadata = Base.metadata


t_actor_link = Table(
    'actor_link', metadata,
    Column('actor_id', Integer, ForeignKey('actor.actor_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Column('role', Text),
    Column('cast_order', Integer),
    Index('ix_actor_link_2', 'actor_id', 'media_id', 'media_type', 'role', unique=True)
)


t_country_link = Table(
    'country_link', metadata,
    Column('country_id', Integer, ForeignKey('country.country_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Index('ix_country_link_2', 'media_id', 'media_type', 'country_id', unique=True),
    Index('ix_country_link_1', 'country_id', 'media_type', 'media_id', unique=True)
)


t_director_link = Table(
    'director_link', metadata,
    Column('actor_id', Integer, ForeignKey('actor.actor_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Index('ix_director_link_2', 'media_id', 'media_type', 'actor_id', unique=True),
    Index('ix_director_link_1', 'actor_id', 'media_type', 'media_id', unique=True)
)


t_genre_link = Table(
    'genre_link', metadata,
    Column('genre_id', Integer, ForeignKey('genre.genre_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Index('ix_genre_link_2', 'media_id', 'media_type', 'genre_id', unique=True),
    Index('ix_genre_link_1', 'genre_id', 'media_type', 'media_id', unique=True)
)


t_writer_link = Table(
    'writer_link', metadata,
    Column('actor_id', Integer, ForeignKey('actor.actor_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Index('ix_writer_link_2', 'media_id', 'media_type', 'actor_id', unique=True),
    Index('ix_writer_link_1', 'actor_id', 'media_type', 'media_id', unique=True)
)


t_studio_link = Table(
    'studio_link', metadata,
    Column('studio_id', Integer, ForeignKey('studio.studio_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Index('ix_studio_link_1', 'studio_id', 'media_type', 'media_id', unique=True),
    Index('ix_studio_link_2', 'media_id', 'media_type', 'studio_id', unique=True)
)


t_tag_link = Table(
    'tag_link', metadata,
    Column('tag_id', Integer, ForeignKey('tag.tag_id')),
    Column('media_id', Integer),
    Column('media_type', Text, index=True),
    Index('ix_tag_link_2', 'media_id', 'media_type', 'tag_id', unique=True),
    Index('ix_tag_link_1', 'tag_id', 'media_type', 'media_id', unique=True)
)


t_tvshowlinkpath = Table(
    'tvshowlinkpath', metadata,
    Column('idShow', Integer, ForeignKey('tvshow.idShow')),
    Column('idPath', Integer, ForeignKey('path.idPath')),
    Index('ix_tvshowlinkpath_2', 'idPath', 'idShow', unique=True),
    Index('ix_tvshowlinkpath_1', 'idShow', 'idPath', unique=True)
)


t_movielinktvshow = Table(
    'movielinktvshow', metadata,
    Column('idMovie', Integer, ForeignKey('movie.idMovie')),
    Column('IdShow', Integer, ForeignKey('tvshow.idShow')),
    Index('ix_movielinktvshow_1', 'IdShow', 'idMovie', unique=True),
    Index('ix_movielinktvshow_2', 'idMovie', 'IdShow', unique=True)
)

# TODO - convert to tables with PKs?
t_stacktimes = Table(
    'stacktimes', metadata,
    Column('idFile', Integer, unique=True),
    Column('times', Text)
)


t_streamdetails = Table(
    'streamdetails', metadata,
    Column('idFile', Integer, index=True),
    Column('iStreamType', Integer),
    Column('strVideoCodec', Text),
    Column('fVideoAspect', Float),
    Column('iVideoWidth', Integer),
    Column('iVideoHeight', Integer),
    Column('strAudioCodec', Text),
    Column('iAudioChannels', Integer),
    Column('strAudioLanguage', Text),
    Column('strSubtitleLanguage', Text),
    Column('iVideoDuration', Integer),
    Column('strStereoMode', Text),
    Column('strVideoLanguage', Text)
)


class Version(Base):
    __tablename__ = 'version'

    id_version = Column('idVersion', Integer, primary_key=True)
    i_compress_count = Column('iCompressCount', Integer)


class TvShow(Base):
    __tablename__ = 'tvshow'

    id_show = Column('idShow', Integer, primary_key=True)
    title = Column('c00', Text)
    plot_summary = Column('c01', Text)
    status = Column('c02', Text)
    c03 = Column('c03', Text)
    rating_id = Column('c04', Text, ForeignKey('rating.rating_id'))
    first_aired = Column('c05', Text)
    thumbnail_url = Column('c06', Text)
    c07 = Column('c07', Text)
    genre_text = Column('c08', Text)
    original_title = Column('c09', Text)
    episode_guide_url = Column('c10', Text)
    fan_art_url = Column('c11', Text)
    unique_scraper_id = Column('c12', Text, ForeignKey('uniqueid.uniqueid_id'))
    content_rating = Column('c13', Text)
    studio_text = Column('c14', Text)
    title_for_sorting = Column('c15', Text)
    trailer = Column('c16', Text)
    c17 = Column('c17', Text)
    c18 = Column('c18', Text)
    c19 = Column('c19', Text)
    c20 = Column('c20', Text)
    c21 = Column('c21', Text)
    c22 = Column('c22', Text)
    c23 = Column('c23', Text)
    userrating = Column('userrating', Integer)
    duration = Column('duration', Integer)

    paths = relationship(
        "Path", secondary=t_tvshowlinkpath, backref="tv_shows")

    # NOTE: These appear to be legacy relationships.
    # unique_scraper = relationship("Uniqueid", backref="tv_shows")
    # rating = relationship("Rating", backref="tv_shows")


class Episode(Base):
    __tablename__ = 'episode'
    __table_args__ = (
        Index('id_episode_file_2', 'idFile', 'idEpisode', unique=True),
        Index('ix_episode_season_episode', 'c12', 'c13'),
        Index('ix_episode_show1', 'idEpisode', 'idShow'),
        Index('ix_episode_show2', 'idShow', 'idEpisode'),
        Index('ix_episode_file_1', 'idEpisode', 'idFile', unique=True)
    )

    id_episode = Column('idEpisode', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    title = Column('c00', Text)
    plot_summary = Column('c01', Text)
    c02 = Column('c02', Text)
    rating_id = Column('c03', Text, ForeignKey('rating.rating_id'))
    writer_text = Column('c04', Text)
    first_aired = Column('c05', Text)
    thumbnail_url = Column('c06', Text)
    thumbnail_url_spoof = Column('c07', Text)
    c08 = Column('c08', Text)
    runtime = Column('c09', Text)
    director_text = Column('c10', Text)
    production_code = Column('c11', Text)
    season_number = Column('c12', String(24))
    episode_number = Column('c13', String(24))
    original_title = Column('c14', Text)
    season_number_specials_sorting = Column('c15', Text)
    episode_number_specials_sorting = Column('c16', Text)
    bookmark = Column('c17', String(24), index=True)
    path_to_file = Column('c18', Text)
    id_path = Column('c19', Text, ForeignKey('path.idPath'), index=True)
    unique_scraper_id = Column('c20', Text, ForeignKey('uniqueid.uniqueid_id'))
    c21 = Column('c21', Text)
    c22 = Column('c22', Text)
    c23 = Column('c23', Text)
    id_show = Column('idShow', Integer, ForeignKey('tvshow.idShow'))
    userrating = Column('userrating', Integer)
    id_season = Column('idSeason', Integer, ForeignKey('seasons.idSeason'))

    tv_show = relationship("TvShow", backref="episodes")
    season = relationship("Season", backref="episodes")
    file = relationship("File", backref="episodes")

    # NOTE: These appear to be legacy relationships.
    # rating = relationship("Rating", backref="episodes")
    # unique_scraper = relationship("Uniqueid", backref="episodes")
    # path = relationship("Path", backref="episodes")


class Movie(Base):
    __tablename__ = 'movie'
    __table_args__ = (
        Index('ix_movie_file_1', 'idFile', 'idMovie', unique=True),
        Index('ix_movie_file_2', 'idMovie', 'idFile', unique=True)
    )

    id_movie = Column('idMovie', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    title = Column('c00', Text)
    plot_summary = Column('c01', Text)
    plot_outline = Column('c02', Text)
    tagline = Column('c03', Text)
    c04 = Column('c04', Text)
    rating_id = Column('c05', Text, ForeignKey('rating.rating_id'))
    writers_text = Column('c06', Text)
    c07 = Column('c07', Text)
    image_url = Column('c08', Text)
    unique_scraper_id = Column('c09', Text, ForeignKey('uniqueid.uniqueid_id'))
    title_for_sorting = Column('c10', Text)
    runtime = Column('c11', Text)
    mpaa_rating = Column('c12', Text)
    imdb_ranking = Column('c13', Text)
    genre_text = Column('c14', Text)
    director_text = Column('c15', Text)
    original_title = Column('c16', Text)
    thumb_url_spoof = Column('c17', Text)
    studio_text = Column('c18', Text)
    trailer_url = Column('c19', Text)
    fan_art_url = Column('c20', Text)
    country_text = Column('c21', Text)
    path_to_file = Column('c22', Text)
    id_path = Column('c23', Text, ForeignKey('path.idPath'), index=True)
    id_set = Column('idSet', Integer, ForeignKey('sets.idSet'))
    userrating = Column('userrating', Integer)
    premiered = Column('premiered', Text)

    tv_shows = relationship(
        "TvShow", secondary=t_movielinktvshow, backref="movies")
    set = relationship("Set", backref="movies")
    file = relationship("File", backref="movies")

    # NOTE: These appear to be legacy relationships.
    # rating = relationship("Rating", backref="movies")
    # unique_scraper = relationship("Uniqueid", backref="movies")
    # path = relationship("Path", backref="movies")


class MusicVideo(Base):
    __tablename__ = 'musicvideo'
    __table_args__ = (
        Index('ix_musicvideo_file_1', 'idMVideo', 'idFile', unique=True),
        Index('ix_musicvideo_file_2', 'idFile', 'idMVideo', unique=True)
    )

    id_m_video = Column('idMVideo', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    title = Column('c00', Text)
    thumb_url = Column('c01', Text)
    thumb_url_spoof = Column('c02', Text)
    c03 = Column('c03', Text)
    runtime = Column('c04', Text)
    director_text = Column('c05', Text)
    studio_text = Column('c06', Text)
    c07 = Column('c07', Text)
    plot_summary = Column('c08', Text)
    album = Column('c09', Text)
    artist = Column('c10', Text)
    genre_text = Column('c11', Text)
    track = Column('c12', Text)
    path_to_file = Column('c13', Text)
    id_path = Column('c14', Text, ForeignKey('path.idPath'), index=True)
    c15 = Column('c15', Text)
    c16 = Column('c16', Text)
    c17 = Column('c17', Text)
    c18 = Column('c18', Text)
    c19 = Column('c19', Text)
    c20 = Column('c20', Text)
    c21 = Column('c21', Text)
    c22 = Column('c22', Text)
    c23 = Column('c23', Text)
    userrating = Column('userrating', Integer)
    premiered = Column('premiered', Text)

    file = relationship("File", backref="music_videos")

    # NOTE: These appear to be legacy relationships.
    # path = relationship("Path", backref="music_videos")


class Season(Base):
    __tablename__ = 'seasons'
    __table_args__ = (
        Index('ix_seasons', 'idShow', 'season'),
    )

    id_season = Column('idSeason', Integer, primary_key=True)
    id_show = Column('idShow', Integer, ForeignKey('tvshow.idShow'))
    season = Column('season', Integer)
    name = Column('name', Text)
    userrating = Column('userrating', Integer)

    tv_show = relationship('TvShow', backref="seasons")


class Set(Base):
    __tablename__ = 'sets'

    id_set = Column('idSet', Integer, primary_key=True)
    str_set = Column('strSet', Text)
    str_overview = Column('strOverview', Text)


class Actor(Base):
    __tablename__ = 'actor'

    actor_id = Column('actor_id', Integer, primary_key=True)
    name = Column('name', Text, unique=True)
    art_urls = Column('art_urls', Text)

    actor_tv_shows = relationship(
        TvShow,
        secondary=t_actor_link,
        primaryjoin=t_actor_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_actor_link.c.media_id == TvShow.id_show,
            t_actor_link.c.media_type == 'tvshow'),
        backref="actors",
        sync_backref=False,
        viewonly=True
    )

    actor_episodes = relationship(
        Episode,
        secondary=t_actor_link,
        primaryjoin=t_actor_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_actor_link.c.media_id == Episode.id_episode,
            t_actor_link.c.media_type == 'episode'),
        backref="actors",
        sync_backref=False,
        viewonly=True
    )

    actor_movies = relationship(
        Movie,
        secondary=t_actor_link,
        primaryjoin=t_actor_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_actor_link.c.media_id == Movie.id_movie,
            t_actor_link.c.media_type == 'movie'),
        backref="actors",
        sync_backref=False,
        viewonly=True
    )

    actor_music_videos = relationship(
        MusicVideo,
        secondary=t_actor_link,
        primaryjoin=t_actor_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_actor_link.c.media_id == MusicVideo.id_m_video,
            t_actor_link.c.media_type == 'musicvideo'),
        backref="actors",
        sync_backref=False,
        viewonly=True
    )

    director_episodes = relationship(
        Episode,
        secondary=t_director_link,
        primaryjoin=t_director_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_director_link.c.media_id == Episode.id_episode,
            t_director_link.c.media_type == 'episode'),
        backref="directors",
        sync_backref=False,
        viewonly=True
    )

    director_movies = relationship(
        Movie,
        secondary=t_director_link,
        primaryjoin=t_director_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_director_link.c.media_id == Movie.id_movie,
            t_director_link.c.media_type == 'movie'),
        backref="directors",
        sync_backref=False,
        viewonly=True
    )

    director_music_videos = relationship(
        MusicVideo,
        secondary=t_director_link,
        primaryjoin=t_director_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_director_link.c.media_id == MusicVideo.id_m_video,
            t_director_link.c.media_type == 'musicvideo'),  # TODO - CONFIRM
        backref="directors",
        sync_backref=False,
        viewonly=True
    )

    # TODO - Writer for tv show? Other media?
    writer_episodes = relationship(
        Episode,
        secondary=t_writer_link,
        primaryjoin=t_writer_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_writer_link.c.media_id == Episode.id_episode,
            t_writer_link.c.media_type == 'episode'),
        backref="writers",
        sync_backref=False,
        viewonly=True
    )

    writer_movies = relationship(
        Movie,
        secondary=t_writer_link,
        primaryjoin=t_writer_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_writer_link.c.media_id == Movie.id_movie,
            t_writer_link.c.media_type == 'movie'),
        backref="writers",
        sync_backref=False,
        viewonly=True
    )

    writer_music_videos = relationship(
        MusicVideo,
        secondary=t_writer_link,
        primaryjoin=t_writer_link.c.actor_id == actor_id,
        secondaryjoin=and_(
            t_writer_link.c.media_id == MusicVideo.id_m_video,
            t_writer_link.c.media_type == 'musicvideo'),  # TODO - CONFIRM
        backref="writers",
        sync_backref=False,
        viewonly=True
    )


class Art(Base):
    __tablename__ = 'art'
    __table_args__ = (
        Index('ix_art', 'media_id', 'media_type', 'type'),
    )

    art_id = Column('art_id', Integer, primary_key=True)
    media_id = Column('media_id', Integer)
    media_type = Column('media_type', Text)
    type = Column('type', Text)
    url = Column('url', Text)

    movie = relationship(
        Movie,
        primaryjoin=and_(
            Movie.id_movie == foreign(media_id),
            media_type == 'movie'),
        backref="art",
        sync_backref=False,
        viewonly=True
    )

    tv_show = relationship(
        TvShow,
        primaryjoin=and_(
            TvShow.id_show == foreign(media_id),
            media_type == 'tvshow'),
        backref="art",
        sync_backref=False,
        viewonly=True
    )

    season = relationship(
        Season,
        primaryjoin=and_(
            Season.id_season == foreign(media_id),
            media_type == 'season'),
        backref="art",
        sync_backref=False,
        viewonly=True
    )

    episode = relationship(
        Episode,
        primaryjoin=and_(
            Episode.id_episode == foreign(media_id),
            media_type == 'episode'),
        backref="art",
        sync_backref=False,
        viewonly=True
    )

    actor = relationship(
        Actor,
        primaryjoin=and_(
            Actor.actor_id == foreign(media_id),
            media_type.in_(
                ['actor', 'director', 'producer', 'writer', 'gueststar']
            )
        ),
        backref="art",
        sync_backref=False,
        viewonly=True
    )


class Bookmark(Base):
    __tablename__ = 'bookmark'
    __table_args__ = (
        Index('ix_bookmark', 'idFile', 'type'),
    )

    id_bookmark = Column('idBookmark', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    time_in_seconds = Column('timeInSeconds', Float)
    total_time_in_seconds = Column('totalTimeInSeconds', Float)
    thumb_nail_image = Column('thumbNailImage', Text)
    player = Column('player', Text)
    player_state = Column('playerState', Text)
    type = Column('type', Integer)

    file = relationship('File', backref='bookmarks')


class Country(Base):
    __tablename__ = 'country'

    country_id = Column('country_id', Integer, primary_key=True)
    name = Column('name', Text, unique=True)

    movies = relationship(
        Movie,
        secondary=t_country_link,
        primaryjoin=t_country_link.c.country_id == country_id,
        secondaryjoin=and_(
            t_country_link.c.media_id == Movie.id_movie,
            t_country_link.c.media_type == 'movie'),
        backref="countries",
        sync_backref=False,
        viewonly=True
    )


class File(Base):
    __tablename__ = 'files'
    __table_args__ = (
        Index('ix_files', 'idPath', 'strFilename'),
    )

    id_file = Column('idFile', Integer, primary_key=True)
    id_path = Column('idPath', Integer, ForeignKey('path.idPath'))
    str_filename = Column('strFilename', Text)
    play_count = Column('playCount', Integer)
    last_played = Column('lastPlayed', Text)
    date_added = Column('dateAdded', Text)

    path = relationship('Path', backref='files')


class Setting(Base):
    __tablename__ = 'settings'

    id_file = Column(
        'idFile',
        Integer,
        ForeignKey('files.idFile'),
        unique=True,
        primary_key=True)
    deinterlace = Column('Deinterlace', Boolean)
    view_mode = Column('ViewMode', Integer)
    zoom_amount = Column('ZoomAmount', Float)
    pixel_ratio = Column('PixelRatio', Float)
    vertical_shift = Column('VerticalShift', Float)
    audio_stream = Column('AudioStream', Integer)
    subtitle_stream = Column('SubtitleStream', Integer)
    subtitle_delay = Column('SubtitleDelay', Float)
    subtitles_on = Column('SubtitlesOn', Boolean)
    brightness = Column('Brightness', Float)
    contrast = Column('Contrast', Float)
    gamma = Column('Gamma', Float)
    volume_amplification = Column('VolumeAmplification', Float)
    audio_delay = Column('AudioDelay', Float)
    resume_time = Column('ResumeTime', Integer)
    sharpness = Column('Sharpness', Float)
    noise_reduction = Column('NoiseReduction', Float)
    non_lin_stretch = Column('NonLinStretch', Boolean)
    post_process = Column('PostProcess', Boolean)
    scaling_method = Column('ScalingMethod', Integer)
    deinterlace_mode = Column('DeinterlaceMode', Integer)
    stereo_mode = Column('StereoMode', Integer)
    stereo_invert = Column('StereoInvert', Boolean)
    video_stream = Column('VideoStream', Integer)
    tonemap_method = Column('TonemapMethod', Integer)
    tonemap_param = Column('TonemapParam', Float)
    orientation = Column('Orientation', Integer)
    center_mix_level = Column('CenterMixLevel', Integer)

    file = relationship("File", backref=backref("setting", uselist=False))


class Genre(Base):
    __tablename__ = 'genre'

    genre_id = Column('genre_id', Integer, primary_key=True)
    name = Column('name', Text, unique=True)

    movies = relationship(
        Movie,
        secondary=t_genre_link,
        primaryjoin=t_genre_link.c.genre_id == genre_id,
        secondaryjoin=and_(
            t_genre_link.c.media_id == Movie.id_movie,
            t_genre_link.c.media_type == 'movie'),
        backref="genres",
        sync_backref=False,
        viewonly=True
    )

    tv_shows = relationship(
        TvShow,
        secondary=t_genre_link,
        primaryjoin=t_genre_link.c.genre_id == genre_id,
        secondaryjoin=and_(
            t_genre_link.c.media_id == TvShow.id_show,
            t_genre_link.c.media_type == 'tvshow'),
        backref="genres",
        sync_backref=False,
        viewonly=True
    )

    music_videos = relationship(
        MusicVideo,
        secondary=t_genre_link,
        primaryjoin=t_genre_link.c.genre_id == genre_id,
        secondaryjoin=and_(
            t_genre_link.c.media_id == MusicVideo.id_m_video,
            t_genre_link.c.media_type == 'musicvideo'),
        backref="genres",
        sync_backref=False,
        viewonly=True
    )


class Path(Base):
    __tablename__ = 'path'

    id_path = Column('idPath', Integer, primary_key=True)
    str_path = Column('strPath', Text, index=True)
    str_content = Column('strContent', Text)
    str_scraper = Column('strScraper', Text)
    str_hash = Column('strHash', Text)
    scan_recursive = Column('scanRecursive', Integer)
    use_folder_names = Column('useFolderNames', Boolean)
    str_settings = Column('strSettings', Text)
    no_update = Column('noUpdate', Boolean)
    exclude = Column('exclude', Boolean)
    date_added = Column('dateAdded', Text)
    id_parent_path = Column('idParentPath', Integer, index=True)


class Rating(Base):
    __tablename__ = 'rating'
    __table_args__ = (
        Index('ix_rating', 'media_id', 'media_type'),
    )

    rating_id = Column('rating_id', Integer, primary_key=True)
    media_id = Column('media_id', Integer)
    media_type = Column('media_type', Text)
    rating_type = Column('rating_type', Text)
    rating = Column('rating', Float)
    votes = Column('votes', Integer)

    movie = relationship(
        Movie,
        primaryjoin=and_(
            Movie.id_movie == foreign(media_id),
            media_type == 'movie'),
        backref="ratings",
        sync_backref=False,
        viewonly=True
    )

    tv_show = relationship(
        TvShow,
        primaryjoin=and_(
            TvShow.id_show == foreign(media_id),
            media_type == 'tvshow'),
        backref="ratings",
        sync_backref=False,
        viewonly=True
    )

    episode = relationship(
        Episode,
        primaryjoin=and_(
            Episode.id_episode == foreign(media_id),
            media_type == 'episode'),
        backref="ratings",
        sync_backref=False,
        viewonly=True
    )

    music_video = relationship(
        MusicVideo,
        primaryjoin=and_(
            MusicVideo.id_m_video == foreign(media_id),
            media_type == 'musicvideo'),
        backref="ratings",
        sync_backref=False,
        viewonly=True
    )


class Studio(Base):
    __tablename__ = 'studio'

    studio_id = Column('studio_id', Integer, primary_key=True)
    name = Column('name', Text, unique=True)

    movies = relationship(
        Movie,
        secondary=t_studio_link,
        primaryjoin=t_studio_link.c.studio_id == studio_id,
        secondaryjoin=and_(
            t_studio_link.c.media_id == Movie.id_movie,
            t_studio_link.c.media_type == 'movie'),
        backref="studios",
        sync_backref=False,
        viewonly=True
    )

    tv_shows = relationship(
        TvShow,
        secondary=t_studio_link,
        primaryjoin=t_studio_link.c.studio_id == studio_id,
        secondaryjoin=and_(
            t_studio_link.c.media_id == TvShow.id_show,
            t_studio_link.c.media_type == 'tvshow'),
        backref="studios",
        sync_backref=False,
        viewonly=True
    )

    music_videos = relationship(
        MusicVideo,
        secondary=t_studio_link,
        primaryjoin=t_studio_link.c.studio_id == studio_id,
        secondaryjoin=and_(
            t_studio_link.c.media_id == MusicVideo.id_m_video,
            t_studio_link.c.media_type == 'musicvideo'),
        backref="studios",
        sync_backref=False,
        viewonly=True
    )


class Tag(Base):
    __tablename__ = 'tag'

    tag_id = Column('tag_id', Integer, primary_key=True)
    name = Column('name', Text, unique=True)

    movies = relationship(
        Movie,
        secondary=t_tag_link,
        primaryjoin=t_tag_link.c.tag_id == tag_id,
        secondaryjoin=and_(
            t_tag_link.c.media_id == Movie.id_movie,
            t_tag_link.c.media_type == 'movie'),
        backref="tags",
        sync_backref=False,
        viewonly=True
    )

    tv_shows = relationship(
        TvShow,
        secondary=t_tag_link,
        primaryjoin=t_tag_link.c.tag_id == tag_id,
        secondaryjoin=and_(
            t_tag_link.c.media_id == TvShow.id_show,
            t_tag_link.c.media_type == 'tvshow'),
        backref="tags",
        sync_backref=False,
        viewonly=True
    )

    music_videos = relationship(
        MusicVideo,
        secondary=t_tag_link,
        primaryjoin=t_tag_link.c.tag_id == tag_id,
        secondaryjoin=and_(
            t_tag_link.c.media_id == MusicVideo.id_m_video,
            t_tag_link.c.media_type == 'musicvideo'),
        backref="tags",
        sync_backref=False,
        viewonly=True
    )


class TvShowCount(Base):
    __tablename__ = 'tvshowcounts'

    id_show = Column('idShow', Integer, ForeignKey("tvshow.idShow"),
                     primary_key=True)
    last_played = Column('lastPlayed', Text)
    total_count = Column('totalCount', Integer)
    watchedcount = Column('watchedcount', Integer)
    total_seasons = Column('totalSeasons', Integer)
    date_added = Column('dateAdded', Text)

    tv_show = relationship(
        "TvShow", backref=backref("tv_show_count", uselist=False))


class Uniqueid(Base):
    __tablename__ = 'uniqueid'
    __table_args__ = (
        Index('ix_uniqueid2', 'media_type', 'value'),
        Index('ix_uniqueid1', 'media_id', 'media_type', 'type')
    )

    uniqueid_id = Column('uniqueid_id', Integer, primary_key=True)
    media_id = Column('media_id', Integer)
    media_type = Column('media_type', Text)
    value = Column('value', Text)
    type = Column('type', Text)

    movie = relationship(
        Movie,
        primaryjoin=and_(
            Movie.id_movie == foreign(media_id),
            media_type == 'movie'),
        backref="uniqueids",
        sync_backref=False,
        viewonly=True
    )

    tv_show = relationship(
        TvShow,
        primaryjoin=and_(
            TvShow.id_show == foreign(media_id),
            media_type == 'tvshow'),
        backref="uniqueids",
        sync_backref=False,
        viewonly=True
    )

    episode = relationship(
        Episode,
        primaryjoin=and_(
            Episode.id_episode == foreign(media_id),
            media_type == 'episode'),
        backref="uniqueids",
        sync_backref=False,
        viewonly=True
    )

    music_video = relationship(
        MusicVideo,
        primaryjoin=and_(
            MusicVideo.id_m_video == foreign(media_id),
            media_type == 'musicvideo'),
        backref="uniqueids",
        sync_backref=False,
        viewonly=True
    )


class EpisodeView(Base):
    __tablename__ = 'episode_view'

    id_episode = Column('idEpisode', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    title = Column('c00', Text)
    plot_summary = Column('c01', Text)
    c02 = Column('c02', Text)
    rating_id = Column('c03', Text, ForeignKey('rating.rating_id'))
    writer_text = Column('c04', Text)
    first_aired = Column('c05', Text)
    thumbnail_url = Column('c06', Text)
    thumbnail_url_spoof = Column('c07', Text)
    c08 = Column('c08', Text)
    runtime = Column('c09', Text)
    director_text = Column('c10', Text)
    production_code = Column('c11', Text)
    season_number = Column('c12', String(24))
    episode_number = Column('c13', String(24))
    original_title = Column('c14', Text)
    season_number_specials_sorting = Column('c15', Text)
    episode_number_specials_sorting = Column('c16', Text)
    bookmark = Column('c17', String(24))
    path_to_file = Column('c18', Text)
    id_path = Column('c19', Text, ForeignKey('path.idPath'))
    unique_scraper_id = Column('c20', Text, ForeignKey('uniqueid.uniqueid_id'))
    c21 = Column('c21', Text)
    c22 = Column('c22', Text)
    c23 = Column('c23', Text)
    id_show = Column('idShow', Integer, ForeignKey('tvshow.idShow'))
    userrating = Column('userrating', Integer)
    id_season = Column('idSeason', Integer, ForeignKey('seasons.idSeason'))
    str_file_name = Column('strFileName', Text)
    str_path = Column('strPath', Text)
    play_count = Column('playCount', Integer)
    last_played = Column('lastPlayed', Text)
    date_added = Column('dateAdded', Text)
    str_title = Column('strTitle', Text)
    genre = Column('genre', Text)
    studio = Column('studio', Text)
    premiered = Column('premiered', Text)
    mpaa = Column('mpaa', Text)
    resume_time_in_seconds = Column('resumeTimeInSeconds', Float)
    total_time_in_seconds = Column('totalTimeInSeconds', Float)
    player_state = Column('playerState', Text)
    rating = Column('rating', Float)
    votes = Column('votes', Integer)
    rating_type = Column('rating_type', Text)
    uniqueid_value = Column('uniqueid_value', Text)
    uniqueid_type = Column('uniqueid_type', Text)


class MovieView(Base):
    __tablename__ = 'movie_view'

    id_movie = Column('idMovie', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    title = Column('c00', Text)
    plot_summary = Column('c01', Text)
    plot_outline = Column('c02', Text)
    tagline = Column('c03', Text)
    c04 = Column('c04', Text)
    rating_id = Column('c05', Text, ForeignKey('rating.rating_id'))
    writers_text = Column('c06', Text)
    c07 = Column('c07', Text)
    image_url = Column('c08', Text)
    unique_scraper_id = Column('c09', Text, ForeignKey('uniqueid.uniqueid_id'))
    title_for_sorting = Column('c10', Text)
    runtime = Column('c11', Text)
    mpaa_rating = Column('c12', Text)
    imdb_ranking = Column('c13', Text)
    genre_text = Column('c14', Text)
    director_text = Column('c15', Text)
    original_title = Column('c16', Text)
    thumb_url_spoof = Column('c17', Text)
    studio_text = Column('c18', Text)
    trailer_url = Column('c19', Text)
    fan_art_url = Column('c20', Text)
    country_text = Column('c21', Text)
    path_to_file = Column('c22', Text)
    id_path = Column('c23', Text, ForeignKey('path.idPath'))
    id_set = Column('idSet', Integer, ForeignKey('sets.idSet'))
    userrating = Column('userrating', Integer)
    premiered = Column('premiered', Text)
    str_set = Column('strSet', Text)
    str_set_overview = Column('strSetOverview', Text)
    str_file_name = Column('strFileName', Text)
    str_path = Column('strPath', Text)
    play_count = Column('playCount', Integer)
    last_played = Column('lastPlayed', Text)
    date_added = Column('dateAdded', Text)
    resume_time_in_seconds = Column('resumeTimeInSeconds', Float)
    total_time_in_seconds = Column('totalTimeInSeconds', Float)
    player_state = Column('playerState', Text)
    rating = Column('rating', Float)
    votes = Column('votes', Integer)
    rating_type = Column('rating_type', Text)
    uniqueid_value = Column('uniqueid_value', Text)
    uniqueid_type = Column('uniqueid_type', Text)


class MusicVideoView(Base):
    __tablename__ = 'musicvideo_view'

    id_m_video = Column('idMVideo', Integer, primary_key=True)
    id_file = Column('idFile', Integer, ForeignKey('files.idFile'))
    title = Column('c00', Text)
    thumb_url = Column('c01', Text)
    thumb_url_spoof = Column('c02', Text)
    c03 = Column('c03', Text)
    runtime = Column('c04', Text)
    director_text = Column('c05', Text)
    studio_text = Column('c06', Text)
    c07 = Column('c07', Text)
    plot_summary = Column('c08', Text)
    album = Column('c09', Text)
    artist = Column('c10', Text)
    genre_text = Column('c11', Text)
    track = Column('c12', Text)
    path_to_file = Column('c13', Text)
    id_path = Column('c14', Text, ForeignKey('path.idPath'))
    c15 = Column('c15', Text)
    c16 = Column('c16', Text)
    c17 = Column('c17', Text)
    c18 = Column('c18', Text)
    c19 = Column('c19', Text)
    c20 = Column('c20', Text)
    c21 = Column('c21', Text)
    c22 = Column('c22', Text)
    c23 = Column('c23', Text)
    userrating = Column('userrating', Integer)
    premiered = Column('premiered', Text)
    str_file_name = Column('strFileName', Text)
    str_path = Column('strPath', Text)
    play_count = Column('playCount', Integer)
    last_played = Column('lastPlayed', Text)
    date_added = Column('dateAdded', Text)
    resume_time_in_seconds = Column('resumeTimeInSeconds', Float)
    total_time_in_seconds = Column('totalTimeInSeconds', Float)
    player_state = Column('playerState', Text)


class SeasonView(Base):
    __tablename__ = 'season_view'

    id_season = Column('idSeason', Integer, primary_key=True)
    id_show = Column('idShow', Integer)
    season = Column('season', Integer)
    name = Column('name', Text)
    userrating = Column('userrating', Integer)
    str_path = Column('strPath', Text)
    show_title = Column('showTitle', Text)
    plot = Column('plot', Text)
    premiered = Column('premiered', Text)
    genre = Column('genre', Text)
    studio = Column('studio', Text)
    mpaa = Column('mpaa', Text)
    episodes = Column('episodes', Integer)
    play_count = Column('playCount', Integer)
    aired = Column('aired', Text)


class TvShowView(Base):
    __tablename__ = 'tvshow_view'

    id_show = Column('idShow', Integer, primary_key=True)
    title = Column('c00', Text)
    plot_summary = Column('c01', Text)
    status = Column('c02', Text)
    c03 = Column('c03', Text)
    rating_id = Column('c04', Text, ForeignKey('rating.rating_id'))
    first_aired = Column('c05', Text)
    thumbnail_url = Column('c06', Text)
    c07 = Column('c07', Text)
    genre_text = Column('c08', Text)
    original_title = Column('c09', Text)
    episode_guide_url = Column('c10', Text)
    fan_art_url = Column('c11', Text)
    unique_scraper_id = Column('c12', Text, ForeignKey('uniqueid.uniqueid_id'))
    content_rating = Column('c13', Text)
    studio_text = Column('c14', Text)
    title_for_sorting = Column('c15', Text)
    trailer = Column('c16', Text)
    c17 = Column('c17', Text)
    c18 = Column('c18', Text)
    c19 = Column('c19', Text)
    c20 = Column('c20', Text)
    c21 = Column('c21', Text)
    c22 = Column('c22', Text)
    c23 = Column('c23', Text)
    userrating = Column('userrating', Integer)
    duration = Column('duration', Integer)
    id_parent_path = Column('idParentPath', Integer)
    str_path = Column('strPath', Text)
    date_added = Column('dateAdded', Text)
    last_played = Column('lastPlayed', Text)
    total_count = Column('totalCount', Integer)
    watchedcount = Column('watchedcount', Integer)
    total_seasons = Column('totalSeasons', Integer)
    rating = Column('rating', Float)
    votes = Column('votes', Integer)
    rating_type = Column('rating_type', Text)
    uniqueid_value = Column('uniqueid_value', Text)
    uniqueid_type = Column('uniqueid_type', Text)


class TvShowLinkPathMinView(Base):
    __tablename__ = 'tvshowlinkpath_minview'

    id_show = Column('idShow', Integer, primary_key=True)
    id_path = Column('idPath', Integer)
