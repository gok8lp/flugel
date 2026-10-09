#!/bin/bash
. /usr/local/lib/sistem-bakim/whatsapp-kapat.sh  # sistem-bakim
PHONE="<TELEFON>"
APIKEY="<CALLMEBOT_APIKEY>"

MESSAGE_BODY=$(cat)
SUBJECT="${SMARTD_SUBJECT:-SMART Uyarisi}"
DEVICE="${SMARTD_DEVICE:-?}"

MESSAGE="!! SMART UYARISI !!
$SUBJECT
Cihaz: $DEVICE

$MESSAGE_BODY"

curl -s -G "https://api.callmebot.com/whatsapp.php" \
  --data-urlencode "phone=$PHONE" \
  --data-urlencode "text=$MESSAGE" \
  --data-urlencode "apikey=$APIKEY" > /dev/null
