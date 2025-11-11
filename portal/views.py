from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import GuestSession



def connect_view(request):
    """
    - Majourly handle form submissions
    - Get user's phone numbers that we will used to make Mpesa push notification
    - fetch the hiden ID so that we can get a session
    - 
    """
    if request.method == 'POST':
        # get data from the submitted form

        phone_number = request.POST.get('phone_number')
        session_id = request.POST.get('session_id') # get the hidden ID field
        try:
            # get the session in the database
            session = GuestSession.objects.get(id=session_id)
            # update the session with the phone number
            session.phone_number = phone_number
            session.save()

            print(f"--- PHONE UPDATED ---")
            print(f"Session:{session.id}")
            print(f"phone: {session.phone_number}")
            print(f"------------------------")

            # TODO: Redirect to a user to a waitting page

           # context = {'session': session, 'message': 'phone number saved'}
            # after collecting the user's details, redirect the user to a waitting page as we perform mpesa calls
            return redirect('wait_for_payment_view', session_id=session.id)

        except GuestSession.DoesNotExist:
            return HttpResponse("Error: Invalid session. Please  connect to the wifi", status=400)

        # TODO: we will trigger the mpesa push here
        
        # Handle page load - GET request
    else:
        # Get the user's mac Address from the query parameter
        # unifi sends it as a an id
        user_mac =request.GET.get('id')

        # without the mac, we cannot do anython
        if not user_mac:
            return HttpResponse("Invalid request. No mac address provided by the network", status=400)

        # find the session with this mac address and if it does not exist, create a new one

        session, created = GuestSession.objects.get_or_create(
                mac_address=user_mac
                )

        if created:
            print(f"---NEW SESSION CREATED----")
            print(f"MAC: {session.mac_address}")
            print(f"---------------------")
        else:
            print(f"--EXISTING SESSION FOUND---")
            print(f"MAC: {session.mac_address}")
            print(f"---------------------")
        context = {
                'session': session
                }

        return render(request, 'portal/payment_form.html', context)

def wait_for_payment_view(request, session_id):
    # try getting the session, if not, show a 404 page not found erorr
    session = get_object_or_404(GuestSession, id=session_id)

    context = {
            'session': session
            }
    return render(request, 'portal/wait_for_payment.html', context)



