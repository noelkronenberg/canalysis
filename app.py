from flask import Flask, render_template, request
from icalendar import Calendar
import recurring_ical_events
import datetime

app = Flask(__name__)

def calculate_hours(ical_data, titles, time_frame):
    total_hours = {title: 0 for title in titles} # placeholder dictionary
    # format start and end date
    start_date = datetime.datetime.strptime(time_frame[0], '%Y-%m-%d').date() # reference: https://stackoverflow.com/a/46468667
    end_date = datetime.datetime.strptime(time_frame[1], '%Y-%m-%d').date() + datetime.timedelta(days=1) # add one day to include end date (reference: https://stackoverflow.com/a/3240493)
    # iterate through all events
    for event in recurring_ical_events.of(Calendar.from_ical(ical_data)).between(start_date, end_date): # reference: https://stackoverflow.com/a/70479313
        summary = event.get('SUMMARY')
        # iterate through all requested titles
        for title in titles:
            if title in summary:
                start_time = event.get('DTSTART').dt
                end_time = event.get('DTEND').dt
                total_hours[title] += (end_time - start_time).total_seconds() / 3600 # calculate and assign duration to title
    return total_hours

def calculate_hours_files(files, titles, time_frame):
    total_hours = {title: 0 for title in titles} # placeholder dictionary
    # iterate through all files
    for file in files:
        # calculate and update total hours (of current file) for each title
        for title, hours in calculate_hours(file.read(), titles, time_frame).items(): 
            total_hours[title] += hours
    return total_hours

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('ical_files') # get files
        titles = [item.strip() for item in request.form.get('titles').split(',')] # get requested titles
        from_date = request.form['from'] # get start date
        to_date = request.form['to'] # get end date
        total_hours = calculate_hours_files(files, titles, (from_date, to_date))
        return render_template('result.html', data=total_hours)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)