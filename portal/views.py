from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import GuestSession, WifiPlan
from .mpesa_utils import trigger_stk_push
from django.urls import reverse # A helper for creating URLs
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .unifi_utils import authorize_user
def connect_view(request):
    """
    - Majorly handle form submissions
    - Get user's phone numbers that we will used to make Mpesa push notification
    - fetch the hiden ID so that we can get a session
    - 
    """
    if request.method == 'POST':
        # get data from the submitted form

        phone_number = request.POST.get('phone_number') # Get the phone number from the data
        session_id = request.POST.get('session_id') # get the hidden ID field
        plan_id = request.POST.get('plan_id') # get the selected plan
        try:
            # get the session in the database
            session = GuestSession.objects.get(id=session_id)

            plan = WifiPlan.objects.get(id=plan_id) 
            # update the session with the phone number, plan and price
            session.phone_number = phone_number
            session.plan = plan
            session.save()
            amount = plan.price

            print (f"---TRIGGERING STK PUSH for {phone_number}----")

            checkout_request_id = trigger_stk_push(

                    phone_number=phone_number,
                    amount=amount,
                    session_id=session_id # send the session id for tracking
                    )

            session.checkout_request_id = checkout_request_id
            session.save()

            print(f"----STK PUSH   INITIATED, ID: {checkout_request_id}---")

            # after collecting the user's details, redirect the user to a waitting page as we perform mpesa calls
            return redirect('wait_for_payment_view', session_id=session.id)

        except GuestSession.DoesNotExist:
            # incase of an error, fetch the plans again to render the plans
            return HttpResponse("Error: Invalid session. Please  reconnect to the wifi", status=400)

        except Exception as e:
            # Handle Mpesa or other errors

            plans = WifiPlan.objects.all()
            context = {
                   'session': session,
                   'plans': plans,
                   'error': f"payment Error:{e}"
            }
            return render(request, 'portal/payment_form.html', context)

        # Handle page load and show the menu
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

        # get all the plans to display
        plans = WifiPlan.objects.all().order_by('price')

        context = {
                'session': session,
                'plans': plans # send the plans to HTML
                }

        return render(request, 'portal/payment_form.html', context)

def wait_for_payment_view(request, session_id):
    # try getting the session, if not, show a 404 page not found erorr
    session = get_object_or_404(GuestSession, id=session_id)

    context = {
            'session': session
            }
    return render(request, 'portal/wait_for_payment.html', context)

@csrf_exempt # This tells django to allow POSTs from safaricom
def mpesa_callback_view(request):
    """ 
    - This function gets the response from safarcom to confirm that the payment
    was successful or not

    """
    if request.method != 'POST':
        return HttpResponse('Invalid Method', status=400)
    print("---MPESA CALLBACK RECEIVED----")

    # get the json data from the request body
    try:
        body = json.loads(request.body)
        print(f"data: {body}") # log the full respose to the terminal
    except json.JSONDecodeError:
        print("Error: Invalid JSON received")
        return HttpResponse("Invalid JSON", status=400)

    # parse the JSON from safaricom
    try:
        data = body.get('Body', {}).get('stkCallback', {})
        result_code = data.get('ResultCode')

        # check if payment was successfull
        if result_code == 0:
            print("PAYMENT SUCCESSFUL..")

            # get the ID and find our sesison
            checkout_id = data.get('CheckoutRequestID')

            # get the session from the database
            session = GuestSession.objects.get(checkout_request_id=checkout_id)

            # update our session

            session.is_paid = True
            session.paid_at= timezone.now() # mark the payment time
            session.save()
            # calculate time the user will be allowed to connect to the network
            minutes_to_add = session.plan.duration_in_minutes

            authorize_user(session.mac_address, minutes=minutes_to_add)

            print(f"Session {session.id} marked as PAID")

        else:
            # payment failed or was canceled
            print(f"PAYMENT FAILED. Resultcode:{result_code}")
            # TODO: Mark the sesion as failed 


    except Exception as e:
        # Log errors during processing
        print(f"Callback processing error: {e}")

    return JsonResponse({'ResultCode':0, "ResultDesc": "Accepted"})

def check_payment_status_view(request, session_id):
    """
    - An API endpoint that checks if the GuestSession.is_paid is true
    - It querries the database
    """
    try:
        # find the session
        session = GuestSession.objects.get(id=session_id)
        
        # do the necessary check
        if session.is_paid:
            return JsonResponse({'status': 'paid'})
        else:
            return JsonResponse({'status': 'pending'})
    except GuestSession.DoesNotExist:
        return JsonResponse({'status': 'Not_found'}, status=404)
