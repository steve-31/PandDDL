from django.contrib.auth.models import User
from django.db.models import Q
from .models import Team, LeagueGrp, Division

def header_processor(request):
    if request.user.is_authenticated() and not request.user.is_staff:
        team = Team.objects.get(admin=request.user)
    else:
        team=""
        
    active_leagues = LeagueGrp.objects.filter(active=True).order_by('-gender')
    try:
        active_mens = LeagueGrp.objects.get(active=True, gender="Men's")
    except LeagueGrp.DoesNotExist:
        active_mens = None
    try: 
        active_ladies = LeagueGrp.objects.get(active=True, gender="Ladies")
    except LeagueGrp.DoesNotExist:
        active_ladies = None
    active_divisions = Division.objects.filter(leaguegrp__in=active_leagues)
    
    return { "logged_in_team": team, "active_divisions": active_divisions, "active_leagues": active_leagues, "active_mens": active_mens, "active_ladies": active_ladies }

