package org.myai;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.speech.RecognizerIntent;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import org.json.JSONObject;
import java.util.ArrayList;

public class Bridge extends WebChromeClient {
    public static final int REQ_FILE = 4242, REQ_VOICE = 4243;
    private final Activity act;
    private final WebView wv;
    private ValueCallback<Uri[]> cb;

    public Bridge(Activity a, WebView w) { act = a; wv = w; }

    private void js(final String code) {
        act.runOnUiThread(new Runnable() { public void run() { wv.evaluateJavascript(code, null); } });
    }

    // File picker for <input type=file>
    @Override
    public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> c, FileChooserParams p) {
        if (cb != null) cb.onReceiveValue(null);
        cb = c;
        try {
            act.startActivityForResult(p.createIntent(), REQ_FILE);
        } catch (Exception e) {
            cb = null;
            c.onReceiveValue(null);
        }
        return true;
    }

    @Override
    public void onPermissionRequest(final PermissionRequest r) {
        act.runOnUiThread(new Runnable() { public void run() { r.grant(r.getResources()); } });
    }

    // Called from JS: Android.startVoice()
    @JavascriptInterface
    public void startVoice() {
        act.runOnUiThread(new Runnable() {
            public void run() {
                try {
                    Intent i = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                    i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                    i.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak now");
                    act.startActivityForResult(i, REQ_VOICE);
                } catch (Exception e) {
                    js("window.onVoiceError(" + JSONObject.quote("No speech service on this device") + ")");
                }
            }
        });
    }

    // Python forwards onActivityResult here
    public void onResult(int req, int res, Intent data) {
        if (req == REQ_FILE) {
            if (cb != null) {
                cb.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
                cb = null;
            }
        } else if (req == REQ_VOICE) {
            String t = null;
            if (res == Activity.RESULT_OK && data != null) {
                ArrayList<String> r = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                if (r != null && !r.isEmpty()) t = r.get(0);
            }
            if (t != null) js("window.onVoice(" + JSONObject.quote(t) + ")");
            else js("window.onVoiceError('Nothing heard')");
        }
    }
}
