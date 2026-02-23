#!/usr/bin/env python3
"""
Utility functions for handling fMRI scanner triggers in Python experiments.

This module provides trigger initialization, waiting, and cleanup functionality
that matches the MATLAB trigger handling behavior.
"""

import sys
import time
from typing import Optional, Tuple

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not available. Trigger functionality will be disabled.", flush=True)


def print_flush(message: str):
    """Print message and flush immediately for real-time output."""
    print(message, flush=True)


class TriggerManager:
    """Manages fMRI scanner trigger connection and waiting."""
    
    def __init__(self, scanning: bool = False, com_port: str = 'com4', baud_rate: int = 9600):
        """
        Initialize TriggerManager.
        
        Args:
            scanning: Whether scanning mode is enabled (requires trigger)
            com_port: Serial port for trigger (e.g., 'com4')
            baud_rate: Baud rate (default: 9600)
        """
        self.scanning = scanning
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.ser = None
        self.initialized = False
        
    def init_trigger(self) -> bool:
        """
        Initialize serial connection for trigger.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not self.scanning:
            return True  # No trigger needed if not scanning
        
        if not SERIAL_AVAILABLE:
            print_flush("Error: pyserial not available. Cannot initialize trigger.")
            return False
        
        try:
            print_flush(f'Initializing trigger on {self.com_port} at {self.baud_rate} baud...')
            self.ser = serial.Serial(
                port=self.com_port,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1  # Short timeout for non-blocking reads
            )
            self.initialized = True
            print_flush(f'✓ Trigger initialized successfully on {self.com_port}')
            return True
        except serial.SerialException as e:
            print_flush(f'✗ Error initializing trigger: {e}')
            return False
        except Exception as e:
            print_flush(f'✗ Unexpected error initializing trigger: {e}')
            return False
    
    def wait_for_trigger(self, timeout: float = 40.0) -> Tuple[bool, float]:
        """
        Wait for scanner trigger signal using DSR (Data Set Ready) pin status.
        
        This mimics the MATLAB behavior of checking PinStatus.DataSetReady.
        The logic detects edge transitions (off->on or on->off) to detect triggers.
        
        Args:
            timeout: Maximum time to wait for trigger in seconds
        
        Returns:
            Tuple of (success: bool, trigger_time: float)
            trigger_time is the time when trigger was received (or timeout time if failed)
        """
        if not self.scanning:
            # If not scanning, return immediately with current time
            return True, time.time()
        
        if not self.initialized or self.ser is None:
            print_flush('✗ Error: Trigger not initialized. Call init_trigger() first.')
            return False, time.time()
        
        print_flush(f'Waiting for scanner trigger (timeout: {timeout:.1f} seconds)...')
        print_flush('CRITICAL: Experiment will NOT continue without trigger!')
        
        start_time = time.time()
        
        try:
            # Get initial pin state
            initial_dsr = self.ser.dsr
            print_flush(f'Initial DSR pin state: {"ON" if initial_dsr else "OFF"}')
            
            # Wait for an edge transition (change in pin state)
            # If pin starts 'off', wait for it to go 'on'
            # If pin starts 'on', wait for it to go 'off'
            if not initial_dsr:  # Pin starts 'off' (low)
                # Wait for pin to go 'on' (high) - this is the trigger
                print_flush('Waiting for DSR pin to transition from OFF to ON...')
                while not self.ser.dsr:
                    if time.time() - start_time >= timeout:
                        # Timeout reached
                        elapsed_time = time.time() - start_time
                        print_flush(f'✗ Timeout: No trigger received within {timeout:.1f} seconds')
                        print_flush('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue.')
                        return False, time.time()
                    time.sleep(0.001)  # Small delay to avoid CPU spinning
                
                # Pin transitioned from OFF to ON - trigger detected!
                trigger_time = time.time()
                print_flush(f'✓ Trigger received at {trigger_time:.3f} seconds (OFF->ON transition)')
                return True, trigger_time
            else:  # Pin starts 'on' (high)
                # Wait for pin to go 'off' (low), then back 'on' (high) - this is the trigger
                print_flush('Waiting for DSR pin to transition from ON to OFF, then OFF to ON...')
                # First wait for it to go off
                while self.ser.dsr:
                    if time.time() - start_time >= timeout:
                        # Timeout reached
                        elapsed_time = time.time() - start_time
                        print_flush(f'✗ Timeout: No trigger received within {timeout:.1f} seconds')
                        print_flush('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue.')
                        return False, time.time()
                    time.sleep(0.001)
                
                # Now wait for it to go back on
                while not self.ser.dsr:
                    if time.time() - start_time >= timeout:
                        # Timeout reached
                        elapsed_time = time.time() - start_time
                        print_flush(f'✗ Timeout: No trigger received within {timeout:.1f} seconds')
                        print_flush('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue.')
                        return False, time.time()
                    time.sleep(0.001)
                
                # Pin transitioned from ON to OFF to ON - trigger detected!
                trigger_time = time.time()
                print_flush(f'✓ Trigger received at {trigger_time:.3f} seconds (ON->OFF->ON transition)')
                return True, trigger_time
            
            # This should never be reached, but just in case
            elapsed_time = time.time() - start_time
            print_flush(f'✗ Timeout: No trigger received within {timeout:.1f} seconds')
            print_flush('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue.')
            return False, time.time()
            
        except serial.SerialException as e:
            print_flush(f'✗ Serial error while waiting for trigger: {e}')
            print_flush('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue.')
            return False, time.time()
        except Exception as e:
            print_flush(f'✗ Unexpected error while waiting for trigger: {e}')
            print_flush('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue.')
            return False, time.time()
    
    def close_trigger(self):
        """Close trigger connection."""
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.close()
                print_flush('✓ Trigger connection closed')
            except Exception as e:
                print_flush(f'⚠ Warning: Error closing trigger connection: {e}')
        self.initialized = False

