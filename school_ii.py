import matplotlib
matplotlib.use('Agg')  #Agg helps to render plots

import pandas as pd
from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import urllib.parse
import logging
logging.basicConfig(level=logging.DEBUG)

#Dummy DataBase
df = pd.read_csv('StudentsPerformance.csv')

df['TotalScore'] = df[['math score', 'reading score', 'writing score']].sum(axis=1)
df['Percentage'] = df['TotalScore'] / 300 * 100

df['Rank'] = df['TotalScore'].rank(ascending=False, method='min')

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student', methods=['POST'])
def student():
    student_id = int(request.form['student_id'])
    student_details = df[df['ID'] == student_id]
    
    if student_details.empty:
        return render_template('student.html', error=f"Student ID {student_id} not found.")
    else:
        student_data = student_details.to_dict(orient='records')[0]
        return render_template('student.html', student=student_data)

@app.route('/top5')
def top5():
    top_students = df.nlargest(5, 'TotalScore')
    top_students = top_students.to_dict(orient='records')
    return render_template('top5.html', students=top_students)

@app.route('/failures')
def failures():
    failed_students = df[df['Percentage'] < 50]
    failed_students = failed_students.to_dict(orient='records')
    return render_template('failures.html', students=failed_students)

@app.route('/distributions')
def distributions():
    def create_distribution_plot(column, title):
        plt.figure(figsize=(10, 6))
        sns.histplot(df[column], kde=True)
        plt.title(title)
        plt.xlabel(column.replace('_', ' ').title())
        plt.ylabel('Frequency')
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        buf.close()
        return uri

    distributions = {
        'math_score': create_distribution_plot('math score', 'Math Score Distribution'),
        'reading_score': create_distribution_plot('reading score', 'Reading Score Distribution'),
        'writing_score': create_distribution_plot('writing score', 'Writing Score Distribution'),
        'total_score': create_distribution_plot('TotalScore', 'Total Score Distribution')
    }

    statistics = {
        'math_score_mean': df['math score'].mean(),
        'reading_score_mean': df['reading score'].mean(),
        'writing_score_mean': df['writing score'].mean(),
        'total_score_mean': df['TotalScore'].mean(),
        'math_score_top_10': df['math score'].quantile(0.90),
        'reading_score_top_10': df['reading score'].quantile(0.90),
        'writing_score_top_10': df['writing score'].quantile(0.90),
        'total_score_top_10': df['TotalScore'].quantile(0.90)
    }

    return render_template('distributions.html', distributions=distributions, statistics=statistics)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
