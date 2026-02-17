"""
Screen utilities for Windows-compatible screen selection in pygame experiments.
This module provides functions to properly set up screen selection on Windows.
"""

import os
import sys
import pygame
import platform
from screeninfo import get_monitors
import time


def _try_focus_window_windows():
    """
    Best-effort: force the pygame window to the foreground on Windows.
    Returns True on success, False otherwise.
    """
    try:
        if os.name != "nt":
            return False

        wm_info = pygame.display.get_wm_info()
        hwnd = wm_info.get("window")
        if not hwnd:
            return False

        import ctypes
        import ctypes.wintypes as wt

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        SW_RESTORE = 9
        HWND_TOPMOST = -1
        HWND_NOTOPMOST = -2
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040

        # Try a more robust foreground technique:
        # - temporarily attach input threads
        # - restore window
        # - toggle topmost to force z-order update
        # - set foreground/active/focus
        fg_hwnd = user32.GetForegroundWindow()
        fg_pid = wt.DWORD()
        target_pid = wt.DWORD()

        fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, ctypes.byref(fg_pid)) if fg_hwnd else 0
        target_tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(target_pid))
        cur_tid = kernel32.GetCurrentThreadId()

        # Attach current thread to foreground + target threads
        if fg_tid:
            user32.AttachThreadInput(cur_tid, fg_tid, True)
        user32.AttachThreadInput(cur_tid, target_tid, True)

        # Restore and force to top
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

        # Foreground/focus attempts
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        user32.SetActiveWindow(hwnd)
        user32.SetFocus(hwnd)

        # Detach
        user32.AttachThreadInput(cur_tid, target_tid, False)
        if fg_tid:
            user32.AttachThreadInput(cur_tid, fg_tid, False)

        return True
    except Exception as e:
        print(f"Warning: Could not force window focus: {e}")
        return False


def ensure_window_focus_and_debounce(screen=None, focus_timeout_s: float = 2.0, debounce_timeout_s: float = 5.0, show_message: bool = False):
    """
    Ensure the pygame window gets keyboard focus, and optionally debounce held keys.

    This helps when running pygame from MATLAB: MATLAB often remains the foreground window,
    and response-box/keyboard events may go to MATLAB unless we foreground the pygame window.

    Args:
        screen: pygame display surface (optional; only used if show_message=True)
        focus_timeout_s: how long to try focusing the window
        debounce_timeout_s: how long to wait for keys to be released (to prevent a held key
                            from being delivered to MATLAB or immediately acting in pygame)
        show_message: if True, draws a message during debounce; default False (silent)
    """
    # Try to ensure focus
    start = time.time()
    while time.time() - start < focus_timeout_s:
        pygame.event.pump()
        if pygame.key.get_focused():
            break
        _try_focus_window_windows()
        time.sleep(0.05)

    # Clear any queued key events (e.g., repeats)
    try:
        pygame.event.clear()
    except Exception:
        pass

    # Debounce: wait until important keys are released for a brief stable period
    keys_to_check = [
        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_6,
        pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
        pygame.K_RETURN, pygame.K_SPACE,
    ]

    stable_needed_s = 0.2
    stable_start = None
    start = time.time()

    while time.time() - start < debounce_timeout_s:
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        any_pressed = False
        for k in keys_to_check:
            if k < len(pressed) and pressed[k]:
                any_pressed = True
                break

        if not any_pressed:
            if stable_start is None:
                stable_start = time.time()
            if time.time() - stable_start >= stable_needed_s:
                return
        else:
            stable_start = None

        # Intentionally do NOT draw anything by default.
        # (show_message can be enabled for debugging, but is False in experiments.)
        if show_message and screen is not None:
            try:
                font = pygame.font.Font(None, 36)
                msg = "Release buttons to continue..."
                surf = font.render(msg, True, (255, 255, 255))
                rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                screen.blit(surf, rect)
                pygame.display.flip()
            except Exception:
                pass

        time.sleep(0.01)

    # If still held after timeout, continue anyway (but we've at least tried to focus + clear queue)
    print("Warning: Input debounce timeout reached (keys may still be held).")

def setup_screen_selection(screen_number=None):
    """
    Set up screen selection for pygame using screeninfo for proper multi-monitor support.
    
    Args:
        screen_number (int, optional): Screen number to use. If None, uses default behavior.
    
    Returns:
        tuple: (screen, screen_width, screen_height) - pygame screen object and dimensions
    """
    
    # Initialize pygame
    pygame.init()
    
    # Get system info
    system = platform.system()
    print(f"System: {system}")
    
    if screen_number is not None:
        # Use specified screen number with screeninfo
        try:
            # Get list of monitors
            monitors = get_monitors()
            if screen_number >= len(monitors):
                print(f"Invalid monitor index {screen_number}. Only {len(monitors)} monitors available.")
                print("Falling back to default screen.")
                screen_number = None
            else:
                monitor = monitors[screen_number]
                os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor.x},{monitor.y}"
                print(f"Setting display to screen {screen_number} (position: {monitor.x}, {monitor.y})")
                
                # Create borderless window covering entire monitor (avoids fullscreen issues)
                screen = pygame.display.set_mode((monitor.width, monitor.height), pygame.NOFRAME)
                screen_width = monitor.width
                screen_height = monitor.height
                print(f"Borderless window on screen {screen_number}: {screen_width}x{screen_height}")
                ensure_window_focus_and_debounce(screen)
                return screen, screen_width, screen_height
        except Exception as e:
            print(f"Failed to use specified screen {screen_number}, falling back to default: {e}")
            screen_number = None
    
    if screen_number is None:
        # Use hardcoded default screen 0 (primary monitor)
        screen_number = 0
        try:
            monitors = get_monitors()
            if screen_number < len(monitors):
                monitor = monitors[screen_number]
                os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor.x},{monitor.y}"
                screen = pygame.display.set_mode((monitor.width, monitor.height), pygame.NOFRAME)
                screen_width = monitor.width
                screen_height = monitor.height
                print(f"Borderless window on hardcoded screen {screen_number}: {screen_width}x{screen_height}")
                ensure_window_focus_and_debounce(screen)
                return screen, screen_width, screen_height
            else:
                # Fallback to fullscreen if no monitors detected
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                screen_info = pygame.display.Info()
                screen_width = screen_info.current_w
                screen_height = screen_info.current_h
                print(f"Fullscreen mode (fallback): {screen_width}x{screen_height}")
                ensure_window_focus_and_debounce(screen)
                return screen, screen_width, screen_height
        except Exception as e:
            print(f"Failed to use screeninfo, falling back to fullscreen: {e}")
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            screen_info = pygame.display.Info()
            screen_width = screen_info.current_w
            screen_height = screen_info.current_h
            print(f"Fullscreen mode (fallback): {screen_width}x{screen_height}")
            ensure_window_focus_and_debounce(screen)
            return screen, screen_width, screen_height

def get_available_displays():
    """
    Get information about available displays using screeninfo.
    
    Returns:
        list: List of display information dictionaries
    """
    displays = []
    
    try:
        # Use screeninfo to get all monitors
        monitors = get_monitors()
        
        for i, monitor in enumerate(monitors):
            displays.append({
                'index': i,
                'width': monitor.width,
                'height': monitor.height,
                'x': monitor.x,
                'y': monitor.y,
                'bits_per_pixel': 32,  # Default assumption
                'refresh_rate': 60     # Default assumption
            })
        
        print(f"Available displays: {len(displays)}")
        for i, display in enumerate(displays):
            print(f"  Display {i}: {display['width']}x{display['height']} at ({display['x']},{display['y']})")
        
    except Exception as e:
        print(f"Error getting display information: {e}")
        # Fallback to pygame method
        try:
            pygame.display.init()
            display_info = pygame.display.Info()
            displays.append({
                'index': 0,
                'width': display_info.current_w,
                'height': display_info.current_h,
                'x': 0,
                'y': 0,
                'bits_per_pixel': display_info.bitsize,
                'refresh_rate': display_info.refresh_rate if hasattr(display_info, 'refresh_rate') else 0
            })
        except Exception as fallback_e:
            print(f"Fallback method also failed: {fallback_e}")
    
    return displays

def verify_screen_setup(screen_number=None):
    """
    Verify that the screen setup is working correctly.
    
    Args:
        screen_number (int, optional): Screen number to verify
    
    Returns:
        bool: True if setup is successful, False otherwise
    """
    try:
        print(f"\n=== Screen Setup Verification ===")
        print(f"Requested screen: {screen_number if screen_number is not None else 'default'}")
        
        # Get available displays
        displays = get_available_displays()
        
        # Set up screen
        screen, screen_width, screen_height = setup_screen_selection(screen_number)
        
        print(f"✓ Screen setup successful")
        print(f"  Resolution: {screen_width}x{screen_height}")
        print(f"  Screen object: {screen}")
        
        # Test basic pygame functionality
        screen.fill((0, 0, 0))  # Fill with black
        pygame.display.flip()
        
        print(f"✓ Basic pygame functionality test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Screen setup verification failed: {e}")
        return False

if __name__ == "__main__":
    # Test the screen utilities
    print("Testing screen utilities...")
    
    # Test default behavior
    verify_screen_setup()
    
    # Test with screen number (if provided as command line argument)
    if len(sys.argv) > 1:
        try:
            screen_num = int(sys.argv[1])
            verify_screen_setup(screen_num)
        except ValueError:
            print(f"Invalid screen number: {sys.argv[1]}")
    
    pygame.quit()
