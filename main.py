import webview
import json
import os
import sys
import threading

class MagisterBridge:
    def __init__(self):
        self.base_path = os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.abspath(".")
        self.scriptorium_file = os.path.join(self.base_path, "scriptorium_data.json")
        # Give Tabula its own dedicated save file so it doesn't corrupt Scriptorium
        self.tabula_file = os.path.join(self.base_path, "tabula_data.json")

    def load_from_disk(self):
        if os.path.exists(self.scriptorium_file):
            with open(self.scriptorium_file, "r", encoding='utf-8') as f:
                content = f.read()
                return content if content.strip() else "{}"
        return "{}"

    def load_tabula_from_disk(self):
        if os.path.exists(self.tabula_file):
            with open(self.tabula_file, "r", encoding='utf-8') as f:
                content = f.read()
                return content if content.strip() else "{}"
        return "{}"

    def save_to_disk(self, data):
        try:
            # Smart routing: Checks the JSON payload to see who is saving
            target_file = self.tabula_file if '"tabula_data"' in data else self.scriptorium_file
            with open(target_file, "w", encoding='utf-8') as f:
                f.write(data)
            return "SUCCESS"
        except Exception as e:
            print(f"Python Error: {e}")
            return str(e)
            
    def export_individual_item(self, filename, content):
            """Native Save Dialog for individual files."""
            try:
                # Explicitly find the main window
                active_window = webview.active_window()
                if not active_window:
                    active_window = webview.windows[0]

                result = active_window.create_file_dialog(
                    webview.FileDialog.SAVE, 
                    directory='', 
                    save_filename=filename,
                    file_types=('Data Files (*.json;*.csv)', 'All files (*.*)')
                )
                
                # The result is usually a TUPLE or a LIST in newer versions
                if result:
                    # If result is ('C:/path/file.json',), take the first item
                    file_path = result[0] if isinstance(result, (list, tuple)) else result
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"FILE SAVED TO: {file_path}") # Check your terminal!
                    return "SUCCESS"
                
                print("DIALOG CANCELLED BY USER")
                return "CANCELLED"
            except Exception as e:
                print(f"PYTHON EXPORT ERROR: {str(e)}")
                return "CANCELLED"

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def on_closing():
    print("Initiating shutdown...")
    
    # This is the fix: Wrap the JS call in a thread so Python doesn't WAIT for JS to reply.
    def fire_and_forget_save():
        try:
            window.evaluate_js('if(window.triggerAutoBackups) window.triggerAutoBackups();')
        except:
            pass
            
    threading.Thread(target=fire_and_forget_save).start()
    
    print("Backups triggered. Force-closing in 0.3s...")
    
    # Kill the process regardless of what JS is doing.
    import os
    threading.Timer(0.3, lambda: os._exit(0)).start()

if __name__ == "__main__":
    bridge = MagisterBridge()
    html_path = get_resource_path('scriptorium.html') 
    
    window = webview.create_window(
        'Ars Memoria - Magister Edition', 
        html_path, 
        js_api=bridge,
        width=1600,
        height=900,
        background_color='#e6d8c3',
        maximized=True
    )

    window.events.closing += on_closing
    webview.start()