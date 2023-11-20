from flask import Flask, render_template, request
from icalendar import Calendar

app = Flask(__name__)

def calculate_hours(ical_data, titles):
    total_hours = {title: 0 for title in titles} # placeholder dictionary

    cal = Calendar.from_ical(ical_data)

    # iterate through all events
    for event in cal.walk('VEVENT'):
        summary = event.get('SUMMARY')

        # iterate through all requested titles
        for title in titles:
            if summary and title in summary:
                start_time = event.get('DTSTART').dt
                end_time = event.get('DTEND').dt

                event_duration = (end_time - start_time).total_seconds() / 3600
                total_hours[title] += event_duration

    return total_hours

def calculate_hours_files(files, titles):
    total_hours = {title: 0 for title in titles} # placeholder dictionary

    # iterate through all files
    for file in files:
        ical_data = file.read()
        total_hours_file = calculate_hours(ical_data, titles) # calculate hours for current file

        # update total hours for each title
        for title, hours in total_hours_file.items():
            total_hours[title] += hours

    return total_hours

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('ical_files') # get files
        titles = [item.strip() for item in request.form.get('titles').split(',')] # get requested titles

        if files:
            total_hours = calculate_hours_files(files, titles)
            return render_template('result.html', data=total_hours)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)