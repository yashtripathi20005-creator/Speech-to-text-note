#!/usr/bin/env python3
"""
Speech-to-Text Note Taker
Main entry point for the application
"""

import sys
import tkinter as tk
from gui import SpeechToTextGUI


def main():
    """Main application entry point"""
    try:
        # Create root window
        root = tk.Tk()
        
        # Set application icon (optional)
        try:
            root.iconbitmap(default='icon.ico')
        except:
            pass  # Icon file not found, continue without it
        
        # Create application
        app = SpeechToTextGUI(root)
        
        # Start the application
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
