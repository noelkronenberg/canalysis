from flask import Flask, render_template, request
from icalendar import Calendar

app = Flask(__name__)

def calculate_hours(ical_data, titles):
    total_hours = {title: 0 for title in titles} # placeholder dictionary
    # iterate through all events
    for event in Calendar.from_ical(ical_data).walk('VEVENT'):
        summary = event.get('SUMMARY')
        # iterate through all requested titles
        for title in titles:
            if title in summary:
                start_time = event.get('DTSTART').dt
                end_time = event.get('DTEND').dt
                total_hours[title] += (end_time - start_time).total_seconds() / 3600 # calculate and assign duration to title
    return total_hours

def calculate_hours_files(files, titles):
    total_hours = {title: 0 for title in titles} # placeholder dictionary
    # iterate through all files
    for file in files:
        # calculate and update total hours (of current file) for each title
        for title, hours in calculate_hours(file.read(), titles).items(): 
            total_hours[title] += hours
    return total_hours

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('ical_files') # get files
        titles = [item.strip() for item in request.form.get('titles').split(',')] # get requested titles
        total_hours = calculate_hours_files(files, titles)
        return render_template('result.html', data=total_hours)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)