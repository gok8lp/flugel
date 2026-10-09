#!/bin/bash
# FLUGEL APK derleyici (sistem-bakim) — Ubuntu'nun acik kaynak Android araclariyla, Google SDK/Gradle olmadan.
set -e
cd "$(dirname "$0")"
J=/usr/lib/jvm/java-21-openjdk-amd64/bin
A=/usr/lib/android-sdk/platforms/android-23/android.jar
rm -rf gen obj bin; mkdir -p gen obj bin anahtar
aapt package -f -m -J gen -M AndroidManifest.xml -S res -I $A
$J/javac -Xlint:-options -source 8 -target 8 -bootclasspath $A -classpath $A -d obj $(find src gen -name '*.java')
$J/java -jar /usr/lib/android-sdk/build-tools/debian/lib/dx.jar --dex --output=bin/classes.dex obj
aapt package -f -M AndroidManifest.xml -S res -I $A -F bin/imzasiz.apk
(cd bin && aapt add imzasiz.apk classes.dex >/dev/null)
zipalign -f 4 bin/imzasiz.apk bin/hizali.apk
# imza anahtari: ilk derlemede uretilir (rastgele sifre, sadece bu klasorde). Ayni anahtarla imzalanan surumler ustune kurulur.
if [ ! -f anahtar/flugel.jks ]; then
  head -c 24 /dev/urandom | base64 | tr -d '/+=' > anahtar/sifre; chmod 600 anahtar/sifre
  $J/keytool -genkeypair -keystore anahtar/flugel.jks -alias flugel -keyalg RSA -keysize 3072 -validity 36500 \
    -storepass "$(cat anahtar/sifre)" -keypass "$(cat anahtar/sifre)" -dname "CN=FLUGEL, O=flugelserver" >/dev/null 2>&1
fi
apksigner sign --ks anahtar/flugel.jks --ks-pass file:anahtar/sifre --out bin/FLUGEL.apk bin/hizali.apk
apksigner verify --print-certs bin/FLUGEL.apk | head -3
ls -la bin/FLUGEL.apk
