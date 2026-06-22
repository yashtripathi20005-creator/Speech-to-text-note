"""
Note Manager Module
Handles saving, loading, and managing notes
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class NoteManager:
    def __init__(self, save_directory: str = "notes"):
        """Initialize the note manager with a save directory"""
        self.save_directory = save_directory
        self.current_note = ""
        self.note_history = []
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # Load existing notes
        self.load_notes()
    
    def add_text(self, text: str):
        """Add text to the current note"""
        if text:
            self.current_note += text + " "
    
    def get_current_note(self) -> str:
        """Get the current note content"""
        return self.current_note.strip()
    
    def clear_current_note(self):
        """Clear the current note"""
        self.current_note = ""
    
    def save_note(self, filename: Optional[str] = None) -> str:
        """Save the current note to a file"""
        if not self.current_note.strip():
            return "No content to save"
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}.txt"
        
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.current_note)
            
            # Add to history
            self.note_history.append({
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'preview': self.current_note[:100] + "..." if len(self.current_note) > 100 else self.current_note
            })
            
            self.save_note_history()
            return f"Note saved as: {filename}"
        
        except Exception as e:
            return f"Error saving note: {e}"
    
    def load_note(self, filename: str) -> str:
        """Load a note from a file"""
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.current_note = content
            return content
        except Exception as e:
            return f"Error loading note: {e}"
    
    def get_all_notes(self) -> List[Dict]:
        """Get a list of all saved notes"""
        notes = []
        
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.save_directory, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    notes.append({
                        'filename': filename,
                        'content': content,
                        'size': len(content),
                        'modified': os.path.getmtime(filepath)
                    })
            
            # Sort by modified time (newest first)
            notes.sort(key=lambda x: x['modified'], reverse=True)
            return notes
        
        except Exception as e:
            print(f"Error listing notes: {e}")
            return []
    
    def delete_note(self, filename: str) -> bool:
        """Delete a note file"""
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
    
    def save_note_history(self):
        """Save the note history to a JSON file"""
        history_file = os.path.join(self.save_directory, "history.json")
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.note_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_notes(self):
        """Load the note history from a JSON file"""
        history_file = os.path.join(self.save_directory, "history.json")
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.note_history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.note_history = []
    
    def export_note(self, filename: str, format: str = "txt") -> str:
        """Export a note in different formats (txt, md, pdf coming soon)"""
        filepath = os.path.join(self.save_directory, filename)
        
        if not os.path.exists(filepath):
            return "File not found"
        
        if format == "txt":
            # Already in txt format
            return filepath
        elif format == "md":
            # Convert to markdown
            md_filename = filename.replace('.txt', '.md')
            md_filepath = os.path.join(self.save_directory, md_filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Speech-to-Text Note\n\n")
                    f.write(f"*Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                    f.write(content)
                
                return md_filepath
            except Exception as e:
                return f"Error exporting: {e}"
        
        return "Unsupported format"
