# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import IntegerField, related
import datetime

# Create your models here.
class LeagueGrp(models.Model):
    gender=models.CharField(max_length=100)
    season=models.CharField(max_length=100)
    year=models.IntegerField()
    displayyear=models.CharField(max_length=10)
    active=models.BooleanField(default=True)
    finished=models.BooleanField(default=False)
    class Meta:
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'
    
class Division(models.Model):
    name=models.CharField(max_length=1)
    leaguegrp=models.ForeignKey(LeagueGrp)
    singlesbestoflegs=IntegerField()
    doublesbestoflegs=IntegerField()
    
class Team(models.Model):
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=300)
    division=models.ForeignKey(Division)
    pubphoneno=models.CharField(max_length=20)
    captainphoneno=models.CharField(max_length=20)
    paidleaguefee=models.BooleanField(default=False)
    admin=models.ForeignKey(User)
    newpassword=models.BooleanField()
    
class Player(models.Model):
    firstname=models.CharField(max_length=100)
    surname=models.CharField(max_length=100)
    team=models.ForeignKey(Team)
    iscaptain=models.BooleanField()
    dateadded=models.DateField()
    
class Fixture(models.Model):
    hometeam=models.ForeignKey(Team, related_name="home")
    awayteam=models.ForeignKey(Team, related_name="away")
    homescore=models.IntegerField(default=0)
    awayscore=models.IntegerField(default=0)
    date=models.DateField()
    resultentered=models.BooleanField(default=False)
    resultenteredby=models.ForeignKey(User, blank=True, null=True)
    resultverified=models.BooleanField(default=False)
    resultsheet=models.ImageField(upload_to='resultSheets', null=True, blank=True)
    walkover=models.BooleanField(default=False)
    division=models.ForeignKey(Division)

class Result(models.Model):
    team=models.ForeignKey(Team, related_name='team')
    opposition=models.ForeignKey(Team, related_name='opposition')
    fixture=models.ForeignKey(Fixture)
    played=models.IntegerField(default=1)
    win=models.IntegerField()
    lose=models.IntegerField()
    legs_for=models.IntegerField()
    legs_against=models.IntegerField()
    points=models.IntegerField()
    
class TopFinish(models.Model):
    player=models.ForeignKey(Player)
    finish=models.IntegerField()
    fixture=models.ForeignKey(Fixture)
    class Meta:
        verbose_name = 'Top Finish'
        verbose_name_plural = 'Top Finishes'

class TopScore(models.Model):
    player=models.ForeignKey(Player)
    score=models.IntegerField()
    fixture=models.ForeignKey(Fixture)
        
class Maximum(models.Model):
    player=models.ForeignKey(Player)
    fixture=models.ForeignKey(Fixture)

class SinglesMatch(models.Model):
    fixture=models.ForeignKey(Fixture)
    homeplayer=models.ForeignKey(Player, related_name="home", null=True, blank=True)
    awayplayer=models.ForeignKey(Player, related_name="away", null=True, blank=True)
    homescore=models.IntegerField(default=0)
    awayscore=models.IntegerField(default=0)
    class Meta:
        verbose_name = 'Singles Match'
        verbose_name_plural = 'Singles Matches'

class SinglesResult(models.Model):
    match=models.ForeignKey(SinglesMatch)
    player=models.ForeignKey(Player, related_name='singlesplayer')
    opposition=models.ForeignKey(Player, related_name='opposition', null=True, blank=True)
    played=models.IntegerField(default=1)
    win=models.IntegerField()
    lose=models.IntegerField()
    legs_for=models.IntegerField()
    legs_against=models.IntegerField()
    
class DoublesMatch(models.Model):
    fixture=models.ForeignKey(Fixture)
    homeplayer1=models.ForeignKey(Player, related_name="home1")
    homeplayer2=models.ForeignKey(Player, related_name="home2")
    awayplayer1=models.ForeignKey(Player, related_name="away1")
    awayplayer2=models.ForeignKey(Player, related_name="away2")
    homescore=models.IntegerField(default=0)
    awayscore=models.IntegerField(default=0)
    class Meta:
        verbose_name = 'Doubles Match'
        verbose_name_plural = 'Doubles Matches'
        
class DoublesResult(models.Model):
    match=models.ForeignKey(DoublesMatch)
    player=models.ForeignKey(Player, related_name='doublesplayer')
    partner=models.ForeignKey(Player, related_name='partner')
    opposition1=models.ForeignKey(Player, related_name='opposition1')
    opposition2=models.ForeignKey(Player, related_name='opposition2')
    played=models.IntegerField(default=1)
    win=models.IntegerField()
    lose=models.IntegerField()
    legs_for=models.IntegerField()
    legs_against=models.IntegerField()
    
class TriplesMatch(models.Model):
    fixture=models.ForeignKey(Fixture)
    homeplayer1=models.ForeignKey(Player, related_name="thome1")
    homeplayer2=models.ForeignKey(Player, related_name="thome2")
    homeplayer3=models.ForeignKey(Player, related_name="thome3")
    awayplayer1=models.ForeignKey(Player, related_name="taway1")
    awayplayer2=models.ForeignKey(Player, related_name="taway2")
    awayplayer3=models.ForeignKey(Player, related_name="taway3")
    homescore=models.IntegerField(default=0)
    awayscore=models.IntegerField(default=0)
    class Meta:
        verbose_name = 'Triples Match'
        verbose_name_plural = 'Triples Matches'
        
class TriplesResult(models.Model):
    match=models.ForeignKey(TriplesMatch)
    player=models.ForeignKey(Player, related_name='triplesplayer')
    partner1=models.ForeignKey(Player, related_name='partner1')
    partner2=models.ForeignKey(Player, related_name='partner2')
    opposition1=models.ForeignKey(Player, related_name='topposition1')
    opposition2=models.ForeignKey(Player, related_name='topposition2')
    opposition3=models.ForeignKey(Player, related_name='topposition3')
    played=models.IntegerField(default=1)
    win=models.IntegerField()
    lose=models.IntegerField()
    legs_for=models.IntegerField()
    legs_against=models.IntegerField()

class PointsDeduction(models.Model):
    team=models.ForeignKey(Team)
    points=models.IntegerField()
    reason=models.CharField(max_length=500)
    date=models.DateField()
    
class KeyDate(models.Model):
    date=models.DateField()
    time=models.TimeField()
    name=models.CharField(max_length=400)
    location=models.CharField(max_length=300)
    league=models.ForeignKey(LeagueGrp)
    
class CupComp(models.Model):
    name=models.CharField(max_length=100)
    leaguegrp=models.ForeignKey(LeagueGrp)

class CupRound(models.Model):
    name=models.CharField(max_length=150)
    roundnumber=models.IntegerField()
    comp=models.ForeignKey(CupComp)

class CupFixture(models.Model):
    hometeam=models.ForeignKey(Team, related_name="cuphome")
    awayteam=models.ForeignKey(Team, related_name="cupaway")
    homescore=models.IntegerField()
    awayscore=models.IntegerField()
    date=models.DateField()
    resultentered=models.BooleanField(default=False)
    resultenteredby=models.ForeignKey(User, blank=True, null=True)
    resultverified=models.BooleanField(default=False)
    walkover=models.BooleanField(default=False)
    round=models.ForeignKey(CupRound)

class FixtureFile(models.Model):
    file=models.FileField(upload_to="fixtures")
    
class Photo(models.Model):
    photo=models.ImageField(upload_to="photo_galleries")
    
class PhotoGallery(models.Model):
    name=models.CharField(max_length=200)
    date=models.DateField()
    photos=models.ManyToManyField(Photo, related_name="photos")
    coverphoto=models.ForeignKey(Photo, related_name="coverphoto", null=True)
    
class Announcement(models.Model):
    date=models.DateTimeField()
    heading=models.TextField()
    text=models.TextField(null=True)
    picture=models.ImageField(upload_to="announcements", blank=True, null=True)
    gallery=models.ForeignKey(PhotoGallery, null=True)
    showonhome=models.BooleanField()

class NoOfAnnouncements(models.Model):
    number=models.IntegerField()

class Competition(models.Model):
    keydate=models.ForeignKey(KeyDate)
    comptype=models.CharField(max_length=100)
    winner1=models.ForeignKey(Player, related_name="winner1", null=True, blank=True)
    winner2=models.ForeignKey(Player, related_name="winner2", null=True, blank=True)
    winner3=models.ForeignKey(Player, related_name="winner3", null=True, blank=True)
    runnerup1=models.ForeignKey(Player, related_name="runnerup1", null=True, blank=True)
    runnerup2=models.ForeignKey(Player, related_name="runnerup2", null=True, blank=True)
    runnerup3=models.ForeignKey(Player, related_name="runnerup3", null=True, blank=True)
    
class Proposal(models.Model):
    entered_by=models.CharField(max_length=100)
    proposal=models.CharField(max_length=1000)
    
class AGMminutes(models.Model):
    date=models.DateField()
    location=models.CharField(max_length=200)
    minutes=models.FileField(upload_to="AGMminutes", blank=True, null=True)
    proposals=models.ManyToManyField(Proposal)
    
class MiscFile(models.Model):
    date_uploaded=models.DateTimeField()
    description=models.CharField(max_length=300)
    file=models.FileField(upload_to="files")

class Problem(models.Model):
    date_reported=models.DateTimeField()
    reporter_email=models.CharField(max_length=300, blank=True, null=True)
    problem_desc=models.CharField(max_length=2000)
    completed=models.BooleanField()

class ArchiveSeason(models.Model):
    display_name=models.CharField(max_length=50)
    year=models.IntegerField()
    gender=models.CharField(max_length=20)
    season=models.CharField(max_length=20)

class ArchiveDivision(models.Model):
    season=models.ForeignKey(ArchiveSeason)
    division_name=models.CharField(max_length=20)
    winner=models.CharField(max_length=100)
    runner_up=models.CharField(max_length=100)

class ArchiveComp(models.Model):
    season=models.ForeignKey(ArchiveSeason)
    comp_name=models.CharField(max_length=400)
    winner1=models.CharField(max_length=200, null=True, blank=True)
    winner2=models.CharField(max_length=200, null=True, blank=True)
    winner3=models.CharField(max_length=200, null=True, blank=True)
    runnerup1=models.CharField(max_length=200, null=True, blank=True)
    runnerup2=models.CharField(max_length=200, null=True, blank=True)
    runnerup3=models.CharField(max_length=200, null=True, blank=True)
    