# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
from django.conf import settings
import pandas
import xlrd
import math
import datetime
import logging
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.db.models import Q, Count, Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse, Http404
from operator import itemgetter 
from .models import *


# Create your views here.

logger = logging.getLogger(__name__)

def handler403(request, *args, **argv):
    return render(request, 'PandDDL/403.html', status=403)

def handler404(request, *args, **argv):
    return render(request, 'PandDDL/404.html', status=404)

def handler500(request, *args, **argv):
    return render(request, 'PandDDL/500.html', status=500)

def home(request):
    leaguegrps = LeagueGrp.objects.filter(active=True)
    mens_divs = Division.objects.filter(leaguegrp__in=leaguegrps, leaguegrp__gender='Men\'s').order_by('name')
    ladies_divs = Division.objects.filter(leaguegrp__in=leaguegrps, leaguegrp__gender='Ladies').order_by('name')
    noofannouncements = NoOfAnnouncements.objects.get(pk=1)
    announcements = Announcement.objects.filter(showonhome=True).order_by('-date')[:noofannouncements.number]
    galleries = PhotoGallery.objects.all()
    
    context = {
        "leaguegrps": leaguegrps,
        "announcements": announcements,
        "galleries": galleries,
        "mens_divs": mens_divs,
        "ladies_divs": ladies_divs,
    }
    
    return render(request, 'PandDDL/home.html', context)

def contactUs(request):
    context = {}
    
    return render(request, 'PandDDL/contact.html', context)

def reportProblem(request):
    report_success = False
    if 'problem_reported' in request.session:
        if request.session['problem_reported']:
            report_success = True
    
    try:
        del request.session['problem_reported']
    except:
        pass
    
    if request.method == "POST":
        problemdesc = request.POST.get('problem-description')
        reporter = request.POST.get('reporter-email')
        newproblem = Problem(date_reported=datetime.datetime.now(), reporter_email=reporter, problem_desc=problemdesc, completed=False)
        newproblem.save()
        request.session['problem_reported'] = True
        
        return redirect('PandDDL:reportProblem')
        
    
    context = {
        "report_success": report_success,
    }
    
    return render(request, 'PandDDL/reportproblem.html', context)

def completeIssue(request, pid):
    issue = Problem.objects.get(pk=pid)
    issue.completed=True
    issue.save()
    return redirect('PandDDL:adminPage')

def authlogin(request):
    
    if request.method == "POST":
        postusername = request.POST.get('username')
        postpassword = request.POST.get('password')
        user = authenticate(username=postusername, password=postpassword)
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            if not user.is_staff:
                user_team = Team.objects.get(admin__pk=user.pk)
                if user_team.newpassword:
                    return redirect('PandDDL:changePassword', user.pk)
            return redirect('PandDDL:home')
        else:
            # No backend authenticated the credentials
            return redirect('PandDDL:login')
    
    context = {
    
    }
    
    return render(request, 'PandDDL/login.html', context)

def changePassword(request, uid):
    user_test = User.objects.get(pk=uid)
    if request.user != user_test:
        raise PermissionDenied
    if request.method == "POST":
        
        user = authenticate(username=user_test.username, password=request.POST.get('old-password'))
        if user is not None and request.POST.get('change-password') and request.POST.get('change-password') == request.POST.get('change-password-confirm'):
            user.set_password(request.POST.get('change-password'))
            team = Team.objects.get(admin=user)
            team.newpassword = False
            team.save()
            user.save()
            login(request, user)
            return redirect('PandDDL:home')
        else: 
            return redirect('PandDDL:changePassword', user.pk)
    
    context = {
    
    }
    
    return render(request, 'PandDDL/changePassword.html', context)

def authlogout(request):
    logout(request)
    
    return redirect('PandDDL:home')

def league(request, lge_gender, lge_season, lge_year):
    lge = LeagueGrp.objects.get(gender=lge_gender, season=lge_season, year=lge_year)
    divs = Division.objects.filter(leaguegrp=lge.pk)
    cups = CupComp.objects.filter(leaguegrp=lge.pk)
    
    context = {
        "league": lge,
        "divs": divs,
        "cups": cups,
    }
            
    return render(request, 'PandDDL/league.html', context)

def CompetitionPage(request):
    results = Competition.objects.filter(keydate__league__active=True).exclude(winner1=None).order_by('keydate__date')
    fixtures = Competition.objects.filter(keydate__league__active=True, winner1=None).order_by('keydate__date')
    
    context = {
        "cup_results": results,
        "cup_fixtures": fixtures,
    }
    
    return render(request, 'PandDDL/cup.html', context)

def division(request, lge_gender, lge_season, lge_year, div_id):
    lge = LeagueGrp.objects.get(gender=lge_gender, season=lge_season, year=lge_year)
    div = Division.objects.get(leaguegrp=lge.pk, name=div_id)
    div_teams = Team.objects.filter(division=div.pk)
    points_deductions = PointsDeduction.objects.filter(team__in=div_teams).order_by('date', 'team__name')
    no_of_teams_form = 5
    points_deductions_teams = []
    for d in points_deductions:
        points_deductions_teams.append(d.team.name)
    div_table = Result.objects.filter(team__division=div.pk, fixture__resultverified=True).values('team__name', 'team__id').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against'), Cpoints=Sum('points')).order_by('-Cpoints', '-Clegs_for', 'Clegs_ags', 'team__name')
    div_table_f = []
    for team in div_teams:
        try:
            table_team = div_table.get(team=team)
        except Result.DoesNotExist:
            table_team = None
        points_deducted = 0
        for d in points_deductions:
            if team == d.team:
                points_deducted += d.points
        if table_team != None:
            teamresults = Result.objects.filter(team=team, fixture__resultverified=True).order_by('-fixture__date')[:no_of_teams_form][::-1]
            teamobj = {"teamName": table_team['team__name'], "teamid": table_team['team__id'], "Cplayed": table_team['Cplayed'], "Cwon": table_team['Cwon'], "Clost": table_team['Clost'], "Clegs_for": table_team['Clegs_for'], "Clegs_ags": table_team['Clegs_ags'], "Cpoints": table_team['Cpoints']-points_deducted, "results": teamresults}
        else:
            teamobj = {"teamName": team.name, "teamid": team.id, "division": team.division, "Cplayed": 0, "Cwon": 0, "Clost": 0, "Clegs_for": 0, "Clegs_ags": 0, "Cpoints": 0-points_deducted}
        div_table_f.append(teamobj)
        div_table_f = sorted(div_table_f, key=itemgetter('Clegs_ags', 'teamName'))
        div_table_f = sorted(div_table_f, key=itemgetter('Cpoints', 'Clegs_for'), reverse=True)
        
    div_players = Player.objects.filter(team__in=div_teams)
    maximum_table= Maximum.objects.filter(player__team__division=div.pk, fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Count("id")).order_by('-id__count', 'player__surname')
    finishes_table = TopFinish.objects.filter(player__in=div_players, fixture__resultverified=True).order_by('-finish', 'fixture__date')
    scores_table = TopScore.objects.filter(player__in=div_players, fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Sum("score")).order_by('-score__sum', 'player__surname')
    fixture_dates = Fixture.objects.filter(division=div).values('date').order_by('date').distinct()
    fixtures = Fixture.objects.filter(hometeam__in=div_teams).order_by('date')
    teams_with_bye = []
    for d in fixture_dates:
        fixtures_on_date = fixtures.filter(date=d['date'])
        teams_on_date = []
        for fixture in fixtures_on_date:
            teams_on_date.append(fixture.hometeam)
            teams_on_date.append(fixture.awayteam)
        for team in div_teams:
            if not team in teams_on_date:
                teams_with_bye.append({"date":d['date'], "team":team})
    top_singles_table = SinglesResult.objects.filter(player__team__in=div_teams, match__fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against')).order_by('-Cwon', '-Clegs_for', 'Clegs_ags', 'player__surname')
    top_singles_table = top_singles_table.filter(Cwon__gt=0)[:10]
    top_doubles_table = DoublesResult.objects.filter(player__team__in=div_teams, match__fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against')).order_by('-Cwon', '-Clegs_for', 'Clegs_ags', 'player__surname')
    top_doubles_table = top_doubles_table.filter(Cwon__gt=0)[:10]
    top_triples_table = TriplesResult.objects.filter(player__team__in=div_teams, match__fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against')).order_by('-Cwon', '-Clegs_for', 'Clegs_ags', 'player__surname')
    top_triples_table = top_triples_table.filter(Cwon__gt=0)[:10]
    today = datetime.date.today()
    
    if len(fixture_dates) % 2 == 0:
        length = len(fixture_dates)/2
    else:
        length = (len(fixture_dates)+1)/2
    
    first_half_fixtures = fixture_dates[:length]
    second_half_fixtures = fixture_dates[length:]
    
    context = {
        "lge": lge,
        "div": div,
        "div_table": div_table_f,
        "div_teams": div_teams,
        "maximum_table": maximum_table,
        "finishes_table": finishes_table,
        "scores_table": scores_table,
        "fixture_dates": fixture_dates,
        "fixtures": fixtures,
        "top_singles_table": top_singles_table,
        "top_doubles_table": top_doubles_table,
        "top_triples_table": top_triples_table,
        "today": today,
        "first_half_fixtures": first_half_fixtures,
        "second_half_fixtures": second_half_fixtures,
        "teams_with_bye": teams_with_bye,
        "points_deductions": points_deductions,
        "points_deductions_teams":points_deductions_teams,
    }
            
    return render(request, 'PandDDL/division.html', context)

def fixture(request, fix_id):
    fixture = Fixture.objects.get(pk=fix_id)
    hometeam_players = Player.objects.filter(team=fixture.hometeam)
    awayteam_players = Player.objects.filter(team=fixture.awayteam)
    usertest = request.user == fixture.hometeam.admin or request.user.is_staff
    single_matches = SinglesMatch.objects.filter(fixture=fixture.pk)
    double_matches = DoublesMatch.objects.filter(fixture=fixture.pk)
    triple_matches = TriplesMatch.objects.filter(fixture=fixture.pk)
    singleslegstowin = 0 if not fixture.division.singlesbestoflegs else ((int(fixture.division.singlesbestoflegs) + 1) / 2)
    doubleslegstowin = 0 if not fixture. division.doublesbestoflegs else ((int(fixture.division.doublesbestoflegs) + 1) / 2)
    tripleslegstowin = 0 if not fixture.division.triplesbestoflegs else ((int(fixture.division.triplesbestoflegs) + 1) / 2)
    beforegame = True if datetime.date.today() < fixture.date else False
    hometeamlast5games = Result.objects.filter(team=fixture.hometeam.pk, fixture__resultverified=True).order_by('fixture__date')[:5]
    awayteamlast5games = Result.objects.filter(team=fixture.awayteam.pk, fixture__resultverified=True).order_by('fixture__date')[:5]
    maximums = Maximum.objects.filter(fixture=fixture.pk).order_by('player__team__name', 'player__surname')
    top_finishes = TopFinish.objects.filter(fixture=fixture.pk).order_by('player__team__name', 'player__surname')
    top_scores = TopScore.objects.filter(fixture=fixture.pk).order_by('player__team__name', 'player__surname')
    
    context = {
        "fixture": fixture,
        "home_team_players": hometeam_players,
        "away_team_players": awayteam_players,
        "usertest": usertest,
        "single_matches": single_matches,
        "double_matches": double_matches,
        "triple_matches": triple_matches,
        "singleslegstowin": singleslegstowin,
        "doubleslegstowin": doubleslegstowin,
        "tripleslegstowin": tripleslegstowin,
        "beforegame": beforegame,
        "hometeamlast5games": hometeamlast5games,
        "awayteamlast5games": awayteamlast5games,
        "maximums": maximums,
        "topFinishes": top_finishes,
        "topScores": top_scores,
    }
    
    if request.method == "POST":
        if request.POST.get('home-team-concede'):
            ConcedeFixture(fixture, "home", request.user)
            
        if request.POST.get('away-team-concede'): 
            ConcedeFixture(fixture, "away", request.user)
            
        if request.POST.get('results-entered'):
            errors = False
            homescore = 0
            awayscore = 0
            singlesmatches = []
            singlesresults = []
            doublesmatches = []
            doublesresults = []
            triplesmatches = []
            triplesresults = []
            topscores = []
            topfinishes = []
            maximums = []
            
            if fixture.division.leaguegrp.gender == "Men's":
                for i in range(1,6):
                    singlesmatches, singlesresults, homescore, awayscore, singleserrors = SinglesFixture(fixture, request.POST.get('singles-home-player-'+str(i)), request.POST.get('singles-away-player-'+str(i)), request.POST.get('singles-home-score-'+str(i)), request.POST.get('singles-away-score-'+str(i)), homescore, awayscore, singlesmatches, singlesresults)
                    if singleserrors:
                        errors = True
                        
                for i in range(1,3):
                    doublesmatches, doublesresults, homescore, awayscore, doubleserrors = DoublesFixture(fixture, request.POST.get('doubles-home-player-1-'+str(i)), request.POST.get('doubles-home-player-2-'+str(i)), request.POST.get('doubles-away-player-1-'+str(i)), request.POST.get('doubles-away-player-2-'+str(i)), request.POST.get('doubles-home-score-'+str(i)), request.POST.get('doubles-away-score-'+str(i)), homescore, awayscore, doublesmatches, doublesresults)
                    if doubleserrors:
                        errors = True
                    
                for i in range(1,7):
                    maximums, maximumerrors = CreateMaximum(fixture, request.POST.get('maximums-1-'+str(i)), maximums)
                    if maximumerrors:
                        errors = True
                    maximums, maximumerrors = CreateMaximum(fixture, request.POST.get('maximums-2-'+str(i)), maximums)
                    if maximumerrors:
                        errors = True
                    
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-1-'+str(i)), request.POST.get('finishes-amount-1-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-2-'+str(i)), request.POST.get('finishes-amount-2-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
                    
                        
            else:           # Ladies Fixture
                for i in range(1,5):
                    singlesmatches, singlesresults, homescore, awayscore, singleserrors = SinglesFixture(fixture, request.POST.get('singles-home-player-'+str(i)), request.POST.get('singles-away-player-'+str(i)), request.POST.get('singles-home-score-'+str(i)), request.POST.get('singles-away-score-'+str(i)), homescore, awayscore, singlesmatches, singlesresults)
                    if singleserrors:
                        errors = True
                        
                for i in range(1,3):
                    doublesmatches, doublesresults, homescore, awayscore, doubleserrors = DoublesFixture(fixture, request.POST.get('doubles-home-player-1-'+str(i)), request.POST.get('doubles-home-player-2-'+str(i)), request.POST.get('doubles-away-player-1-'+str(i)), request.POST.get('doubles-away-player-2-'+str(i)), request.POST.get('doubles-home-score-'+str(i)), request.POST.get('doubles-away-score-'+str(i)), homescore, awayscore, doublesmatches, doublesresults)
                    if doubleserrors:
                        errors = True
                        
                for i in range(1,2):
                    triplesmatches, triplesresults, homescore, awayscore, tripleserrors = TriplesFixture(fixture, request.POST.get('triples-home-player-1-'+str(i)), request.POST.get('triples-home-player-2-'+str(i)), request.POST.get('triples-home-player-3-'+str(i)), request.POST.get('triples-away-player-1-'+str(i)), request.POST.get('triples-away-player-2-'+str(i)), request.POST.get('triples-away-player-3-'+str(i)), request.POST.get('triples-home-score-'+str(i)), request.POST.get('triples-away-score-'+str(i)), homescore, awayscore, triplesmatches, triplesresults)
                    if tripleserrors:
                        errors = True
                
                for i in range(1,7):
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-1-'+str(i)), request.POST.get('score-score-1-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-2-'+str(i)), request.POST.get('score-score-2-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-3-'+str(i)), request.POST.get('score-score-3-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-4-'+str(i)), request.POST.get('score-score-4-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-1-'+str(i)), request.POST.get('finishes-amount-1-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-2-'+str(i)), request.POST.get('finishes-amount-2-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
            
            if not errors:
                if fixture.resultentered:
                    ResetFixture(fixture)
                        
                for s in singlesmatches:
                    s.save()
                for s in singlesresults:
                    newmatch = SinglesMatch.objects.get(pk=s.match.id)
                    s.match = newmatch
                    s.save()
                for d in doublesmatches:
                    d.save()
                for d in doublesresults:
                    newmatch = DoublesMatch.objects.get(pk=d.match.id)
                    d.match = newmatch
                    d.save()
                for t in triplesmatches:
                    t.save()
                for t in triplesresults:
                    newmatch = TriplesMatch.objects.get(pk=t.match.id)
                    t.match = newmatch
                    t.save()
                for m in maximums:
                    m.save()
                for t in topfinishes:
                    t.save()
                for t in topscores:
                    t.save()
                
                fixture.homescore = homescore
                fixture.awayscore = awayscore
                fixture.resultentered = True
                fixture.resultenteredby = request.user
                
                homewin = 1 if fixture.homescore > fixture.awayscore else 0
                homelose = 0 if fixture.homescore > fixture.awayscore else 1
                homepoints = homewin * 2
                awaywin = 1 if fixture.awayscore > fixture.homescore else 0
                awaylose = 0 if fixture.awayscore > fixture.homescore else 1
                awaypoints = awaywin * 2
                
                homeresult = Result(team=fixture.hometeam, opposition=fixture.awayteam, fixture=fixture, win=homewin, lose=homelose, legs_for=fixture.homescore, legs_against=fixture.awayscore, points=homepoints)
                homeresult.save()
                awayresult = Result(team=fixture.awayteam, opposition=fixture.hometeam, fixture=fixture, win=awaywin, lose=awaylose, legs_for=fixture.awayscore, legs_against=fixture.homescore, points=awaypoints)
                awayresult.save()
                
                if request.FILES:
                    fixture.resultsheet = request.FILES['result-sheet']
            
                fixture.save()
                
        if fixture.resultentered: 
            if request.POST.get('result-verified') or fixture.resultenteredby.is_staff: 
                fixture.resultverified = True
                fixture.save()
        elif request.POST.get('result-rejected') == "True":
            results = Result.objects.filter(fixture=fixture)
            for r in results:
                print r.win
                r.delete()
            singles_matches = SinglesMatch.objects.filter(fixture=fixture)
            for s in singles_matches:
                singles_result = SinglesResult.objects.filter(match=s)
                for sr in singles_result:
                    sr.delete()
                s.delete()
            doubles_matches = DoublesMatch.objects.filter(fixture=fixture)
            for d in doubles_matches:
                doubles_result = DoublesResult.objects.filter(match=d)
                for dr in doubles_result:
                    dr.delete()
                d.delete()
            triples_matches = TriplesMatch.objects.filter(fixture=fixture)
            for t in triples_matches:
                triples_result = TriplesResult.objects.filter(match=t)
                for tr in triples_result:
                    tr.delete()
                t.delete()
                
            maximums = Maximum.objects.filter(fixture=fixture)
            for m in maximums:
                m.delete()
            top_finishes = TopFinish.objects.filter(fixture=fixture)
            for tf in top_finishes:
                tf.delete()
            top_scores = TopScore.objects.filter(fixture=fixture)
            for ts in top_scores:
                ts.delete()
            fixture.walkover = False
            fixture.homescore = 0
            fixture.awayscore = 0
            fixture.resultentered = False
            fixture.resultenteredby = None
            fixture.resultverified = False
            fixture.save()
        
        return redirect('PandDDL:fixture', fixture.pk)   
        
    if fixture.division.leaguegrp.gender == "Men's":
        return render(request, 'PandDDL/mensfixture.html', context)
    else:
        return render(request, 'PandDDL/ladiesfixture.html', context)

def team(request, tid):
    team = Team.objects.get(pk=tid)
    fixtures = Fixture.objects.filter(Q(hometeam=team.pk) | Q(awayteam=team.pk), Q(resultverified=False)).order_by('date')
    fixture_dates = Fixture.objects.filter(division=team.division).values('date').order_by('date').distinct()
    allfixtures = Fixture.objects.filter(hometeam__division=team.division).order_by('date')
    results = Result.objects.filter(team=team.pk, fixture__resultverified=True).order_by('fixture__date')
    players = Player.objects.filter(team=team.pk)
    singlesresults = SinglesResult.objects.filter(player__in=players, match__fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against')).order_by('-Cwon', '-Clegs_for', 'Clegs_ags', 'player__surname')
    singlesresults_f = []
    playersaddedafterstart = False
    if len(fixture_dates) == 0:
        seasonstartdate = 0
    else:
        seasonstartdate = fixture_dates[len(fixture_dates)/2]['date']
    for player in players:
        playerafterstart = False
        if seasonstartdate != 0 and player.dateadded > seasonstartdate:
            playersaddedafterstart = True
            playerafterstart = True
        try:
            sresultplayer = singlesresults.get(player=player)
        except SinglesResult.DoesNotExist:
            sresultplayer = None
        if sresultplayer != None:
            splayerobj = {"player": sresultplayer['player'], "playerFirstName": sresultplayer['player__firstname'], "playerSurname": sresultplayer['player__surname'], "Cplayed": sresultplayer['Cplayed'], "Cwon": sresultplayer['Cwon'], "Clost": sresultplayer['Clost'], "Clegs_for": sresultplayer['Clegs_for'], "Clegs_ags": sresultplayer['Clegs_ags'], "addedafterstart": playerafterstart}
        else:
            splayerobj = {"player": player.pk, "playerFirstName": player.firstname, "playerSurname": player.surname, "Cplayed": 0, "Cwon": 0, "Clost": 0, "Clegs_for": 0, "Clegs_ags": 0, "addedafterstart": playerafterstart}
        singlesresults_f.append(splayerobj)
        singlesresults_f = sorted(singlesresults_f, key=itemgetter('Clegs_ags', 'playerSurname'))
        singlesresults_f = sorted(singlesresults_f, key=itemgetter('Cwon', 'Clegs_for'), reverse=True)
        
    doublesresults = DoublesResult.objects.filter(player__in=players, match__fixture__resultverified=True).values('player', 'player__firstname', 'player__surname', 'player__team__name').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against')).order_by('-Cwon', '-Clegs_for', 'Clegs_ags', 'player__surname')
    doublesresults_f = []
    for player in players:
        try:
            dresultplayer = doublesresults.get(player=player)
        except DoublesResult.DoesNotExist:
            dresultplayer = None
        if dresultplayer != None:
            dplayerobj = {"player": dresultplayer['player'], "playerFirstName": dresultplayer['player__firstname'], "playerSurname": dresultplayer['player__surname'], "Cplayed": dresultplayer['Cplayed'], "Cwon": dresultplayer['Cwon'], "Clost": dresultplayer['Clost'], "Clegs_for": dresultplayer['Clegs_for'], "Clegs_ags": dresultplayer['Clegs_ags']}
        else:
            dplayerobj = {"player": player.pk, "playerFirstName": player.firstname, "playerSurname": player.surname, "Cplayed": 0, "Cwon": 0, "Clost": 0, "Clegs_for": 0, "Clegs_ags": 0}
        doublesresults_f.append(dplayerobj)
        doublesresults_f = sorted(doublesresults_f, key=itemgetter('Clegs_ags', 'playerSurname'))
        doublesresults_f = sorted(doublesresults_f, key=itemgetter('Cwon', 'Clegs_for'), reverse=True)
        
    try:
        captain = Player.objects.get(team=team.pk, iscaptain=True)
    except Player.DoesNotExist:
        captain = None
        
    dates = []
    for newdate in fixtures:
        d = {"pk": newdate.pk, "date": newdate.date, "hometeam": newdate.hometeam, "homescore": newdate.homescore, "awayscore": newdate.awayscore, "awayteam": newdate.awayteam}
        dates.append(d)
    
    for date in results:
        d = {"pk": date.fixture.pk, "date": date.fixture.date, "hometeam": date.fixture.hometeam, "homescore": date.fixture.homescore, "awayscore": date.fixture.awayscore, "awayteam": date.fixture.awayteam, "lose": date.lose, "win": date.win}
        dates.append(d)
    
    for d in fixture_dates:
        fixtures_on_date = allfixtures.filter(date=d['date'])
        teams_on_date = []
        for fixture in fixtures_on_date:
            teams_on_date.append(fixture.hometeam)
            teams_on_date.append(fixture.awayteam)
        if not team in teams_on_date:
            print teams_on_date
            dates.append({"date":d['date'], "team":team, "bye": True})
        
    dates = sorted(dates, key=itemgetter('date'))
    
    context = {
        "team": team,
        "players": players,
        "singlesResults": singlesresults_f,
        "doublesResults": doublesresults_f,
        "captain": captain,
        "fixtures": fixtures,
        "results": results,
        "dates": dates,
        "playersaddedafterstart": playersaddedafterstart,
    }
    
    return render(request, 'PandDDL/team.html', context)

def rules(request):
    
    context = {
    
    }
    
    return render(request, 'PandDDL/rules.html', context)

def printFixtures(request, lge_gender, lge_season, lge_year, div_id):
    lge = LeagueGrp.objects.get(gender=lge_gender, season=lge_season, year=lge_year)
    div = Division.objects.get(leaguegrp=lge.pk, name=div_id)
    div_teams = Team.objects.filter(division=div.pk)
    fixture_dates = Fixture.objects.filter(division=div).values('date').order_by('date').distinct()
    fixtures = Fixture.objects.filter(hometeam__in=div_teams).order_by('date', 'hometeam__name')
    key_dates = KeyDate.objects.filter(league=lge.pk).order_by('date', 'time', 'name')
    today = datetime.date.today()
    
    teams_with_bye = []
    for d in fixture_dates:
        fixtures_on_date = fixtures.filter(date=d['date'])
        teams_on_date = []
        for fixture in fixtures_on_date:
            teams_on_date.append(fixture.hometeam)
            teams_on_date.append(fixture.awayteam)
        for team in div_teams:
            if not team in teams_on_date:
                teams_with_bye.append({"date":d['date'], "team":team})
    
    if len(fixture_dates) % 2 == 0:
        length = len(fixture_dates)/2
    else:
        length = (len(fixture_dates)+1)/2
    
    first_half_fixtures = fixture_dates[:length]
    second_half_fixtures = fixture_dates[length:]
    
    context = {
        "lge": lge,
        "div": div,
        "fixture_dates": fixture_dates,
        "fixtures": fixtures,
        "first_half_fixtures": first_half_fixtures,
        "second_half_fixtures": second_half_fixtures,
        "key_dates": key_dates,
        "today":today,
        "teams_with_bye": teams_with_bye,
    }
    
    return render(request, 'PandDDL/printFixtures.html', context)

def printTeamFixtures(request, team_id):
    team = Team.objects.get(pk=team_id)
    lge = LeagueGrp.objects.get(pk=team.division.leaguegrp.pk)
    fixture_dates = Fixture.objects.filter(division=team.division).values('date').order_by('date').distinct()
    fixtures = Fixture.objects.filter(Q(hometeam=team.pk) | Q(awayteam=team.pk), Q(resultverified=False)).order_by('date')
    allfixtures = Fixture.objects.filter(hometeam__division=team.division).order_by('date')
    results = Result.objects.filter(team=team.pk, fixture__resultverified=True).order_by('fixture__date')
    key_dates = KeyDate.objects.filter(league=lge.pk).order_by('date', 'time')
    dates = []
    for date in fixtures:
        d = {"date": date.date, "hometeam": date.hometeam, "homescore": date.homescore, "awayscore": date.awayscore, "awayteam": date.awayteam}
        dates.append(d)
    
    for date in results:
        d = {"date": date.fixture.date, "hometeam": date.fixture.hometeam, "homescore": date.fixture.homescore, "awayscore": date.fixture.awayscore, "awayteam": date.fixture.awayteam, "win": date.win, "lose": date.lose}
        dates.append(d)
        
    for date in key_dates:
        d = {"date": date.date, "time": date.time, "name": date.name, "location": date.location}
        dates.append(d)
    
    for d in fixture_dates:
        fixtures_on_date = allfixtures.filter(date=d['date'])
        teams_on_date = []
        for fixture in fixtures_on_date:
            teams_on_date.append(fixture.hometeam)
            teams_on_date.append(fixture.awayteam)
        if not team in teams_on_date:
            dates.append({"date":d['date'], "team":team, "bye": True})
        
    dates = sorted(dates, key=itemgetter('date'))
    
        
    context = {
        "team": team,
        "lge": lge,
        "dates": dates,
    }
    
    return render(request, 'PandDDL/printTeamFixtures.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def adminPage(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    results_not_entered = Fixture.objects.filter(date__lte=datetime.date.today(), resultentered=False).order_by('date')
    mens_results_not_entered = results_not_entered.filter(division__leaguegrp__gender="Men's")
    ladies_results_not_entered = results_not_entered.filter(division__leaguegrp__gender="Ladies")
    results_not_verified = Fixture.objects.filter(resultentered=True, resultverified=False).order_by('date')
    mens_results_not_verified = results_not_verified.filter(division__leaguegrp__gender="Men's")
    ladies_results_not_verified = results_not_verified.filter(division__leaguegrp__gender="Ladies")
    all_teams = Team.objects.filter(division__leaguegrp__in=active_leagues)
    player_comps = Competition.objects.filter(keydate__league__active=True, winner1=None, keydate__date__lte=datetime.datetime.today())
    all_players = Player.objects.filter(team__division__leaguegrp__in=active_leagues).order_by('firstname')
    all_open_issues = Problem.objects.filter(completed=False)
    
    if request.method == "POST":
        if request.POST.get('key-date-name'):
            newdate = KeyDate(date=request.POST.get('key-date-date'), time=request.POST.get('key-date-time'), name=request.POST.get('key-date-name'), location=request.POST.get('key-date-location'), league=LeagueGrp.objects.get(pk=request.POST.get('key-date-league')))
            newdate.save()
        
        
        return redirect('PandDDL:adminPage')
            
    context = {
        "active_leagues": active_leagues,
        "mens_results_not_entered": mens_results_not_entered,
        "ladies_results_not_entered": ladies_results_not_entered,
        "mens_results_not_verified": mens_results_not_verified,
        "ladies_results_not_verified": ladies_results_not_verified,
        "all_teams": all_teams,
        "player_comps": player_comps,
        "all_players":all_players,
        "reported_problems": all_open_issues,
    }
    
    return render(request, 'PandDDL/adminPage.html', context)

def fixtureUpload(request):
    if request.method == 'POST':
        fixturefile = FixtureFile(file=request.FILES['fixtures-file'])
        fixturefile.save()
        league = LeagueGrp.objects.get(pk=request.POST.get('fixture-file-league'))
        df = pandas.read_excel(fixturefile.file.path)
        for fix in range(0,len(df['Home Team'])):
            same_fixture = Fixture.objects.filter(Q(date=df['Date'][fix]), Q(hometeam__name__iexact=df['Home Team'][fix]) | Q(awayteam__name__iexact=df['Home Team'][fix]) | Q(hometeam__name__iexact=df['Away Team'][fix]) | Q(awayteam__name__iexact=df['Away Team']))
            for f in same_fixture:
                f.delete()
            fixture = Fixture(hometeam=Team.objects.get(name__iexact=df['Home Team'][fix], division=Division.objects.get(name__iexact=df['Division'][fix], leaguegrp=league)), awayteam=Team.objects.get(name__iexact=df['Away Team'][fix], division=Division.objects.get(name__iexact=df['Division'][fix], leaguegrp=league)), date=df['Date'][fix], division=Division.objects.get(name__iexact=df['Division'][fix], leaguegrp=league))
            fixture.save()
    return redirect('PandDDL:adminFixture')

def photoGalleries(request):
    
    galleries = PhotoGallery.objects.all()
    
    context = {
        "galleries": galleries,
    }
    
    return render(request, 'PandDDL/photoGalleries.html', context)

def gallery(request, gid):
    
    gallery = PhotoGallery.objects.get(pk=gid)
    
    context = {
        "gallery": gallery,
    }
    
    return render(request, 'PandDDL/photoGallery.html', context)

def archive(request):
    mens_archive_leagues = ArchiveSeason.objects.filter(gender="Men's").order_by('-year', '-season')
    mens_archive_divs = ArchiveDivision.objects.filter(season__in=mens_archive_leagues).order_by('division_name')
    mens_player_comps = ArchiveComp.objects.filter(season__in=mens_archive_leagues)
    ladies_archive_leagues = ArchiveSeason.objects.filter(gender="Ladies").order_by('-year', '-season')
    ladies_archive_divs = ArchiveDivision.objects.filter(season__in=ladies_archive_leagues).order_by('division_name')
    ladies_player_comps = ArchiveComp.objects.filter(season__in=ladies_archive_leagues)
    
    context = {
        "mens_archive_leagues": mens_archive_leagues,
        "mens_archive_divs": mens_archive_divs,
        "mens_player_comps": mens_player_comps,
        "ladies_archive_leagues": ladies_archive_leagues,
        "ladies_archive_divs": ladies_archive_divs,
        "ladies_player_comps": ladies_player_comps,
    }
    
    return render(request, 'PandDDL/archive.html', context)

def AGMminutesList(request):
    
    all_minutes = AGMminutes.objects.all().order_by('date')
    files = MiscFile.objects.all()
    
    proposal_success = False
    if 'proposal_submit' in request.session:
        if request.session['proposal_submit']:
            proposal_success = True
    
    try:
        del request.session['proposal_submit']
    except:
        pass
    
    if request.method == "POST":
        agm = AGMminutes.objects.get(pk=request.POST.get("agmid"))
        proposal = Proposal(entered_by=request.POST.get("proposer-name"), proposal=request.POST.get("proposal-text"))
        proposal.save()
        agm.proposals.add(proposal)
        request.session['proposal_submit'] = True
        return redirect('PandDDL:AGMminutesList')
    
    context = {
        "all_minutes": all_minutes,
        "proposal_success": proposal_success,
        "files": files,
    }
    
    return render(request, 'PandDDL/AGMminutesList.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AGMminutesAdd(request):
    
    if request.method == "POST":
        mins = AGMminutes(date=request.POST.get('agm-date'), minutes=request.POST.get('agm-minutes'))
        mins.save()
        return redirect('PandDDL:AGMminutes', mins.pk)
    
    context = {

    }
    
    return render(request, 'PandDDL/AGMminutesAdd.html', context)

def AGMminute(request, min_id):
    
    minutes = AGMminutes.objects.get(pk=min_id)
    
    context = {
        "minutes": minutes,
    }
    
    return render(request, 'PandDDL/AGMminutes.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminLeague(request):
    all_leagues = LeagueGrp.objects.all().order_by('-year', '-season')
    mens_leagues = all_leagues.filter(gender="Men's")
    ladies_leagues = all_leagues.filter(gender='Ladies')
    
    if request.method == 'POST':
        if request.POST.get('new-league-gender'):
            if request.POST.get('new-league-season') == "Winter":
                year = int(request.POST.get('new-league-year'))
                next_year = year - 1999
                display_year = str(year) + "-" + str(next_year)
            else:
                display_year = request.POST.get('new-league-year')
            newleague = LeagueGrp(gender=request.POST.get('new-league-gender'), season=request.POST.get('new-league-season'), year=request.POST.get('new-league-year'), displayyear=display_year, active=False)
            newleague.save()
            
        
        
        return redirect('PandDDL:adminLeague')
    
    
    context = {
        "all_leagues": all_leagues,
        "mens_leagues": mens_leagues,
        "ladies_leagues": ladies_leagues,
    }
    
    return render(request, 'PandDDL/adminLeague.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def setActiveLeague(request, lg_id):
    
    newactivelg = LeagueGrp.objects.get(pk=lg_id)
    try:
        oldactivelg = LeagueGrp.objects.get(gender=newactivelg.gender, active=True)
        oldactivelg.active = False
        oldactivelg.save()
    except LeagueGrp.DoesNotExist:
        pass
    newactivelg.active = True
    newactivelg.finished = False
    newactivelg.save()
    
    return redirect('PandDDL:adminLeague')

@permission_required('request.user.is_staff', raise_exception=True)
def FinishSeason(request, lge_id):
    
    newleague, created = LeagueGrp.objects.get_or_create(gender=request.POST.get('new-league-gender'), season=request.POST.get('new-league-season'), year=request.POST.get('new-league-year'))
    newleague.active = True
    if request.POST.get('new-league-season') == "Winter":
        year = int(request.POST.get('new-league-year'))
        year = year - 2000
        next_year = year + 1
        newleague.displayyear = str(year) + "-" + str(next_year)
    else:
        newleague.displayyear = request.POST.get('new-league-year')
    newleague.save()
        
    oldleague = LeagueGrp.objects.get(pk=lge_id)
    oldleague.active = False
    oldleague.finished = True
    oldleague.save()
    
    leaguename = oldleague.season + " League " + str(oldleague.displayyear)
    archiveseason = ArchiveSeason(display_name=leaguename, year=oldleague.year, season=oldleague.season, gender=oldleague.gender)
    archiveseason.save()
    
    olddivisions = Division.objects.filter(leaguegrp=oldleague)
    for div in olddivisions:
        div_teams = Team.objects.filter(division=div.pk)
        points_deductions = PointsDeduction.objects.filter(team__in=div_teams).order_by('date', 'team__name')
        div_table = Result.objects.filter(team__division=div.pk, fixture__resultverified=True).values('team__name', 'team__id').annotate(Cplayed=Sum('played'), Cwon=Sum('win'), Clost=Sum('lose'), Clegs_for=Sum('legs_for'), Clegs_ags=Sum('legs_against'), Cpoints=Sum('points')).order_by('-Cpoints', '-Clegs_for', 'Clegs_ags', 'team__name')
        div_table_f = []
        for team in div_teams:
            points_deducted = 0
            for d in points_deductions:
                if team == d.team:
                    points_deducted += d.points
            
            try:
                table_team = div_table.get(team=team)
                teamobj = {"teamName": table_team['team__name'], "teamid": table_team['team__id'], "Cplayed": table_team['Cplayed'], "Cwon": table_team['Cwon'], "Clost": table_team['Clost'], "Clegs_for": table_team['Clegs_for'], "Clegs_ags": table_team['Clegs_ags'], "Cpoints": table_team['Cpoints']-points_deducted}
                div_table_f.append(teamobj)
            except Result.DoesNotExist:
                table_team = None
            
            div_table_f = sorted(div_table_f, key=itemgetter('Clegs_ags', 'teamName'))
            div_table_f = sorted(div_table_f, key=itemgetter('Cpoints', 'Clegs_for'), reverse=True)
            
        divname = "Division " + div.name
        if div_table.count() >= 2:
            archivedivision = ArchiveDivision(season=archiveseason, division_name=divname, winner=div_table_f[0]['teamName'], runner_up=div_table_f[1]['teamName'])
            archivedivision.save()
    
    oldcomps = Competition.objects.filter(keydate__league=oldleague)
    for comp in oldcomps:
        print comp.keydate.name
        print comp.winner1
        w1 = None if not comp.winner1 else comp.winner1.firstname + " " + comp.winner1.surname
        w2 = None if not comp.winner2 else comp.winner2.firstname + " " + comp.winner2.surname
        w3 = None if not comp.winner3 else comp.winner3.firstname + " " + comp.winner3.surname
        r1 = None if not comp.runnerup1 else comp.runnerup1.firstname + " " + comp.runnerup1.surname
        r2 = None if not comp.runnerup2 else comp.runnerup2.firstname + " " + comp.runnerup2.surname
        r3 = None if not comp.runnerup3 else comp.runnerup3.firstname + " " + comp.runnerup3.surname
        print w1
        print r1
        archivecomp = ArchiveComp(season=archiveseason, comp_name=comp.keydate.name, winner1=w1, winner2=w2, winner3=w3, runnerup1=r1, runnerup2=r2, runnerup3=r3)
        archivecomp.save()
    
    return redirect('PandDDL:adminLeague')

@permission_required('request.user.is_staff', raise_exception=True)
def LeagueDelete(request, lge_id):
    lge = LeagueGrp.objects.get(pk=lge_id)
    lge.delete()
    
    return redirect('PandDDL:adminLeague')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminDivision(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    active_divs = Division.objects.filter(leaguegrp__in=active_leagues).order_by('name')
    mens_divs = active_divs.filter(leaguegrp__gender="Men's")
    ladies_divs = active_divs.filter(leaguegrp__gender="Ladies")
    
    if request.method == "POST":
        if request.POST.get('new-div-name'):
            stripped_div_name = re.sub(r'[Dd]ivision|[Dd]iv| ','',request.POST.get('new-div-name'))
            if not request.POST.get('new-div-legs-triples'):
                tripleslegs = None
            new_div = Division(name=stripped_div_name, leaguegrp=LeagueGrp.objects.get(pk=request.POST.get('new-div-league')), singlesbestoflegs=request.POST.get('new-div-legs-singles'), doublesbestoflegs=request.POST.get('new-div-legs-doubles'), triplesbestoflegs=tripleslegs)
            new_div.save()
        
        if request.POST.get('edit-div-id'):
            edit_div = Division.objects.get(pk=request.POST.get('edit-div-id'))
            edit_div.name = request.POST.get('edit-div-name')
            edit_div.singlesbestoflegs = request.POST.get('edit-div-legs-singles')
            edit_div.doublesbestoflegs = request.POST.get('edit-div-legs-doubles')
            edit_div.triplesbestoflegs = request.POST.get('edit-div-legs-triples')
            edit_div.save()
        
        return redirect('PandDDL:adminDivision')
    
    
    context = {
        "active_leagues": active_leagues,
        "active_divs": active_divs,
        "mens_divs": mens_divs,
        "ladies_divs": ladies_divs,
    }
    
    return render(request, 'PandDDL/adminDivision.html', context)

def AdminDivisionDelete(request, div_id):
    div = Division.objects.get(pk=div_id)
    div.delete()
    
    return redirect('PandDDL:adminDivision')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminTeam(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    active_divs = Division.objects.filter(leaguegrp__in=active_leagues).order_by('leaguegrp__gender','name')
    mens_divs = active_divs.filter(leaguegrp__gender="Men's")
    ladies_divs = active_divs.filter(leaguegrp__gender="Ladies")
    all_users = User.objects.filter(is_staff=False).order_by('username')
    active_teams = Team.objects.filter(division__in=active_divs).order_by('name')
    points_deductions = PointsDeduction.objects.filter(team__in=active_teams).order_by('date')
    points_deductions_teams = points_deductions.values_list('team__pk', flat=True)
    
    if request.method == "POST":
        if request.POST.get('points-deduction-team'):
            deduction = PointsDeduction(team=Team.objects.get(pk=request.POST.get('points-deduction-team')), points=request.POST.get('points-deducted'), reason=request.POST.get('points-deduction-reason'), date=datetime.datetime.today())
            deduction.save()
        
        if request.POST.get('edit-team-name'):
            team = Team.objects.get(pk=request.POST.get('edit-team-id'))
            team.name = request.POST.get('edit-team-name')
            team.division = Division.objects.get(pk=request.POST.get('edit-team-div'))
            team.address = request.POST.get('edit-team-address')
            team.pubphoneno = request.POST.get('edit-team-pub-phone')
            team.captainphoneno = request.POST.get('edit-team-captain-phone')
            team.admin.username = request.POST.get('edit-team-name').lower().replace(" ", "")
            team.save()
        
        if request.POST.get('new-team-name'):
            if request.POST.get('userType') == "existing":
                adminacct = User.objects.get(pk=request.POST.get('new-user-name-existing'))
            elif request.POST.get('userType') == "new":
                adminacct = User.objects.create_user(request.POST.get('new-user-name-new'), "", 'Pandddl180')
            newteam = Team(name=request.POST.get('new-team-name'), address=request.POST.get('new-team-address'), pubphoneno=request.POST.get('new-team-pub-phone'), captainphoneno=request.POST.get('new-team-captain-phone'), division=Division.objects.get(pk=request.POST.get('new-team-div')), admin=adminacct, newpassword=True)
            newteam.save()
            
        return redirect('PandDDL:adminTeam')
    
    
    context = {
        "active_leagues": active_leagues,
        "active_divs": active_divs,
        "active_teams": active_teams,
        "mens_divs": mens_divs,
        "ladies_divs": ladies_divs,
        "points_deductions": points_deductions,
        "points_deductions_teams": points_deductions_teams,
        "all_users": all_users,
    }
    
    return render(request, 'PandDDL/adminTeam.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminTeamPayLeagueFee(request, tid):
    team = Team.objects.get(pk=tid)
    team.paidleaguefee = True
    team.save()
    
    return redirect('PandDDL:adminTeam')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminTeamDelete(request, tid):
    team = Team.objects.get(pk=tid)
    team.delete()
    
    return redirect('PandDDL:adminTeam')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminTeamPasswordChange(request, uid):
    team = Team.objects.get(admin__pk=uid)
    user = User.objects.get(pk=uid)
    user.set_password('Pandddl180')
    user.save()
    team.newpassword = True
    team.save()
    
    return redirect('PandDDL:adminTeam')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminTeamPointsDeductionDelete(request, pd_id):
    pd = PointsDeduction.objects.get(pk=pd_id)
    pd.delete()
    
    return redirect('PandDDL:adminTeam')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPlayer(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    active_divs = Division.objects.filter(leaguegrp__in=active_leagues).order_by('leaguegrp__gender','name')
    mens_divs = active_divs.filter(leaguegrp__gender="Men's")
    ladies_divs = active_divs.filter(leaguegrp__gender="Ladies")
    active_teams = Team.objects.filter(division__in=active_divs).order_by('name')
    active_players = Player.objects.filter(team__in=active_teams).order_by('firstname')
    
    if request.method == "POST":
        if request.POST.get('new-player-firstname'):
            player_team = Team.objects.get(pk=request.POST.get('new-player-team'))
            iscap = True if request.POST.get('new-player-iscaptain') else False
            player = Player(firstname=request.POST.get('new-player-firstname'), surname=request.POST.get('new-player-surname'), team=player_team, iscaptain=iscap, dateadded=request.POST.get('new-player-date-added'))
            if request.POST.get('new-player-iscaptain'):
                try:
                    cap = Player.objects.get(team=player_team, iscaptain=True)
                    cap.iscaptain = False
                    cap.save()
                except Player.DoesNotExist:
                    pass
            player.save()
            
        if request.POST.get('edit-player-id'):
            player = Player.objects.get(pk=request.POST.get('edit-player-id'))
            player.firstname = request.POST.get('edit-player-firstname')
            player.surname = request.POST.get('edit-player-surname')
            player.team = Team.objects.get(pk=request.POST.get('edit-player-team'))
            player.dateadded = request.POST.get('edit-player-date-added')
            
            player.save()
        
        return redirect('PandDDL:adminPlayer')
    
    context = {
        "active_leagues": active_leagues,
        "active_divs": active_divs,
        "active_teams": active_teams,
        "mens_divs": mens_divs,
        "ladies_divs": ladies_divs,
        "active_players": active_players,
        "today": datetime.datetime.today(),
    }
    
    return render(request, 'PandDDL/adminPlayer.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPlayerSelectTeam(request):
    team = Team.objects.get(pk=request.POST.get('team-select'))
    players = Player.objects.filter(team=team)
    
    teamobj = {'name': team.name, 'pk': team.pk}
    
    playerlist = []
    for player in players:
        playerlist.append({'pk': player.pk, 'firstname': player.firstname, 'surname': player.surname, 'iscaptain': player.iscaptain, 'team': player.team.pk, 'dateadded': player.dateadded})
    
    return JsonResponse({"players": playerlist, "team": teamobj})

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPlayerSetCaptain(request, pid):
    player = Player.objects.get(pk=pid)
    previous_captain = Player.objects.filter(team__pk=player.team.pk, iscaptain=True)
    
    for cap in previous_captain:
        cap.iscaptain = False
        cap.save()
        
    player.iscaptain = True
    player.save()
    
    return redirect('PandDDL:adminPlayer')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPlayerDelete(request, pid):
    player = Player.objects.get(pk=pid)
    if not player.iscaptain:
        player.delete()
    
    return redirect('PandDDL:adminPlayer')
    

@permission_required('request.user.is_staff', raise_exception=True)
def AdminFixture(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    active_divs = Division.objects.filter(leaguegrp__in=active_leagues).order_by('leaguegrp__gender','name')
    mens_divs = active_divs.filter(leaguegrp__gender="Men's")
    ladies_divs = active_divs.filter(leaguegrp__gender="Ladies")
    print ladies_divs
    mens_fixtures = Fixture.objects.filter(division__in=mens_divs).order_by('date', 'hometeam__name')
    ladies_fixtures = Fixture.objects.filter(division__in=ladies_divs).order_by('date', 'hometeam__name')
    mens_teams = Team.objects.filter(division__in=mens_divs)
    ladies_teams = Team.objects.filter(division__in=ladies_divs)
    
    if request.method == "POST":
        if request.POST.get('fixture-home-team'):
            hometeam = Team.objects.get(pk=request.POST.get('fixture-home-team'))
            awayteam = Team.objects.get(pk=request.POST.get('fixture-away-team'))
            same_fixture = Fixture.objects.filter(Q(date=request.POST.get('fixture-date')), Q(hometeam__name__iexact=hometeam.name) | Q(awayteam__name__iexact=hometeam.name) | Q(hometeam__name__iexact=awayteam.name) | Q(awayteam__name__iexact=awayteam.name))
            for f in same_fixture:
                f.delete()
            fixture = Fixture(hometeam=Team.objects.get(pk=request.POST.get('fixture-home-team')), awayteam=Team.objects.get(pk=request.POST.get('fixture-away-team')), date=request.POST.get('fixture-date'), division=Division.objects.get(pk=request.POST.get('fixture-div')))
            fixture.save()
        
        return redirect('PandDDL:adminFixture')
    
    context = {
        "active_leagues": active_leagues,
        "active_divs": active_divs,
        "mens_divs": mens_divs,
        "ladies_divs": ladies_divs,
        "mens_fixtures": mens_fixtures,
        "ladies_fixtures": ladies_fixtures,
        "mens_teams": mens_teams,
        "ladies_teams": ladies_teams,
    }
    
    return render(request, 'PandDDL/adminFixture.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminFixtureDelete(request, fid):
    fixture = Fixture.objects.get(pk=fid)
    fixture.delete()
    
    return redirect('PandDDL:adminFixture')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminFixtureEdit(request, fid):
    fixture = Fixture.objects.get(pk=fid)
    division = fixture.division
    
    singleslegstowin = 0 if not division.singlesbestoflegs else ((int(division.singlesbestoflegs) + 1) / 2)
    doubleslegstowin = 0 if not division.doublesbestoflegs else ((int(division.doublesbestoflegs) + 1) / 2)
    tripleslegstowin = 0 if not division.triplesbestoflegs else ((int(division.triplesbestoflegs) + 1) / 2)
    home_team_players = Player.objects.filter(team=Team.objects.get(pk=fixture.hometeam.pk))
    away_team_players = Player.objects.filter(team=Team.objects.get(pk=fixture.awayteam.pk))
    
    singles_matches = SinglesMatch.objects.filter(fixture=fixture)
    doubles_matches = DoublesMatch.objects.filter(fixture=fixture)
    triples_matches = TriplesMatch.objects.filter(fixture=fixture)
    
    maximums = Maximum.objects.filter(fixture=fixture).order_by('player__team__name', 'player__surname')
    tonplus = TopScore.objects.filter(fixture=fixture).order_by('player__team__name', 'player__surname')
    top_finishes = TopFinish.objects.filter(fixture=fixture).order_by('player__team__name', 'player__surname')
    
    context = {
        "fixture": fixture,
        "home_team_players": home_team_players,
        "away_team_players": away_team_players,
        "singles_matches": singles_matches,
        "doubles_matches": doubles_matches,
        "triples_matches": triples_matches,
        "top_scores": tonplus,
        "maximums": maximums, 
        "top_finishes": top_finishes,
        "singleslegstowin": singleslegstowin,
        "doubleslegstowin": doubleslegstowin,
        "tripleslegstowin": tripleslegstowin,
    } 
    
    if request.method == "POST":
        if request.POST.get('home-team-concede'):
            ConcedeFixture(fixture, "home", request.user)
            
        if request.POST.get('away-team-concede'): 
            ConcedeFixture(fixture, "away", request.user)
            
        if request.POST.get('results-entered'):
            errors = False
            homescore = 0
            awayscore = 0
            singlesmatches = []
            singlesresults = []
            doublesmatches = []
            doublesresults = []
            triplesmatches = []
            triplesresults = []
            topscores = []
            topfinishes = []
            maximums = []
            
            if fixture.division.leaguegrp.gender == "Men's":
                for i in range(1,6):
                    singlesmatches, singlesresults, homescore, awayscore, singleserrors = SinglesFixture(fixture, request.POST.get('singles-home-player-'+str(i)), request.POST.get('singles-away-player-'+str(i)), request.POST.get('singles-home-score-'+str(i)), request.POST.get('singles-away-score-'+str(i)), homescore, awayscore, singlesmatches, singlesresults)
                    if singleserrors:
                        errors = True
                        
                for i in range(1,3):
                    doublesmatches, doublesresults, homescore, awayscore, doubleserrors = DoublesFixture(fixture, request.POST.get('doubles-home-player-1-'+str(i)), request.POST.get('doubles-home-player-2-'+str(i)), request.POST.get('doubles-away-player-1-'+str(i)), request.POST.get('doubles-away-player-2-'+str(i)), request.POST.get('doubles-home-score-'+str(i)), request.POST.get('doubles-away-score-'+str(i)), homescore, awayscore, doublesmatches, doublesresults)
                    if doubleserrors:
                        errors = True
                    
                for i in range(1,7):
                    maximums, maximumerrors = CreateMaximum(fixture, request.POST.get('maximums-1-'+str(i)), maximums)
                    if maximumerrors:
                        errors = True
                    maximums, maximumerrors = CreateMaximum(fixture, request.POST.get('maximums-2-'+str(i)), maximums)
                    if maximumerrors:
                        errors = True
                    
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-1-'+str(i)), request.POST.get('finishes-amount-1-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-2-'+str(i)), request.POST.get('finishes-amount-2-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
                    
                        
            else:           # Ladies Fixture
                for i in range(1,5):
                    singlesmatches, singlesresults, homescore, awayscore, singleserrors = SinglesFixture(fixture, request.POST.get('singles-home-player-'+str(i)), request.POST.get('singles-away-player-'+str(i)), request.POST.get('singles-home-score-'+str(i)), request.POST.get('singles-away-score-'+str(i)), homescore, awayscore, singlesmatches, singlesresults)
                    if singleserrors:
                        errors = True
                        
                for i in range(1,3):
                    doublesmatches, doublesresults, homescore, awayscore, doubleserrors = DoublesFixture(fixture, request.POST.get('doubles-home-player-1-'+str(i)), request.POST.get('doubles-home-player-2-'+str(i)), request.POST.get('doubles-away-player-1-'+str(i)), request.POST.get('doubles-away-player-2-'+str(i)), request.POST.get('doubles-home-score-'+str(i)), request.POST.get('doubles-away-score-'+str(i)), homescore, awayscore, doublesmatches, doublesresults)
                    if doubleserrors:
                        errors = True
                        
                for i in range(1,2):
                    triplesmatches, triplesresults, homescore, awayscore, tripleserrors = TriplesFixture(fixture, request.POST.get('triples-home-player-1-'+str(i)), request.POST.get('triples-home-player-2-'+str(i)), request.POST.get('triples-home-player-3-'+str(i)), request.POST.get('triples-away-player-1-'+str(i)), request.POST.get('triples-away-player-2-'+str(i)), request.POST.get('triples-away-player-3-'+str(i)), request.POST.get('triples-home-score-'+str(i)), request.POST.get('triples-away-score-'+str(i)), homescore, awayscore, triplesmatches, triplesresults)
                    if tripleserrors:
                        errors = True
                
                for i in range(1,7):
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-1-'+str(i)), request.POST.get('score-score-1-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-2-'+str(i)), request.POST.get('score-score-2-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-3-'+str(i)), request.POST.get('score-score-3-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    topscores, topscoreerrors = CreateTopScore(fixture, request.POST.get('score-name-4-'+str(i)), request.POST.get('score-score-4-'+str(i)), topscores)
                    if topscoreerrors:
                        errors = True
                    
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-1-'+str(i)), request.POST.get('finishes-amount-1-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
                    topfinishes, topfinisherrors = CreateTopFinish(fixture, request.POST.get('finishes-name-2-'+str(i)), request.POST.get('finishes-amount-2-'+str(i)), topfinishes)
                    if topfinisherrors:
                        errors = True
            
            if not errors:
                if fixture.resultentered:
                    ResetFixture(fixture)
                        
                for s in singlesmatches:
                    s.save()
                for s in singlesresults:
                    newmatch = SinglesMatch.objects.get(pk=s.match.id)
                    s.match = newmatch
                    s.save()
                for d in doublesmatches:
                    d.save()
                for d in doublesresults:
                    newmatch = DoublesMatch.objects.get(pk=d.match.id)
                    d.match = newmatch
                    d.save()
                for t in triplesmatches:
                    t.save()
                for t in triplesresults:
                    newmatch = TriplesMatch.objects.get(pk=t.match.id)
                    t.match = newmatch
                    t.save()
                for m in maximums:
                    m.save()
                for t in topfinishes:
                    t.save()
                for t in topscores:
                    t.save()
                
                fixture.homescore = homescore
                fixture.awayscore = awayscore
                fixture.resultentered = True
                fixture.resultenteredby = request.user
                
                homewin = 1 if fixture.homescore > fixture.awayscore else 0
                homelose = 0 if fixture.homescore > fixture.awayscore else 1
                homepoints = homewin * 2
                awaywin = 1 if fixture.awayscore > fixture.homescore else 0
                awaylose = 0 if fixture.awayscore > fixture.homescore else 1
                awaypoints = awaywin * 2
                
                homeresult = Result(team=fixture.hometeam, opposition=fixture.awayteam, fixture=fixture, win=homewin, lose=homelose, legs_for=fixture.homescore, legs_against=fixture.awayscore, points=homepoints)
                homeresult.save()
                awayresult = Result(team=fixture.awayteam, opposition=fixture.hometeam, fixture=fixture, win=awaywin, lose=awaylose, legs_for=fixture.awayscore, legs_against=fixture.homescore, points=awaypoints)
                awayresult.save()
                
                if request.FILES:
                    fixture.resultsheet = request.FILES['result-sheet']
            
                fixture.save()
            
        if request.POST.get('result-verified') or fixture.resultenteredby and fixture.resultenteredby.is_staff: 
            fixture.resultverified = True
            fixture.save()
        
        return redirect('PandDDL:fixture', fixture.pk)
    
    
    if fixture.division.leaguegrp.gender == "Men's":
        return render(request, 'PandDDL/adminEditFixture.html', context)
    else:
        return render(request, 'PandDDL/adminEditLadiesFixture.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminKeyDates(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    mens_key_dates = KeyDate.objects.filter(league__in=active_leagues, league__gender="Men's").order_by('date')
    ladies_key_dates = KeyDate.objects.filter(league__in=active_leagues, league__gender="Ladies").order_by('date')
    
    if request.method == "POST":
        if request.POST.get('key-date-name'):
            newdate = KeyDate(name=request.POST.get('key-date-name'), location=request.POST.get('key-date-location'), date=request.POST.get('key-date-date'), time=request.POST.get('key-date-time'), league=LeagueGrp.objects.get(pk=request.POST.get('key-date-league')))
            newdate.save()
        if request.POST.get('edit-key-date-id'):
            date = KeyDate.objects.get(pk=request.POST.get('edit-key-date-id'))
            date.name = request.POST.get('edit-key-date-name')
            date.location = request.POST.get('edit-key-date-location')
            date.date = request.POST.get('edit-key-date-date')
            date.time = request.POST.get('edit-key-date-time')
            date.league = LeagueGrp.objects.get(pk=request.POST.get('edit-key-date-league'))
            date.save()
        
        return redirect('PandDDL:adminKeyDates')
    
    context = {
        "mens_key_dates": mens_key_dates,
        "ladies_key_dates": ladies_key_dates, 
    }
    
    return render(request, 'PandDDL/adminKeyDates.html', context)

def AdminKeyDateDelete(request, kid):
    date = KeyDate.objects.get(pk=kid)
    date.delete()
    
    return redirect('PandDDL:adminKeyDates')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminAnnouncements(request):
    announcements = Announcement.objects.all().order_by('-date')
    max_announcements = NoOfAnnouncements.objects.get(pk=1)
    max_announcements = max_announcements.number
    galleries = PhotoGallery.objects.all()
    
    if request.method == "POST":
        if request.POST.get('announcement-heading'):
            no_ann = NoOfAnnouncements.objects.get(pk=1)
            shown_ann = Announcement.objects.filter(showonhome=True).order_by('date')
            if shown_ann.count() >= no_ann.number:
                remove_ann = shown_ann.first()
                remove_ann.showonhome = False
                remove_ann.save()
            heading = request.POST.get('announcement-heading')
            text = request.POST.get('announcement-text')
            print request.POST.get('announcement-gallery')
            if request.POST.get('announcement-gallery') == "None":
                gallery = None
            else:
                gallery = PhotoGallery.objects.get(pk=request.POST.get('announcement-gallery'))
            if 'announcement-photo' in request.FILES:
                image = request.FILES['announcement-photo']
            else: 
                image = None
            date = datetime.datetime.now()
            a = Announcement(heading=heading, date=date, text=text, gallery=gallery, picture=image, showonhome=True)
            a.save()
            
        if request.POST.get('edit-announcement-heading'):
            announcement = Announcement.objects.get(pk=request.POST.get('edit-announcement-id'))
            announcement.heading = request.POST.get('edit-announcement-heading')
            announcement.text = request.POST.get('edit-announcement-text')
            if request.POST.get('edit-announcement-gallery') == "None":
                gallery = None
            else:
                announcement.gallery = PhotoGallery.objects.get(pk=request.POST.get('edit-announcement-gallery'))
            if 'edit-announcement-photo' in request.FILES:
                announcement.picture = request.FILES['edit-announcement-photo']
            announcement.save()
        
        if request.POST.get('max-announcements'):
            if request.POST.get('max-announcements') > 0:
                noofann = NoOfAnnouncements.objects.get(pk=1)
                noofann.number = request.POST.get('max-announcements')
                noofann.save()
                ann = Announcement.objects.filter(showonhome=True).order_by('-date')[noofann.number:]
                for a in ann: 
                    print a.text
                    a.showonhome = False
                    a.save()
        
        return redirect('PandDDL:adminAnnouncements')
    
    context = {
        "announcements": announcements,
        "max_announcements": max_announcements,
        "galleries": galleries,
    }
    
    return render(request, 'PandDDL/adminAnnouncements.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminAnnouncementDelete(request, aid):
    ann = Announcement.objects.get(pk=aid)
    ann.delete()
    
    return redirect('PandDDL:adminAnnouncements')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminAnnouncementDisplay(request, aid):
    no_ann = NoOfAnnouncements.objects.get(pk=1)
    shown_ann = Announcement.objects.filter(showonhome=True).order_by('date')
    while shown_ann.count() >= no_ann.number:
        shown_ann = Announcement.objects.filter(showonhome=True).order_by('date')
        remove_ann = shown_ann.first()
        remove_ann.showonhome = False
        remove_ann.save()
    
    ann = Announcement.objects.get(pk=aid)
    ann.showonhome = True
    ann.save()
    return redirect('PandDDL:adminAnnouncements')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminAnnouncementHide(request, aid):
    ann = Announcement.objects.get(pk=aid)
    ann.showonhome = False
    ann.save()
    return redirect('PandDDL:adminAnnouncements')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminCupComps(request):
    
    context = {
    
    }
    
    return render(request, 'PandDDL/adminCupComps.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPlayerComps(request):
    active_leagues = LeagueGrp.objects.filter(active=True)
    active_teams = Team.objects.filter(division__leaguegrp__in=active_leagues)
    active_comps = Competition.objects.filter(keydate__league__active=True).order_by('keydate__date')
    all_players = Player.objects.filter(team__in=active_teams).order_by('firstname')
    mens_comps = active_comps.filter(keydate__league__gender="Men's")
    mens_players = all_players.filter(team__division__leaguegrp__gender="Men's")
    ladies_comps = active_comps.filter(keydate__league__gender="Ladies")
    ladies_players = all_players.filter(team__division__leaguegrp__gender="Ladies")
    
    if request.method == "POST":
        if request.POST.get('player-comp-name'):
            newdate = KeyDate(date=request.POST.get('player-comp-date'), time=request.POST.get('player-comp-time'), name=request.POST.get('player-comp-name'), location=request.POST.get('player-comp-location'), league=LeagueGrp.objects.get(pk=request.POST.get('player-comp-league')))
            newdate.save()
            comp = Competition(keydate=newdate, comptype=request.POST.get('player-comp-type'))
            comp.save()
        if request.POST.get('comp-winner1'):
            comp = Competition.objects.get(pk=request.POST.get('comp-id'))
            comp.winner1 = Player.objects.get(pk=request.POST.get('comp-winner1'))
            comp.runnerup1 = Player.objects.get(pk=request.POST.get('comp-runnerup1'))
            if request.POST.get('comp-winner2'):
                comp.winner2 = Player.objects.get(pk=request.POST.get('comp-winner2'))
                comp.runnerup2 = Player.objects.get(pk=request.POST.get('comp-runnerup2'))
            if request.POST.get('comp-winner3'):
                comp.winner3 = Player.objects.get(pk=request.POST.get('comp-winner3'))
                comp.runnerup3 = Player.objects.get(pk=request.POST.get('comp-runnerup3'))
            comp.save()
        if request.POST.get('edit-comp-id'):
            comp = Competition.objects.get(pk=request.POST.get('edit-comp-id'))
            key_date = comp.keydate
            comp.comptype = request.POST.get('edit-comp-type')
            key_date.name = request.POST.get('edit-comp-name')
            key_date.date = request.POST.get('edit-comp-date')
            key_date.time = request.POST.get('edit-comp-time')
            key_date.location = request.POST.get('edit-comp-location')
            key_date.league = LeagueGrp.objects.get(pk=request.POST.get('edit-comp-league'))
            key_date.save()
            comp.save()
            
        return redirect('PandDDL:adminPlayerComps')
    
    context = {
        "active_leagues": active_leagues,
        "active_comps": active_comps,
        "mens_comps": mens_comps,
        "ladies_comps": ladies_comps,
        "all_players": all_players,
        "mens_players": mens_players,
        "ladies_players": ladies_players,
    }
    
    return render(request, 'PandDDL/adminPlayerComps.html', context)

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPlayerCompsDelete(request, cid):
    comp = Competition.objects.get(pk=cid)
    comp.delete()
    
    return redirect('PandDDL:adminPlayerComps')

@permission_required('request.user.is_staff', raise_exception=True)
def AdminPhotoGalleries(request):
    photo_galleries = PhotoGallery.objects.all()
    
    if request.method == "POST":
        if request.POST.get('new-gal-name'):
            newgal = PhotoGallery(name=request.POST.get('new-gal-name'), date=request.POST.get('new-gal-date'))
            newgal.save()
            print request.POST.get('new-gal-name')
            print request.POST.get('new-gal-date')
        if request.POST.get('edit-gal-id'):
            gallery = PhotoGallery.objects.get(pk=request.POST.get('edit-gal-id'))
            gallery.name = request.POST.get('edit-gal-name')
            gallery.date = request.POST.get('edit-gal-date')
            gallery.save()
        if request.POST.get('add-photo-gal-id'):
            gallery = PhotoGallery.objects.get(pk=request.POST.get('add-photo-gal-id'))
            if 'upload-gal-photos' in request.FILES:
                photos = request.FILES.getlist('upload-gal-photos')
                for p in photos:
                    pic = Photo(photo=p)
                    pic.save()
                    gallery.photos.add(pic)
                    
        if request.POST.get('set-cover-photo-gal-id'):
            gallery = PhotoGallery.objects.get(pk=request.POST.get('set-cover-photo-gal-id'))
            if request.POST.get('cover-photo-choice'):
                gallery.coverphoto = Photo.objects.get(pk=request.POST.get('cover-photo-choice'))
            else: 
                gallery.coverphoto = None
            gallery.save()
                            
        return redirect('PandDDL:adminPhotoGalleries')
    
    context = {
        "photo_galleries": photo_galleries,
    }
    
    return render(request, 'PandDDL/adminPhotoGalleries.html', context)

@permission_required('request.user.is_staff', raise_exception=True)    
def AdminPhotoGalleriesDelete(request, pid):
    gal = PhotoGallery.objects.get(pk=pid)
    gal.delete()
    
    return redirect('PandDDL:adminPhotoGalleries')

@permission_required('request.user.is_staff', raise_exception=True) 
def AdminAGMminutes(request):
    
    agmminutes = AGMminutes.objects.all().order_by('date')
    agmfile = ""
    files = MiscFile.objects.all()
    
    if request.method == "POST":
        if request.POST.get('agm-date'):
            if request.FILES:
                agmfile = request.FILES['AGMminutesfile']
            mins = AGMminutes(date=request.POST.get('agm-date'), location=request.POST.get('agm-location'), minutes=agmfile)
            mins.save()
        
        if request.POST.get('file-desc'):
            if request.FILES:
                miscfile = request.FILES['file']
            newdate = timezone.now()
            newfile = MiscFile(date_uploaded=newdate, description=request.POST.get('file-desc'), file=miscfile)
            newfile.save()
            
        if request.POST.get('edit-file-desc'):
            fileobj = MiscFile.objects.get(pk=request.POST.get('edit-file-id'))
            if request.FILES:
                miscfile = request.FILES['edit-file']
                fileobj.file = miscfile
            fileobj.date_uploaded = timezone.now()
            fileobj.description = request.POST.get('edit-file-desc')
            fileobj.save()
            
        if request.POST.get('edit-agm-date'):
            editmins = AGMminutes.objects.get(pk=request.POST.get('agm-id'))
            if request.POST.get('del-mins') == "True":
                editmins.minutes.delete()
            if request.FILES:
                agmfile = request.FILES['edit-AGMminutesfile']
                editmins.minutes = agmfile
            editmins.date = request.POST.get('edit-agm-date')
            editmins.location = request.POST.get('edit-agm-location')
            editmins.save()
            
            
        return redirect('PandDDL:adminAGMminutes')
    
    context = {
        "agmminutes": agmminutes,
        "files": files,
    }
    
    return render(request, 'PandDDL/adminAGMminutes.html', context)

@permission_required('request.user.is_staff', raise_exception=True) 
def AdminAGMminutesDelete(request, aid):
    minutes = AGMminutes.objects.get(pk=aid)
    minutes.delete()
    
    return redirect('PandDDL:adminAGMminutes')

def AGMMinutesDownload(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

@permission_required('request.user.is_staff', raise_exception=True)
def FileDelete(request, fid):
    file = MiscFile.objects.get(pk=fid)
    file.delete()
    
    return redirect('PandDDL:adminAGMminutes')

def ConcedeFixture(fixture, team, user):
    ResetFixture(fixture)
    fixture.resultentered = True
    fixture.resultenteredby = user
    fixture.walkover = True
    
    if team == "home":
        fixture.homescore = 0
        fixture.awayscore = 7
        homeresult = Result(team=fixture.hometeam, opposition=fixture.awayteam, fixture=fixture, win=0, lose=1, legs_for=fixture.homescore, legs_against=fixture.awayscore, points=0)
        awayresult = Result(team=fixture.awayteam, opposition=fixture.hometeam, fixture=fixture, win=1, lose=0, legs_for=fixture.awayscore, legs_against=fixture.homescore, points=2)
        
    if team == "away": 
        fixture.homescore = 7
        fixture.awayscore = 0
        homeresult = Result(team=fixture.hometeam, opposition=fixture.awayteam, fixture=fixture, win=1, lose=0, legs_for=fixture.homescore, legs_against=fixture.awayscore, points=2)
        awayresult = Result(team=fixture.awayteam, opposition=fixture.hometeam, fixture=fixture, win=0, lose=1, legs_for=fixture.awayscore, legs_against=fixture.homescore, points=0)
    
    homeresult.save()
    awayresult.save()
    fixture.save()
    return

def SinglesFixture(fixture, homePlayer, awayPlayer, homeScore, awayScore, homeTotal, awayTotal, singlesmatches, singlesresults):
    errors = False
    singleslegstowin = (fixture.division.singlesbestoflegs + 1) / 2
    try:
        homeWalkover = True if int(homePlayer) == 0 else False
        homePlayerObj = None if homeWalkover else Player.objects.get(pk=homePlayer)
        for s in singlesmatches:
            if homePlayerObj == s.homeplayer:
                errors = True
                print "Home Player exists"
        awayWalkover = True if int(awayPlayer) == 0 else False
        awayPlayerObj = None if awayWalkover else Player.objects.get(pk=awayPlayer)
        for s in singlesmatches:
            if awayPlayerObj == s.awayplayer:
                errors = True
                print "away player exists"
        if int(homeScore) < 0 or int(homeScore) > singleslegstowin:
            errors = True
            print "home legs " + str(homeScore) + " greater than " + str(singleslegstowin)
        if int(awayScore) < 0 or int(awayScore) > singleslegstowin:
            errors = True
            print "away legs " + str(awayScore) + " greater than " + str(singleslegstowin)
        if int(homeScore) != singleslegstowin and int(awayScore) != singleslegstowin:
            errors = True
            print "neither team wins max legs " + str(singleslegstowin)
    
        if homeWalkover:
            if awayPlayerObj:
                match = SinglesMatch(fixture=fixture, homeplayer=homePlayerObj, awayplayer=awayPlayerObj, homescore=homeScore, awayscore=awayScore)
                singlesmatches.append(match)
                
                homewin = 1 if match.homescore > match.awayscore else 0
                homeTotal += homewin
                homelose = 0 if match.homescore > match.awayscore else 1
                awaywin = 1 if match.awayscore > match.homescore else 0
                awayTotal += awaywin
                awaylose = 0 if match.awayscore > match.homescore else 1
                
                awayresult = SinglesResult(match=match, player=awayPlayerObj, opposition=homePlayerObj, win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
                singlesresults.append(awayresult)
            else: 
                errors = True
                print "away player obj does not exist"
        
        elif awayWalkover:
            if homePlayerObj:
                match = SinglesMatch(fixture=fixture, homeplayer=homePlayerObj, awayplayer=awayPlayerObj, homescore=homeScore, awayscore=awayScore)
                singlesmatches.append(match)
            
                homewin = 1 if match.homescore > match.awayscore else 0
                homeTotal += homewin
                homelose = 0 if match.homescore > match.awayscore else 1
                awaywin = 1 if match.awayscore > match.homescore else 0
                awayTotal += awaywin
                awaylose = 0 if match.awayscore > match.homescore else 1
                
                homeresult = SinglesResult(match=match, player=homePlayerObj, opposition=awayPlayerObj, win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
                singlesresults.append(homeresult)
            else:
                errors = True
                print "home player obj does not exist"
                
        else:
            if homePlayerObj and awayPlayerObj:
                match = SinglesMatch(fixture=fixture, homeplayer=homePlayerObj, awayplayer=awayPlayerObj, homescore=homeScore, awayscore=awayScore)
                singlesmatches.append(match)
            
                homewin = 1 if match.homescore > match.awayscore else 0
                homeTotal += homewin
                homelose = 0 if match.homescore > match.awayscore else 1
                awaywin = 1 if match.awayscore > match.homescore else 0
                awayTotal += awaywin
                awaylose = 0 if match.awayscore > match.homescore else 1
            else:
                errors = True
                print "one player obj does not exist" + homePlayerObj + ", " + awayPlayerObj
            
            if homePlayerObj:
                homeresult = SinglesResult(match=match, player=homePlayerObj, opposition=awayPlayerObj, win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
                singlesresults.append(homeresult)
            else:
                errors = True
                print "home player obj does not exist"
            
            if awayPlayerObj:
                awayresult = SinglesResult(match=match, player=awayPlayerObj, opposition=homePlayerObj, win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
                singlesresults.append(awayresult)
            else: 
                errors = True
                print "away player obj does not exist"
    except:
        errors = True
        print "singles exception error"
    
    return singlesmatches, singlesresults, homeTotal, awayTotal, errors

def DoublesFixture(fixture, homePlayer1, homePlayer2, awayPlayer1, awayPlayer2, homeScore, awayScore, homeTotal, awayTotal, doublesmatches, doublesresults):
    errors = False
    doubleslegstowin = (fixture.division.doublesbestoflegs + 1) / 2
    try:
        homePlayer1Obj = None if homePlayer1 == 0 else Player.objects.get(pk=homePlayer1)
        homePlayer2Obj = None if homePlayer2 == 0 else Player.objects.get(pk=homePlayer2)
        for d in doublesmatches:
            if homePlayer1Obj == d.homeplayer1 or homePlayer1Obj == d.homeplayer2:
                errors = True
                print "home player 1 already used"
            if homePlayer2Obj == d.homeplayer1 or homePlayer2Obj == d.homeplayer2:
                errors = True
                print "home player 2 already used"
            
        awayPlayer1Obj = None if awayPlayer1 == 0 else Player.objects.get(pk=awayPlayer1)
        awayPlayer2Obj = None if awayPlayer2 == 0 else Player.objects.get(pk=awayPlayer2)
        for d in doublesmatches:
            if awayPlayer1Obj == d.awayplayer1 or awayPlayer1Obj == d.awayplayer2:
                errors = True
                print "away player 1 already used"
            if awayPlayer2Obj == d.awayplayer1 or awayPlayer2Obj == d.awayplayer2:
                errors = True
                print "away player 2 already used"
                
        if int(homeScore) < 0 or int(homeScore) > doubleslegstowin:
            errors = True
            print "home score greater than " + str(doubleslegstowin)
        if int(awayScore) < 0 or int(awayScore) > doubleslegstowin:
            errors = True
            print "away score greater than " + str(doubleslegstowin)
        if int(homeScore) != doubleslegstowin and int(awayScore) != doubleslegstowin:
            errors = True
            print "neither score equals " + str(doubleslegstowin)
        
        if homePlayer1Obj and homePlayer2Obj and awayPlayer1Obj and awayPlayer2Obj:
            match = DoublesMatch(fixture=fixture, homeplayer1=homePlayer1Obj, homeplayer2=homePlayer2Obj, awayplayer1=awayPlayer1Obj, awayplayer2=awayPlayer2Obj, homescore=homeScore, awayscore=awayScore)
            doublesmatches.append(match)
        
            homewin = 1 if match.homescore > match.awayscore else 0
            homeTotal += homewin
            homelose = 0 if match.homescore > match.awayscore else 1
            awaywin = 1 if match.awayscore > match.homescore else 0
            awayTotal += awaywin
            awaylose = 0 if match.awayscore > match.homescore else 1
            
            homeresult1 = DoublesResult(match=match, player=homePlayer1Obj, partner=homePlayer2Obj, opposition1=awayPlayer1Obj, opposition2=awayPlayer2Obj, win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
            doublesresults.append(homeresult1)
            homeresult2 = DoublesResult(match=match, player=homePlayer2Obj, partner=homePlayer1Obj, opposition1=awayPlayer1Obj, opposition2=awayPlayer2Obj, win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
            doublesresults.append(homeresult2)
            awayresult1 = DoublesResult(match=match, player=awayPlayer1Obj, partner=awayPlayer2Obj, opposition1=homePlayer1Obj, opposition2=homePlayer2Obj, win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
            doublesresults.append(awayresult1)
            awayresult2 = DoublesResult(match=match, player=awayPlayer2Obj, partner=awayPlayer1Obj, opposition1=homePlayer1Obj, opposition2=homePlayer2Obj, win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
            doublesresults.append(awayresult2)
        else: 
            errors = True
            print "not all player obj exist"
            
    except:
        errors = True
        print "doubles exception error"
    
    return doublesmatches, doublesresults, homeTotal, awayTotal, errors

def TriplesFixture(fixture, homePlayer1, homePlayer2, homePlayer3, awayPlayer1, awayPlayer2, awayPlayer3, homeScore, awayScore, homeTotal, awayTotal, triplesmatches, triplesresults):
    errors = False
    tripleslegstowin = (fixture.division.triplesbestoflegs + 1) / 2
    try:
        homePlayer1Obj = None if homePlayer1 == 0 else Player.objects.get(pk=homePlayer1)
        homePlayer2Obj = None if homePlayer2 == 0 else Player.objects.get(pk=homePlayer2)
        homePlayer3Obj = None if homePlayer3 == 0 else Player.objects.get(pk=homePlayer3)
        if homePlayer2Obj == homePlayer1Obj:
            errors = True
            print "home player 2 already used"
        if homePlayer3Obj == homePlayer1Obj or homePlayer3Obj == homePlayer2Obj:
            errors = True
            print "home player 3 already used"
            
        awayPlayer1Obj = None if awayPlayer1 == 0 else Player.objects.get(pk=awayPlayer1)
        awayPlayer2Obj = None if awayPlayer2 == 0 else Player.objects.get(pk=awayPlayer2)
        awayPlayer3Obj = None if awayPlayer3 == 0 else Player.objects.get(pk=awayPlayer3)
        if awayPlayer2Obj == awayPlayer1Obj:
            errors = True
            print "away player 2 already used"
        if awayPlayer3Obj == awayPlayer1Obj or awayPlayer3Obj == awayPlayer2Obj:
            errors = True
            print "away player 3 already used"
    
        if int(homeScore) < 0 or int(homeScore) > tripleslegstowin:
            errors = True
            print "home score greater than " + str(tripleslegstowin)
        if int(awayScore) < 0 or int(awayScore) > tripleslegstowin:
            errors = True
            print "away score greater than " + str(tripleslegstowin)
        if int(homeScore) != tripleslegstowin and int(awayScore) != tripleslegstowin:
            errors = True
            print "neither score equals " + str(tripleslegstowin)
    
        if homePlayer1Obj and homePlayer2Obj and homePlayer3Obj and awayPlayer1Obj and awayPlayer2Obj and awayPlayer3Obj:
            match = TriplesMatch(fixture=fixture, homeplayer1=Player.objects.get(pk=homePlayer1), homeplayer2=Player.objects.get(pk=homePlayer2), homeplayer3=Player.objects.get(pk=homePlayer3), awayplayer1=Player.objects.get(pk=awayPlayer1), awayplayer2=Player.objects.get(pk=awayPlayer2), awayplayer3=Player.objects.get(pk=awayPlayer3), homescore=homeScore, awayscore=awayScore)
            triplesmatches.append(match)
                
            homewin = 1 if match.homescore > match.awayscore else 0
            homeTotal += homewin
            homelose = 0 if match.homescore > match.awayscore else 1
            awaywin = 1 if match.awayscore > match.homescore else 0
            awayTotal += awaywin
            awaylose = 0 if match.awayscore > match.homescore else 1
                
            homeresult1 = TriplesResult(match=match, player=Player.objects.get(pk=homePlayer1), partner1=Player.objects.get(pk=homePlayer2), partner2=Player.objects.get(pk=homePlayer3), opposition1=Player.objects.get(pk=awayPlayer1), opposition2=Player.objects.get(pk=awayPlayer2), opposition3=Player.objects.get(pk=awayPlayer3), win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
            triplesresults.append(homeresult1)
            homeresult2 = TriplesResult(match=match, player=Player.objects.get(pk=homePlayer2), partner1=Player.objects.get(pk=homePlayer1), partner2=Player.objects.get(pk=homePlayer3), opposition1=Player.objects.get(pk=awayPlayer1), opposition2=Player.objects.get(pk=awayPlayer2), opposition3=Player.objects.get(pk=awayPlayer3), win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
            triplesresults.append(homeresult2)
            homeresult3 = TriplesResult(match=match, player=Player.objects.get(pk=homePlayer3), partner1=Player.objects.get(pk=homePlayer1), partner2=Player.objects.get(pk=homePlayer2), opposition1=Player.objects.get(pk=awayPlayer1), opposition2=Player.objects.get(pk=awayPlayer2), opposition3=Player.objects.get(pk=awayPlayer3), win=homewin, lose=homelose, legs_for=homeScore, legs_against=awayScore)
            triplesresults.append(homeresult3)
            awayresult1 = TriplesResult(match=match, player=Player.objects.get(pk=awayPlayer1), partner1=Player.objects.get(pk=awayPlayer2), partner2=Player.objects.get(pk=awayPlayer3), opposition1=Player.objects.get(pk=homePlayer1), opposition2=Player.objects.get(pk=homePlayer2), opposition3=Player.objects.get(pk=homePlayer3), win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
            triplesresults.append(awayresult1)
            awayresult2 = TriplesResult(match=match, player=Player.objects.get(pk=awayPlayer2), partner1=Player.objects.get(pk=awayPlayer1), partner2=Player.objects.get(pk=awayPlayer3), opposition1=Player.objects.get(pk=homePlayer1), opposition2=Player.objects.get(pk=homePlayer2), opposition3=Player.objects.get(pk=homePlayer3), win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
            triplesresults.append(awayresult2)
            awayresult3 = TriplesResult(match=match, player=Player.objects.get(pk=awayPlayer3), partner1=Player.objects.get(pk=awayPlayer1), partner2=Player.objects.get(pk=awayPlayer2), opposition1=Player.objects.get(pk=homePlayer1), opposition2=Player.objects.get(pk=homePlayer2), opposition3=Player.objects.get(pk=homePlayer3), win=awaywin, lose=awaylose, legs_for=awayScore, legs_against=homeScore)
            triplesresults.append(awayresult3)
        else:
            errors = True
            print "not all player objs exist"

    except:
        errors = True
        print "triples exception error"
    
    return triplesmatches, triplesresults, homeTotal, awayTotal, errors

def CreateTopScore(fixture, scorename, score, topscores):
    errors = False
    if scorename != None and scorename != "" and score >= 100:
        ts = TopScore(player=Player.objects.get(pk=scorename), score=score, fixture=fixture)
        topscores.append(ts)
    
    return topscores, errors

def CreateTopFinish(fixture, finishname, score, topfinishes):
    errors = False
    if finishname != None and finishname != "" and score >= 100:
        tf = TopFinish(player=Player.objects.get(pk=finishname), finish=score, fixture=fixture)
        topfinishes.append(tf)
    
    return topfinishes, errors

def CreateMaximum(fixture, maximumname, maximums):
    errors = False
    if maximumname != None and maximumname != "":
        m = Maximum(player=Player.objects.get(pk=maximumname), fixture=fixture)
        maximums.append(m)
    
    return maximums, errors

def ResetFixture(fixture):
    fixture.resultentered = False
    fixture.resultenteredby = None
    fixture.resultverified = False
    fixture.walkover = False
    results = Result.objects.filter(fixture__pk=fixture.pk)
    for r in results:
        r.delete()
    singles = SinglesMatch.objects.filter(fixture__pk=fixture.pk)
    for s in singles:
        s.delete()
    doubles = DoublesMatch.objects.filter(fixture__pk=fixture.pk)
    for d in doubles:
        d.delete()
    triples = TriplesMatch.objects.filter(fixture__pk=fixture.pk)
    for t in triples:
        t.delete()
    top_finishes = TopFinish.objects.filter(fixture__pk=fixture.pk)
    for tf in top_finishes:
        tf.delete()
    top_scores = TopScore.objects.filter(fixture__pk=fixture.pk)
    for ts in top_scores:
        ts.delete()
    maximums = Maximum.objects.filter(fixture__pk=fixture.pk)
    for m in maximums:
        m.delete()