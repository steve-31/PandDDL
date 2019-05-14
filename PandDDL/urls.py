"""PDDL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

app_name = 'PandDDL'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.authlogin, name='login'),
    url(r'^changepassword/(?P<uid>[0-9]+)/$', views.changePassword, name='changePassword'),
    url(r'^logout/$', views.authlogout, name='logout'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^admin/$', views.adminPage, name='adminPage'),
    url(r'^admin/league/$', views.AdminLeague, name='adminLeague'),
    url(r'^admin/league/setactivelg/(?P<lg_id>[0-9]+)/$', views.setActiveLeague, name='setActiveLeague'),
    url(r'^admin/league/delete/(?P<lge_id>[0-9]+)/$', views.LeagueDelete, name='LeagueDelete'),
    url(r'^admin/league/finishseason/(?P<lge_id>[0-9]+)/$', views.FinishSeason, name='FinishSeason'),
    url(r'^admin/division/$', views.AdminDivision, name='adminDivision'),
    url(r'^admin/division/delete/(?P<div_id>[0-9]+)/$', views.AdminDivisionDelete, name='adminDivisionDelete'),
    url(r'^admin/team/$', views.AdminTeam, name='adminTeam'),
    url(r'^admin/team/pay/(?P<tid>[0-9]+)/$', views.AdminTeamPayLeagueFee, name='adminTeamLeagueFee'),
    url(r'^admin/team/delete/(?P<tid>[0-9]+)/$', views.AdminTeamDelete, name='adminTeamDelete'),
    url(r'^admin/team/points_deduction/delete/(?P<pd_id>[0-9]+)/$', views.AdminTeamPointsDeductionDelete, name='adminTeamDeductionDelete'),
    url(r'^admin/team/password_change/(?P<uid>[0-9]+)/$', views.AdminTeamPasswordChange, name='adminTeamPasswordChange'),
    url(r'^admin/player/$', views.AdminPlayer, name='adminPlayer'),
    url(r'^admin/player/team_select/$', views.AdminPlayerSelectTeam, name='adminPlayerSelectTeam'),
    url(r'^admin/player/captain/(?P<pid>[0-9]+)/$', views.AdminPlayerSetCaptain, name='adminPlayerSetCaptain'),
    url(r'^admin/player/delete/(?P<pid>[0-9]+)/$', views.AdminPlayerDelete, name='adminPlayerDelete'),
    url(r'^admin/fixture/$', views.AdminFixture, name='adminFixture'),
    url(r'^admin/fixture/upload/$', views.fixtureUpload, name='fixtureUpload'),
    url(r'^admin/fixture/delete/(?P<fid>[0-9]+)/$', views.AdminFixtureDelete, name='adminFixtureDelete'),
    url(r'^admin/fixture/edit/(?P<fid>[0-9]+)/$', views.AdminFixtureEdit, name='adminFixtureEdit'),
    url(r'^admin/KeyDates/$', views.AdminKeyDates, name='adminKeyDates'),
    url(r'^admin/KeyDates/delete/(?P<kid>[0-9]+)/$', views.AdminKeyDateDelete, name='adminKeyDateDelete'),
    url(r'^admin/announcements/$', views.AdminAnnouncements, name='adminAnnouncements'),
    url(r'^admin/announcements/show/(?P<aid>[0-9]+)/$', views.AdminAnnouncementDisplay, name='adminAnnouncementShow'),
    url(r'^admin/announcements/hide/(?P<aid>[0-9]+)/$', views.AdminAnnouncementHide, name='adminAnnouncementHide'),
    url(r'^admin/announcements/delete/(?P<aid>[0-9]+)/$', views.AdminAnnouncementDelete, name='adminAnnouncementDelete'),
    url(r'^admin/cupcomps/$', views.AdminCupComps, name='adminCupComps'),
    url(r'^admin/playercomps/$', views.AdminPlayerComps, name='adminPlayerComps'),
    url(r'^admin/playercomps/delete/(?P<cid>[0-9]+)/$', views.AdminPlayerCompsDelete, name='adminPlayerCompDelete'),
    url(r'^admin/photo_galleries/$', views.AdminPhotoGalleries, name='adminPhotoGalleries'),
    url(r'^admin/photo_galleries/delete/(?P<pid>[0-9]+)/$', views.AdminPhotoGalleriesDelete, name='adminPhotoGalleriesDelete'),
    url(r'^admin/AGM/$', views.AdminAGMminutes, name='adminAGMminutes'),
    url(r'^galleries/$', views.photoGalleries, name="photoGalleries"),
    url(r'^galleries/(?P<gid>[0-9]+)/$', views.gallery, name="gallery"),
    url(r'^archive/$', views.archive, name="archive"),
    url(r'^AGM/$', views.AGMminutesList, name="AGMminutesList"),
    url(r'^AGM/(?P<path>.*)/$', views.AGMMinutesDownload, name="fileDownload"),
    url(r'^admin/file/delete/(?P<fid>[0-9]+)', views.FileDelete, name="FileDelete"),
    url(r'^admin/AGM/delete/(?P<aid>[0-9]+)/$', views.AdminAGMminutesDelete, name="AGMminutesDelete"),
    url(r'^fixtures/print/(?P<lge_gender>[A-Za-z0-9\']+)_(?P<lge_season>[A-Za-z0-9]+)_(?P<lge_year>[0-9]+)/div(?P<div_id>[A-Za-z0-9]+)/$', views.printFixtures, name='printFixtures'),
    url(r'^fixtures/print/(?P<team_id>[0-9]+)/$', views.printTeamFixtures, name='printTeamFixtures'),
    url(r'^(?P<lge_gender>[A-Za-z0-9\']+)_(?P<lge_season>[A-Za-z0-9]+)_(?P<lge_year>[0-9]+)/$', views.league, name='league'),
    url(r'^(?P<lge_gender>[A-Za-z0-9\']+)_(?P<lge_season>[A-Za-z0-9]+)_(?P<lge_year>[0-9]+)/div(?P<div_id>[A-Za-z0-9]+)/$', views.division, name='division'),
    url(r'^(?P<lge_gender>[A-Za-z0-9\']+)_(?P<lge_season>[A-Za-z0-9]+)_(?P<lge_year>[0-9]+)/(?P<cup_id>[A-Za-z0-9 ]+)/$', views.cupComp, name='cup'),
    url(r'^fixture/(?P<fix_id>[0-9]+)/$', views.fixture, name='fixture'),
    url(r'^team/(?P<tid>[0-9\']+)/$',views.team, name='team'),
    url(r'^contact/$',views.contactUs, name='contactUs'),
    url(r'^reportproblem/$', views.reportProblem, name='reportProblem'),
    url(r'^admin/completeissue/(?P<pid>[0-9]+)/$', views.completeIssue, name='completeIssue'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


