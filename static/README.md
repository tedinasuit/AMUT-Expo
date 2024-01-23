Hello reader!
To use this code you will have to install a couple of packages first.
Run this command in a terminal to install all of them at once: pip install Flask Flask-SocketIO tobii-research

To run the program, connect your Tobii pro Spark eye tracker to your device. Then you have to run an external program called 'Tobi eye tracker manager' to be able to calibrate it to your specific display. You can find that here: https://connect.tobii.com/s/etm-downloads?language=en_US. Run the app and turn on the position guide option to fire up the eye tracker. If this is your first time using the eye tracker on a device you will also have to calibrate it. 
You can then minimize the application as it is running in the background. 
If you skip this step the tracker will not work. You can't skip this step :)

That's all the setup taken care of!

Run 'app.py' to start the program.
After that, go to this adress in your browser to view the WebUI: http://127.0.0.1:5000/

There you go!

