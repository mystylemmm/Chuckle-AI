import os
import traceback

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

try:
    from jnius import autoclass
    from android import activity as android_activity
    from android.runnable import run_on_ui_thread
    from android.permissions import request_permissions, Permission

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
    Bridge = autoclass('org.myai.Bridge')
    ANDROID_OK = True
    IMPORT_ERROR = ""
except Exception:
    ANDROID_OK = False
    IMPORT_ERROR = traceback.format_exc()


class MyAIApp(App):
    webview = None
    bridge = None

    def build(self):
        Window.bind(on_keyboard=self.on_back_key)
        self.root = BoxLayout()
        if not ANDROID_OK:
            return Label(text="Android WebView error:\n" + IMPORT_ERROR)
        return self.root

    def on_start(self):
        if ANDROID_OK:
            try:
                request_permissions([Permission.RECORD_AUDIO])
            except Exception:
                pass
            android_activity.bind(on_activity_result=self.on_activity_result)
            self.create_webview()

    def on_activity_result(self, request_code, result_code, intent):
        try:
            if self.bridge:
                self.bridge.onResult(request_code, result_code, intent)
        except Exception:
            print(traceback.format_exc())

    @run_on_ui_thread
    def create_webview(self):
        try:
            activity = PythonActivity.mActivity
            activity.getWindow().setSoftInputMode(16)

            wv = WebView(activity)
            s = wv.getSettings()
            s.setJavaScriptEnabled(True)
            s.setDomStorageEnabled(True)
            s.setDatabaseEnabled(True)
            s.setAllowFileAccess(True)
            s.setAllowContentAccess(True)
            s.setMediaPlaybackRequiresUserGesture(False)
            s.setLoadWithOverviewMode(True)
            s.setUseWideViewPort(True)

            wv.setFocusable(True)
            wv.setFocusableInTouchMode(True)
            wv.setWebViewClient(WebViewClient())

            self.bridge = Bridge(activity, wv)
            wv.setWebChromeClient(self.bridge)
            wv.addJavascriptInterface(self.bridge, "Android")

            base = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base, "index.html")
            if os.path.exists(path):
                wv.loadUrl("file://" + path)
            else:
                wv.loadData("<h2>index.html not found</h2>", "text/html", "UTF-8")

            activity.addContentView(
                wv, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
            wv.requestFocus()
            self.webview = wv
        except Exception:
            print(traceback.format_exc())

    @run_on_ui_thread
    def go_back(self):
        try:
            if self.webview and self.webview.canGoBack():
                self.webview.goBack()
            else:
                PythonActivity.mActivity.moveTaskToBack(True)
        except Exception:
            pass

    def on_back_key(self, window, key, *args):
        if key == 27:
            self.go_back()
            return True
        return False

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    MyAIApp().run()
