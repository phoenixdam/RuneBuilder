#!/usr/bin/env python3
"""
League of Legends Champion Rune Builder

A desktop application for building and managing League of Legends rune pages
using the Model-View-Controller (MVC) architectural pattern.
"""

from controllers.main_controller import MainController


def main():
    """Main entry point for the application"""
    app = MainController()
    app.run()


if __name__ == "__main__":
    main()