import tkinter as tk
from tkinter import ttk, messagebox, font
import requests
import base64
import json
import time
import threading
from tkinter import BooleanVar

class DiscordServerCloner:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Nexus Cloner by Cyberseal")
        self.window.geometry("850x700")
        self.window.configure(bg="#1a1a1a")

        self.create_template_var = BooleanVar()
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.colors = {
            "bg": "#1a1a1a",
            "fg": "#ffffff",
            "accent": "#5865F2",
            "input_bg": "#2d2d2d",
            "secondary": "#4a4a4a",
            "success": "#43b581",
            "error": "#f04747"
        }
        
        self.configure_styles()
        self.create_widgets()
        
        self.token = ""
        self.headers = {}
        self.base_url = "https://discord.com/api/v9"
        self.create_template_var = BooleanVar()
        
        self.running = False

    def configure_styles(self):
        self.style.configure(
            'TFrame', 
            background=self.colors["bg"]
        )
        
        self.style.configure(
            'Rounded.TButton',
            background=self.colors["accent"],
            foreground=self.colors["fg"],
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            padding=10,
            relief='flat',
            bordercolor=self.colors["accent"],
            focuscolor=self.colors["accent"],
            width=15
        )
        self.style.map('Rounded.TButton',
            background=[('active', self.colors["accent"]), ('!disabled', self.colors["accent"])],
            foreground=[('active', self.colors["fg"])]
        )
        
        self.style.configure(
            'Dark.TEntry',
            fieldbackground=self.colors["input_bg"],
            foreground=self.colors["fg"],
            insertcolor=self.colors["fg"],
            bordercolor="#363636",
            lightcolor="#363636",
            darkcolor="#363636",
            padding=8
        )
        
        self.style.configure(
            'Custom.TCheckbutton',
            background=self.colors["bg"],
            foreground=self.colors["fg"],
            indicatorcolor=self.colors["accent"],
            font=("Segoe UI", 9)
        )

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.window)
        header_frame.pack(pady=20, fill='x')
        
        title = tk.Label(
            header_frame,
            text="SERVER CLONER PRO",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["bg"]
        )
        title.pack()

        input_frame = ttk.Frame(self.window)
        input_frame.pack(pady=15, fill='x', padx=30)

        self.create_input_field(input_frame, "User Token:", 0)
        self.create_input_field(input_frame, "Source Server ID:", 1)
        self.create_input_field(input_frame, "Target Server ID:", 2)

        self.template_check = ttk.Checkbutton(
            input_frame,
            text="Create Server Template After Cloning",
            variable=self.create_template_var,
            style='Custom.TCheckbutton'
        )
        self.template_check.grid(row=3, column=1, pady=10, sticky='w')

        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=15)
        
        self.clone_btn = ttk.Button(
            button_frame,
            text="Start Cloning",
            style='Rounded.TButton',
            command=self.toggle_process
        )
        self.clone_btn.pack(side=tk.LEFT, padx=10)

        log_frame = ttk.Frame(self.window)
        log_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self.log = tk.Text(
            log_frame,
            bg=self.colors["input_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            font=("Consolas", 9),
            wrap=tk.WORD,
            padx=12,
            pady=12
        )
        self.log.pack(fill='both', expand=True)
        
        self.template_link = tk.Label(
            log_frame,
            text="",
            fg=self.colors["accent"],
            bg=self.colors["input_bg"],
            font=("Segoe UI", 9, "underline")
        )
        self.template_link.pack(pady=5)

    def create_input_field(self, frame, label_text, row):
        label = tk.Label(
            frame,
            text=label_text,
            fg=self.colors["fg"],
            bg=self.colors["bg"],
            font=("Segoe UI", 9)
        )
        label.grid(row=row, column=0, sticky='w', pady=5)
        
        entry = ttk.Entry(
            frame,
            width=50,
            style='Dark.TEntry',
            font=("Segoe UI", 9)
        )
        entry.grid(row=row, column=1, padx=10, pady=5)
        
        if "Token" in label_text:
            self.token_entry = entry
        elif "Source" in label_text:
            self.source_id_entry = entry
        else:
            self.target_id_entry = entry

    def toggle_process(self):
        if not self.running:
            self.start_clone()
        else:
            self.stop_clone()

    def start_clone(self):
        self.token = self.token_entry.get().strip()
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        if not self.validate_inputs():
            return
            
        self.running = True
        self.clone_btn.config(text="Stop Cloning")
        threading.Thread(target=self.clone_process, daemon=True).start()

    def stop_clone(self):
        self.running = False
        self.clone_btn.config(text="Start Cloning")
        self.log_message("Process stopped by user", "error")

    def validate_inputs(self):
        required_fields = [
            (self.token, "User Token"),
            (self.source_id_entry.get(), "Source Server ID"),
            (self.target_id_entry.get(), "Target Server ID")
        ]
        
        for value, name in required_fields:
            if not value:
                self.show_error(f"{name} is required!")
                return False
                
        user_req = requests.get(f"{self.base_url}/users/@me", headers=self.headers)
        if user_req.status_code != 200:
            self.show_error("Invalid User Token!")
            return False
            
        return True

    def clone_process(self):
        try:
            source_id = self.source_id_entry.get().strip()
            target_id = self.target_id_entry.get().strip()
            
            self.clear_target_server(target_id)
            self.clone_server_settings(source_id, target_id)
            roles_mapping = self.clone_roles(source_id, target_id)
            self.clone_channels(source_id, target_id, roles_mapping)
            self.clone_emojis(source_id, target_id)
            
            if self.create_template_var.get():
                template_url = self.create_server_template(target_id)
                if template_url:
                    self.template_link.config(text=f"Template Created: {template_url}")
            
            self.log_message("Cloning process completed successfully!", "success")
            
        except Exception as e:
            self.log_message(f"Critical error: {str(e)}", "error")
        finally:
            self.running = False
            self.clone_btn.config(text="Start Cloning")

    def api_request(self, method, endpoint, **kwargs):
        for _ in range(3):
            response = requests.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                self.log_message(f"Rate limited - Retrying in {retry_after}s...", "warning")
                time.sleep(retry_after)
                continue
                
            return response
        return response

    def clear_target_server(self, target_id):
        self.log_message("Starting server cleanup...", "info")
        
        channels = self.api_request("GET", f"/guilds/{target_id}/channels").json()
        for channel in channels:
            self.api_request("DELETE", f"/channels/{channel['id']}")
            self.log_message(f"Deleted channel: {channel['name']}", "debug")
            time.sleep(0.5)

        roles = self.api_request("GET", f"/guilds/{target_id}/roles").json()
        for role in roles:
            if role['name'] != '@everyone':
                self.api_request("DELETE", f"/guilds/{target_id}/roles/{role['id']}")
                self.log_message(f"Deleted role: {role['name']}", "debug")
                time.sleep(0.5)

        emojis = self.api_request("GET", f"/guilds/{target_id}/emojis").json()
        for emoji in emojis:
            self.api_request("DELETE", f"/guilds/{target_id}/emojis/{emoji['id']}")
            self.log_message(f"Deleted emoji: {emoji['name']}", "debug")
            time.sleep(0.5)

    def clone_server_settings(self, source_id, target_id):
        self.log_message("Cloning server settings...", "info")
        source = self.api_request("GET", f"/guilds/{source_id}").json()
        
        payload = {
            "name": source['name'],
            "verification_level": source['verification_level'],
            "afk_timeout": source['afk_timeout'],
            "system_channel_flags": source.get('system_channel_flags', 0)
        }
        
        if 'icon' in source:
            icon_url = f"https://cdn.discordapp.com/icons/{source_id}/{source['icon']}.png?size=4096"
            icon_data = requests.get(icon_url).content
            payload["icon"] = f"data:image/png;base64,{base64.b64encode(icon_data).decode('utf-8')}"
        
        self.api_request("PATCH", f"/guilds/{target_id}", json=payload)
        time.sleep(1)

    def clone_roles(self, source_id, target_id):
        self.log_message("Cloning roles...", "info")
        roles = self.api_request("GET", f"/guilds/{source_id}/roles").json()
        role_mapping = {}
        
        for role in reversed(roles):
            if role['name'] == '@everyone':
                payload = {
                    "permissions": role['permissions'],
                    "color": role['color'],
                    "hoist": role['hoist'],
                    "mentionable": role['mentionable']
                }
                self.api_request("PATCH", f"/guilds/{target_id}/roles/{target_id}", json=payload)
                role_mapping[role['id']] = target_id
                continue
                
            payload = {
                "name": role['name'],
                "permissions": role['permissions'],
                "color": role['color'],
                "hoist": role['hoist'],
                "mentionable": role['mentionable']
            }
            
            new_role = self.api_request("POST", f"/guilds/{target_id}/roles", json=payload).json()
            role_mapping[role['id']] = new_role['id']
            self.log_message(f"Created role: {role['name']}", "debug")
            time.sleep(0.7)
            
        return role_mapping

    def clone_channels(self, source_id, target_id, role_mapping):
        self.log_message("Cloning channels...", "info")
        channels = self.api_request("GET", f"/guilds/{source_id}/channels").json()
        category_mapping = {}
        
        for channel in channels:
            if channel['type'] == 4:
                payload = self.create_channel_payload(channel, role_mapping)
                new_category = self.api_request("POST", f"/guilds/{target_id}/channels", json=payload).json()
                category_mapping[channel['id']] = new_category['id']
                self.log_message(f"Created category: {channel['name']}", "debug")
                time.sleep(0.7)

        for channel in channels:
            if channel['type'] != 4:
                payload = self.create_channel_payload(channel, role_mapping)
                if channel.get('parent_id'):
                    payload['parent_id'] = category_mapping.get(channel['parent_id'])
                    
                new_channel = self.api_request("POST", f"/guilds/{target_id}/channels", json=payload).json()
                self.log_message(f"Created channel: {channel['name']}", "debug")
                time.sleep(0.7)

    def create_channel_payload(self, channel, role_mapping):
        payload = {
            "name": channel['name'],
            "type": channel['type'],
            "position": channel['position'],
            "topic": channel.get('topic', ''),
            "nsfw": channel.get('nsfw', False),
            "rate_limit_per_user": channel.get('rate_limit_per_user', 0),
            "bitrate": channel.get('bitrate', 64000),
            "user_limit": channel.get('user_limit', 0),
            "permission_overwrites": []
        }
        
        for overwrite in channel['permission_overwrites']:
            new_id = role_mapping.get(overwrite['id'], overwrite['id'])
            payload['permission_overwrites'].append({
                "id": new_id,
                "type": overwrite['type'],
                "allow": str(overwrite['allow']),
                "deny": str(overwrite['deny'])
            })
            
        return payload

    def clone_emojis(self, source_id, target_id):
        self.log_message("Cloning emojis...", "info")
        emojis = self.api_request("GET", f"/guilds/{source_id}/emojis").json()
        
        for emoji in emojis:
            try:
                ext = "gif" if emoji['animated'] else "png"
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji['id']}.{ext}"
                emoji_data = requests.get(emoji_url).content
                
                payload = {
                    "name": emoji['name'],
                    "image": f"data:image/{ext};base64,{base64.b64encode(emoji_data).decode('utf-8')}"
                }
                
                self.api_request("POST", f"/guilds/{target_id}/emojis", json=payload)
                self.log_message(f"Created emoji: {emoji['name']}", "debug")
                time.sleep(1)
            except Exception as e:
                self.log_message(f"Failed to clone emoji {emoji['name']}: {str(e)}", "error")

    def create_server_template(self, guild_id):
        try:
            payload = {
                "name": "Cloned Template",
                "description": "Automatically generated by Nexus Cloner"
            }
            response = self.api_request("POST", f"/guilds/{guild_id}/templates", json=payload)
            
            if response.status_code == 201:
                template_data = response.json()
                return f"https://discord.new/{template_data['code']}"
            return None
        except Exception as e:
            self.log_message(f"Template error: {str(e)}", "error")
            return None

    def log_message(self, message, level="info"):
        color_map = {
            "info": self.colors["fg"],
            "success": self.colors["success"],
            "error": self.colors["error"],
            "warning": "#faa81a",
            "debug": "#747f8d"
        }
        
        tag = f"[{level.upper()}]" if level != "debug" else ""
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {tag} {message}\n", level)
        self.log.tag_config(level, foreground=color_map[level])
        self.log.config(state=tk.DISABLED)
        self.log.see(tk.END)
        self.window.update_idletasks()

    def show_error(self, message):
        messagebox.showerror("Error", message, parent=self.window)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    cloner = DiscordServerCloner()
    cloner.run()