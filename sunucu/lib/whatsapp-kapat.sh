# sistem-bakim: WhatsApp (CallMeBot) kapatildi. callmebot'a giden curl cagrilari /usr/local/bin/bildirim'e yonlendirilir.
curl() {
  case "$*" in
    *callmebot.com/whatsapp*)
      local t="" a
      for a in "$@"; do
        case "$a" in
          text=*) t="${a#text=}" ;;
          *text=*) t=$(printf '%s' "$a" | sed -n 's/.*[?&]text=\([^&]*\).*/\1/p') ;;
        esac
      done
      /usr/local/bin/bildirim "$t"; return 0 ;;
  esac
  command curl "$@"
}
