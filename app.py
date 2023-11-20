from flask import Flask, render_template, request
from icalendar import Calendar

app = Flask(__name__)

def calculate_total_hours(ical_data, titles_to_track):
    total_hours_by_title = {title: 0 for title in titles_to_track} # placeholder dictionary

    cal = Calendar.from_ical(ical_data)

    # iterate through all events
    for event in cal.walk('VEVENT'):
        summary = event.get('SUMMARY')

        # iterate through all requested titles
        for title in titles_to_track:
            if summary and title in summary:
                start_time = event.get('DTSTART').dt
                end_time = event.get('DTEND').dt

                event_duration = (end_time - start_time).total_seconds() / 3600
                total_hours_by_title[title] += event_duration

    return total_hours_by_title

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        uploaded_file = request.files['ical_file'] # get the calendar file
        titles_to_track = [item.strip() for item in request.form.get('titles').split(',')] # get requested titles as list

        if uploaded_file:
            ical_data = uploaded_file.read()
            total_hours_by_title = calculate_total_hours(ical_data, titles_to_track) # calculate total hours for each title

            return render_template('result.html', total_hours_by_title=total_hours_by_title)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)