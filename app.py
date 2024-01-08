from flask import Flask, render_template, request
from icalendar import Calendar
import recurring_ical_events
import datetime

app = Flask(__name__)

def calculate_hours(files, titles, time_frame):
    total_hours = {title: 0 for title in titles} # placeholder dictionary
    # format start and end date
    start_date = datetime.datetime.strptime(time_frame[0], '%Y-%m-%d').date() # reference: https://stackoverflow.com/a/46468667
    end_date = datetime.datetime.strptime(time_frame[1], '%Y-%m-%d').date() + datetime.timedelta(days=1) # add one day to include end date (reference: https://stackoverflow.com/a/3240493)
     # iterate through all files
    for file in files:
        ical_data = file.read()
        # iterate through all events
        for event in recurring_ical_events.of(Calendar.from_ical(ical_data)).between(start_date, end_date): # reference: https://stackoverflow.com/a/70479313
            summary = event.get('SUMMARY')
            # iterate through all (requested) titles
            for title in titles:
                if title in summary:
                    start_time = event.get('DTSTART').dt
                    end_time = event.get('DTEND').dt
                    total_hours[title] += (end_time - start_time).total_seconds() / 3600 # calculate and assign duration to title
    return total_hours

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('ical_files')
        titles = [item.strip() for item in request.form.get('titles').split(',')]
        from_date = request.form['from']
        to_date = request.form['to']
        total_hours = calculate_hours(files, titles, (from_date, to_date))
        rounded_hours = {k: round(v,2) for k, v in total_hours.items()}
        sorted_hours = dict(sorted(rounded_hours.items(), key=lambda item: item[1], reverse=True))
        return render_template('result.html', data=sorted_hours)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)