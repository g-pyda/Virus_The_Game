from django.shortcuts import render


def game_index(request):
    return render(request, 'virus_game_mother/index.html')