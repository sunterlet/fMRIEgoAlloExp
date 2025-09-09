from psychopy import visual, core, event

# Create a window (800x600 pixels with a black background)
win = visual.Window(size=[800, 600], color='black', units='pix')

# Create a text stimulus to display
message = visual.TextStim(win, text="Hello, PsychoPy is working!", color='white', height=30)

# Draw the stimulus and flip the window to update the display
message.draw()
win.flip()

# Wait for a key press to exit
event.waitKeys()

# Clean up: close the window and quit PsychoPy
win.close()
core.quit()
