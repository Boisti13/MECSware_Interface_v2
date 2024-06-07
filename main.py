from nicegui import ui

import subprocess
import threading
import json

# Global variables to store the retrieved values
frequency_value = ""
bandwidth_value = ""
power_value = ""

# Create a list of options for each combobox
freq_options = ["3710", "3720", "3730", "3740", "3750", "3760", "3770", "3780", "3790"]
bw_options = ["20", "40", "50", "60", "80", "90", "100"]
ratio_options = ["5:5", "7:3", "4:1"]
power_options = ["10", "12", "14", "16", "18", "20"]

# Initial setup values
ip_initial = "10.0.1.2"
port_initial = "6327"
name_initial = "BS-114"
id_initial = "14"
band_initial = "78"
freq_initial = "3710"
bw_initial = "20"
ratio_initial = "5:5"
power_initial = "10"

# Functions

def clear_console():
    """Clears the console."""
    output_text.clear()

def send_command_message():
    """Displays a message indicating the command is being sent."""
    output_text.set_value("Sending command... Waiting for confirmation.\n")

def trigger_terminal_command_submit_data():
    """Function to trigger the submission of terminal command and clear the console."""
    clear_console()
    send_command_message()
    threading.Thread(target=execute_put_command).start()

def execute_put_command():
    """Function to execute a PUT command using the entered parameters."""
    try:
        # Retrieve values from the input fields
        ip_address = ip_entry.value
        port = port_entry.value
        frequency = freq_combobox.value
        bandwidth = bw_combobox.value
        ratio = ratio_combobox.value
        power = power_combobox.value

        # Construct the command to be executed
        command = (
            f"curl -X PUT https://{ip_address}:{port}/5g/bs/conf -k -u admin:admin -d "
            f"'{{\"Name\": \"BS-114\", \"ID\": \"14\", \"Band\": \"78\", \"Bandwidth\": \"{bandwidth}\", "
            f"\"Frequency\": \"{frequency}\", \"Ratio\": \"{ratio}\", \"Power\": \"{power}\", \"Sync\": \"free\"}}' "
            f"-H \"Content-Type: application/json\" -v"
        )

        # Run the command in a subprocess with a timeout
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout

        # Update the output text widget with the result
        output_text.set_value(output)

        # Check if the data was received successfully
        if "data received" in output.lower():
            output_text.set_value("")
    except subprocess.TimeoutExpired:
        ui.notify("No data received within 30 seconds. Operation timed out.", type='error')
        clear_console()
    except Exception as e:
        ui.notify(f"An error occurred: {e}", type='error')
        clear_console()

def ping_test():
    """Function to execute a ping test to the provided IP address."""
    try:
        # Retrieve the IP address from the input field
        ip_address = ip_entry.value
        clear_console()
        # Run the ping command
        result = subprocess.run(['ping', '-c', '1', ip_address], capture_output=True, text=True)
        output_text.set_value(result.stdout)

        # Show the ping result in a notification
        if result.returncode == 0:
            ui.notify("Ping successful!", type='info')
        else:
            ui.notify("Ping failed!", type='error')
    except Exception as e:
        ui.notify(f"An error occurred: {e}", type='error')

def submit_command():
    """Function to submit a command and show a confirmation message."""
    trigger_terminal_command_submit_data()
    ui.notify("Terminal command executed successfully.", type='info')

def ping_command():
    """Function to start the ping test in a separate thread."""
    threading.Thread(target=ping_test).start()

def show_waiting_message():
    """Function to display a waiting message in the console."""
    clear_console()
    output_text.set_value("Waiting for response from server...\n")

def get_current_data():
    """Function to get the current data from the server."""
    global frequency_value, bandwidth_value, power_value

    try:
        # Retrieve values from the input fields
        ip_address = ip_entry.value
        port = port_entry.value
        name = name_entry.value

        # Construct the command to be executed
        command = (
            f"curl -X GET https://{ip_address}:{port}/5g/bs/status/{name} -k -u admin:admin "
            f"-H \"Content-Type: application/json\" -v"
        )

        show_waiting_message()
        # Run the command in a subprocess with a timeout
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout

        # Update the output text widget with the result
        output_text.set_value(output)

        # Parse the JSON response
        data = json.loads(output)
        frequency_value = data.get("frequency", "")
        bandwidth_value = data.get("bandwidth", "")
        power_value = data.get("tx_power", "")

        # Update the labels with the current data
        current_freq_label.set_text(f"Frequency: {frequency_value}")
        current_bw_label.set_text(f"Bandwidth: {bandwidth_value}")
        current_power_label.set_text(f"Power: {power_value}")

        ui.notify(f"Frequency: {frequency_value}\nBandwidth: {bandwidth_value}\nPower: {power_value}", type='info')
    except subprocess.TimeoutExpired:
        ui.notify("No data received within 30 seconds. Operation timed out.", type='error')
        clear_console()
    except Exception as e:
        ui.notify(f"An error occurred: {e}", type='error')
        clear_console()

# Define UI components
with ui.column().classes('items-stretch') as main_column:
    #ui.label('MECSware Interface').classes('text-h4')
    
    with ui.row():
        ui.label('IP Address:')
        ip_entry = ui.input(value=ip_initial)
        ui.label('Port:')
        port_entry = ui.input(value=port_initial)
        ui.button('Test Connection', on_click=ping_command)

    with ui.row():
        ui.label('Name:')
        name_entry = ui.input(value=name_initial)
        ui.label('ID:')
        id_entry = ui.input(value=id_initial)
        ui.label('Band:')
        band_entry = ui.input(value=band_initial)

    with ui.grid(columns=3):
        ui.label('')
        ui.label('Current Settings').classes('text-h6')
        ui.label('Desired Settings').classes('text-h6')

        ui.label('Frequency:')
        ui.label(frequency_value)
        freq_combobox = ui.select(freq_options, value=freq_initial)

        current_bw_label = ui.label('Bandwidth:')
        ui.label('bandwidth_value')
        bw_combobox = ui.select(bw_options, value=bw_initial)

        ui.label('Ratio:')
        ui.label('')
        ratio_combobox = ui.select(ratio_options, value=ratio_initial)

        current_power_label = ui.label('Power:')
        ui.label('power_value')
        power_combobox = ui.select(power_options, value=power_initial)



    
    with ui.row():
        ui.button('Get Current Data', on_click=get_current_data)
        ui.button('Submit Command', on_click=submit_command)
    
    output_text = ui.textarea().props('rows=10')

# Run the NiceGUI app
ui.run(port=8082)
