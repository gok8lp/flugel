package com.flugel.akis;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

/**
 * FLUGEL — sunucudaki FLUGEL Akis'i acan sade kabuk (sistem-bakim).
 * Sadece Tailscale agindaki adresi yukler; baska alan adlari telefonun tarayicisinda acilir.
 * Arka plan servisi, veri toplama, ek izin YOK.
 */
public class Ana extends Activity {
    static final String EV = "flugelserver.tail42f1f4.ts.net";
    static final String ADRES = "https://" + EV + ":8443/#/ana";
    WebView web;
    FrameLayout kok;
    View tamEkran;
    WebChromeClient.CustomViewCallback tamEkranGeri;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        Window w = getWindow();
        w.setStatusBarColor(Color.BLACK);
        w.setNavigationBarColor(Color.BLACK);
        kok = new FrameLayout(this);
        kok.setBackgroundColor(Color.BLACK);
        web = new WebView(this);
        web.setBackgroundColor(Color.BLACK);
        kok.addView(web, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(kok);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setSupportMultipleWindows(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, String adres) {
                Uri u = Uri.parse(adres);
                if (EV.equals(u.getHost())) return false;          // kendi sunucumuz: uygulamada kal
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception e) { }
                return true;                                         // digerleri: telefonun tarayicisi
            }

            @Override
            public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
                if (r.isForMainFrame()) hataGoster();
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onShowCustomView(View gorunum, CustomViewCallback geri) {   // YouTube tam ekran
                tamEkran = gorunum; tamEkranGeri = geri;
                kok.addView(gorunum, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
                web.setVisibility(View.GONE);
                getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
            }

            @Override
            public void onHideCustomView() {
                if (tamEkran != null) kok.removeView(tamEkran);
                tamEkran = null;
                web.setVisibility(View.VISIBLE);
                getWindow().getDecorView().setSystemUiVisibility(0);
                if (tamEkranGeri != null) tamEkranGeri.onCustomViewHidden();
            }
        });
        if (b != null) web.restoreState(b); else web.loadUrl(ADRES);
    }

    void hataGoster() {
        String sayfa = "<html><body style='background:#000;color:#e7e9ea;font-family:sans-serif;display:flex;flex-direction:column;"
            + "align-items:center;justify-content:center;height:90vh;text-align:center;padding:24px'>"
            + "<div style='font-size:42px;letter-spacing:.3em;font-family:serif'>FLUGEL</div>"
            + "<p style='color:#8b9095;margin:18px 0'>Sunucuya ulaşılamadı.<br>Telefonda <b>Tailscale</b> açık mı?</p>"
            + "<a href='" + ADRES + "' style='background:#1d9bf0;color:#fff;padding:12px 26px;border-radius:999px;text-decoration:none;font-weight:bold'>Tekrar dene</a>"
            + "</body></html>";
        web.loadDataWithBaseURL("https://" + EV + ":8443/", sayfa, "text/html", "utf-8", null);
    }

    @Override
    public void onBackPressed() {
        if (tamEkran != null) { onHideCustomViewSafe(); return; }
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    void onHideCustomViewSafe() {
        if (tamEkranGeri != null) tamEkranGeri.onCustomViewHidden();
        if (tamEkran != null) kok.removeView(tamEkran);
        tamEkran = null;
        web.setVisibility(View.VISIBLE);
        getWindow().getDecorView().setSystemUiVisibility(0);
    }

    @Override
    protected void onSaveInstanceState(Bundle b) { super.onSaveInstanceState(b); web.saveState(b); }
}
