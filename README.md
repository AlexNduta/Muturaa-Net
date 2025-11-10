# Muturaa-Net


This is a payment gateway that enables our WISP clients to make paynmets via mpesa.

**Componets**
- UCG: Controls the network
- sends users to our web server

**Django application**
- web server that:
    > Frontend: serves payment page to the user
    > backend: takes a user's phone number, calls the mpes API and triggers an STK push
    > Callback: Listens for callbacks from safaricom to confirm the payment

**APIs**
> Safaricom Daraja API is used to initiate payments
> Unifi API used by django app to send and 'authorize' command back to the UCG ultra



