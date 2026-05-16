from .models import Suburb
from django.http import JsonResponse

# names the view that handles the request
def search(request):
    # creates an empty list
    suburb_search_list = []
    # request.GET is a dictionary object holding all the relevant values
    # get(search looks up the search key and if it is missing retrns an empty string
    search = request.GET.get('search', '')
    # only runs if search has something in it
    if search:
        # database query
        # suburb__istartswith=search — the double underscore is Django's syntax for "field lookups"
        # [:5] take only the first 5 results and limits the dropdown
        objs = Suburb.objects.filter(suburb__istartswith=search, state='NSW')[:5] 
        # loop through each suburb
        for obj in objs:
            # payload is the list we created at the top
            suburb_search_list.append({'suburb': obj.suburb})
    # react will query suburb_matches
    return JsonResponse({'status': True, 'suburb_matches': suburb_search_list})