from django.shortcuts import render


def tool_id_card_view(request):
    # 直接返回HTML模板
    return render(request, 'tool_card.html')