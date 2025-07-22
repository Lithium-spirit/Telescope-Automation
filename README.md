# Telescope-Automation

Project Overview: 
Our goal is to automate a manual telescope mount using two stepper motors controlled via an ESP32 microcontroller. We aim to move the telescope based on Right Ascension (RA) and Declination (Dec) coordinates of celestial objects.

1) Hardware Setup:
  We followed the guide from Microcontrollers Lab to connect stepper motors to an A4988 Driver Module and the ESP32.
  However, when we added a second motor, everything worked as expected initially, but the next day, upon connecting the ESP32 to the laptop, the laptop shut down, and the ESP32 began overheating.
  This Issue was resolved by adding a Heatsink to all the components of the setup.
2) Equipment:
  ESP32 microcontroller
  Stepper motors
  A4988 stepper motor drivers
  Wooden Setup to hold telescope
  Rubber belts to move setup using Stepper motor
3) Software :
  We have a Python script that generates the RA and Dec coordinates of a celestial body.
  We convert these coordinates into stepper motor movements.
  We use both the conveyer belts to cause motion in RA and DEC.
  ESP32 Compatibility: Adapted the Python code to run on ESP32.

The Python code for RA-Dec coordinate generation can be found in the repository.
