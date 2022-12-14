import PySimpleGUI as sg
sg.theme('Black')

label1 = sg.Text("Enter workweek:")
input1 = sg.Input(key="workweek")
convert_button = sg.Button("Convert", key="convert")
exit_button = sg.Button("Exit", key="exit")
output_label = sg.Text(key="output", text_color="green")

window = sg.Window("Convertor", layout=[[label1, input1], [convert_button, exit_button, output_label]])

while True:
    event, values = window.read()
    if event == "convert":
        if (values['feet'] == '') or (values['inches'] == ''):
            sg.popup("Enter two numbers")
        else:
            meters = feet_to_meter(values["feet"], values["inches"])
            window["output"].update(value=str(meters) + " m")
    elif event == "exit":
        break

window.close()