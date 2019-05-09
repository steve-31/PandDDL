# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django import forms
from .models import *

# Register your models here.

class LeagueGrpAdminForm(forms.ModelForm):
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=(('Men\'s','Men\'s'),('Ladies','Ladies')))
    season = forms.ChoiceField(widget=forms.RadioSelect, choices=(('Summer','Summer'),('Winter','Winter')))

class LeagueGrpAdmin(admin.ModelAdmin):
    list_display = ('leagueName',)    
    form = LeagueGrpAdminForm
    
    def leagueName(self, obj):
        return ("%s %s League %s" % (obj.gender, obj.season, obj.displayyear))
    leagueName.short_description = "Name"
admin.site.register(LeagueGrp, LeagueGrpAdmin)



class LeagueModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s %s League %s" % (obj.gender, obj.season, obj.displayyear))

class DivisionAdminForm(forms.ModelForm):
    leaguegrp = LeagueModelNameField(queryset=LeagueGrp.objects.all()) 
    class Meta:
        model = Division
        fields = ('name', 'leaguegrp', 'singlesbestoflegs', 'doublesbestoflegs', )

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'leagueName', 'singlesbestoflegs', 'doublesbestoflegs', )
    list_filter = ('leaguegrp__gender', 'leaguegrp__year', 'leaguegrp__season')
    form = DivisionAdminForm
      
    def leagueName(self, obj):
        return ("%s %s League %s" % (obj.leaguegrp.gender, obj.leaguegrp.season, obj.leaguegrp.year))
    leagueName.short_description = "League"
admin.site.register(Division, DivisionAdmin)


class CupCompModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s" % (obj.name))

class CupCompRoundAdminForm(forms.ModelForm):
    comp = CupCompModelNameField(queryset=CupComp.objects.all()) 
    class Meta:
        model = CupRound
        fields = ('name', 'roundnumber', 'comp')

class CupCompRoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'roundnumber', 'compName')
    form = CupCompRoundAdminForm
    
    def compName(self, obj):
        return ("%s" % (obj.comp.name))
    compName.short_description = "Cup Comp"
admin.site.register(CupRound, CupCompRoundAdmin)



class CupCompAdminForm(forms.ModelForm):
    leaguegrp = LeagueModelNameField(queryset=LeagueGrp.objects.all()) 
    class Meta:
        model = Division
        fields = ('name', 'leaguegrp')

class CupCompAdmin(admin.ModelAdmin):
    list_display = ('name', 'leagueName')
    form = CupCompAdminForm
    
    def leagueName(self, obj):
        return ("%s %s League %s" % (obj.leaguegrp.gender, obj.leaguegrp.season, obj.leaguegrp.year))
    leagueName.short_description = "League"
admin.site.register(CupComp, CupCompAdmin)


class DivisionModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s %s League %s Division %s" % (obj.leaguegrp.gender, obj.leaguegrp.season, obj.leaguegrp.year, obj.name))

class TeamAdminForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea)
    division = DivisionModelNameField(queryset=Division.objects.all())
    class Meta:
        model = Team
        fields = ('name', 'address', 'division', 'newpassword', 'admin')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'leagueName', 'divisionName')
    list_filter = ('division__leaguegrp__gender', 'division__leaguegrp__year', 'division__leaguegrp__season', 'division__name')
    form = TeamAdminForm
    
    def leagueName(self, obj):
        return ("%s %s League %s" % (obj.division.leaguegrp.gender, obj.division.leaguegrp.season, obj.division.leaguegrp.year))
    leagueName.short_description = "League"
    
    def divisionName(self, obj):
        return ("Division %s" % (obj.division.name))
    divisionName.short_description = "Division"
admin.site.register(Team, TeamAdmin)




class TeamModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s" % (obj.name))

class PlayerAdminForm(forms.ModelForm):
    team = TeamModelNameField(queryset=Team.objects.all())
    class Meta:
        model = Player
        exclude = ()

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('playerName', 'teamName', 'iscaptain')
    list_filter = ('team__name','iscaptain')
    form = PlayerAdminForm
    
    def playerName(self, obj):
        return ("%s %s" % (obj.firstname, obj.surname))
    playerName.short_description = "Player"
    
    def teamName(self, obj):
        return ("%s" % (obj.team.name))
    teamName.short_description = "Team"
admin.site.register(Player, PlayerAdmin)


class PlayerModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s %s" % (obj.firstname, obj.surname))

class TopFinishForm(forms.ModelForm):
    player = PlayerModelNameField(queryset=Player.objects.all())
    class Meta:
        model = TopFinish
        fields = ('player', 'finish')

class TopFinishAdmin(admin.ModelAdmin):
    list_display = ('playerName', 'Team', 'Division', 'finish')
    form = TopFinishForm
    
    
    def playerName(self, obj):
        return ("%s %s" % (obj.player.firstname, obj.player.surname))
    playerName.short_description = "Player"
    
    def Team(self, obj):
        return ("%s" % (obj.player.team.name))
    
    def Division(self, obj):
        return ("%s %s League %s Division %s" % (obj.player.team.division.leaguegrp.gender, obj.player.team.division.leaguegrp.season, obj.player.team.division.leaguegrp.year, obj.player.team.division.name))
admin.site.register(TopFinish, TopFinishAdmin)

class MaximumAdmin(admin.ModelAdmin):
    list_display = ('playerName', 'Team', 'fixtureName')
    
    
    def playerName(self, obj):
        return ("%s %s" % (obj.player.firstname, obj.player.surname))
    playerName.short_description = "Player"
    
    def Team(self, obj):
        return ("%s" % (obj.player.team.name))
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.fixture.hometeam.name, obj.fixture.homescore, obj.fixture.awayscore, obj.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(Maximum, MaximumAdmin)

class FixtureAdminForm(forms.ModelForm):
    hometeam = TeamModelNameField(queryset=Team.objects.all())
    awayteam = TeamModelNameField(queryset=Team.objects.all())
    division = DivisionModelNameField(queryset=Division.objects.all())
    class Meta:
        model = Fixture
        fields = ('date', 'hometeam', 'awayteam', 'division', 'homescore', 'awayscore', 'resultentered', 'resultenteredby', 'resultverified')

class FixtureAdmin(admin.ModelAdmin):
    list_display = ('fixtureName', 'divisionName', 'date', 'resultentered', 'resultverified')
    form = FixtureAdminForm
    
    def resultEnteredBy(self, obj):
        return ("%s" % obj.resultenteredby.username)
    
    def divisionName(self, obj):
        return ("Division %s" % (obj.division.name))
    divisionName.short_description = "Division"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.hometeam.name, obj.homescore, obj.awayscore, obj.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(Fixture, FixtureAdmin)


class CupRoundModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s %s %s %s" % (obj.comp.leaguegrp.gender, obj.comp.name, obj.comp.leaguegrp.year, obj.name))

class CupFixtureAdminForm(forms.ModelForm):
    hometeam = TeamModelNameField(queryset=Team.objects.all())
    awayteam = TeamModelNameField(queryset=Team.objects.all())
    round = CupRoundModelNameField(queryset=CupRound.objects.all())
    class Meta:
        model = CupFixture
        fields = ('date', 'hometeam', 'awayteam', 'round', 'homescore', 'awayscore', 'resultentered', 'resultenteredby', 'resultverified')

class CupFixtureAdmin(admin.ModelAdmin):
    list_display = ('fixtureName', 'cupRoundName', 'cupName', 'date', 'resultentered', 'resultverified')
    form = CupFixtureAdminForm
    
    def resultEnteredBy(self, obj):
        return ("%s" % obj.resultenteredby.username)
    
    def cupName(self, obj):
        return ("%s" % (obj.round.comp.name))
    cupName.short_description = "Cup"
    
    def cupRoundName(self, obj):
        return ("%s" % (obj.round.name))
    cupRoundName.short_description = "Round"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.hometeam.name, obj.homescore, obj.awayscore, obj.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(CupFixture, CupFixtureAdmin)


class FixtureModelNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s - %s" % (obj.hometeam.name, obj.awayteam.name))

class SinglesMatchAdminForm(forms.ModelForm):
    fixture = FixtureModelNameField(queryset=Fixture.objects.all())
    homeplayer = PlayerModelNameField(queryset=Player.objects.all())
    awayplayer = PlayerModelNameField(queryset=Player.objects.all())

class SinglesMatchAdmin(admin.ModelAdmin):
    list_display = ('matchName', 'fixtureName')
    form = SinglesMatchAdminForm
    
    def matchName(self, obj):
        homeplayer_firstname = "WALKOVER" if obj.homeplayer == None else obj.homeplayer.firstname
        homeplayer_surname = "" if obj.homeplayer == None else obj.homeplayer.surname
        awayplayer_firstname = "WALKOVER" if obj.awayplayer == None else obj.awayplayer.firstname
        awayplayer_surname = "" if obj.awayplayer == None else obj.awayplayer.surname
        return ("%s %s %s - %s %s %s" % (homeplayer_firstname, homeplayer_surname, obj.homescore, obj.awayscore, awayplayer_firstname, awayplayer_surname))
    matchName.short_description = "Match"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.fixture.hometeam.name, obj.fixture.homescore, obj.fixture.awayscore, obj.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(SinglesMatch, SinglesMatchAdmin)



class DoublesMatchAdminForm(forms.ModelForm):
    fixture = FixtureModelNameField(queryset=Fixture.objects.all())
    homeplayer1 = PlayerModelNameField(queryset=Player.objects.all())
    awayplayer1 = PlayerModelNameField(queryset=Player.objects.all())
    homeplayer2 = PlayerModelNameField(queryset=Player.objects.all())
    awayplayer2 = PlayerModelNameField(queryset=Player.objects.all())

class DoublesMatchAdmin(admin.ModelAdmin):
    list_display = ('matchName', 'fixtureName')
    form = DoublesMatchAdminForm
    
    def matchName(self, obj):
        return ("%s %s & %s %s %s - %s %s %s & %s %s" % (obj.homeplayer1.firstname, obj.homeplayer1.surname, obj.homeplayer2.firstname, obj.homeplayer2.surname, obj.homescore, obj.awayscore, obj.awayplayer1.firstname, obj.awayplayer1.surname, obj.awayplayer2.firstname, obj.awayplayer2.surname))
    matchName.short_description = "Match"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.fixture.hometeam.name, obj.fixture.homescore, obj.fixture.awayscore, obj.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(DoublesMatch, DoublesMatchAdmin)


class DoublesResultAdmin(admin.ModelAdmin):
    list_display = ('playerName','matchName', 'fixtureName', 'played', 'win', 'lose', 'legs_for', 'legs_against')
    
    def playerName(self, obj):
        return ("%s %s" % (obj.player.firstname, obj.player.surname)) 
    
    def matchName(self, obj):
        return ("%s %s & %s %s %s - %s %s %s & %s %s" % (obj.match.homeplayer1.firstname, obj.match.homeplayer1.surname, obj.match.homeplayer2.firstname, obj.match.homeplayer2.surname, obj.match.homescore, obj.match.awayscore, obj.match.awayplayer1.firstname, obj.match.awayplayer1.surname, obj.match.awayplayer2.firstname, obj.match.awayplayer2.surname))
    matchName.short_description = "Match"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.match.fixture.hometeam.name, obj.match.fixture.homescore, obj.match.fixture.awayscore, obj.match.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(DoublesResult, DoublesResultAdmin)

class TriplesMatchAdmin(admin.ModelAdmin):
    list_display = ('matchName', 'fixtureName')
    
    def matchName(self, obj):
        return ("%s %s & %s %s & %s %s %s - %s %s %s & %s %s & %s %s" % (obj.homeplayer1.firstname, obj.homeplayer1.surname, obj.homeplayer2.firstname, obj.homeplayer2.surname, obj.homeplayer3.firstname, obj.homeplayer3.surname, obj.homescore, obj.awayscore, obj.awayplayer1.firstname, obj.awayplayer1.surname, obj.awayplayer2.firstname, obj.awayplayer2.surname, obj.awayplayer3.firstname, obj.awayplayer3.surname))
    matchName.short_description = "Match"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.fixture.hometeam.name, obj.fixture.homescore, obj.fixture.awayscore, obj.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(TriplesMatch, TriplesMatchAdmin)


class TriplesResultAdmin(admin.ModelAdmin):
    list_display = ('playerName','matchName', 'fixtureName', 'played', 'win', 'lose', 'legs_for', 'legs_against')
    
    def playerName(self, obj):
        return ("%s %s" % (obj.player.firstname, obj.player.surname)) 
    
    def matchName(self, obj):
        return ("%s %s & %s %s & %s %s %s - %s %s %s & %s %s & %s %s" % (obj.match.homeplayer1.firstname, obj.match.homeplayer1.surname, obj.match.homeplayer2.firstname, obj.match.homeplayer2.surname, obj.match.homeplayer3.firstname, obj.match.homeplayer3.surname, obj.match.homescore, obj.match.awayscore, obj.match.awayplayer1.firstname, obj.match.awayplayer1.surname, obj.match.awayplayer2.firstname, obj.match.awayplayer2.surname, obj.match.awayplayer3.firstname, obj.match.awayplayer3.surname))
    matchName.short_description = "Match"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.match.fixture.hometeam.name, obj.match.fixture.homescore, obj.match.fixture.awayscore, obj.match.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(TriplesResult, TriplesResultAdmin)


class SinglesResultAdmin(admin.ModelAdmin):
    list_display = ('playerName','matchName', 'fixtureName', 'played', 'win', 'lose', 'legs_for', 'legs_against')
    
    def playerName(self, obj):
        return ("%s %s" % (obj.player.firstname, obj.player.surname)) 
    
    def matchName(self, obj):
        return (" %s %s %s - %s %s %s" % (obj.match.homeplayer.firstname, obj.match.homeplayer.surname, obj.match.homescore, obj.match.awayscore, obj.match.awayplayer.firstname, obj.match.awayplayer.surname))
    matchName.short_description = "Match"
    
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.match.fixture.hometeam.name, obj.match.fixture.homescore, obj.match.fixture.awayscore, obj.match.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(SinglesResult, SinglesResultAdmin)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('fixtureName',)
    def fixtureName(self, obj):
        return ("%s %s - %s %s" % (obj.fixture.hometeam.name, obj.fixture.homescore, obj.fixture.awayscore, obj.fixture.awayteam.name))
    fixtureName.short_description = "Fixture"
admin.site.register(Result, ResultAdmin)

admin.site.register(NoOfAnnouncements)
admin.site.register(AGMminutes)

class ArchiveSeasonAdmin(admin.ModelAdmin):
    list_display = ('display_name',)
admin.site.register(ArchiveSeason, ArchiveSeasonAdmin)

class ArchiveSeasonField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ("%s %s" % (obj.gender, obj.display_name))

class ArchiveDivisionAdminForm(forms.ModelForm):
    season = ArchiveSeasonField(queryset=ArchiveSeason.objects.all())
    
class ArchiveDivisionAdmin(admin.ModelAdmin):
    list_display = ('division_name', 'winner', 'runner_up',)
    form = ArchiveDivisionAdminForm
admin.site.register(ArchiveDivision, ArchiveDivisionAdmin)
admin.site.register(ArchiveComp)