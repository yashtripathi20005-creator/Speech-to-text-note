"""
GUI Module
Main application window using tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from audio_handler import AudioHandler
from note_manager import NoteManager
import time


class SpeechToTextGUI:
    def __init__(self, root):
        """Initialize the main GUI application"""
        self.root = root
        self.root.title("Speech-to-Text Note Taker")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.audio_handler = AudioHandler()
        self.note_manager = NoteManager()
        
        # State variables
        self.is_recording = False
        self.auto_punctuation = True
        self.live_transcription = True
        self.current_text = ""
        
        # Setup GUI
        self.setup_menu()
        self.setup_main_layout()
        self.setup_controls()
        self.setup_status_bar()
        
        # Start checking for audio input
        self.update_transcription()
    
    def setup_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Note", command=self.new_note, accelerator="Ctrl+N")
        file_menu.add_command(label="Save Note", command=self.save_note, accelerator="Ctrl+S")
        file_menu.add_command(label="Load Note", command=self.load_note, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export as Markdown", command=self.export_markdown)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear", command=self.clear_note)
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_checkbutton(label="Auto Punctuation", variable=tk.BooleanVar(value=True))
        settings_menu.add_checkbutton(label="Live Transcription", variable=tk.BooleanVar(value=True))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_main_layout(self):
        """Set up the main application layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Speech-to-Text Note Taker", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Note text area
        self.note_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                    font=('Arial', 12), height=20)
        self.note_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure tags for formatting
        self.note_text.tag_config('new', background='#e8f5e9')
    
    def setup_controls(self):
        """Set up the control buttons and settings"""
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.root.columnconfigure(0, weight=1)
        
        # Control buttons
        self.record_button = ttk.Button(control_frame, text="🎤 Start Recording", 
                                        command=self.toggle_recording, width=20)
        self.record_button.grid(row=0, column=0, padx=(0, 10))
        
        self.pause_button = ttk.Button(control_frame, text="⏸ Pause", 
                                       command=self.pause_recording, width=15, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_button = ttk.Button(control_frame, text="🗑 Clear", 
                                       command=self.clear_note, width=15)
        self.clear_button.grid(row=0, column=2, padx=(0, 10))
        
        self.save_button = ttk.Button(control_frame, text="💾 Save Note", 
                                      command=self.save_note, width=15)
        self.save_button.grid(row=0, column=3, padx=(0, 10))
        
        # Settings
        settings_frame = ttk.Frame(control_frame)
        settings_frame.grid(row=0, column=4, padx=(20, 0))
        
        self.punct_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Auto Punctuation", 
                       variable=self.punct_var).pack(side=tk.LEFT, padx=(0, 10))
        
        self.live_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Live Transcription", 
                       variable=self.live_var).pack(side=tk.LEFT)
    
    def setup_status_bar(self):
        """Set up the status bar at the bottom"""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding="5")
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.recording_indicator = ttk.Label(self.status_bar, text="●", foreground="gray")
        self.recording_indicator.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.word_count_label = ttk.Label(self.status_bar, text="Words: 0", anchor=tk.E)
        self.word_count_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def toggle_recording(self):
        """Toggle the recording state"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording audio"""
        try:
            self.audio_handler.start_listening()
            self.is_recording = True
            self.record_button.config(text="⏹ Stop Recording")
            self.pause_button.config(state=tk.NORMAL)
            self.status_label.config(text="Recording... Speak now!")
            self.recording_indicator.config(foreground="red")
        except Exception as e:
            messagebox.showerror("Error", f"Could not start recording: {e}")
    
    def stop_recording(self):
        """Stop recording audio"""
        try:
            self.audio_handler.stop_listening()
            self.is_recording = False
            self.record_button.config(text="🎤 Start Recording")
            self.pause_button.config(text="⏸ Pause", state=tk.DISABLED)
            self.status_label.config(text="Ready")
            self.recording_indicator.config(foreground="gray")
        except Exception as e:
            messagebox.showerror("Error", f"Could not stop recording: {e}")
    
    def pause_recording(self):
        """Pause/resume recording"""
        if self.is_recording:
            # Pause
            self.audio_handler.stop_listening()
            self.is_recording = False
            self.pause_button.config(text="▶ Resume")
            self.status_label.config(text="Paused")
            self.recording_indicator.config(foreground="orange")
        else:
            # Resume
            self.audio_handler.start_listening()
            self.is_recording = True
            self.pause_button.config(text="⏸ Pause")
            self.status_label.config(text="Recording... Speak now!")
            self.recording_indicator.config(foreground="red")
    
    def update_transcription(self):
        """Update the note text with transcribed audio"""
        if self.live_var.get():
            # Get all pending transcriptions
            texts = self.audio_handler.get_all_texts()
            
            if texts:
                for text in texts:
                    if text:
                        # Add text to current note
                        self.note_manager.add_text(text)
                        
                        # Insert text with new tag for visual feedback
                        self.note_text.insert(tk.END, text + " ", 'new')
                        self.note_text.see(tk.END)
                
                self.update_word_count()
        
        # Schedule next update
        self.root.after(100, self.update_transcription)
    
    def clear_note(self):
        """Clear the current note"""
        if self.note_text.get(1.0, tk.END).strip():
            if messagebox.askyesno("Clear Note", "Are you sure you want to clear the current note?"):
                self.note_text.delete(1.0, tk.END)
                self.note_manager.clear_current_note()
                self.update_word_count()
                self.status_label.config(text="Note cleared")
    
    def new_note(self):
        """Create a new note"""
        if self.note_text.get(1.0, tk.END).strip():
            if messagebox.askyesno("New Note", "Save current note before creating new?"):
                self.save_note()
        self.note_text.delete(1.0, tk.END)
        self.note_manager.clear_current_note()
        self.update_word_count()
        self.status_label.config(text="New note created")
    
    def save_note(self):
        """Save the current note"""
        content = self.note_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Save Note", "No content to save!")
            return
        
        self.note_manager.current_note = content
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.note_manager.save_directory
        )
        
        if filename:
            import os
            filename = os.path.basename(filename)
            result = self.note_manager.save_note(filename)
            messagebox.showinfo("Save Note", result)
            self.status_label.config(text=result)
    
    def load_note(self):
        """Load a note from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.note_manager.save_directory
        )
        
        if filename:
            import os
            filename = os.path.basename(filename)
            content = self.note_manager.load_note(filename)
            self.note_text.delete(1.0, tk.END)
            self.note_text.insert(1.0, content)
            self.update_word_count()
            self.status_label.config(text=f"Loaded: {filename}")
    
    def export_markdown(self):
        """Export current note as Markdown"""
        content = self.note_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Export", "No content to export!")
            return
        
        # Save as markdown
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialdir=self.note_manager.save_directory
        )
        
        if filename:
            import os
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Speech-to-Text Note\n\n")
                    f.write(f"*Created: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                    f.write(content)
                
                messagebox.showinfo("Export", f"Note exported to: {os.path.basename(filename)}")
                self.status_label.config(text=f"Exported: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")
    
    def select_all(self):
        """Select all text in the note"""
        self.note_text.tag_add('sel', '1.0', tk.END)
    
    def update_word_count(self):
        """Update the word count label"""
        content = self.note_text.get(1.0, tk.END).strip()
        word_count = len(content.split()) if content else 0
        self.word_count_label.config(text=f"Words: {word_count}")
    
    def show_help(self):
        """Show help information"""
        help_text = """
        Speech-to-Text Note Taker - How to Use
        
        1. Click "Start Recording" to begin capturing speech
        2. Speak clearly into your microphone
        3. Text will appear in real-time in the note area
        4. Use "Pause" to temporarily stop recording
        5. Click "Save Note" to save your work
        6. Use "Clear" to start a new note
        7. Export notes as Markdown for formatting
        
        Keyboard Shortcuts:
        - Ctrl+N: New Note
        - Ctrl+S: Save Note
        - Ctrl+O: Load Note
        - Ctrl+A: Select All
        - Ctrl+Q: Exit
        
        Tips:
        - Speak clearly and at a moderate pace
        - Use "Auto Punctuation" for automatic periods and commas
        - Adjust microphone settings in your system
        """
        
        messagebox.showinfo("How to Use", help_text)
    
    def show_about(self):
        """Show about information"""
        about_text = """
        Speech-to-Text Note Taker v1.0
        
        A real-time speech recognition application
        for taking notes using voice input.
        
        Built with:
        - Python 3
        - SpeechRecognition
        - tkinter
        - PyAudio
        
        Features:
        - Real-time transcription
        - Save/Load notes
        - Export to Markdown
        - Auto punctuation
        - Word count tracking
        
        © 2024 Speech-to-Text Note Taker
        """
        
        messagebox.showinfo("About", about_text)
