# CONFIGURATION INFORMATION


db_host = "HOST IP"
db_user = "username"
db_password = "password"
db_name = "megaporttest"

# INTERNAL NETWORK INFORMATION
internal_net_time = '60'  # please enter the time, in seconds, that you want iperf to run

# TIMING
# Either duration or number of iterations must complete in order for the testing to stop.
iterations = 10000  # Specify the number of iterations this testing should complete,
duration = 48  # Duration and duration value will limit the time the suite will be running for.
duration_value = "hours"  # Please enter seconds, minutes, hours, or days

if duration_value.lower() == "seconds":
    duration = duration
elif duration_value.lower() == "minutes":
    duration = duration * 60
elif duration_value.lower() == "hours":
    duration = duration * 3600
elif duration_value.lower() == "days":
    duration = duration * 86400

# FILE CONFIGURATIONS
# Add files and number of files in the format --> files = [(file_size_in_bytes, no_of_files), ......]
file_config_list = [
                        (128000,1),
						(1280000,10),
                        (1280000,100),
						(128000000,4),
]
